""
Database Module
--------------
Handles all database operations for the traceability system.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations for the traceability system."""
    
    def __init__(self, db_path: str = 'traceability.db'):
        """Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_database()
    
    def connect(self):
        """Establish a connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.debug(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def initialize_database(self):
        """Initialize the database with required tables if they don't exist."""
        try:
            self.connect()
            
            # Create products table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL UNIQUE,
                product_type TEXT NOT NULL,
                batch_id TEXT NOT NULL,
                manufacturing_date TEXT NOT NULL,
                rohs_compliant INTEGER NOT NULL,
                has_defects INTEGER NOT NULL,
                inspection_result TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            ''')
            
            # Create defects table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS defects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                defect_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
            ''')
            
            # Create components table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT NOT NULL,
                component_name TEXT NOT NULL,
                is_present INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
            ''')
            
            # Create audit_log table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                changes TEXT,
                performed_by TEXT,
                performed_at TEXT NOT NULL
            )
            ''')
            
            # Create indexes for better performance
            self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_products_product_id 
            ON products (product_id)
            ''')
            
            self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_products_batch_id 
            ON products (batch_id)
            ''')
            
            self.conn.commit()
            logger.info("Database initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            self.conn.rollback()
            raise
    
    def log_transaction(
        self,
        product_id: str,
        batch_id: str,
        status: str,
        timestamp: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log a product inspection transaction to the database.
        
        Args:
            product_id: Unique identifier for the product
            batch_id: Batch identifier
            status: Inspection status (e.g., 'PASSED', 'FAILED')
            timestamp: ISO format timestamp of the inspection
            metadata: Additional metadata about the inspection
            
        Returns:
            bool: True if the transaction was logged successfully, False otherwise
        """
        if not self.conn:
            self.connect()
        
        try:
            # Convert metadata to JSON string
            metadata_json = json.dumps(metadata) if metadata else '{}'
            
            # Insert product record
            self.cursor.execute('''
            INSERT INTO products (
                product_id, product_type, batch_id, manufacturing_date,
                rohs_compliant, has_defects, inspection_result,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_id,
                metadata.get('product_type', 'UNKNOWN') if metadata else 'UNKNOWN',
                batch_id,
                metadata.get('manufacturing_date', timestamp[:10]) if metadata else timestamp[:10],
                1 if metadata and metadata.get('rohs_compliant', False) else 0,
                1 if metadata and metadata.get('has_defects', False) else 0,
                status,
                timestamp,
                timestamp
            ))
            
            # Log defects if any
            if metadata and 'defects' in metadata and metadata['defects']:
                for defect in metadata['defects']:
                    self.cursor.execute('''
                    INSERT INTO defects (
                        product_id, defect_type, severity, confidence, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    ''', (
                        product_id,
                        defect.get('type', 'unknown'),
                        defect.get('severity', 'low'),
                        defect.get('confidence', 0.0),
                        timestamp
                    ))
            
            # Log components status
            if metadata and 'components_present' in metadata and metadata['components_present']:
                for component, is_present in metadata['components_present'].items():
                    self.cursor.execute('''
                    INSERT INTO components (
                        product_id, component_name, is_present, created_at
                    ) VALUES (?, ?, ?, ?)
                    ''', (
                        product_id,
                        component,
                        1 if is_present else 0,
                        timestamp
                    ))
            
            # Log the transaction in audit log
            self.cursor.execute('''
            INSERT INTO audit_log (
                action, table_name, record_id, changes, performed_by, performed_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'INSERT',
                'products',
                self.cursor.lastrowid,
                f"Added product {product_id} with status {status}",
                'system',
                timestamp
            ))
            
            self.conn.commit()
            logger.info(f"Transaction logged for product {product_id}")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error logging transaction: {e}")
            self.conn.rollback()
            return False
    
    def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a product by its ID.
        
        Args:
            product_id: The unique product identifier
            
        Returns:
            Dictionary containing product information, or None if not found
        """
        if not self.conn:
            self.connect()
        
        try:
            self.cursor.execute('''
            SELECT * FROM products WHERE product_id = ?
            ''', (product_id,))
            
            product_row = self.cursor.fetchone()
            if not product_row:
                return None
            
            # Convert row to dictionary
            product = dict(product_row)
            
            # Get defects for this product
            self.cursor.execute('''
            SELECT defect_type, severity, confidence 
            FROM defects 
            WHERE product_id = ?
            ''', (product_id,))
            
            product['defects'] = [dict(row) for row in self.cursor.fetchall()]
            
            # Get components for this product
            self.cursor.execute('''
            SELECT component_name, is_present 
            FROM components 
            WHERE product_id = ?
            ''', (product_id,))
            
            product['components'] = {
                row['component_name']: bool(row['is_present'])
                for row in self.cursor.fetchall()
            }
            
            return product
            
        except sqlite3.Error as e:
            logger.error(f"Error retrieving product {product_id}: {e}")
            return None
    
    def get_products_by_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        """Retrieve all products in a specific batch.
        
        Args:
            batch_id: The batch identifier
            
        Returns:
            List of product dictionaries
        """
        if not self.conn:
            self.connect()
        
        try:
            self.cursor.execute('''
            SELECT product_id FROM products WHERE batch_id = ?
            ''', (batch_id,))
            
            product_ids = [row['product_id'] for row in self.cursor.fetchall()]
            return [self.get_product(pid) for pid in product_ids if self.get_product(pid)]
            
        except sqlite3.Error as e:
            logger.error(f"Error retrieving products in batch {batch_id}: {e}")
            return []
    
    def get_audit_log(
        self, 
        limit: int = 100, 
        action: Optional[str] = None,
        table_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve audit log entries.
        
        Args:
            limit: Maximum number of entries to return
            action: Filter by action (e.g., 'INSERT', 'UPDATE', 'DELETE')
            table_name: Filter by table name
            
        Returns:
            List of audit log entries
        """
        if not self.conn:
            self.connect()
        
        try:
            query = 'SELECT * FROM audit_log'
            params = []
            
            conditions = []
            if action:
                conditions.append('action = ?')
                params.append(action)
            if table_name:
                conditions.append('table_name = ?')
                params.append(table_name)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY performed_at DESC LIMIT ?'
            params.append(limit)
            
            self.cursor.execute(query, params)
            return [dict(row) for row in self.cursor.fetchall()]
            
        except sqlite3.Error as e:
            logger.error(f"Error retrieving audit log: {e}")
            return []
    
    def export_to_csv(self, output_dir: str = '.') -> Dict[str, str]:
        """Export database tables to CSV files.
        
        Args:
            output_dir: Directory to save CSV files
            
        Returns:
            Dictionary mapping table names to output file paths
        """
        import csv
        import os
        from pathlib import Path
        
        if not self.conn:
            self.connect()
        
        output_files = {}
        tables = ['products', 'defects', 'components', 'audit_log']
        
        try:
            # Ensure output directory exists
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            for table in tables:
                # Get table data
                self.cursor.execute(f'SELECT * FROM {table}')
                rows = self.cursor.fetchall()
                
                if not rows:
                    continue
                
                # Write to CSV
                output_path = os.path.join(output_dir, f'{table}.csv')
                with open(output_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(dict(row) for row in rows)
                
                output_files[table] = output_path
                logger.info(f"Exported {len(rows)} rows from {table} to {output_path}")
            
            return output_files
            
        except Exception as e:
            logger.error(f"Error exporting database to CSV: {e}")
            return {}
    
    def backup_database(self, backup_dir: str = 'backups') -> Optional[str]:
        """Create a backup of the database.
        
        Args:
            backup_dir: Directory to store the backup
            
        Returns:
            Path to the backup file, or None if backup failed
        """
        import shutil
        from datetime import datetime
        import os
        
        try:
            # Ensure backup directory exists
            os.makedirs(backup_dir, exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'traceability_backup_{timestamp}.db')
            
            # Close the database connection if it's open
            if self.conn:
                self.conn.close()
            
            # Copy the database file
            shutil.copy2(self.db_path, backup_path)
            
            # Reopen the connection
            self.connect()
            
            logger.info(f"Database backup created at {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            # Try to reconnect if backup failed
            self.connect()
            return None
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            logger.info("Database connection closed")
    
    def __del__(self):
        """Destructor to ensure the database connection is closed."""
        self.close()


def test_database():
    """Test function for the DatabaseManager class."""
    import tempfile
    import os
    
    print("Testing DatabaseManager...")
    
    # Create a temporary directory for the test database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = os.path.join(temp_dir, 'test_traceability.db')
        
        try:
            # Initialize the database
            print("\nInitializing database...")
            db = DatabaseManager(db_path)
            
            # Test logging a transaction
            print("\nLogging test transaction...")
            test_product_id = "TEST-001"
            test_batch_id = "BATCH-001"
            test_timestamp = "2023-05-20T14:30:00"
            test_metadata = {
                'product_type': 'DEV001',
                'manufacturing_date': '2023-05-20',
                'rohs_compliant': True,
                'has_defects': False,
                'defects': [],
                'components_present': {
                    'USB Connector': True,
                    'Microcontroller': True,
                    'Pins': True
                }
            }
            
            db.log_transaction(
                product_id=test_product_id,
                batch_id=test_batch_id,
                status="PASSED",
                timestamp=test_timestamp,
                metadata=test_metadata
            )
            
            print(f"Logged transaction for product {test_product_id}")
            
            # Test retrieving the product
            print("\nRetrieving product from database...")
            product = db.get_product(test_product_id)
            
            if product:
                print(f"Retrieved product: {product['product_id']}")
                print(f"Type: {product['product_type']}")
                print(f"Batch: {product['batch_id']}")
                print(f"Status: {product['inspection_result']}")
                print(f"Components: {product['components']}")
            else:
                print("Failed to retrieve product")
            
            # Test audit log
            print("\nRetrieving audit log...")
            log_entries = db.get_audit_log(limit=5)
            print(f"Found {len(log_entries)} log entries")
            if log_entries:
                print(f"Latest entry: {log_entries[0]['action']} on {log_entries[0]['table_name']}")
            
            # Test export to CSV
            print("\nExporting database to CSV...")
            export_dir = os.path.join(temp_dir, 'export')
            exported_files = db.export_to_csv(export_dir)
            
            print(f"Exported {len(exported_files)} tables:")
            for table, path in exported_files.items():
                print(f"- {table}: {path}")
            
            # Test backup
            print("\nCreating database backup...")
            backup_path = db.backup_database(os.path.join(temp_dir, 'backups'))
            print(f"Backup created at: {backup_path}")
            
            # Clean up
            db.close()
            print("\nDatabase test completed successfully!")
            
        except Exception as e:
            print(f"Error during database test: {e}")
            raise


if __name__ == "__main__":
    test_database()
