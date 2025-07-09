# Smart Product Traceability System

A comprehensive solution for automated product labeling, quality verification, and traceability in manufacturing environments.

## Features

- **Automated Product Inspection**: Uses computer vision to verify product quality and compliance
- **Smart Labeling**: Generates and applies labels with QR codes, barcodes, and product information
- **Quality Control**: Performs real-time quality checks and rejects non-compliant products
- **Data Logging**: Maintains a complete audit trail of all products and inspections
- **Modular Design**: Easily extensible for different product types and manufacturing processes

## System Architecture

```
smart_traceability_system/
│
├── src/                          # Source code
│   ├── ai/                      # AI and machine learning components
│   │   └── quality_inspector.py # Product quality inspection logic
│   │
│   ├── hardware/                # Hardware interface components
│   │   ├── camera.py           # Camera control and image capture
│   │   └── actuators.py        # Control for label printers and reject mechanisms
│   │
│   ├── utils/                   # Utility modules
│   │   ├── database.py         # Database operations
│   │   └── label_generator.py  # Label generation and printing
│   │
│   └── main.py                 # Main application entry point
│
├── data/                        # Data storage
│   ├── models/                 # Trained ML models
│   ├── labels/                 # Label templates
│   └── logs/                   # System logs
│
├── tests/                      # Test scripts
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Prerequisites

- Python 3.8+
- OpenCV
- NumPy
- SQLite3
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/somyadev77/smart-traceability-system.git
   cd smart-traceability-system
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the example configuration file and modify as needed:
   ```bash
   cp config.example.json config.json
   ```

2. Edit `config.json` to match your hardware setup and requirements.

## Usage

### Running the System

```bash
python -m src.main
```

### Command Line Options

- `--debug`: Enable debug mode
- `--simulate`: Run in simulation mode (no hardware required)
- `--config PATH`: Specify a custom configuration file

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

## API Documentation

The system provides a REST API for integration with other systems:

- `GET /api/products`: List all products
- `GET /api/products/<product_id>`: Get product details
- `GET /api/batches/<batch_id>`: Get all products in a batch
- `POST /api/inspect`: Submit a product for inspection

## Hardware Requirements

- Camera (USB or IP camera)
- Label printer (supports EPL/ZPL or image printing)
- Conveyor system with reject mechanism (optional)
- Barcode/QR code scanner (optional)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

For questions or support, please contact somyadev77@gmail.com
