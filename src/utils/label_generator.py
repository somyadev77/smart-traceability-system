""
Label Generator Module
---------------------
Handles the generation of product labels with QR codes, barcodes, and other product information.
"""

import qrcode
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import os
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import textwrap

# Set up logging
logger = logging.getLogger(__name__)

class LabelGenerator:
    """Generates product labels with various formats and information."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the label generator with configuration.
        
        Args:
            config: Configuration dictionary for label generation
        """
        self.config = config or self._get_default_config()
        self.fonts = self._load_fonts()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for label generation.
        
        Returns:
            Dictionary with default configuration
        """
        return {
            'label': {
                'width': 800,  # pixels
                'height': 500,  # pixels
                'dpi': 300,  # dots per inch
                'background_color': (255, 255, 255),  # white
                'margin': 20,  # pixels
                'padding': 15,  # pixels
                'corner_radius': 10,  # pixels
                'border_width': 2,  # pixels
                'border_color': (0, 0, 0),  # black
            },
            'header': {
                'height': 60,  # pixels
                'background_color': (41, 128, 185),  # blue
                'text_color': (255, 255, 255),  # white
                'font_size': 24,
            },
            'content': {
                'text_color': (0, 0, 0),  # black
                'font_size': 14,
                'line_spacing': 5,  # pixels
                'section_spacing': 15,  # pixels
            },
            'qr_code': {
                'size': 150,  # pixels
                'border': 2,  # modules
                'error_correction': qrcode.constants.ERROR_CORRECT_H,  # High error correction
                'fill_color': (0, 0, 0),  # black
                'back_color': (255, 255, 255),  # white
            },
            'barcode': {
                'height': 60,  # pixels
                'write_text': False,  # Don't show text under barcode
                'text_distance': 2,  # pixels from barcode to text
            },
            'footer': {
                'height': 30,  # pixels
                'background_color': (236, 240, 241),  # light gray
                'text_color': (127, 140, 141),  # dark gray
                'font_size': 10,
            },
        }
    
    def _load_fonts(self) -> Dict[str, Any]:
        """Load fonts for label generation.
        
        Returns:
            Dictionary containing font objects
        """
        fonts = {}
        try:
            # Try to load a nice font if available, otherwise fall back to default
            try:
                fonts['header'] = ImageFont.truetype("arialbd.ttf", 
                    self.config['header']['font_size'])
                fonts['content'] = ImageFont.truetype("arial.ttf", 
                    self.config['content']['font_size'])
                fonts['footer'] = ImageFont.truetype("arial.ttf", 
                    self.config['footer']['font_size'])
            except IOError:
                # Fall back to default fonts if specified fonts are not available
                fonts['header'] = ImageFont.load_default()
                fonts['content'] = ImageFont.load_default()
                fonts['footer'] = ImageFont.load_default()
                
        except Exception as e:
            logger.warning(f"Could not load fonts: {e}. Using default fonts.")
            fonts = {
                'header': ImageFont.load_default(),
                'content': ImageFont.load_default(),
                'footer': ImageFont.load_default(),
            }
            
        return fonts
    
    def generate_label(self, product_info: Dict[str, Any]) -> Image.Image:
        """Generate a product label with the given information.
        
        Args:
            product_info: Dictionary containing product information
            
        Returns:
            PIL Image object containing the generated label
        """
        try:
            # Create a new image with white background
            label = Image.new(
                'RGB',
                (self.config['label']['width'], self.config['label']['height']),
                self.config['label']['background_color']
            )
            
            # Get drawing context
            draw = ImageDraw.Draw(label)
            
            # Draw header
            self._draw_header(draw, product_info)
            
            # Draw content area
            content_y = self._draw_content(draw, product_info)
            
            # Draw QR code
            self._draw_qr_code(label, product_info, content_y)
            
            # Draw barcode
            self._draw_barcode(label, product_info, content_y)
            
            # Draw footer
            self._draw_footer(draw, product_info)
            
            # Draw border
            self._draw_border(draw)
            
            logger.info(f"Generated label for product {product_info.get('product_id', 'unknown')}")
            return label
            
        except Exception as e:
            logger.error(f"Error generating label: {e}")
            raise
    
    def _draw_header(self, draw: ImageDraw.Draw, product_info: Dict[str, Any]):
        """Draw the header section of the label.
        
        Args:
            draw: ImageDraw object for drawing
            product_info: Dictionary containing product information
        """
        try:
            header_config = self.config['header']
            label_config = self.config['label']
            
            # Draw header background
            header_box = [
                (0, 0),
                (label_config['width'], header_config['height'])
            ]
            draw.rectangle(header_box, fill=header_config['background_color'])
            
            # Draw title
            title = product_info.get('product_type', 'PRODUCT LABEL')
            title_bbox = draw.textbbox((0, 0), title, font=self.fonts['header'])
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            
            title_x = (label_config['width'] - title_width) // 2
            title_y = (header_config['height'] - title_height) // 2
            
            draw.text(
                (title_x, title_y),
                title,
                fill=header_config['text_color'],
                font=self.fonts['header']
            )
            
        except Exception as e:
            logger.error(f"Error drawing header: {e}")
            raise
    
    def _draw_content(self, draw: ImageDraw.Draw, product_info: Dict[str, Any]) -> int:
        """Draw the main content area of the label.
        
        Args:
            draw: ImageDraw object for drawing
            product_info: Dictionary containing product information
            
        Returns:
            Y-coordinate where the content ends
        """
        try:
            label_config = self.config['label']
            content_config = self.config['content']
            header_height = self.config['header']['height']
            
            # Starting position for content
            x = label_config['margin']
            y = header_height + content_config['section_spacing']
            
            # Product ID
            y = self._draw_text_block(
                draw,
                f"Product ID: {product_info.get('product_id', 'N/A')}",
                (x, y),
                'content',
                is_bold=True
            )
            
            # Batch ID
            y = self._draw_text_block(
                draw,
                f"Batch: {product_info.get('batch_id', 'N/A')}",
                (x, y + content_config['section_spacing']),
                'content'
            )
            
            # Manufacturing Date
            y = self._draw_text_block(
                draw,
                f"Manufactured: {product_info.get('manufacturing_date', 'N/A')}",
                (x, y + content_config['line_spacing']),
                'content'
            )
            
            # RoHS Compliance
            rohs_status = "Yes" if product_info.get('rohs_compliant', False) else "No"
            y = self._draw_text_block(
                draw,
                f"RoHS Compliant: {rohs_status}",
                (x, y + content_config['line_spacing']),
                'content'
            )
            
            # Add some spacing before the next section
            y += content_config['section_spacing']
            
            # Add additional product information if available
            if 'additional_info' in product_info:
                for key, value in product_info['additional_info'].items():
                    y = self._draw_text_block(
                        draw,
                        f"{key}: {value}",
                        (x, y + content_config['line_spacing']),
                        'content'
                    )
            
            return y
            
        except Exception as e:
            logger.error(f"Error drawing content: {e}")
            raise
    
    def _draw_text_block(
        self, 
        draw: ImageDraw.Draw, 
        text: str, 
        position: Tuple[int, int], 
        font_type: str = 'content',
        is_bold: bool = False,
        max_width: Optional[int] = None
    ) -> int:
        """Draw a block of text with word wrapping.
        
        Args:
            draw: ImageDraw object for drawing
            text: Text to draw
            position: (x, y) starting position
            font_type: Type of font to use ('header', 'content', 'footer')
            is_bold: Whether to use bold text
            max_width: Maximum width for text wrapping (None for no wrapping)
            
        Returns:
            Y-coordinate after the text block
        """
        try:
            x, y = position
            font = self.fonts[font_type]
            line_spacing = self.config['content']['line_spacing']
            
            # If max_width is not specified, use the remaining width of the label
            if max_width is None:
                max_width = self.config['label']['width'] - x - self.config['label']['margin']
            
            # Wrap text if needed
            if max_width > 0:
                # Get average character width
                avg_char_width = font.getlength('x')
                max_chars = int(max_width / avg_char_width)
                
                # Simple word wrapping
                lines = []
                for line in text.split('\n'):
                    if font.getlength(line) <= max_width:
                        lines.append(line)
                    else:
                        # Need to wrap this line
                        words = line.split(' ')
                        current_line = []
                        current_length = 0
                        
                        for word in words:
                            word_length = font.getlength(word + ' ')
                            if current_length + word_length <= max_width:
                                current_line.append(word)
                                current_length += word_length
                            else:
                                if current_line:
                                    lines.append(' '.join(current_line))
                                current_line = [word]
                                current_length = word_length
                        
                        if current_line:
                            lines.append(' '.join(current_line))
            else:
                lines = text.split('\n')
            
            # Draw each line
            for line in lines:
                draw.text((x, y), line, fill=self.config['content']['text_color'], font=font)
                y += font.size + line_spacing
            
            return y
            
        except Exception as e:
            logger.error(f"Error drawing text block: {e}")
            return position[1]  # Return original Y position on error
    
    def _draw_qr_code(
        self, 
        image: Image.Image, 
        product_info: Dict[str, Any],
        content_y: int
    ):
        """Draw a QR code on the label.
        
        Args:
            image: PIL Image object to draw on
            product_info: Dictionary containing product information
            content_y: Y-coordinate where the content ends
        """
        try:
            qr_config = self.config['qr_code']
            label_config = self.config['label']
            
            # Create QR code data
            qr_data = {
                'product_id': product_info.get('product_id', ''),
                'product_type': product_info.get('product_type', ''),
                'batch_id': product_info.get('batch_id', ''),
                'manufacturing_date': product_info.get('manufacturing_date', ''),
                'rohs_compliant': product_info.get('rohs_compliant', False),
                'timestamp': datetime.now().isoformat()
            }
            
            # Convert to string for QR code
            qr_data_str = '\n'.join(f"{k}:{v}" for k, v in qr_data.items())
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qr_config['error_correction'],
                box_size=10,
                border=qr_config['border']
            )
            qr.add_data(qr_data_str)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(
                fill_color=qr_config['fill_color'],
                back_color=qr_config['back_color']
            ).convert('RGB')
            
            # Resize QR code
            qr_img = qr_img.resize((qr_config['size'], qr_config['size']), Image.Resampling.LANCZOS)
            
            # Calculate position (bottom right corner)
            x = label_config['width'] - qr_config['size'] - label_config['margin']
            y = label_config['height'] - qr_config['size'] - self.config['footer']['height'] - label_config['margin']
            
            # Paste QR code onto label
            image.paste(qr_img, (x, y))
            
            # Add label below QR code
            draw = ImageDraw.Draw(image)
            qr_label = "Scan for\nproduct info"
            label_bbox = draw.textbbox((0, 0), qr_label, font=self.fonts['content'])
            label_width = label_bbox[2] - label_bbox[0]
            label_x = x + (qr_config['size'] - label_width) // 2
            label_y = y + qr_config['size'] + 5
            
            for i, line in enumerate(qr_label.split('\n')):
                line_bbox = draw.textbbox((0, 0), line, font=self.fonts['content'])
                line_width = line_bbox[2] - line_bbox[0]
                line_x = x + (qr_config['size'] - line_width) // 2
                draw.text(
                    (line_x, label_y + i * (self.fonts['content'].size + 2)),
                    line,
                    fill=self.config['content']['text_color'],
                    font=self.fonts['content']
                )
            
        except Exception as e:
            logger.error(f"Error drawing QR code: {e}")
            # Don't raise, as QR code is non-essential
    
    def _draw_barcode(
        self, 
        image: Image.Image, 
        product_info: Dict[str, Any],
        content_y: int
    ):
        """Draw a barcode on the label.
        
        Args:
            image: PIL Image object to draw on
            product_info: Dictionary containing product information
            content_y: Y-coordinate where the content ends
        """
        try:
            barcode_config = self.config['barcode']
            label_config = self.config['label']
            
            # Use product ID for barcode
            barcode_data = product_info.get('product_id', '123456789012')
            
            # Generate barcode (Code128 is a common format)
            barcode_class = barcode.get_barcode_class('code128')
            
            # Create a temporary file for the barcode
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_path = temp_file.name
            
            # Generate barcode image
            barcode_img = barcode_class(
                barcode_data,
                writer=ImageWriter()
            )
            
            # Save barcode to temporary file
            barcode_img.save(
                temp_path,
                {
                    'format': 'PNG',
                    'write_text': barcode_config['write_text'],
                    'text_distance': barcode_config['text_distance'],
                    'module_height': barcode_config['height']
                }
            )
            
            # Load barcode image
            barcode_img = Image.open(temp_path)
            
            # Calculate position (above QR code)
            x = label_config['width'] - barcode_img.width - label_config['margin']
            y = content_y + self.config['content']['section_spacing']
            
            # Paste barcode onto label
            image.paste(barcode_img, (x, y))
            
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Could not delete temporary barcode file: {e}")
            
        except Exception as e:
            logger.error(f"Error drawing barcode: {e}")
            # Don't raise, as barcode is non-essential
    
    def _draw_footer(self, draw: ImageDraw.Draw, product_info: Dict[str, Any]):
        """Draw the footer section of the label.
        
        Args:
            draw: ImageDraw object for drawing
            product_info: Dictionary containing product information
        """
        try:
            footer_config = self.config['footer']
            label_config = self.config['label']
            
            # Draw footer background
            footer_box = [
                (0, label_config['height'] - footer_config['height']),
                (label_config['width'], label_config['height'])
            ]
            draw.rectangle(footer_box, fill=footer_config['background_color'])
            
            # Draw footer text
            footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            text_bbox = draw.textbbox((0, 0), footer_text, font=self.fonts['footer'])
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = (label_config['width'] - text_width) // 2
            text_y = label_config['height'] - footer_config['height'] // 2 - text_height // 2
            
            draw.text(
                (text_x, text_y),
                footer_text,
                fill=footer_config['text_color'],
                font=self.fonts['footer']
            )
            
        except Exception as e:
            logger.error(f"Error drawing footer: {e}")
            # Don't raise, as footer is non-essential
    
    def _draw_border(self, draw: ImageDraw.Draw):
        """Draw a border around the label.
        
        Args:
            draw: ImageDraw object for drawing
        """
        try:
            label_config = self.config['label']
            
            border_box = [
                (label_config['border_width'] // 2, label_config['border_width'] // 2),
                (label_config['width'] - label_config['border_width'] // 2, 
                 label_config['height'] - label_config['border_width'] // 2)
            ]
            
            draw.rectangle(
                border_box,
                outline=label_config['border_color'],
                width=label_config['border_width']
            )
            
        except Exception as e:
            logger.error(f"Error drawing border: {e}")
            # Don't raise, as border is non-essential
    
    def save_label(self, label: Image.Image, output_path: str, format: str = 'PNG') -> bool:
        """Save the generated label to a file.
        
        Args:
            label: PIL Image object containing the label
            output_path: Path to save the label image
            format: Image format (e.g., 'PNG', 'JPEG')
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save the image
            label.save(output_path, format=format, dpi=(self.config['label']['dpi'], 
                                                      self.config['label']['dpi']))
            
            logger.info(f"Label saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving label: {e}")
            return False


def test_label_generator():
    """Test function for the LabelGenerator class."""
    import tempfile
    import os
    
    print("Testing LabelGenerator...")
    
    # Create a temporary directory for test output
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Initialize label generator
            generator = LabelGenerator()
            
            # Create test product info
            test_product = {
                'product_id': 'DEV001-20230520-1234',
                'product_type': 'Arduino Nano',
                'batch_id': 'BATCH-ARD-20230520',
                'manufacturing_date': '2023-05-20',
                'rohs_compliant': True,
                'additional_info': {
                    'Weight': '7g',
                    'Dimensions': '45x18x7.5mm',
                    'Voltage': '5V',
                    'Current': '19mA'
                }
            }
            
            # Generate label
            print("\nGenerating label...")
            label = generator.generate_label(test_product)
            
            # Save label to file
            output_path = os.path.join(temp_dir, 'test_label.png')
            if generator.save_label(label, output_path):
                print(f"Label saved to {output_path}")
                
                # Try to open the image if we're in an interactive environment
                try:
                    label.show()
                except:
                    print("Could not display image. Please check the saved file.")
            else:
                print("Failed to save label")
            
            print("\nLabel generation test completed!")
            
        except Exception as e:
            print(f"Error during label generation test: {e}")
            raise


if __name__ == "__main__":
    test_label_generator()
