"""Custom exceptions for video transcription pipeline."""


class VideoTranscriptionError(Exception):
    """Base exception for video transcription pipeline."""
    pass


class DependencyError(VideoTranscriptionError):
    """Raised when required dependencies are missing."""
    pass


class ValidationError(VideoTranscriptionError):
    """Raised when input validation fails."""
    pass


class ExtractionError(VideoTranscriptionError):
    """Raised when audio extraction fails."""
    pass


class TranscriptionError(VideoTranscriptionError):
    """Raised when transcription fails."""
    pass