""
Quality Inspector Module
----------------------
Implements AI-based quality inspection and verification for products.
"""

import cv2
import numpy as np
import logging
import os
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

class QualityInspector:
    """Handles quality inspection of products using computer vision and AI."""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the quality inspector with an optional pre-trained model.
        
        Args:
            model_path: Path to a pre-trained model file
        """
        self.model = None
        self.labels = {}
        self.min_confidence = 0.7
        self.initialize_model(model_path)
        
        # Initialize default product specifications
        self.product_specs = self._load_default_specs()
    
    def initialize_model(self, model_path: Optional[str] = None):
        """Initialize the AI model for quality inspection.
        
        Args:
            model_path: Optional path to a custom model file
        """
        try:
            # In a real implementation, this would load a pre-trained model
            # For this example, we'll use a placeholder
            if model_path and os.path.exists(model_path):
                logger.info(f"Loading model from {model_path}")
                # Load model logic here
                # self.model = load_model(model_path)
            else:
                logger.info("Using default quality inspection model")
                # Initialize with default weights or configurations
                
            logger.info("Quality inspection model initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize quality inspection model: {e}")
            raise
    
    def _load_default_specs(self) -> Dict[str, Dict[str, Any]]:
        """Load default product specifications.
        
        Returns:
            Dictionary containing product specifications
        """
        return {
            'DEV001': {  # Arduino Nano
                'name': 'Arduino Nano',
                'dimensions': {'length': 45, 'width': 18, 'height': 7.5},  # mm
                'weight': 7,  # grams
                'rohs_compliant': True,
                'required_components': ['USB Connector', 'Microcontroller', 'Pins'],
                'tolerances': {
                    'dimensions': 0.5,  # mm
                    'weight': 0.2,  # grams
                }
            },
            'DEV002': {  # Raspberry Pi
                'name': 'Raspberry Pi',
                'dimensions': {'length': 85, 'width': 56, 'height': 17},  # mm
                'weight': 45,  # grams
                'rohs_compliant': True,
                'required_components': ['HDMI Port', 'USB Ports', 'GPIO Pins', 'Ethernet Port'],
                'tolerances': {
                    'dimensions': 0.8,  # mm
                    'weight': 2.0,  # grams
                }
            },
            'DEV003': {  # ESP32 Module
                'name': 'ESP32 Module',
                'dimensions': {'length': 25, 'width': 13, 'height': 3},  # mm
                'weight': 3,  # grams
                'rohs_compliant': True,
                'required_components': ['Antenna', 'Chip', 'Pins'],
                'tolerances': {
                    'dimensions': 0.3,  # mm
                    'weight': 0.1,  # grams
                }
            }
        }
    
    def analyze_product(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze a product image to extract relevant information.
        
        Args:
            image: Input image of the product (numpy array in RGB format)
            
        Returns:
            Dictionary containing product information
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid or empty image provided")
        
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Detect product type (simplified for example)
            product_type = self._detect_product_type(image)
            
            # Check for defects
            has_defects, defects = self._detect_defects(image, product_type)
            
            # Verify components
            components_present = self._verify_components(image, product_type)
            
            # Check RoHS compliance (simulated)
            is_rohs_compliant = self._check_rohs_compliance(image, product_type)
            
            # Generate a unique ID for this product
            product_id = self._generate_product_id(product_type)
            
            # Get current timestamp
            timestamp = datetime.now().isoformat()
            
            # Compile results
            result = {
                'product_id': product_id,
                'product_type': product_type,
                'batch_id': f"BATCH-{product_type}-{timestamp[:10].replace('-', '')}",
                'manufacturing_date': timestamp[:10],  # YYYY-MM-DD
                'rohs_compliant': is_rohs_compliant,
                'has_defects': has_defects,
                'defects': defects,
                'components_present': components_present,
                'inspection_timestamp': timestamp,
                'image_dimensions': {
                    'height': image.shape[0],
                    'width': image.shape[1],
                    'channels': image.shape[2] if len(image.shape) > 2 else 1
                }
            }
            
            logger.info(f"Product analysis complete: {result['product_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing product: {e}")
            raise
    
    def _detect_product_type(self, image: np.ndarray) -> str:
        """Detect the type of product in the image.
        
        Args:
            image: Input image of the product
            
        Returns:
            Product type ID (e.g., 'DEV001')
        """
        # In a real implementation, this would use a trained model
        # For this example, we'll use a simple size-based detection
        height, width = image.shape[:2]
        
        # Simple size-based detection (very simplified for example)
        if width > 500:  # Raspberry Pi is larger
            return 'DEV002'
        elif width > 200:  # Arduino Nano
            return 'DEV001'
        else:  # ESP32 is smallest
            return 'DEV003'
    
    def _detect_defects(self, image: np.ndarray, product_type: str) -> Tuple[bool, list]:
        """Detect defects in the product image.
        
        Args:
            image: Input image of the product
            product_type: Type of product being inspected
            
        Returns:
            Tuple of (has_defects, defects_list)
        """
        # In a real implementation, this would use computer vision or ML
        # For this example, we'll simulate defect detection
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Simple edge detection (Canny)
        edges = cv2.Canny(gray, 50, 150)
        
        # Count white pixels (edges)
        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.shape[0] * edges.shape[1]
        edge_ratio = edge_pixels / total_pixels
        
        # Simulate defects based on edge ratio (just for example)
        defects = []
        has_defects = False
        
        # Check for scratches (high edge density)
        if edge_ratio > 0.1:  # Arbitrary threshold
            defects.append({
                'type': 'scratch',
                'severity': 'high' if edge_ratio > 0.15 else 'low',
                'confidence': min(0.95, edge_ratio * 5)  # Scale to 0-0.95
            })
            has_defects = True
        
        # Check for missing components (placeholder)
        if np.random.random() < 0.1:  # 10% chance of simulated missing component
            defects.append({
                'type': 'missing_component',
                'component': 'resistor' if np.random.random() > 0.5 else 'capacitor',
                'severity': 'critical',
                'confidence': 0.85
            })
            has_defects = True
        
        return has_defects, defects
    
    def _verify_components(self, image: np.ndarray, product_type: str) -> Dict[str, bool]:
        """Verify that all required components are present.
        
        Args:
            image: Input image of the product
            product_type: Type of product being inspected
            
        Returns:
            Dictionary mapping component names to presence status
        """
        # In a real implementation, this would use object detection
        # For this example, we'll return random results
        
        if product_type not in self.product_specs:
            logger.warning(f"Unknown product type: {product_type}")
            return {}
        
        required_components = self.product_specs[product_type].get('required_components', [])
        components_status = {}
        
        for component in required_components:
            # Simulate component detection (90% accuracy)
            components_status[component] = np.random.random() > 0.1
        
        return components_status
    
    def _check_rohs_compliance(self, image: np.ndarray, product_type: str) -> bool:
        """Check if the product is RoHS compliant.
        
        Args:
            image: Input image of the product
            product_type: Type of product being inspected
            
        Returns:
            bool: True if RoHS compliant, False otherwise
        """
        # In a real implementation, this might involve:
        # 1. Checking material composition (via spectroscopy or database)
        # 2. Verifying compliance certificates
        # 3. Physical inspection for RoHS labels/markings
        
        # For this example, we'll use the product specification
        if product_type in self.product_specs:
            return self.product_specs[product_type].get('rohs_compliant', False)
        
        return False
    
    def _generate_product_id(self, product_type: str) -> str:
        """Generate a unique product ID.
        
        Args:
            product_type: Type of product
            
        Returns:
            Unique product ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = f"{np.random.randint(1000, 9999):04d}"
        return f"{product_type}-{timestamp}-{random_suffix}"
    
    def verify_quality(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """Verify the quality of a product based on inspection results.
        
        Args:
            product_info: Dictionary containing product information from analyze_product()
            
        Returns:
            Dictionary with quality verification results
        """
        if not product_info:
            return {
                'passed': False,
                'reason': 'No product information provided',
                'score': 0.0
            }
        
        # Initialize quality score (0.0 to 1.0)
        quality_score = 1.0
        reasons = []
        
        # Check for defects
        if product_info.get('has_defects', False):
            defect_severity = max(
                [d.get('severity', 'low') for d in product_info.get('defects', [])],
                key=lambda x: {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}.get(x, 0)
            )
            
            # Adjust score based on defect severity
            severity_weights = {
                'low': 0.1,
                'medium': 0.3,
                'high': 0.6,
                'critical': 1.0
            }
            
            quality_score -= severity_weights.get(defect_severity, 0.0)
            reasons.append(f"Found {defect_severity} severity defects")
        
        # Check for missing components
        components_present = product_info.get('components_present', {})
        missing_components = [
            comp for comp, present in components_present.items() 
            if not present
        ]
        
        if missing_components:
            quality_score -= 0.5  # Significant penalty for missing components
            reasons.append(f"Missing components: {', '.join(missing_components)}")
        
        # Check RoHS compliance
        if not product_info.get('rohs_compliant', False):
            quality_score = 0.0  # Automatic fail for non-compliant products
            reasons.append("Product is not RoHS compliant")
        
        # Ensure score is within bounds
        quality_score = max(0.0, min(1.0, quality_score))
        
        # Determine pass/fail
        passed = quality_score >= 0.7  # 70% threshold for passing
        
        if passed:
            reasons.append("Product meets all quality standards")
        
        return {
            'passed': passed,
            'score': quality_score,
            'reasons': reasons,
            'timestamp': datetime.now().isoformat()
        }


def test_quality_inspector():
    """Test function for the QualityInspector class."""
    import matplotlib.pyplot as plt
    
    print("Testing QualityInspector...")
    
    try:
        # Create a test image (solid color as a placeholder)
        test_image = np.ones((300, 400, 3), dtype=np.uint8) * 200
        
        # Add some random noise to simulate a real image
        noise = np.random.normal(0, 25, test_image.shape).astype(np.uint8)
        test_image = cv2.add(test_image, noise)
        
        # Initialize the quality inspector
        inspector = QualityInspector()
        
        # Analyze the test image
        print("\nAnalyzing test product...")
        product_info = inspector.analyze_product(test_image)
        
        # Print analysis results
        print("\nProduct Analysis Results:")
        print(f"Product ID: {product_info['product_id']}")
        print(f"Product Type: {product_info['product_type']}")
        print(f"Batch ID: {product_info['batch_id']}")
        print(f"Manufacturing Date: {product_info['manufacturing_date']}")
        print(f"RoHS Compliant: {'Yes' if product_info['rohs_compliant'] else 'No'}")
        print(f"Defects Found: {len(product_info['defects']) if product_info['has_defects'] else 'None'}")
        
        if product_info['has_defects']:
            print("\nDetected Defects:")
            for i, defect in enumerate(product_info['defects'], 1):
                print(f"  {i}. Type: {defect['type']}, Severity: {defect['severity']}, "
                      f"Confidence: {defect['confidence']:.2f}")
        
        print("\nComponent Status:")
        for component, present in product_info['components_present'].items():
            print(f"  - {component}: {'✓' if present else '✗'}")
        
        # Verify quality
        print("\nVerifying quality...")
        quality_result = inspector.verify_quality(product_info)
        
        print(f"\nQuality Verification:")
        print(f"Status: {'PASSED' if quality_result['passed'] else 'FAILED'}")
        print(f"Quality Score: {quality_result['score']:.2f}/1.00")
        print("\nDetails:")
        for reason in quality_result['reasons']:
            print(f"- {reason}")
        
        # Display the test image
        plt.figure(figsize=(10, 8))
        plt.imshow(cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB))
        plt.title("Test Product Image")
        plt.axis('off')
        plt.show()
        
        print("\nQuality inspection test completed successfully!")
        
    except Exception as e:
        print(f"Error during quality inspection test: {e}")
        raise


if __name__ == "__main__":
    test_quality_inspector()
