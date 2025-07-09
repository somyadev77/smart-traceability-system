"""
Smart Product Traceability System
-------------------------------
A comprehensive system for automated product labeling, quality verification,
and traceability in manufacturing environments.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traceability_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SmartTraceabilitySystem:
    """Main class for the Smart Product Traceability System."""
    
    def __init__(self):
        """Initialize the traceability system with default configuration."""
        self.running = False
        self.version = "2.0.0"
        self.start_time = datetime.now()
        self.initialize_components()
        
    def initialize_components(self):
        """Initialize all system components."""
        try:
            # Import components
            from hardware.camera import CameraSystem
            from hardware.actuators import ActuatorSystem
            from ai.quality_inspector import QualityInspector
            from utils.database import DatabaseManager
            from utils.label_generator import LabelGenerator
            
            # Initialize components
            self.camera = CameraSystem()
            self.actuators = ActuatorSystem()
            self.quality_inspector = QualityInspector()
            self.database = DatabaseManager('traceability.db')
            self.label_generator = LabelGenerator()
            
            logger.info("All system components initialized successfully.")
            
        except ImportError as e:
            logger.error(f"Failed to initialize system components: {e}")
            raise
    
    def start(self):
        """Start the traceability system."""
        if self.running:
            logger.warning("System is already running.")
            return
            
        logger.info(f"Starting Smart Product Traceability System v{self.version}")
        self.running = True
        
        try:
            self.main_loop()
        except KeyboardInterrupt:
            logger.info("Shutdown signal received.")
        except Exception as e:
            logger.error(f"System error: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def main_loop(self):
        """Main processing loop of the system."""
        logger.info("Entering main processing loop...")
        
        while self.running:
            try:
                # 1. Capture product image
                product_image = self.camera.capture_image()
                
                # 2. Process product image and extract information
                product_info = self.quality_inspector.analyze_product(product_image)
                
                # 3. Verify product quality and compliance
                inspection_result = self.quality_inspector.verify_quality(product_info)
                
                # 4. Generate and apply label if product passes inspection
                if inspection_result["passed"]:
                    label_image = self.label_generator.generate_label(product_info)
                    self.actuators.apply_label(label_image)
                    logger.info(f"Label applied to product {product_info['product_id']}")
                else:
                    self.actuators.reject_product()
                    logger.warning(f"Product rejected: {inspection_result['reason']}")
                
                # 5. Log the transaction
                self.database.log_transaction(
                    product_id=product_info['product_id'],
                    batch_id=product_info['batch_id'],
                    status="PASSED" if inspection_result["passed"] else "REJECTED",
                    timestamp=datetime.now().isoformat(),
                    metadata={
                        'inspection_result': inspection_result,
                        'product_info': product_info
                    }
                )
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                # Add error recovery logic here
                
    def shutdown(self):
        """Safely shut down the system."""
        logger.info("Initiating system shutdown...")
        self.running = False
        
        # Clean up resources
        try:
            self.camera.cleanup()
            self.actuators.cleanup()
            self.database.close()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        uptime = datetime.now() - self.start_time
        logger.info(f"System shutdown complete. Uptime: {uptime}")


def main():
    """Entry point for the application."""
    try:
        app = SmartTraceabilitySystem()
        app.start()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
