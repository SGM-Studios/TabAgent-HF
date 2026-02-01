"""
SplitterAgent - Audio Stem Separation using Demucs
Separates audio into guitar and bass stems, with mid-side processing
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import librosa
import soundfile as sf


class SplitterAgent:
    """
    Audio stem separation using Demucs v4 with htdemucs model.
    
    Pipeline:
    1. Demucs separation: Full mix → Guitar + Bass stems
    2. Mid-side processing: Guitar → Lead + Rhythm L + Rhythm R
    3. Frequency filtering: Bass → Clean bass (reduced fret noise)
    """
    
    def __init__(self, output_dir: str = "separated_stems"):
        """
        Initialize SplitterAgent.
        
        Args:
            output_dir: Directory for output stems
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def separate_stems(self, audio_path: str) -> Dict[str, str]:
        """
        Separate audio into guitar and bass stems using Demucs.
        
        Args:
            audio_path: Path to input audio file
            
        Returns:
            Dictionary with paths to separated stems
        """
        audio_path = Path(audio_path)
        print(f"🎵 Separating stems with Demucs: {audio_path.name}")
        
        # Create output subdirectory
        stem_dir = self.output_dir / audio_path.stem
        stem_dir.mkdir(parents=True, exist_ok=True)
        
        # Run Demucs for guitar and bass separation
        try:
            cmd = [
                "demucs",
                "--two-stems", "other",  # Splits into vocals/other, we want other (instruments)
                "-n", "htdemucs",
                "-o", str(stem_dir),
                str(audio_path)
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Demucs outputs to htdemucs/songname/
            demucs_output = stem_dir / "htdemucs" / audio_path.stem
            
            # For guitar/bass, we need to run again with different stems
            # Actually, let's use the 4-stem model and extract guitar/bass
            cmd_full = [
                "demucs",
                "-n", "htdemucs",
                "-o", str(stem_dir),
                str(audio_path)
            ]
            subprocess.run(cmd_full, check=True, capture_output=True)
            
            # htdemucs outputs: bass.wav, drums.wav, other.wav, vocals.wav
            # "other" contains guitars, synths, etc.
            guitar_path = demucs_output / "other.wav"
            bass_path = demucs_output / "bass.wav"
            
            if not guitar_path.exists() or not bass_path.exists():
                raise FileNotFoundError("Demucs output not found")
                
            return {
                "guitar": str(guitar_path),
                "bass": str(bass_path),
                "original": str(audio_path)
            }
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Demucs failed: {e}")
            # Fallback: return original as both guitar and bass
            return {
                "guitar": str(audio_path),
                "bass": str(audio_path),
                "original": str(audio_path)
            }
        except FileNotFoundError:
            print("⚠️  Demucs not installed, using original audio")
            return {
                "guitar": str(audio_path),
                "bass": str(audio_path),
                "original": str(audio_path)
            }
    
    def process_guitars(self, guitar_stem_path: str) -> Dict[str, str]:
        """
        Process guitar stem using mid-side technique to separate lead/rhythm.
        
        Mid-side processing:
        - Mid (center): Lead guitar (typically center-panned)
        - Side (L/R): Rhythm guitars (typically panned left/right)
        
        Args:
            guitar_stem_path: Path to guitar stem audio
            
        Returns:
            Dictionary with paths to processed guitar parts
        """
        print(f"🎸 Processing guitars with mid-side technique...")
        
        guitar_path = Path(guitar_stem_path)
        output_base = self.output_dir / guitar_path.stem
        
        # Load stereo audio
        audio, sr = librosa.load(str(guitar_path), sr=None, mono=False)
        
        # Handle mono files
        if audio.ndim == 1 or audio.shape[0] == 1:
            audio = np.vstack([audio.flatten(), audio.flatten()])
        
        left = audio[0]
        right = audio[1]
        
        # Mid-side processing
        mid = (left + right) / 2  # Center/Lead
        side_l = left - (mid * 0.8)  # Left rhythm (with some bleed)
        side_r = right - (mid * 0.8)  # Right rhythm (with some bleed)
        
        # Normalize to prevent clipping
        mid = mid / (np.max(np.abs(mid)) + 1e-8) * 0.9
        side_l = side_l / (np.max(np.abs(side_l)) + 1e-8) * 0.9
        side_r = side_r / (np.max(np.abs(side_r)) + 1e-8) * 0.9
        
        # Save processed stems
        lead_path = str(output_base) + "_lead.wav"
        rhythm_l_path = str(output_base) + "_rhythm_L.wav"
        rhythm_r_path = str(output_base) + "_rhythm_R.wav"
        
        sf.write(lead_path, mid, sr)
        sf.write(rhythm_l_path, side_l, sr)
        sf.write(rhythm_r_path, side_r, sr)
        
        print(f"   ✅ Lead guitar: {Path(lead_path).name}")
        print(f"   ✅ Rhythm L: {Path(rhythm_l_path).name}")
        print(f"   ✅ Rhythm R: {Path(rhythm_r_path).name}")
        
        return {
            "lead": lead_path,
            "left": rhythm_l_path,
            "right": rhythm_r_path
        }
    
    def process_bass(self, bass_stem_path: str) -> str:
        """
        Process bass stem with frequency-domain filtering.
        
        Bass processing:
        - Preserve low frequencies (fundamental tones)
        - Reduce high frequencies (fret noise, harmonics)
        
        Args:
            bass_stem_path: Path to bass stem audio
            
        Returns:
            Path to processed bass audio
        """
        print(f"🎸 Processing bass with frequency filtering...")
        
        bass_path = Path(bass_stem_path)
        output_path = str(self.output_dir / bass_path.stem) + "_clean.wav"
        
        # Load audio
        audio, sr = librosa.load(str(bass_path), sr=None, mono=True)
        
        # STFT-based frequency filtering
        stft = librosa.stft(audio)
        
        # Calculate frequency bins
        freqs = librosa.fft_frequencies(sr=sr)
        
        # Create filter: keep lows, reduce highs
        cutoff_hz = 200  # Preserve everything below 200Hz
        filter_mask = np.ones(stft.shape[0])
        
        for i, freq in enumerate(freqs):
            if freq > cutoff_hz:
                # Gradual rolloff above cutoff
                filter_mask[i] = max(0.5, 1.0 - (freq - cutoff_hz) / 2000)
        
        # Apply filter to magnitude
        stft_filtered = stft * filter_mask[:, np.newaxis]
        
        # Inverse STFT
        audio_clean = librosa.istft(stft_filtered)
        
        # Normalize
        audio_clean = audio_clean / (np.max(np.abs(audio_clean)) + 1e-8) * 0.9
        
        sf.write(output_path, audio_clean, sr)
        print(f"   ✅ Clean bass: {Path(output_path).name}")
        
        return output_path
