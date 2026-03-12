"""Input validation and dependency checking."""

import shutil
import os
from pathlib import Path
from typing import List
import logging

from .exceptions import DependencyError, ValidationError


class Validator:
    """Input validation and dependency checking."""
    
    SUPPORTED_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm'}
    SUPPORTED_MODELS = {'tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'}
    SUPPORTED_METHODS = {'ffmpeg', 'moviepy', 'gstreamer'}
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def validate_dependencies(self) -> None:
        """Validate all required dependencies are available."""
        missing_deps = []
        
        # Check ffmpeg
        if not shutil.which('ffmpeg'):
            missing_deps.append('ffmpeg')
        
        # Check moviepy
        try:
            import moviepy
        except ImportError:
            missing_deps.append('moviepy')
        
        # Check gstreamer
        gst_cmd = shutil.which('gst-launch-1.0')
        if not gst_cmd:
            gst_cmd = r"C:\Program Files\gstreamer\1.0\msvc_x86_64\bin\gst-launch-1.0.exe"
            if not os.path.exists(gst_cmd):
                missing_deps.append('gstreamer')
        
        if missing_deps:
            raise DependencyError(f"Missing required dependencies: {', '.join(missing_deps)}")
        
        self.logger.info("All dependencies validated successfully")
    
    def validate_inputs(self, input_folder: Path, output_folder: Path, 
                       whisper_model: str, audio_extraction_method: str) -> None:
        """Validate input parameters."""
        # Validate input folder
        if not input_folder.exists():
            raise ValidationError(f"Input folder does not exist: {input_folder}")
        
        if not input_folder.is_dir():
            raise ValidationError(f"Input path is not a directory: {input_folder}")
        
        # Validate whisper model
        if whisper_model not in self.SUPPORTED_MODELS:
            raise ValidationError(f"Unsupported Whisper model: {whisper_model}. "
                                f"Supported models: {', '.join(self.SUPPORTED_MODELS)}")
        
        # Validate extraction method
        if audio_extraction_method not in self.SUPPORTED_METHODS:
            raise ValidationError(f"Unsupported extraction method: {audio_extraction_method}. "
                                f"Supported methods: {', '.join(self.SUPPORTED_METHODS)}")
        
        # Create output folder if it doesn't exist
        output_folder.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Input validation completed successfully")
    
    def scan_videos(self, input_folder: Path) -> List[Path]:
        """Scan for supported video files."""
        videos = []
        for file in input_folder.iterdir():
            if file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                videos.append(file)
        
        if not videos:
            raise ValidationError(f"No supported video files found in {input_folder}")
        
        self.logger.info(f"Found {len(videos)} video files")
        return videos