""
Actuator System Module
---------------------
Manages all actuator operations for the traceability system,
including label application and product rejection mechanisms.
"""

import time
import logging
from typing import Optional, Dict, Any
import serial
import RPi.GPIO as GPIO

# Set up logging
logger = logging.getLogger(__name__)

class ActuatorSystem:
    """Manages all actuator operations in the traceability system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the actuator system with configuration.
        
        Args:
            config: Dictionary containing configuration for actuators
        """
        self.config = config or self._get_default_config()
        self.initialized = False
        self.printer = None
        self._initialize_actuators()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for actuators.
        
        Returns:
            Dictionary with default configuration
        """
        return {
            'label_printer': {
                'enabled': True,
                'type': 'serial',  # 'serial', 'network', or 'simulated'
                'port': '/dev/ttyUSB0',  # For serial printers
                'baudrate': 9600,
                'timeout': 5,
            },
            'rejection_mechanism': {
                'enabled': True,
                'type': 'gpio',  # 'gpio', 'pneumatic', or 'simulated'
                'gpio_pin': 17,  # For GPIO-based rejection
                'activation_time': 0.5,  # seconds
            },
            'conveyor': {
                'enabled': True,
                'type': 'gpio',  # 'gpio', 'relay', or 'simulated'
                'speed_control_pin': 18,  # PWM pin for speed control
                'direction_pin': 23,  # For direction control if applicable
            }
        }
    
    def _initialize_actuators(self):
        """Initialize all actuators based on configuration."""
        try:
            # Initialize label printer
            if self.config['label_printer']['enabled']:
                self._initialize_printer()
            
            # Initialize rejection mechanism
            if self.config['rejection_mechanism']['enabled']:
                self._initialize_rejection_mechanism()
            
            # Initialize conveyor control
            if self.config['conveyor']['enabled']:
                self._initialize_conveyor()
            
            self.initialized = True
            logger.info("Actuator system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize actuators: {e}")
            self.cleanup()
            raise
    
    def _initialize_printer(self):
        """Initialize the label printer."""
        printer_config = self.config['label_printer']
        
        if printer_config['type'] == 'serial':
            try:
                self.printer = serial.Serial(
                    port=printer_config['port'],
                    baudrate=printer_config['baudrate'],
                    timeout=printer_config['timeout']
                )
                logger.info(f"Label printer initialized on {printer_config['port']}")
            except Exception as e:
                logger.error(f"Failed to initialize label printer: {e}")
                self.printer = None
        
        elif printer_config['type'] == 'simulated':
            logger.info("Using simulated label printer")
            self.printer = None
        
        else:
            logger.warning(f"Unsupported printer type: {printer_config['type']}")
    
    def _initialize_rejection_mechanism(self):
        """Initialize the product rejection mechanism."""
        rejection_config = self.config['rejection_mechanism']
        
        if rejection_config['type'] == 'gpio':
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(rejection_config['gpio_pin'], GPIO.OUT)
                GPIO.output(rejection_config['gpio_pin'], GPIO.LOW)
                logger.info(f"Rejection mechanism initialized on GPIO {rejection_config['gpio_pin']}")
            except Exception as e:
                logger.error(f"Failed to initialize rejection mechanism: {e}")
        
        elif rejection_config['type'] == 'simulated':
            logger.info("Using simulated rejection mechanism")
        
        else:
            logger.warning(f"Unsupported rejection mechanism type: {rejection_config['type']}")
    
    def _initialize_conveyor(self):
        """Initialize the conveyor control."""
        conveyor_config = self.config['conveyor']
        
        if conveyor_config['type'] == 'gpio':
            try:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(conveyor_config['speed_control_pin'], GPIO.OUT)
                if 'direction_pin' in conveyor_config:
                    GPIO.setup(conveyor_config['direction_pin'], GPIO.OUT)
                self.conveyor_pwm = GPIO.PWM(conveyor_config['speed_control_pin'], 1000)  # 1kHz
                self.conveyor_pwm.start(0)  # Start with 0% duty cycle (stopped)
                logger.info("Conveyor control initialized")
            except Exception as e:
                logger.error(f"Failed to initialize conveyor control: {e}")
        
        elif conveyor_config['type'] == 'simulated':
            logger.info("Using simulated conveyor control")
        
        else:
            logger.warning(f"Unsupported conveyor control type: {conveyor_config['type']}")
    
    def apply_label(self, label_data: Any, product_info: Optional[Dict] = None) -> bool:
        """Apply a label to the product.
        
        Args:
            label_data: The label data to print (image or text)
            product_info: Additional product information for the label
            
        Returns:
            bool: True if label was applied successfully, False otherwise
        """
        if not self.initialized or not self.config['label_printer']['enabled']:
            logger.warning("Label printer is not enabled or initialized")
            return False
        
        try:
            if self.printer is not None:
                # For real printers, you would format the label data appropriately
                # and send it to the printer. This is a simplified example.
                if isinstance(label_data, str):
                    # If label_data is a string, encode and send it
                    self.printer.write(label_data.encode())
                else:
                    # For binary data (like images), send as is
                    self.printer.write(label_data)
                
                logger.info("Label sent to printer")
            else:
                # Simulate printing delay
                time.sleep(1.0)
                logger.info("Simulated label printing")
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying label: {e}")
            return False
    
    def reject_product(self) -> bool:
        """Activate the rejection mechanism to remove a product from the line.
        
        Returns:
            bool: True if rejection was successful, False otherwise
        """
        if not self.initialized or not self.config['rejection_mechanism']['enabled']:
            logger.warning("Rejection mechanism is not enabled or initialized")
            return False
        
        try:
            rejection_config = self.config['rejection_mechanism']
            
            if rejection_config['type'] == 'gpio':
                # Activate the rejection mechanism (e.g., a solenoid or air valve)
                GPIO.output(rejection_config['gpio_pin'], GPIO.HIGH)
                time.sleep(rejection_config['activation_time'])
                GPIO.output(rejection_config['gpio_pin'], GPIO.LOW)
                
                logger.info("Product rejected")
                return True
                
            elif rejection_config['type'] == 'simulated':
                logger.info("Simulated product rejection")
                return True
                
            else:
                logger.warning(f"Unsupported rejection mechanism: {rejection_config['type']}")
                return False
                
        except Exception as e:
            logger.error(f"Error rejecting product: {e}")
            return False
    
    def set_conveyor_speed(self, speed: float) -> bool:
        """Set the conveyor belt speed.
        
        Args:
            speed: Speed value (0.0 to 100.0)
            
        Returns:
            bool: True if speed was set successfully, False otherwise
        """
        if not self.initialized or not self.config['conveyor']['enabled']:
            logger.warning("Conveyor control is not enabled or initialized")
            return False
        
        try:
            # Clamp speed to valid range
            speed = max(0.0, min(100.0, speed))
            
            conveyor_config = self.config['conveyor']
            
            if conveyor_config['type'] == 'gpio':
                # Set PWM duty cycle to control speed
                self.conveyor_pwm.ChangeDutyCycle(speed)
                logger.info(f"Conveyor speed set to {speed}%")
                return True
                
            elif conveyor_config['type'] == 'simulated':
                logger.info(f"Simulated conveyor speed set to {speed}%")
                return True
                
            else:
                logger.warning(f"Unsupported conveyor control type: {conveyor_config['type']}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting conveyor speed: {e}")
            return False
    
    def stop_conveyor(self) -> bool:
        """Stop the conveyor belt.
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self.set_conveyor_speed(0.0)
    
    def cleanup(self):
        """Clean up resources used by the actuators."""
        try:
            # Stop the conveyor
            if hasattr(self, 'conveyor_pwm'):
                self.conveyor_pwm.stop()
            
            # Close the printer connection
            if hasattr(self, 'printer') and self.printer is not None:
                self.printer.close()
            
            # Clean up GPIO
            if any([
                self.config['rejection_mechanism']['enabled'] and 
                self.config['rejection_mechanism']['type'] == 'gpio',
                self.config['conveyor']['enabled'] and 
                self.config['conveyor']['type'] == 'gpio'
            ]):
                GPIO.cleanup()
            
            self.initialized = False
            logger.info("Actuator system cleaned up")
            
        except Exception as e:
            logger.error(f"Error during actuator cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure resources are properly released."""
        self.cleanup()


def test_actuators():
    """Test function for the actuators module."""
    import time
    
    print("Testing ActuatorSystem...")
    
    # Use simulated actuators for testing
    config = {
        'label_printer': {'enabled': True, 'type': 'simulated'},
        'rejection_mechanism': {'enabled': True, 'type': 'simulated', 'activation_time': 0.5},
        'conveyor': {'enabled': True, 'type': 'simulated'}
    }
    
    try:
        # Initialize actuator system
        actuators = ActuatorSystem(config)
        
        # Test conveyor control
        print("\nTesting conveyor control...")
        print("Starting conveyor at 50% speed")
        actuators.set_conveyor_speed(50.0)
        time.sleep(2.0)
        
        print("Stopping conveyor")
        actuators.stop_conveyor()
        
        # Test label application
        print("\nTesting label application...")
        test_label = "TEST_LABEL_12345"
        if actuators.apply_label(test_label):
            print(f"Label applied: {test_label}")
        
        # Test product rejection
        print("\nTesting product rejection...")
        if actuators.reject_product():
            print("Product rejected successfully")
        
        # Clean up
        actuators.cleanup()
        print("\nActuator test completed successfully!")
        
    except Exception as e:
        print(f"Error during actuator test: {e}")
        raise


if __name__ == "__main__":
    test_actuators()
