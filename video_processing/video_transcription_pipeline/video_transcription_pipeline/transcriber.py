"""Whisper transcription functionality."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

import whisper

from .exceptions import TranscriptionError


class WhisperTranscriber:
    """Whisper model management and transcription."""
    
    SUPPORTED_MODELS = {'tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'}
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.model = None
        self.current_model_name = None
        self.model_type = None
        self.openai_api_key = None
        self.openai_model = None
    
    def load_model(self, model_name: str, model_type: str = 'local', openai_api_key: str = None, openai_model: str = 'whisper-1') -> None:
        """Load Whisper model (local or OpenAI API)."""
        self.model_type = model_type
        
        if model_type == 'local':
            if model_name not in self.SUPPORTED_MODELS:
                raise TranscriptionError(f"Unsupported model: {model_name}")
            
            if self.model is None or self.current_model_name != model_name:
                self.logger.info(f"Loading local Whisper model: {model_name}")
                try:
                    self.model = whisper.load_model(model_name)
                    self.current_model_name = model_name
                except Exception as e:
                    raise TranscriptionError(f"Failed to load Whisper model {model_name}: {e}")
        
        elif model_type == 'openai':
            if not openai_api_key:
                raise TranscriptionError("OpenAI API key is required for OpenAI Whisper")
            
            self.openai_api_key = openai_api_key
            self.openai_model = openai_model
            self.logger.info(f"Using OpenAI Whisper API with model: {openai_model}")
        
        else:
            raise TranscriptionError(f"Invalid model_type: {model_type}. Use 'local' or 'openai'")
    
    def transcribe(self, audio_path: Path) -> Dict[str, Any]:
        """Transcribe audio using Whisper."""
        if self.model_type == 'local':
            return self._transcribe_local(audio_path)
        elif self.model_type == 'openai':
            return self._transcribe_openai(audio_path)
        else:
            raise TranscriptionError("Model not loaded")
    
    def _transcribe_local(self, audio_path: Path) -> Dict[str, Any]:
        """Transcribe using local Whisper model."""
        if self.model is None:
            raise TranscriptionError("No model loaded")
        
        try:
            result = self.model.transcribe(str(audio_path), task="transcribe")
            return result
        except Exception as e:
            raise TranscriptionError(f"Whisper transcription failed: {e}")
    
    def _transcribe_openai(self, audio_path: Path) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_api_key)
            
            self.logger.info(f"Transcribing with OpenAI Whisper API...")
            
            with open(audio_path, 'rb') as audio_file:
                response = client.audio.transcriptions.create(
                    model=self.openai_model,
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            result = {
                'text': response.text,
                'language': response.language if hasattr(response, 'language') else 'en'
            }
            
            return result
            
        except ImportError:
            raise TranscriptionError("OpenAI package not installed. Install with: pip install openai")
        except Exception as e:
            raise TranscriptionError(f"OpenAI API transcription failed: {e}")
    
    def translate(self, audio_path: Path) -> Dict[str, Any]:
        """Translate audio to English using Whisper."""
        if self.model_type == 'openai':
            try:
                from openai import OpenAI
                
                client = OpenAI(api_key=self.openai_api_key)
                
                with open(audio_path, 'rb') as audio_file:
                    response = client.audio.translations.create(
                        model=self.openai_model,
                        file=audio_file
                    )
                
                return {'text': response.text, 'language': 'en'}
                
            except Exception as e:
                raise TranscriptionError(f"OpenAI translation failed: {e}")
        
        else:
            if self.model is None:
                raise TranscriptionError("No model loaded")
            
            try:
                result = self.model.transcribe(str(audio_path), task="translate")
                return result
            except Exception as e:
                raise TranscriptionError(f"Whisper translation failed: {e}")