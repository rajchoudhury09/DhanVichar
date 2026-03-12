"""Main video transcription pipeline module."""

import logging
from pathlib import Path
from typing import Dict, Any

from .validator import Validator
from .extractors import AudioExtractor
from .transcriber import WhisperTranscriber
from .file_manager import FileManager


class VideoTranscriptionPipeline:
    """Production-ready video transcription pipeline."""
    
    def __init__(self, log_level: str = 'INFO'):
        """Initialize the pipeline.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.logger = self._setup_logging(log_level)
        
        # Initialize components
        self.validator = Validator(self.logger)
        self.extractor = AudioExtractor(self.logger)
        self.transcriber = WhisperTranscriber(self.logger)
        self.file_manager = FileManager(self.logger, self.transcriber)
        
        # Validate dependencies on initialization
        self.validator.validate_dependencies()
    
    def _setup_logging(self, log_level: str) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('video_transcription_pipeline')
        logger.setLevel(getattr(logging, log_level.upper()))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def process_videos(self, input_folder_path: str, output_folder_path: str,
                      whisper_model: str, audio_extraction_method: str, 
                      model_type: str = 'local', openai_api_key: str = None, 
                      openai_model: str = 'whisper-1') -> Dict[str, Any]:
        """Process videos with transcription pipeline.
        
        Args:
            input_folder_path: Path to folder containing video files
            output_folder_path: Path to output folder for transcripts
            whisper_model: Whisper model name (tiny, base, small, medium, large, etc.)
            audio_extraction_method: Audio extraction method (ffmpeg, moviepy, gstreamer)
            model_type: 'local' or 'openai'
            openai_api_key: OpenAI API key (required if model_type='openai')
            openai_model: OpenAI model name (default: whisper-1)
        
        Returns:
            Dict containing processing results and statistics
        """
        # Convert to Path objects
        input_folder = Path(input_folder_path)
        output_folder = Path(output_folder_path)
        
        # Validate inputs
        self.validator.validate_inputs(input_folder, output_folder, whisper_model, audio_extraction_method)
        
        # Load Whisper model
        self.transcriber.load_model(whisper_model, model_type, openai_api_key, openai_model)
        
        # Scan for videos
        videos = self.validator.scan_videos(input_folder)
        
        # Process each video
        results = {
            'total_videos': len(videos),
            'successful': 0,
            'failed': 0,
            'processing_details': {},
            'content_types': {},
            'extraction_methods_used': {}
        }
        
        for video in videos:
            video_name = video.stem
            self.logger.info(f"Processing video: {video_name}")
            
            try:
                # Extract audio with fallback
                audio_result = self.extractor.extract_with_fallback(video, audio_extraction_method)
                
                # Check if audio has content
                if audio_result[2] is False:  # has_audio is False
                    # Move to without_audio folder
                    without_audio_folder = output_folder / 'without_audio'
                    without_audio_folder.mkdir(parents=True, exist_ok=True)
                    
                    results['processing_details'][video_name] = {
                        'status': 'no_audio',
                        'extraction_method': audio_result[1],
                        'message': 'Video has no audio content (RMS = 0)'
                    }
                    results['content_types']['without_audio'] = results['content_types'].get('without_audio', 0) + 1
                    
                    # Create marker file
                    marker_file = without_audio_folder / f"{video_name}.txt"
                    with open(marker_file, 'w', encoding='utf-8') as f:
                        f.write(f"Video: {video.name}\nStatus: No audio content detected (RMS value = 0)\n")
                    
                    self.logger.warning(f"Video {video_name} has no audio content")
                    continue
                
                audio_path, used_method = audio_result[0], audio_result[1]
                
                # Transcribe
                transcription_result = self.transcriber.transcribe(audio_path)
                
                # Save transcripts
                content_type = self.file_manager.save_transcripts(transcription_result, video_name, output_folder, audio_path)
                
                # Save audio file to method-specific folder
                audio_output_folder = output_folder / 'audio_files' / used_method
                audio_output_folder.mkdir(parents=True, exist_ok=True)
                saved_audio_path = audio_output_folder / f"{video_name}.wav"
                if audio_path.exists():
                    import shutil
                    shutil.copy(audio_path, saved_audio_path)
                    audio_path.unlink()  # Delete temp file
                
                # Update results
                results['successful'] += 1
                results['processing_details'][video_name] = {
                    'status': 'success',
                    'extraction_method': used_method,
                    'content_type': content_type,
                    'language': transcription_result.get('language', 'unknown')
                }
                
                # Update statistics
                results['content_types'][content_type] = results['content_types'].get(content_type, 0) + 1
                results['extraction_methods_used'][used_method] = results['extraction_methods_used'].get(used_method, 0) + 1
                
                self.logger.info(f"Successfully processed {video_name}")
                
            except Exception as e:
                results['failed'] += 1
                results['processing_details'][video_name] = {
                    'status': 'failed',
                    'error': str(e)
                }
                self.logger.error(f"Failed to process {video_name}: {e}")
        
        # Log final results
        self.logger.info(f"Processing complete: {results['successful']}/{results['total_videos']} successful")
        
        return results