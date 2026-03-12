"""File management and transcript saving functionality."""

import logging
from pathlib import Path
from typing import Dict, Any

from .transcriber import WhisperTranscriber


class FileManager:
    """Handle file operations and transcript saving."""
    
    def __init__(self, logger: logging.Logger, transcriber: WhisperTranscriber):
        self.logger = logger
        self.transcriber = transcriber
    
    def save_transcripts(self, result: Dict[str, Any], video_name: str, 
                        output_folder: Path, audio_path: Path) -> str:
        """Save transcripts organized by content type."""
        language = result.get('language', 'unknown')
        text = result.get('text', '').strip()
        
        if language == 'en':
            # English content
            transcript_dir = output_folder / 'english'
            transcript_dir.mkdir(parents=True, exist_ok=True)
            
            transcript_file = transcript_dir / f"{video_name}.txt"
            transcript_file.write_text(text, encoding='utf-8')
            
            self.logger.info(f"Saved English transcript: {transcript_file}")
            return 'english'
        
        else:
            # Non-English content - save original and translated
            # Original
            original_dir = output_folder / 'non_english'
            original_dir.mkdir(parents=True, exist_ok=True)
            
            original_file = original_dir / f"{video_name}_{language}.txt"
            original_file.write_text(text, encoding='utf-8')
            
            # Translated
            translated_dir = output_folder / 'translated'
            translated_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                translated_result = self.transcriber.translate(audio_path)
                translated_text = translated_result.get('text', '').strip()
                
                translated_file = translated_dir / f"{video_name}_en.txt"
                translated_file.write_text(translated_text, encoding='utf-8')
                
                self.logger.info(f"Saved original ({language}) and translated transcripts")
                return f'non_english_{language}'
            
            except Exception as e:
                self.logger.warning(f"Translation failed: {e}")
                return f'non_english_{language}_only'