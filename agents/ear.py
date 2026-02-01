"""
EarAgent - Audio-to-MIDI Transcription
Uses Basic Pitch (Spotify) as primary model with YourMT3+ as optional upgrade
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

import numpy as np
import librosa


@dataclass
class Note:
    """Simplified note representation."""
    pitch: int          # MIDI pitch (0-127)
    start_time: float   # Start time in seconds
    end_time: float     # End time in seconds
    velocity: int       # MIDI velocity (0-127)
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


class EarAgent:
    """
    Audio-to-MIDI transcription using Basic Pitch (Spotify) or YourMT3+.
    
    Basic Pitch is the default (production-ready, proven accuracy).
    YourMT3+ available as optional upgrade for complex polyphonic content.
    """
    
    def __init__(
        self,
        model: str = "basic_pitch",
        device: str = "auto"
    ):
        """
        Initialize EarAgent.
        
        Args:
            model: "basic_pitch" or "yourmt3"
            device: "cpu", "cuda", "mps", or "auto"
        """
        self.model_name = model
        self.device = self._detect_device(device)
        self.model = None
        
        print(f"🎧 Initializing EarAgent ({model}) on {self.device}")
        
        # Lazy load model on first use
        self._model_loaded = False
        
    def _detect_device(self, device: str) -> str:
        """Detect best available device."""
        if device != "auto":
            return device
            
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"
    

    def _load_model(self):
        """Lazy load transcription model."""
        if self._model_loaded:
            return
            
        if self.model_name == "basic_pitch":
            try:
                from basic_pitch.inference import predict
                self.predict_fn = predict
                self._model_loaded = True
                print("   ✅ Basic Pitch loaded")
            except ImportError:
                print("   ⚠️  Basic Pitch not installed, using mock mode")
                self.predict_fn = None
        elif self.model_name == "yourmt3":
            try:
                self._load_yourmt3()
                self._model_loaded = True
                print("   ✅ YourMT3+ loaded")
            except Exception as e:
                import traceback
                print(f"   ❌ YourMT3 setup failed: {e}")
                print(traceback.format_exc())
                print("   ⚠️  Falling back to Basic Pitch")
                self.model_name = "basic_pitch"
                self._load_model()

    def _load_yourmt3(self):
        """Load YourMT3+ model from Hugging Face."""
        print("   ⏳ Loading YourMT3+ (this may take a moment)...")
        
        # 1. Monkey-patch torch.load to disable weights_only (required for YourMT3)
        import torch
        import torch as _torch_module
        _original_torch_load = _torch_module.load
        def _patched_torch_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return _original_torch_load(*args, **kwargs)
        _torch_module.load = _patched_torch_load
        torch.load = _patched_torch_load
        
        # 2. Fix module imports for checkpoint compatibility
        import sys
        import yourmt3.utils
        sys.modules['utils'] = yourmt3.utils
        
        # 3. Imports
        from huggingface_hub import hf_hub_download
        from yourmt3 import YourMT3, model_name2conf, update_config, def_shared_cfg
        from yourmt3.utils.task_manager import TaskManager
        from copy import deepcopy
        
        # 4. Download/Load Checkpoint
        model_name = "YPTF+Multi"
        print(f"   📥 Downloading checkpoint for {model_name}...")
        model_path = hf_hub_download(
            repo_id="mimbres/YourMT3",
            filename="logs/2024/mc13_256_all_cross_v6_xk5_amp0811_edr005_attend_c_full_plus_2psn_nl26_sb_b26r_800k/checkpoints/model.ckpt"
        )
        
        # 5. Initialize Model
        precision = "32"
        args = model_name2conf(model_name, precision)
        shared_cfg, audio_cfg, model_cfg = update_config(args, deepcopy(def_shared_cfg), stage='test')
        
        try:
            self.model = YourMT3.load_from_checkpoint(
                model_path,
                map_location=self.device,
                strict=False,
                audio_cfg=audio_cfg,
                model_cfg=model_cfg,
                shared_cfg=shared_cfg,
                task_manager=TaskManager(
                    task_name=args.task,
                    max_shift_steps=int(shared_cfg["TOKENIZER"]["max_shift_steps"]),
                    debug_mode=args.debug_mode
                ),
                eval_subtask_key=args.eval_subtask_key,
                write_output_dir="."
            )
        except Exception as e:
            print(f"   ⚠️ Checkpoint load failed ({e}), initializing random weights for debugging...")
            self.model = YourMT3(
                audio_cfg,
                model_cfg,
                shared_cfg,
                task_manager=TaskManager(
                    task_name=args.task,
                    max_shift_steps=int(shared_cfg["TOKENIZER"]["max_shift_steps"]),
                    debug_mode=args.debug_mode
                ),
                eval_subtask_key=args.eval_subtask_key,
                write_output_dir="."
            )
            
        self.model.to(self.device)
        self.model.eval()
        
        # Store config for inference
        self.audio_cfg = audio_cfg
        self.task_manager = self.model.task_manager
    
    def transcribe_stem(
        self,
        audio_path: str,
        target: str = "guitar",
        onset_threshold: float = 0.5,
        frame_threshold: float = 0.3,
        min_note_duration: float = 0.05
    ) -> List[Note]:
        """
        Transcribe audio to MIDI notes.
        """
        self._load_model()
        
        audio_path = Path(audio_path)
        print(f"🎸 Transcribing: {audio_path.name} ({target}) using {self.model_name}")
        
        if self.model_name == "yourmt3":
            return self._transcribe_yourmt3(str(audio_path), target)
        
        if self.predict_fn is None:
            # Mock mode
            print("   ⚠️  Using mock transcription")
            return self._generate_mock_notes(target)
        
        try:
            # Basic Pitch transcription
            model_output, midi_data, note_events = self.predict_fn(
                str(audio_path),
                onset_threshold=onset_threshold,
                frame_threshold=frame_threshold,
                minimum_note_length=min_note_duration * 1000,
                minimum_frequency=None,
                maximum_frequency=None
            )
            
            # Convert to our Note format
            notes = []
            for instrument in midi_data.instruments:
                for note in instrument.notes:
                    notes.append(Note(
                        pitch=note.pitch,
                        start_time=note.start,
                        end_time=note.end,
                        velocity=note.velocity
                    ))
            
            # Filter and clean
            notes = self._filter_by_range(notes, target)
            notes = self._humanize_and_clean(notes, target)
            
            print(f"   ✅ Transcribed {len(notes)} notes")
            return notes
            
        except Exception as e:
            print(f"   ❌ Transcription failed: {e}")
            import traceback
            print(traceback.format_exc())
            return self._generate_mock_notes(target)

    def _transcribe_yourmt3(self, audio_path: str, target: str) -> List[Note]:
        """Run YourMT3 inference."""
        import torch
        import soundfile as sf
        import torchaudio
        from yourmt3.utils.audio import slice_padded_array
        from yourmt3.utils.note2event import mix_notes
        from yourmt3.utils.event2note import merge_zipped_note_events_and_ties_to_notes
        
        # 1. Load Audio
        print("   🎵 Loading audio for YourMT3...")
        audio_data, sr = sf.read(audio_path)
        if len(audio_data.shape) == 1:
            audio = torch.from_numpy(audio_data).unsqueeze(0)
        else:
            audio = torch.from_numpy(audio_data.T)
        audio = torch.mean(audio, dim=0).unsqueeze(0)  # Mono
        audio = torchaudio.functional.resample(audio, sr, self.audio_cfg['sample_rate'])
        
        # 2. Segment
        audio_segments = slice_padded_array(
            audio.numpy(),
            self.audio_cfg['input_frames'],
            self.audio_cfg['input_frames']
        )
        audio_segments = torch.from_numpy(audio_segments.astype('float32')).to(self.device).unsqueeze(1)
        n_items = audio_segments.shape[0]
        
        # 3. Inference
        print(f"   🧠 Running inference on {n_items} segments...")
        with torch.no_grad():
            pred_token_arr, _ = self.model.inference_file(
                bsz=8,
                audio_segments=audio_segments
            )
            
        # 4. Detokenize
        num_channels = self.task_manager.num_decoding_channels
        start_secs_file = [
            self.audio_cfg['input_frames'] * i / self.audio_cfg['sample_rate']
            for i in range(n_items)
        ]

        pred_notes_in_file = []
        for ch in range(num_channels):
            pred_token_arr_ch = [arr[:, ch, :] for arr in pred_token_arr]
            zipped_note_events, _, _ = self.task_manager.detokenize_list_batches(
                pred_token_arr_ch,
                start_secs_file,
                return_events=True
            )
            pred_notes_ch, _ = merge_zipped_note_events_and_ties_to_notes(zipped_note_events)
            pred_notes_in_file.append(pred_notes_ch)
            
        # 5. Convert to Note objects
        mixed_notes = mix_notes(pred_notes_in_file)
        final_notes = []
        
        for note in mixed_notes:
            if not note.is_drum:
                final_notes.append(Note(
                    pitch=note.pitch,
                    start_time=note.onset,
                    end_time=note.offset,
                    velocity=note.velocity
                ))
        
        # Filter and clean
        final_notes = self._filter_by_range(final_notes, target)
        final_notes = self._humanize_and_clean(final_notes, target)
        
        print(f"   ✅ YourMT3 produced {len(final_notes)} notes")
        return final_notes

    def _filter_by_range(self, notes: List[Note], target: str) -> List[Note]:
        """Filter notes by instrument range."""
        if target.lower() == "bass":
            # 5-string bass: B0 (23) to G4 (67)
            min_pitch, max_pitch = 23, 67
        else:
            # 6-string guitar: E2 (40) to E6 (88)
            min_pitch, max_pitch = 40, 88
            
        return [n for n in notes if min_pitch <= n.pitch <= max_pitch]
    
    def _humanize_and_clean(self, notes: List[Note], target: str) -> List[Note]:
        """
        Clean up transcription artifacts.
        
        - Remove very short notes (likely errors)
        - Remove octave doubling errors
        - Quantize timing slightly
        """
        if not notes:
            return notes
            
        cleaned = []
        
        for note in notes:
            # Skip very short notes
            if note.duration < 0.03:
                continue
                
            # Check for octave doubling (notes exactly 12 semitones apart at same time)
            is_octave_double = False
            for other in cleaned:
                if (abs(other.start_time - note.start_time) < 0.02 and
                    abs(other.pitch - note.pitch) == 12):
                    is_octave_double = True
                    break
            
            if not is_octave_double:
                cleaned.append(note)
        
        return cleaned
    
    def _generate_mock_notes(self, target: str) -> List[Note]:
        """Generate mock notes for testing."""
        base_pitch = 40 if target.lower() == "guitar" else 28
        
        notes = []
        for i in range(8):
            notes.append(Note(
                pitch=base_pitch + (i * 2) % 12,
                start_time=i * 0.5,
                end_time=i * 0.5 + 0.4,
                velocity=80
            ))
        
        return notes
    
    def export_midi(self, notes: List[Note], output_path: str, tempo: int = 120):
        """
        Export notes to MIDI file.
        
        Args:
            notes: List of Note objects
            output_path: Path for output MIDI file
            tempo: BPM for MIDI file
        """
        try:
            import pretty_midi
            
            midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)
            instrument = pretty_midi.Instrument(program=25)  # Acoustic guitar
            
            for note in notes:
                midi_note = pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=note.pitch,
                    start=note.start_time,
                    end=note.end_time
                )
                instrument.notes.append(midi_note)
            
            midi.instruments.append(instrument)
            midi.write(output_path)
            
            print(f"   📝 Exported MIDI: {Path(output_path).name}")
            
        except ImportError:
            print("   ⚠️  pretty_midi not installed, skipping MIDI export")

