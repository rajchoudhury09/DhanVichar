"""Test script for video transcription pipeline."""

import sys
from pathlib import Path

# Add package to path
package_path = Path(__file__).parent.parent / 'video_transcription_pipeline' / 'video_transcription_pipeline'
sys.path.insert(0, str(package_path.parent))

from video_transcription_pipeline.config_loader import ConfigLoader
from video_transcription_pipeline.pipeline import VideoTranscriptionPipeline


def test_transcription():
    """Test video transcription with config file."""
    
    # Load configuration
    config_path = package_path.parent / 'config.yaml'
    config_loader = ConfigLoader(str(config_path))
    config = config_loader.get_config()
    
    print(f"Configuration loaded:")
    print(f"  Input folder: {config['input_folder']}")
    print(f"  Output folder: {config['output_folder']}")
    print(f"  Model type: {config['model_type']}")
    print(f"  Local model: {config['local_model']}")
    print(f"  Extraction method: {config['extraction_method']}")
    print(f"  Log level: {config['log_level']}")
    print()
    
    # Initialize pipeline
    pipeline = VideoTranscriptionPipeline(log_level=config['log_level'])
    
    # Process videos
    print("Starting transcription...")
    results = pipeline.process_videos(
        input_folder_path=config['input_folder'],
        output_folder_path=config['output_folder'],
        whisper_model=config['local_model'],
        audio_extraction_method=config['extraction_method'],
        model_type=config['model_type'],
        openai_api_key=config.get('openai_api_key')
    )
    
    # Display results
    print("\nTranscription Results:")
    print(f"Total videos: {results['total_videos']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"\nContent Types: {results['content_types']}")
    print(f"Extraction Methods: {results['extraction_methods_used']}")
    
    print("\nProcessing Details:")
    for video_name, details in results['processing_details'].items():
        print(f"\n  Video: {video_name}")
        print(f"  Status: {details['status']}")
        if details['status'] == 'success':
            print(f"  Language: {details.get('language', 'N/A')}")
            print(f"  Content Type: {details.get('content_type', 'N/A')}")
            print(f"  Extraction Method: {details.get('extraction_method', 'N/A')}")
        elif details['status'] == 'no_audio':
            print(f"  Message: {details.get('message', 'N/A')}")
        else:
            print(f"  Error: {details.get('error', 'N/A')}")


if __name__ == '__main__':
    test_transcription()
