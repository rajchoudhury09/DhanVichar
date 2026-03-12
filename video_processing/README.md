# Video Transcription Pipeline - Production Package

A production-ready Python package for automated video transcription with multiple audio extraction methods and Whisper AI models. Supports both local Whisper models and OpenAI Whisper API.

## Features

- Multiple audio extraction methods (FFmpeg, MoviePy, GStreamer)
- Automatic language detection and translation
- Audio quality detection (RMS-based)
- Intelligent fallback mechanism
- Method-specific audio file organization
- Both local and OpenAI Whisper API support
- Comprehensive validation and profiling tools

## Installation

### Prerequisites

**1. Python 3.8+**
```bash
python --version  # Verify Python installation
```

**2. FFmpeg (Required)**

FFmpeg is required for audio extraction. Install based on your OS:

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH
4. Verify: `ffmpeg -version`

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**3. Install Package**
```bash
cd video_transcription_pipeline
pip install -r requirements.txt
pip install -e .
```

### Optional Dependencies

**GStreamer** (for fallback extraction):
- Windows: Download from https://gstreamer.freedesktop.org/download/
- macOS: `brew install gstreamer`
- Linux: `sudo apt install gstreamer1.0-tools`

## Quick Start

### 1. Configure Settings

Edit `config.yaml`:
```yaml
paths:
  input_folder: ./input_videos
  output_folder: ./output_transcripts

whisper:
  model_type: local  # or 'openai'
  local_model: medium  # tiny/base/small/medium/large
  openai_api_key: null  # Add your API key if using OpenAI

audio:
  extraction_method: ffmpeg  # ffmpeg/moviepy/gstreamer

logging:
  log_level: INFO
```

### 2. Run Transcription

**Using Test Script:**
```bash
python test/test_transcription.py
```

**Using Python API:**
```python
from video_transcription_pipeline.pipeline import VideoTranscriptionPipeline

pipeline = VideoTranscriptionPipeline(log_level='INFO')
results = pipeline.process_videos(
    input_folder_path='./input_videos',
    output_folder_path='./output_transcripts',
    whisper_model='medium',
    audio_extraction_method='ffmpeg',
    model_type='local'
)
```

## Choosing the Right Extraction Method

### Use FFmpeg If:
- You need **fast processing** (fastest method)
- You have **limited memory** (minimal memory usage)
- You want **small audio file sizes**
- You're processing **English content** (best accuracy for English)
- **Recommended for most use cases**

### Use MoviePy If:
- You prioritize **slightly better accuracy** for English
- Speed and resources are not critical
- You can accept slower processing
- You need **high-quality audio extraction**

### Use GStreamer If:
- You're processing **non-English content** (better for multilingual)
- You need **low memory usage**
- You can accept moderate processing speed
- FFmpeg and MoviePy are unavailable

## Whisper Model Selection

| Model | Speed | Accuracy | Memory | Use Case |
|-------|-------|----------|--------|----------|
| tiny | Fastest | Lowest | ~1GB | Quick testing |
| base | Fast | Low | ~1GB | Draft transcripts |
| small | Moderate | Good | ~2GB | General use |
| medium | Slow | High | ~5GB | Production quality |
| large | Slowest | Highest | ~10GB | Maximum accuracy |

## Output Structure

```
output_transcripts/
├── audio_files/
│   ├── ffmpeg/              # Audio extracted with FFmpeg
│   ├── moviepy/             # Audio extracted with MoviePy
│   └── gstreamer/           # Audio extracted with GStreamer
├── english/                 # English transcripts
├── non_english/             # Original non-English transcripts
├── translated/              # English translations
└── without_audio/           # Videos with no audio content
```



## Validation Tools

### Profiling
```bash
python validation/profiling/profiler.py
```
Generates performance metrics for your chosen extraction method.

### Audio Quality Analysis
```bash
python validation/audio_quality/audio_quality.py
```
Analyzes audio quality metrics (RMS, spectral features).

### WER Analysis
```bash
python validation/wer_analysis/wer_analysis.py
```
Calculates Word Error Rate against ground truth transcripts.

## Configuration Options

### Local Whisper Models
```yaml
whisper:
  model_type: local
  local_model: medium  # tiny/base/small/medium/large/large-v2/large-v3
```

### OpenAI Whisper API
```yaml
whisper:
  model_type: openai
  openai_api_key: sk-your-api-key-here
  openai_model: whisper-1
```

## Troubleshooting

**FFmpeg not found:**
- Verify installation: `ffmpeg -version`
- Check PATH environment variable
- Restart terminal after installation

**Out of memory:**
- Use smaller Whisper model (tiny/base/small)
- Process fewer videos at once
- Close other applications

**Slow processing:**
- Use FFmpeg extraction method
- Use smaller Whisper model
- Consider OpenAI API for faster processing

**No audio detected:**
- Check video has audio track
- Verify audio is not muted
- Try different extraction method

## Advanced Usage

### Batch Processing
```python
pipeline = VideoTranscriptionPipeline()
for folder in ['batch1', 'batch2', 'batch3']:
    pipeline.process_videos(
        input_folder_path=f'./videos/{folder}',
        output_folder_path=f'./transcripts/{folder}',
        whisper_model='medium',
        audio_extraction_method='ffmpeg'
    )
```

### Custom Output Handling
```python
results = pipeline.process_videos(...)
for video, details in results['processing_details'].items():
    if details['status'] == 'success':
        print(f"✓ {video}: {details['language']}")
    else:
        print(f"✗ {video}: {details.get('error')}")
```

## Project Structure

```
video_processing/
├── video_transcription_pipeline/  # Main package
│   ├── video_transcription_pipeline/  # Core modules
│   ├── config.yaml               # Configuration
│   ├── requirements.txt          # Dependencies
│   └── pyproject.toml           # Package metadata
├── validation/                   # Validation tools
│   ├── profiling/               # Performance profiling
│   ├── audio_quality/           # Audio analysis
│   └── wer_analysis/            # Accuracy analysis
├── test/                        # Test scripts
├── input_videos/                # Input folder
├── output_transcripts/          # Output folder
└── README.md                    # This file
```

## License

MIT License

## Support

For issues and questions:
1. Check troubleshooting section
2. Review validation tool outputs
3. Check configuration settings
4. Verify all dependencies installed