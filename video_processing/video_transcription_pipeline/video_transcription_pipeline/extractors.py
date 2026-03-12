"""Audio extraction methods for video transcription pipeline."""

import subprocess
import shutil
import os
import tempfile
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Tuple, Optional, TYPE_CHECKING
import logging

from .exceptions import ExtractionError

if TYPE_CHECKING:
    from moviepy.editor import VideoFileClip  # type: ignore


class AudioExtractor:
    """Audio extraction methods with fallback support."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def calculate_rms(self, audio_path: Path) -> float:
        """Calculate RMS value of audio file."""
        try:
            audio_data, sample_rate = sf.read(str(audio_path))
            rms = np.sqrt(np.mean(audio_data**2))
            return rms
        except Exception as e:
            self.logger.warning(f"Failed to calculate RMS: {e}")
            return 0.0
    
    def extract_with_fallback(self, video_path: Path, preferred_method: str) -> Tuple[Path, str, bool]:
        """Extract audio with fallback methods. Returns (audio_path, method, has_audio)."""
        # Define method priority (gstreamer always last)
        methods = [preferred_method]
        for method in ['ffmpeg', 'moviepy']:
            if method != preferred_method:
                methods.append(method)
        if 'gstreamer' not in methods:
            methods.append('gstreamer')
        
        extraction_functions = {
            'ffmpeg': self._extract_ffmpeg,
            'moviepy': self._extract_moviepy,
            'gstreamer': self._extract_gstreamer
        }
        
        for method in methods:
            self.logger.info(f"Attempting audio extraction with {method}")
            
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                audio_path = Path(tmp_file.name)
            
            try:
                if extraction_functions[method](video_path, audio_path):
                    self.logger.info(f"Audio extraction successful with {method}")
                    
                    # Check RMS value
                    rms = self.calculate_rms(audio_path)
                    self.logger.info(f"Audio RMS value: {rms}")
                    
                    if rms == 0.0 or rms < 1e-6:
                        self.logger.warning(f"Audio has zero RMS value - no audio content")
                        if audio_path.exists():
                            audio_path.unlink()
                        return None, method, False
                    
                    return audio_path, method, True
                else:
                    # Clean up failed attempt
                    if audio_path.exists():
                        audio_path.unlink()
            except Exception as e:
                self.logger.warning(f"Audio extraction with {method} failed: {e}")
                if audio_path.exists():
                    audio_path.unlink()
        
        raise ExtractionError(f"All audio extraction methods failed for {video_path.name}")
    
    def _extract_ffmpeg(self, video_path: Path, audio_path: Path) -> bool:
        """Extract audio using ffmpeg."""
        cmd = [
            'ffmpeg', '-y', '-i', str(video_path),
            '-vn', '-ac', '1', '-ar', '16000',
            str(audio_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            success = result.returncode == 0 and audio_path.exists() and audio_path.stat().st_size > 0
            
            if not success:
                self.logger.warning(f"FFmpeg extraction failed: {result.stderr}")
            
            return success
        except subprocess.TimeoutExpired:
            self.logger.warning("FFmpeg extraction timed out")
            return False
        except Exception as e:
            self.logger.warning(f"FFmpeg extraction error: {e}")
            return False
    
    def _extract_moviepy(self, video_path: Path, audio_path: Path) -> bool:
        """Extract audio using moviepy."""
        try:
            from moviepy.editor import VideoFileClip  #type :ignore
            
            with VideoFileClip(str(video_path)) as clip:
                if clip.audio is None:
                    self.logger.warning(f"No audio track in {video_path.name}")
                    return False
                
                clip.audio.write_audiofile(str(audio_path), logger=None)
            
            success = audio_path.exists() and audio_path.stat().st_size > 0
            if not success:
                self.logger.warning("MoviePy extraction produced empty file")
            
            return success
        except Exception as e:
            self.logger.warning(f"MoviePy extraction error: {e}")
            return False
    
    def _extract_gstreamer(self, video_path: Path, audio_path: Path) -> bool:
        """Extract audio using gstreamer."""
        gst_cmd = shutil.which('gst-launch-1.0')
        if not gst_cmd:
            gst_cmd = r"C:\Program Files\gstreamer\1.0\msvc_x86_64\bin\gst-launch-1.0.exe"
        
        input_path = str(video_path).replace('\\', '/')
        output_path = str(audio_path).replace('\\', '/')
        
        cmd = [
            gst_cmd, 'filesrc', f'location={input_path}',
            '!', 'decodebin', '!', 'audioconvert', '!', 'audioresample',
            '!', 'audio/x-raw,rate=16000,channels=1', '!', 'wavenc',
            '!', 'filesink', f'location={output_path}'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            success = result.returncode == 0 and audio_path.exists() and audio_path.stat().st_size > 0
            
            if not success:
                self.logger.warning(f"GStreamer extraction failed: {result.stderr}")
            
            return success
        except subprocess.TimeoutExpired:
            self.logger.warning("GStreamer extraction timed out")
            return False
        except Exception as e:
            self.logger.warning(f"GStreamer extraction error: {e}")
            return False