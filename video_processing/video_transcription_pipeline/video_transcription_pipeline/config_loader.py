"""Configuration loader for video transcription pipeline."""

import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    """Load and validate configuration from config file."""
    
    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def get_config(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        return {
            'input_folder': self.config['paths']['input_folder'],
            'output_folder': self.config['paths']['output_folder'],
            'model_type': self.config['whisper']['model_type'],
            'local_model': self.config['whisper']['local_model'],
            'openai_api_key': self.config['whisper']['openai_api_key'],
            'openai_model': self.config['whisper']['openai_model'],
            'extraction_method': self.config['audio']['extraction_method'],
            'log_level': self.config['logging']['log_level']
        }
