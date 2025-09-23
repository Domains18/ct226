"""Configuration management for Contact Importer."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """Configuration manager for the Contact Importer."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Look for config.yaml in the project root
        current_dir = Path(__file__).parent.parent
        config_file = current_dir / "config.yaml"
        return str(config_file)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Warning: Config file not found at {self.config_path}")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file is not found."""
        return {
            "defaults": {
                "output_format": "vcf",
                "country_code": "KE",
                "output_filename": "imported_contacts",
                "duplicate_handling": "skip"
            },
            "phone_formatting": {
                "remove_chars": ["-", "(", ")", " ", "."],
                "international_format": True,
                "auto_add_country_code": True
            },
            "validation": {
                "strict_mode": False,
                "min_length": 7,
                "max_length": 15
            },
            "logging": {
                "level": "INFO",
                "log_file": "contact_importer.log",
                "console_output": True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default settings."""
        return self.get('defaults', {})
    
    def get_phone_formatting(self) -> Dict[str, Any]:
        """Get phone formatting settings."""
        return self.get('phone_formatting', {})
    
    def get_validation(self) -> Dict[str, Any]:
        """Get validation settings."""
        return self.get('validation', {})
    
    def get_logging(self) -> Dict[str, Any]:
        """Get logging settings."""
        return self.get('logging', {})
    
    def get_country_code(self, country: str) -> str:
        """Get country code for a specific country."""
        country_codes = self.get('country_codes', {})
        return country_codes.get(country.upper(), '')


# Global config instance
config = Config()
