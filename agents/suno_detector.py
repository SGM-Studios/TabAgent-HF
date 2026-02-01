"""
SunoDetector - AI-Generated Audio Detection
Detects Suno, Udio, and other AI-generated music artifacts
"""

import numpy as np
import librosa
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple


@dataclass
class AudioAnalysis:
    """Results from audio quality analysis."""
    is_ai_generated: bool
    confidence: float  # 0-1
    high_freq_ratio: float
    spectral_flatness: float
    temporal_consistency: float
    artifacts_detected: list
    preprocessing_recommended: bool


class SunoDetector:
    """
    Detect AI-generated audio artifacts (Suno, Udio, etc.)
    
    AI-generated music often has:
    - Higher energy in 8-16kHz range (metallic shimmer)
    - More consistent spectral patterns (less natural variation)
    - Grid-like artifacts in spectrogram
    - Unusual phase coherence
    """
    
    def __init__(
        self,
        high_freq_threshold: float = 0.15,
        spectral_flatness_threshold: float = 0.4,
        consistency_threshold: float = 0.7
    ):
        """
        Initialize detector with thresholds.
        
        Args:
            high_freq_threshold: Max normal ratio of 8-16kHz energy
            spectral_flatness_threshold: Min natural spectral flatness
            consistency_threshold: Max natural temporal consistency
        """
        self.high_freq_threshold = high_freq_threshold
        self.spectral_flatness_threshold = spectral_flatness_threshold
        self.consistency_threshold = consistency_threshold
    
    def analyze(self, audio_path: str) -> AudioAnalysis:
        """
        Analyze audio for AI-generation artifacts.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            AudioAnalysis with detection results
        """
        print(f"🔍 Analyzing audio: {Path(audio_path).name}")
        
        # Load audio
        audio, sr = librosa.load(str(audio_path), sr=22050, mono=True)
        
        # Compute features
        high_freq_ratio = self._analyze_high_freq(audio, sr)
        spectral_flatness = self._analyze_spectral_flatness(audio, sr)
        temporal_consistency = self._analyze_temporal_consistency(audio, sr)
        
        # Detect artifacts
        artifacts = []
        
        if high_freq_ratio > self.high_freq_threshold:
            artifacts.append("high_frequency_shimmer")
        
        if spectral_flatness < self.spectral_flatness_threshold:
            artifacts.append("low_spectral_variation")
        
        if temporal_consistency > self.consistency_threshold:
            artifacts.append("unnatural_consistency")
        
        # Calculate overall AI probability
        scores = [
            high_freq_ratio / self.high_freq_threshold,
            1 - (spectral_flatness / self.spectral_flatness_threshold),
            temporal_consistency / self.consistency_threshold
        ]
        ai_score = np.mean([min(s, 1.0) for s in scores])
        
        is_ai = ai_score > 0.6
        
        result = AudioAnalysis(
            is_ai_generated=is_ai,
            confidence=ai_score,
            high_freq_ratio=high_freq_ratio,
            spectral_flatness=spectral_flatness,
            temporal_consistency=temporal_consistency,
            artifacts_detected=artifacts,
            preprocessing_recommended=is_ai
        )
        
        if is_ai:
            print(f"   ⚠️  AI-generated audio detected (confidence: {ai_score:.1%})")
            print(f"   Artifacts: {', '.join(artifacts)}")
        else:
            print(f"   ✅ Natural audio (confidence: {1-ai_score:.1%})")
        
        return result
    
    def _analyze_high_freq(self, audio: np.ndarray, sr: int) -> float:
        """Analyze high frequency energy ratio (8-16kHz)."""
        # Compute spectrogram
        spec = np.abs(librosa.stft(audio))
        freqs = librosa.fft_frequencies(sr=sr)
        
        # Find frequency bins
        low_mask = freqs < 8000
        high_mask = (freqs >= 8000) & (freqs < 16000)
        
        # Calculate energy ratio
        low_energy = np.sum(spec[low_mask, :])
        high_energy = np.sum(spec[high_mask, :])
        
        if low_energy == 0:
            return 0.0
        
        return high_energy / low_energy
    
    def _analyze_spectral_flatness(self, audio: np.ndarray, sr: int) -> float:
        """Analyze spectral flatness (natural variation)."""
        flatness = librosa.feature.spectral_flatness(y=audio)
        return float(np.mean(flatness))
    
    def _analyze_temporal_consistency(self, audio: np.ndarray, sr: int) -> float:
        """Analyze temporal consistency (unnaturally consistent = AI)."""
        # Compute RMS energy over time
        rms = librosa.feature.rms(y=audio)[0]
        
        if len(rms) < 2:
            return 0.0
        
        # Calculate variance of RMS changes
        rms_diff = np.diff(rms)
        variance = np.var(rms_diff)
        
        # Lower variance = more consistent = more AI-like
        # Normalize to 0-1 (higher = more consistent)
        consistency = 1.0 / (1.0 + variance * 100)
        
        return float(consistency)
    
    def preprocess(
        self,
        audio_path: str,
        output_path: str = None,
        reduce_shimmer: bool = True,
        reduce_artifacts: bool = True
    ) -> str:
        """
        Preprocess AI-generated audio to improve transcription.
        
        Args:
            audio_path: Input audio path
            output_path: Output path (None = auto-generate)
            reduce_shimmer: Apply high-frequency reduction
            reduce_artifacts: Apply artifact reduction
            
        Returns:
            Path to processed audio
        """
        import soundfile as sf
        
        audio_path = Path(audio_path)
        if output_path is None:
            output_path = str(audio_path.parent / f"{audio_path.stem}_processed.wav")
        
        print(f"🔧 Preprocessing: {audio_path.name}")
        
        # Load audio
        audio, sr = librosa.load(str(audio_path), sr=None, mono=False)
        
        # Handle stereo
        if audio.ndim > 1:
            audio_mono = np.mean(audio, axis=0)
        else:
            audio_mono = audio
        
        processed = audio_mono.copy()
        
        if reduce_shimmer:
            # Apply gentle low-pass above 10kHz
            processed = self._reduce_high_freq(processed, sr, cutoff=10000)
            print("   ✅ Reduced high-frequency shimmer")
        
        if reduce_artifacts:
            # Apply spectral smoothing
            processed = self._smooth_spectrum(processed, sr)
            print("   ✅ Applied spectral smoothing")
        
        # Normalize
        processed = processed / (np.max(np.abs(processed)) + 1e-8) * 0.9
        
        sf.write(output_path, processed, sr)
        print(f"   📝 Saved: {Path(output_path).name}")
        
        return output_path
    
    def _reduce_high_freq(
        self,
        audio: np.ndarray,
        sr: int,
        cutoff: int = 10000
    ) -> np.ndarray:
        """Apply gentle high-frequency reduction."""
        from scipy import signal
        
        # Design a gentle low-pass filter
        nyquist = sr / 2
        normalized_cutoff = min(cutoff / nyquist, 0.99)
        
        b, a = signal.butter(2, normalized_cutoff, btype='low')
        filtered = signal.filtfilt(b, a, audio)
        
        # Blend original and filtered
        return 0.7 * audio + 0.3 * filtered
    
    def _smooth_spectrum(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Apply spectral smoothing to reduce grid artifacts."""
        # STFT
        stft = librosa.stft(audio)
        
        # Apply median filter to magnitude spectrum
        mag = np.abs(stft)
        phase = np.angle(stft)
        
        # Smooth magnitude (simple moving average)
        kernel_size = 3
        from scipy.ndimage import uniform_filter
        mag_smooth = uniform_filter(mag, size=(kernel_size, kernel_size))
        
        # Blend original and smoothed
        mag_blend = 0.8 * mag + 0.2 * mag_smooth
        
        # Reconstruct
        stft_smooth = mag_blend * np.exp(1j * phase)
        audio_smooth = librosa.istft(stft_smooth)
        
        return audio_smooth
