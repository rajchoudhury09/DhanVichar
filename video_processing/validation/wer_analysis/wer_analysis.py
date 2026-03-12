"""Word Error Rate (WER) analysis for video transcription pipeline."""

from pathlib import Path
import jiwer
import json
import re
import sys
from difflib import SequenceMatcher

sys.path.insert(0, str(Path(__file__).parent.parent))

from video_transcription_pipeline.config_loader import ConfigLoader


class WERAnalyzer:
    """Analyze Word Error Rate for transcriptions."""
    
    def __init__(self, config_path=None, ground_truth_dir=None):
        if config_path is None:
            # Default to package config location
            config_path = Path(__file__).parent.parent.parent / 'video_transcription_pipeline' / 'config.yaml'
        self.config = ConfigLoader(str(config_path)).get_config()
        
        # Resolve output folder to absolute path
        output_folder = Path(self.config['output_folder'])
        if not output_folder.is_absolute():
            package_dir = Path(__file__).parent.parent.parent / 'video_transcription_pipeline'
            output_folder = (package_dir / output_folder).resolve()
        
        self.output_folder = output_folder
        
        # Set ground truth directory
        if ground_truth_dir is None:
            ground_truth_dir = Path(__file__).parent.parent / 'ground_truth'
        self.ground_truth_dir = Path(ground_truth_dir)
        self.results = []
    
    def normalize_text(self, text: str, keep_unicode=False) -> str:
        """Normalize text for comparison."""
        text = text.lower()
        
        if not keep_unicode:
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        
        text = jiwer.RemovePunctuation()(text)
        text = jiwer.RemoveMultipleSpaces()(text)
        text = jiwer.Strip()(text)
        return text
    
    def calculate_wer(self, reference, hypothesis, use_cer=False):
        """Calculate Word Error Rate or Character Error Rate."""
        try:
            ref_norm = self.normalize_text(reference, keep_unicode=use_cer)
            hyp_norm = self.normalize_text(hypothesis, keep_unicode=use_cer)
            
            if use_cer:
                return jiwer.cer(ref_norm, hyp_norm)
            else:
                return jiwer.wer(ref_norm, hyp_norm)
        except Exception as e:
            print(f"Error calculation failed: {e}")
            return None
    
    def find_matching_transcript(self, video_name: str) -> Path:
        """Find transcript file matching the video name."""
        # Search in all subdirectories
        for transcript_file in self.output_folder.rglob("*.txt"):
            # Extract base name without extensions
            transcript_stem = transcript_file.stem
            
            # Remove common suffixes
            transcript_base = re.sub(r'_(en|ta|te|ml|hi)$', '', transcript_stem)
            
            # Calculate similarity
            similarity = SequenceMatcher(None, video_name.lower(), transcript_base.lower()).ratio()
            
            if similarity > 0.8:  # 80% match threshold
                return transcript_file
        
        return None
    
    def load_text(self, file_path: Path) -> str:
        """Load text from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def analyze_wer(self):
        """Analyze WER for all ground truth files."""
        print("=" * 70)
        print("WORD ERROR RATE (WER) ANALYSIS")
        print("=" * 70)
        
        if not self.ground_truth_dir.exists():
            print(f"Ground truth directory not found: {self.ground_truth_dir}")
            return
        
        gt_files = list(self.ground_truth_dir.glob("*.txt"))
        
        if not gt_files:
            print(f"No ground truth files found in {self.ground_truth_dir}")
            return
        
        print(f"Found {len(gt_files)} ground truth files\n")
        
        for gt_file in gt_files:
            video_name = gt_file.stem
            ground_truth = self.load_text(gt_file)
            
            if not ground_truth:
                print(f"[SKIP] {video_name}: Cannot read ground truth\n")
                continue
            
            print(f"Video: {video_name}")
            print("-" * 70)
            
            # Find matching transcript
            transcript_path = self.find_matching_transcript(video_name)
            
            if not transcript_path:
                print(f"  [ERROR] No matching transcript found\n")
                self.results.append({
                    "video": video_name,
                    "status": "no_transcript",
                    "wer": None
                })
                continue
            
            hypothesis = self.load_text(transcript_path)
            
            if not hypothesis:
                print(f"  [ERROR] Cannot read transcript: {transcript_path}\n")
                self.results.append({
                    "video": video_name,
                    "status": "read_error",
                    "wer": None
                })
                continue
            
            # Detect if non-English (use CER instead of WER)
            is_non_english = any(ord(char) > 127 for char in ground_truth[:100])
            metric_name = "CER" if is_non_english else "WER"
            
            error_rate = self.calculate_wer(ground_truth, hypothesis, use_cer=is_non_english)
            
            if error_rate is None:
                print(f"  [ERROR] {metric_name} calculation failed\n")
                self.results.append({
                    "video": video_name,
                    "status": "calc_error",
                    "wer": None
                })
                continue
            
            print(f"  [OK] Transcript: {transcript_path.name}")
            print(f"  [OK] {metric_name}: {error_rate:.4f} ({error_rate*100:.2f}%)\n")
            
            self.results.append({
                "video": video_name,
                "transcript": str(transcript_path),
                "metric": metric_name,
                "wer": error_rate,
                "wer_percentage": error_rate * 100,
                "status": "success"
            })
        
        # Save results
        self._save_results()
        self._generate_report()
    
    def _save_results(self):
        """Save results to JSON file."""
        output_json = Path(__file__).parent / "wer_results.json"
        with open(output_json, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Results saved to: {output_json}")
    
    def _generate_report(self):
        """Generate human-readable WER report."""
        report = []
        report.append("WORD ERROR RATE (WER) ANALYSIS REPORT")
        report.append("=" * 70)
        
        # Individual results
        for result in self.results:
            report.append(f"\nVideo: {result['video']}")
            report.append("-" * 70)
            
            if result['status'] == 'success':
                report.append(f"  Transcript: {Path(result['transcript']).name}")
                report.append(f"  {result['metric']}: {result['wer']:.4f} ({result['wer_percentage']:.2f}%)")
            else:
                report.append(f"  Status: {result['status']}")
        
        # Summary
        report.append("\n" + "=" * 70)
        report.append("SUMMARY")
        report.append("=" * 70)
        
        successful = [r for r in self.results if r['status'] == 'success']
        
        if successful:
            avg_wer = sum(r['wer'] for r in successful) / len(successful)
            report.append(f"\nTotal videos analyzed: {len(self.results)}")
            report.append(f"Successful: {len(successful)}")
            report.append(f"Failed: {len(self.results) - len(successful)}")
            report.append(f"Average WER: {avg_wer:.4f} ({avg_wer*100:.2f}%)")
            
            # Best and worst
            best = min(successful, key=lambda x: x['wer'])
            worst = max(successful, key=lambda x: x['wer'])
            
            report.append(f"\nBest: {best['video']} (WER: {best['wer_percentage']:.2f}%)")
            report.append(f"Worst: {worst['video']} (WER: {worst['wer_percentage']:.2f}%)")
        else:
            report.append("\nNo successful WER calculations")
        
        output_txt = Path(__file__).parent / "wer_report.txt"
        with open(output_txt, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"Report saved to: {output_txt}")
        print("\n" + "=" * 70)
        print("WER analysis complete!")
        print("=" * 70)


if __name__ == "__main__":
    try:
        analyzer = WERAnalyzer()
        analyzer.analyze_wer()
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install: pip install jiwer")
