# Tab Agent MVP - File Manifest

## Core Files (Required)

### Python Scripts
- **`main.py`** (11.7 KB) - Main pipeline orchestrator
  - Stages 0-5 of transcription
  - Suno detection integration
  - User preferences loading

- **`agents.py`** (25.7 KB) - Core agent implementations
  - `SplitterAgent` - Demucs stem separation
  - `EarAgent` - Basic Pitch transcription
  - `TabAgent` - Dynamic programming tablature generation

- **`suno_postprocessor.py`** (9.9 KB) - AI artifact detection and cleanup
  - `SunoArtifactDetector` - Spectral analysis
  - `SunoAudioPreprocessor` - Pre-transcription cleanup
  - `SunoNotePostprocessor` - Post-transcription cleanup

- **`test_pipeline.py`** (2.4 KB) - Dependency verification script
  - Checks all required packages
  - Tests agent initialization

## Configuration

- **`requirements.txt`** (421 B) - Python dependencies
  - Basic Pitch, Demucs, Librosa, PyTorch, etc.
  - Pinned to tested versions

- **`user_memory/user_preferences.json`** (232 B) - User configuration
  - Tuning settings (guitar, bass)
  - Session history
  - Editable by users

## Documentation

- **`README.md`** (5.3 KB) - Main documentation
  - Features, installation, usage
  - Performance expectations
  - Troubleshooting guide

- **`QUICKSTART.md`** (3.1 KB) - 5-minute getting started guide
  - Minimal steps to first transcription
  - Common issues and solutions

- **`LICENSE`** (1.4 KB) - MIT license
  - Third-party component licenses

- **`MANIFEST.md`** (This file) - File inventory

## Setup Scripts

- **`setup.sh`** (Unix/Mac) - Automated setup
  - Creates venv
  - Installs dependencies
  - Runs tests

- **`setup.bat`** (Windows) - Automated setup
  - Same as setup.sh for Windows

## Infrastructure

- **`.gitignore`** (340 B) - Git exclusions
  - Python artifacts
  - Output files
  - OS-specific files

## Directories

- **`input/`** - Place audio files here
- **`output/`** - Generated tabs, MIDI, JSON
- **`user_memory/`** - Configuration and session history

---

## Total Size: ~56 KB (code only)

**Dependencies download**: ~500 MB (PyTorch, TensorFlow, models)

---

## Minimal Working Set

If you only want the bare minimum:
1. `main.py`
2. `agents.py`
3. `suno_postprocessor.py`
4. `requirements.txt`
5. `user_memory/user_preferences.json`

That's 48 KB of code. Everything else is documentation and convenience.

---

## What's NOT Included

❌ Training data
❌ LoRA adapters (see Path 2 in main repo)
❌ Test audio files
❌ Docker configuration (optional)
❌ Web interface (future enhancement)
❌ Robust mode agents (future enhancement)

---

## File Dependencies

```
main.py
  ├─ imports: agents.py
  ├─ imports: suno_postprocessor.py
  └─ reads: user_memory/user_preferences.json

agents.py
  ├─ calls: demucs (CLI)
  └─ imports: basic_pitch, librosa, note_seq

suno_postprocessor.py
  └─ imports: librosa, scipy

test_pipeline.py
  ├─ imports: agents.py
  └─ checks: all dependencies
```

---

## Version Information

- **MVP Version**: 1.0.0
- **Created**: January 2026
- **Python**: 3.8+ required
- **Platform**: Windows, Mac, Linux

---

## Checksum (SHA256)

Run to verify file integrity:
```bash
sha256sum *.py requirements.txt
```
