"""
Configuration Manager for Smart Product Traceability System

This module provides a centralized way to manage configuration settings
for the entire application, with support for loading from JSON files,
environment variables, and command-line arguments.
"""

import os
import json
import logging
from typing import Any, Dict, Optional, Type, TypeVar
from pathlib import Path
import jsonschema
from dotenv import load_dotenv

# Type variable for configuration class
T = TypeVar('T', bound='ConfigManager')

# Default configuration schema
DEFAULT_SCHEMA = {
    "type": "object",
    "properties": {
        "system": {"type": "object"},
        "camera": {"type": "object"},
        "label_printer": {"type": "object"},
        "conveyor": {"type": "object"},
        "reject_mechanism": {"type": "object"},
        "database": {"type": "object"},
        "logging": {"type": "object"},
        "network": {"type": "object"},
        "ai": {"type": "object"},
        "label": {"type": "object"},
        "notifications": {"type": "object"}
    },
    "required": ["system"],
    "additionalProperties": True
}

class ConfigManager:
    """
    A class to manage application configuration with support for JSON files,
    environment variables, and command-line arguments.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_file: Optional[str] = None, env_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the JSON configuration file
            env_file: Path to the .env file (default: .env in project root)
        """
        if self._initialized:
            return
            
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables
        self._load_environment(env_file)
        
        # Load configuration
        self.config = {}
        self._schema = DEFAULT_SCHEMA
        self._config_file = config_file or os.getenv('CONFIG_FILE', 'config.json')
        self._env_file = env_file or os.getenv('ENV_FILE', '.env')
        
        # Load configuration from file
        self.load_config(self._config_file)
        
        # Mark as initialized
        self._initialized = True
        self.logger.info("Configuration manager initialized")
    
    def _load_environment(self, env_file: Optional[str] = None) -> None:
        """Load environment variables from .env file."""
        env_path = Path(env_file) if env_file else Path(__file__).parent.parent.parent / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            self.logger.debug(f"Loaded environment variables from {env_path}")
    
    def load_config(self, config_file: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_file: Path to the JSON configuration file
            
        Raises:
            FileNotFoundError: If the config file doesn't exist
            json.JSONDecodeError: If the config file is not valid JSON
            jsonschema.ValidationError: If the config doesn't match the schema
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            # Validate against schema
            self._validate_config()
            
            # Resolve environment variables in string values
            self._resolve_environment_variables()
            
            # Set default values
            self._set_defaults()
            
            self.logger.info(f"Loaded configuration from {config_path}")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {e}")
            raise
        except jsonschema.ValidationError as e:
            self.logger.error(f"Configuration validation error: {e}")
            raise
    
    def _validate_config(self) -> None:
        """Validate the configuration against the schema."""
        try:
            jsonschema.validate(instance=self.config, schema=self._schema)
        except jsonschema.ValidationError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise
    
    def _resolve_environment_variables(self) -> None:
        """Resolve environment variables in configuration values."""
        def resolve(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {k: resolve(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [resolve(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
                var_name = obj[2:-1]
                return os.getenv(var_name, obj)
            return obj
        
        self.config = resolve(self.config)
    
    def _set_defaults(self) -> None:
        """Set default values for missing configuration options."""
        defaults = {
            "system": {
                "name": "Smart Product Traceability System",
                "version": "1.0.0",
                "environment": os.getenv("ENVIRONMENT", "development"),
                "log_level": os.getenv("LOG_LEVEL", "INFO"),
                "data_dir": "./data"
            },
            "database": {
                "path": "./data/traceability.db"
            }
        }
        
        # Set defaults for missing sections
        for section, section_defaults in defaults.items():
            if section not in self.config:
                self.config[section] = {}
            
            # Update only missing keys
            for key, value in section_defaults.items():
                if key not in self.config[section]:
                    self.config[section][key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by dot notation.
        
        Example:
            config.get('database.host')
            
        Args:
            key: Configuration key in dot notation (e.g., 'database.host')
            default: Default value if key is not found
            
        Returns:
            The configuration value or default if not found
        """
        try:
            return self._get_nested(self.config, key.split('.'))
        except (KeyError, AttributeError):
            return default
    
    def _get_nested(self, data: Dict[str, Any], keys: list) -> Any:
        """Get a nested dictionary value by a list of keys."""
        if len(keys) == 1:
            return data[keys[0]]
        return self._get_nested(data[keys[0]], keys[1:])
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by dot notation.
        
        Args:
            key: Configuration key in dot notation (e.g., 'database.host')
            value: Value to set
        """
        keys = key.split('.')
        d = self.config
        
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        
        d[keys[-1]] = value
    
    def save(self, config_file: Optional[str] = None) -> None:
        """
        Save the current configuration to a file.
        
        Args:
            config_file: Path to save the configuration (default: loaded config file)
        """
        if config_file is None:
            config_file = self._config_file
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Configuration saved to {config_file}")
        except IOError as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
    
    def reload(self) -> None:
        """Reload the configuration from the file."""
        self.load_config(self._config_file)
    
    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to configuration."""
        return self.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dictionary-style setting of configuration."""
        self.set(key, value)
    
    def __contains__(self, key: str) -> bool:
        """Check if a configuration key exists."""
        try:
            self._get_nested(self.config, key.split('.'))
            return True
        except (KeyError, AttributeError):
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the configuration as a dictionary."""
        return self.config.copy()
    
    def __str__(self) -> str:
        """Return a string representation of the configuration."""
        return json.dumps(self.config, indent=2, ensure_ascii=False)


def get_config() -> ConfigManager:
    """Get the global configuration instance."""
    if ConfigManager._instance is None:
        ConfigManager()
    return ConfigManager._instance


def init_config(config_file: Optional[str] = None, env_file: Optional[str] = None) -> ConfigManager:
    """
    Initialize the global configuration.
    
    Args:
        config_file: Path to the configuration file
        env_file: Path to the .env file
        
    Returns:
        ConfigManager: The global configuration instance
    """
    return ConfigManager(config_file, env_file)


if __name__ == "__main__":
    # Example usage
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize with a config file
    config = init_config("config.example.json")
    
    # Access configuration
    print("System name:", config.get("system.name"))
    print("Environment:", config.get("system.environment"))
    
    # Set a new value
    config.set("system.environment", "production")
    print("Updated environment:", config.get("system.environment"))
    
    # Save configuration
    config.save("config_updated.json")
