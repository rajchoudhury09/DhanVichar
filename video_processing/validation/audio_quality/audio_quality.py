"""Audio quality analysis for video transcription pipeline."""

import librosa
import numpy as np
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from video_transcription_pipeline.pipeline import VideoTranscriptionPipeline
from video_transcription_pipeline.config_loader import ConfigLoader


class AudioQualityAnalyzer:
    """Analyze audio quality metrics for extracted audio files."""
    
    def __init__(self, config_path=None, audio_folder=None):
        if config_path is None:
            # Default to package config location
            config_path = Path(__file__).parent.parent.parent / 'video_transcription_pipeline' / 'config.yaml'
        self.config = ConfigLoader(str(config_path)).get_config()
        
        # Resolve output folder to absolute path
        output_folder = Path(self.config['output_folder'])
        if not output_folder.is_absolute():
            # Resolve relative to package directory
            package_dir = Path(__file__).parent.parent.parent / 'video_transcription_pipeline'
            output_folder = (package_dir / output_folder).resolve()
        
        self.audio_folder = Path(audio_folder) if audio_folder else output_folder / 'audio_files'
        self.results = {}
    
    def analyze_existing_audio(self):
        """Analyze quality of existing audio files."""
        print("=" * 60)
        print("AUDIO QUALITY ANALYSIS (Existing Files)")
        print("=" * 60)
        
        if not self.audio_folder.exists():
            print(f"Audio folder not found: {self.audio_folder}")
            return
        
        # Find all audio files in output folder
        audio_files = list(self.audio_folder.rglob("*.wav"))
        
        if not audio_files:
            print("No audio files found!")
            print(f"Searched in: {self.audio_folder}")
            return
        
        print(f"Found {len(audio_files)} audio files\n")
        
        # Group by parent folder (method or category)
        for audio_file in audio_files:
            category = audio_file.parent.name
            
            if category not in self.results:
                self.results[category] = {}
            
            print(f"Analyzing: {audio_file.name}...")
            metrics = self._analyze_audio_file(audio_file)
            self.results[category][audio_file.stem] = metrics
        
        # Save results
        self._save_results()
        self._generate_report()
    
    def _analyze_audio_file(self, audio_path: Path) -> dict:
        """Analyze audio quality metrics."""
        try:
            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)
            
            # Calculate metrics
            duration = len(y) / sr
            rms_energy = np.sqrt(np.mean(y**2))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            
            # Additional metrics
            spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            
            return {
                "duration_seconds": float(duration),
                "sample_rate": int(sr),
                "rms_energy": float(rms_energy),
                "zero_crossing_rate": float(zero_crossing_rate),
                "spectral_centroid": float(spectral_centroid),
                "spectral_bandwidth": float(spectral_bandwidth),
                "spectral_rolloff": float(spectral_rolloff),
                "file_size_mb": audio_path.stat().st_size / 1024 / 1024
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _save_results(self):
        """Save results to JSON file."""
        output_json = Path(__file__).parent / "audio_quality_results.json"
        with open(output_json, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {output_json}")
    
    def _generate_report(self):
        """Generate human-readable quality comparison report."""
        report = []
        report.append("AUDIO QUALITY COMPARISON REPORT")
        report.append("=" * 60)
        
        # Find common files across methods
        all_files = set()
        for method_results in self.results.values():
            all_files.update(method_results.keys())
        
        for filename in sorted(all_files):
            report.append(f"\nFile: {filename}")
            report.append("-" * 60)
            
            for category in self.results.keys():
                if category in self.results and filename in self.results[category]:
                    data = self.results[category][filename]
                    if "error" not in data:
                        report.append(f"  {category:12}: {data['duration_seconds']:.1f}s, "
                                    f"{data['file_size_mb']:.2f}MB, "
                                    f"RMS: {data['rms_energy']:.4f}, "
                                    f"SR: {data['sample_rate']}Hz")
                    else:
                        report.append(f"  {category:12}: ERROR - {data['error']}")
        
        # Quality comparison summary
        report.append("\n" + "=" * 60)
        report.append("QUALITY METRICS SUMMARY")
        report.append("=" * 60)
        
        for category in self.results.keys():
            valid_results = [v for v in self.results[category].values() if "error" not in v]
            if valid_results:
                avg_rms = np.mean([r['rms_energy'] for r in valid_results])
                avg_duration = np.mean([r['duration_seconds'] for r in valid_results])
                report.append(f"\n{category.upper()}:")
                report.append(f"  Average RMS Energy: {avg_rms:.4f}")
                report.append(f"  Average Duration: {avg_duration:.1f}s")
                report.append(f"  Files Analyzed: {len(valid_results)}/{len(self.results[category])}")
        
        # Recommendations
        report.append("\n" + "=" * 60)
        report.append("RECOMMENDATIONS")
        report.append("=" * 60)
        report.append("- Higher RMS energy indicates louder/clearer audio")
        report.append("- All sample rates should be 16000 Hz for Whisper")
        report.append("- Duration should be consistent across methods")
        report.append("- Spectral centroid indicates brightness of sound")
        
        output_txt = Path(__file__).parent / "audio_quality_report.txt"
        with open(output_txt, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Report saved to: {output_txt}")
        print("\n" + "=" * 60)
        print("Audio quality analysis complete!")
        print("=" * 60)


if __name__ == "__main__":
    try:
        
        analyzer = AudioQualityAnalyzer()
        analyzer.analyze_existing_audio()
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install: pip install librosa")
