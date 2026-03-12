"""
Video Transcription Pipeline

A production-ready Python package for video transcription with configurable audio extraction methods and Whisper models.
"""

from .pipeline import VideoTranscriptionPipeline
from .exceptions import (
    VideoTranscriptionError,
    DependencyError,
    ValidationError,
    ExtractionError,
    TranscriptionError
)

__version__ = "1.0.0"
__all__ = [
    "VideoTranscriptionPipeline",
    "VideoTranscriptionError",
    "DependencyError", 
    "ValidationError",
    "ExtractionError",
    "TranscriptionError"
]