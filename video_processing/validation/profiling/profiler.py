"""Profiling script for video transcription pipeline."""

import cProfile
import pstats
import io
import time
import psutil
import os
import json
from datetime import datetime
from pathlib import Path
from functools import wraps

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from video_transcription_pipeline.pipeline import VideoTranscriptionPipeline
from video_transcription_pipeline.config_loader import ConfigLoader


class PipelineProfiler:
    """Profiler for video transcription pipeline."""
    
    def __init__(self, config_path=None):
        if config_path is None:
            # Default to package config location
            config_path = Path(__file__).parent.parent.parent / 'video_transcription_pipeline' / 'config.yaml'
        self.config = ConfigLoader(str(config_path)).get_config()
        
        # Resolve paths to absolute
        package_dir = Path(__file__).parent.parent.parent / 'video_transcription_pipeline'
        self.input_folder = self._resolve_path(self.config['input_folder'], package_dir)
        self.output_folder = self._resolve_path(self.config['output_folder'], package_dir)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self._get_system_info(),
            "time_profile": {},
            "memory_profile": {},
            "benchmark": {}
        }
        self.process = psutil.Process(os.getpid())
    
    def _resolve_path(self, path_str, base_dir):
        """Resolve relative paths to absolute."""
        path = Path(path_str)
        if not path.is_absolute():
            path = (base_dir / path).resolve()
        return str(path)
    
    def _get_system_info(self):
        """Get system information."""
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}"
        }
    
    def profile_time(self):
        """Profile execution time using cProfile."""
        print("Running time profiling...")
        
        pr = cProfile.Profile()
        pr.enable()
        
        pipeline = VideoTranscriptionPipeline(log_level=self.config['log_level'])
        pipeline.process_videos(
            input_folder_path=self.input_folder,
            output_folder_path=self.output_folder,
            whisper_model=self.config['local_model'],
            audio_extraction_method=self.config['extraction_method'],
            model_type=self.config['model_type'],
            openai_api_key=self.config['openai_api_key'] if self.config['openai_api_key'] else None,
            openai_model=self.config['openai_model']
        )
        
        pr.disable()
        
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(20)
        
        self.results["time_profile"] = {
            "report": s.getvalue(),
            "top_functions": self._extract_top_functions(ps)
        }
    
    def _extract_top_functions(self, ps):
        """Extract top functions from profiling stats."""
        try:
            stats = ps.stats
            if not stats:
                return []
            
            top_funcs = []
            for func, data in list(stats.items())[:10]:
                if len(data) >= 4:
                    cc, nc, tt, ct = data[:4]
                    top_funcs.append({
                        "function": f"{func[0]}:{func[1]}({func[2]})",
                        "calls": nc,
                        "total_time": tt,
                        "cumulative_time": ct
                    })
            return top_funcs
        except Exception as e:
            return [{"error": f"Failed to extract functions: {str(e)}"}]
    
    def profile_memory(self):
        """Profile memory usage."""
        print("Running memory profiling...")
        
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_cpu_percent = self.process.cpu_percent(interval=1)
        start_time = time.time()
        
        pipeline = VideoTranscriptionPipeline(log_level=self.config['log_level'])
        pipeline.process_videos(
            input_folder_path=self.input_folder,
            output_folder_path=self.output_folder,
            whisper_model=self.config['local_model'],
            audio_extraction_method=self.config['extraction_method'],
            model_type=self.config['model_type'],
            openai_api_key=self.config['openai_api_key'] if self.config['openai_api_key'] else None,
            openai_model=self.config['openai_model']
        )
        
        end_memory = self.process.memory_info().rss / 1024 / 1024
        end_cpu_percent = self.process.cpu_percent(interval=1)
        end_time = time.time()
        
        self.results["memory_profile"] = {
            "start_memory_mb": start_memory,
            "end_memory_mb": end_memory,
            "memory_increase_mb": end_memory - start_memory,
            "execution_time_seconds": end_time - start_time,
            "avg_cpu_percent": (start_cpu_percent + end_cpu_percent) / 2
        }
    
    def benchmark_extraction_methods(self):
        """Benchmark extraction by running main pipeline with detailed metrics."""
        print(f"Benchmarking pipeline with {self.config['extraction_method']} method...")
        
        # Get audio folder to check output
        audio_folder = Path(self.output_folder) / 'audio_files' / self.config['extraction_method']
        
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        
        # Run the main pipeline
        pipeline = VideoTranscriptionPipeline(log_level='ERROR')
        results = pipeline.process_videos(
            input_folder_path=self.input_folder,
            output_folder_path=self.output_folder,
            whisper_model=self.config['local_model'],
            audio_extraction_method=self.config['extraction_method'],
            model_type=self.config['model_type'],
            openai_api_key=self.config['openai_api_key'] if self.config['openai_api_key'] else None,
            openai_model=self.config['openai_model']
        )
        
        end_time = time.time()
        end_memory = self.process.memory_info().rss / 1024 / 1024
        
        # Calculate total audio file size
        total_audio_size_mb = 0
        audio_files = []
        if audio_folder.exists():
            for audio_file in audio_folder.glob('*.wav'):
                size_mb = audio_file.stat().st_size / 1024 / 1024
                total_audio_size_mb += size_mb
                audio_files.append({
                    'name': audio_file.name,
                    'size_mb': size_mb
                })
        
        self.results["benchmark"] = {
            "method": self.config['extraction_method'],
            "total_time_seconds": end_time - start_time,
            "memory_mb": end_memory - start_memory,
            "videos_processed": results['total_videos'],
            "successful": results['successful'],
            "failed": results['failed'],
            "total_audio_size_mb": total_audio_size_mb,
            "audio_files": audio_files,
            "details": results['processing_details']
        }
    
    def run_complete_profile(self):
        """Run all profiling methods."""
        print("=" * 60)
        print("VIDEO TRANSCRIPTION PIPELINE PROFILING")
        print("=" * 60)
        
        print("\n1. Time profiling...")
        self.profile_time()
        
        print("\n2. Memory profiling...")
        self.profile_memory()
        
        print("\n3. Benchmarking extraction methods...")
        self.benchmark_extraction_methods()
        
        # Save results
        output_file = Path(__file__).parent / "profile_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate summary
        self._generate_summary(output_file)
        
        print(f"\n{'=' * 60}")
        print(f"Profiling complete!")
        print(f"Results saved to: {output_file}")
        print(f"Summary saved to: profile_summary.txt")
        print("=" * 60)
    
    def _generate_summary(self, json_file):
        """Generate human-readable summary."""
        summary = []
        summary.append("VIDEO TRANSCRIPTION PIPELINE PROFILING SUMMARY")
        summary.append("=" * 60)
        summary.append(f"Timestamp: {self.results['timestamp']}")
        summary.append(f"System: {self.results['system_info']['cpu_count']} CPUs, "
                      f"{self.results['system_info']['memory_total_gb']:.1f}GB RAM")
        
        # Memory profile
        if self.results["memory_profile"]:
            mem = self.results["memory_profile"]
            summary.append(f"\nMEMORY USAGE:")
            summary.append(f"  Start: {mem['start_memory_mb']:.1f} MB")
            summary.append(f"  End: {mem['end_memory_mb']:.1f} MB")
            summary.append(f"  Increase: {mem['memory_increase_mb']:.1f} MB")
            summary.append(f"  CPU usage: {mem['avg_cpu_percent']:.1f}%")
            summary.append(f"  Execution time: {mem['execution_time_seconds']:.2f}s")
        
        # Benchmark results
        if self.results["benchmark"] and isinstance(self.results["benchmark"], dict):
            bench = self.results["benchmark"]
            summary.append(f"\nPIPELINE BENCHMARK ({bench.get('method', 'N/A').upper()}):")
            summary.append(f"  Total time: {bench.get('total_time_seconds', 0):.2f}s")
            summary.append(f"  Memory: {bench.get('memory_mb', 0):.1f}MB")
            summary.append(f"  Videos: {bench.get('videos_processed', 0)} total, {bench.get('successful', 0)} successful, {bench.get('failed', 0)} failed")
            summary.append(f"  Total audio size: {bench.get('total_audio_size_mb', 0):.2f}MB")
            
            if bench.get('audio_files'):
                summary.append(f"\n  Audio files:")
                for audio in bench['audio_files']:
                    summary.append(f"    {audio['name']}: {audio['size_mb']:.2f}MB")
        
        # Top time consumers
        if self.results["time_profile"] and "top_functions" in self.results["time_profile"]:
            summary.append(f"\nTOP TIME CONSUMERS:")
            for func in self.results["time_profile"]["top_functions"][:5]:
                if "error" not in func:
                    summary.append(f"  {func['function']}: {func['cumulative_time']:.3f}s")
        
        summary.append(f"\nDetailed results: {json_file}")
        
        summary_file = Path(__file__).parent / "profile_summary.txt"
        with open(summary_file, 'w') as f:
            f.write('\n'.join(summary))


if __name__ == "__main__":
    profiler = PipelineProfiler()
    profiler.run_complete_profile()
