""
Camera System Module
-------------------
Handles all camera-related functionality for product image capture.
"""

import cv2
import numpy as np
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class CameraSystem:
    """Manages camera operations for the traceability system."""
    
    def __init__(self, camera_index: int = 0, resolution: Tuple[int, int] = (1920, 1080)):
        """Initialize the camera system.
        
        Args:
            camera_index: Index of the camera to use (default: 0)
            resolution: Tuple of (width, height) for camera resolution (default: 1920x1080)
        """
        self.camera = None
        self.camera_index = camera_index
        self.resolution = resolution
        self.initialize_camera()
    
    def initialize_camera(self):
        """Initialize the camera with specified settings."""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            if not self.camera.isOpened():
                raise RuntimeError(f"Could not open camera at index {self.camera_index}")
                
            logger.info(f"Camera initialized at {self.resolution[0]}x{self.resolution[1]}")
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            self.cleanup()
            raise
    
    def capture_image(self, save_path: Optional[str] = None) -> np.ndarray:
        """Capture an image from the camera.
        
        Args:
            save_path: Optional path to save the captured image
            
        Returns:
            Captured image as a numpy array in BGR format
        """
        if not self.camera or not self.camera.isOpened():
            self.initialize_camera()
            
        ret, frame = self.camera.read()
        
        if not ret:
            raise RuntimeError("Failed to capture image from camera")
        
        # Convert to RGB for better compatibility with other libraries
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if save_path:
            cv2.imwrite(save_path, frame)
            logger.info(f"Image saved to {save_path}")
        
        return frame_rgb
    
    def capture_multiple(self, count: int = 3, interval: float = 0.5) -> list:
        """Capture multiple images with a specified interval.
        
        Args:
            count: Number of images to capture
            interval: Time in seconds between captures
            
        Returns:
            List of captured images
        """
        import time
        images = []
        
        for i in range(count):
            logger.info(f"Capturing image {i+1}/{count}")
            try:
                img = self.capture_image()
                images.append(img)
                if i < count - 1:  # No need to wait after the last image
                    time.sleep(interval)
            except Exception as e:
                logger.error(f"Error capturing image {i+1}: {e}")
                
        return images
    
    def set_resolution(self, width: int, height: int):
        """Set the camera resolution.
        
        Args:
            width: Desired frame width
            height: Desired frame height
        """
        if self.camera and self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.resolution = (width, height)
            logger.info(f"Camera resolution set to {width}x{height}")
    
    def get_camera_properties(self) -> dict:
        """Get the current camera properties.
        
        Returns:
            Dictionary containing camera properties
        """
        if not self.camera or not self.camera.isOpened():
            return {}
            
        return {
            'width': int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': self.camera.get(cv2.CAP_PROP_FPS),
            'brightness': self.camera.get(cv2.CAP_PROP_BRIGHTNESS),
            'contrast': self.camera.get(cv2.CAP_PROP_CONTRAST),
            'saturation': self.camera.get(cv2.CAP_PROP_SATURATION),
            'hue': self.camera.get(cv2.CAP_PROP_HUE),
            'gain': self.camera.get(cv2.CAP_PROP_GAIN),
            'exposure': self.camera.get(cv2.CAP_PROP_EXPOSURE)
        }
    
    def cleanup(self):
        """Release camera resources."""
        if hasattr(self, 'camera') and self.camera is not None:
            if self.camera.isOpened():
                self.camera.release()
            logger.info("Camera resources released")
    
    def __del__(self):
        """Destructor to ensure camera is properly released."""
        self.cleanup()


def test_camera():
    """Test function for the camera module."""
    import os
    import tempfile
    
    print("Testing CameraSystem...")
    
    # Create a temporary directory for test images
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Initialize camera
            camera = CameraSystem()
            
            # Test single image capture
            print("Capturing single image...")
            img_path = os.path.join(temp_dir, "test_capture.jpg")
            img = camera.capture_image(save_path=img_path)
            print(f"Image captured: {img.shape} (HxWxC)")
            
            # Test multiple image capture
            print("\nCapturing multiple images...")
            images = camera.capture_multiple(count=2)
            print(f"Captured {len(images)} images")
            
            # Test camera properties
            print("\nCamera properties:")
            props = camera.get_camera_properties()
            for key, value in props.items():
                print(f"{key}: {value}")
                
            print("\nCamera test completed successfully!")
            
        except Exception as e:
            print(f"Error during camera test: {e}")
            raise


if __name__ == "__main__":
    test_camera()
