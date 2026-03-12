"""Simple setup script for video transcription pipeline package."""

import subprocess
import sys
from pathlib import Path

def install_package():
    """Install the video transcription pipeline package."""
    
    package_dir = Path(__file__).parent / "video_transcription_pipeline"
    
    if not package_dir.exists():
        print("[FAIL] Package directory not found!")
        return False
    
    try:
        print("[INFO] Installing video transcription pipeline package...")
        
        # Install in development mode
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", str(package_dir)
        ], check=True)
        
        print("[OK] Package installed successfully!")
        print("\nUsage:")
        print("  from video_transcription_pipeline.pipeline import VideoTranscriptionPipeline")
        print("  pipeline = VideoTranscriptionPipeline()")
        print("  results = pipeline.process_videos('input/', 'output/', 'medium', 'ffmpeg')")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Installation failed: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = install_package()
    sys.exit(0 if success else 1)