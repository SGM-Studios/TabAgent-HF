# CLAUDE.md - Tab Agent Pro

This document provides guidance for AI assistants working with the Tab Agent Pro codebase.

## Project Overview

**Tab Agent Pro** is an AI-powered audio-to-tablature transcription and audio-reactive video generation application. It combines multiple ML models to convert guitar and bass recordings into playable tablature (MIDI, ASCII tabs, JSON) while also generating synchronized videos using Stable Diffusion.

**Current Version:** 2.0.0 (config.yaml) / 1.0 "Viral UI" (frontend)
**Primary Deployment:** HuggingFace Spaces with Zero GPU (A10G)
**License:** MIT

## Repository Structure

```
TabAgent-HF/
├── app.py                      # Main Gradio application
├── config.yaml                 # Central configuration file
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── package.json                # Root npm proxy scripts
├── README.md                   # HuggingFace Space metadata
├── DEPLOYMENT.md               # Deployment documentation
│
├── agents/                     # Audio transcription pipeline
│   ├── __init__.py             # Module exports
│   ├── ear.py                  # EarAgent: Audio→MIDI (Basic Pitch/YourMT3+)
│   ├── splitter.py             # SplitterAgent: Demucs stem separation
│   ├── tab.py                  # TabAgent: MIDI→Tablature (Viterbi algorithm)
│   ├── suno_detector.py        # AI-generated audio detection
│   ├── types.py                # Shared type definitions (Note, TabNote, Tuning)
│   ├── exceptions.py           # Custom exception classes
│   └── utils.py                # Utility functions
│
├── deforum/                    # Video generation module
│   ├── __init__.py             # Module exports
│   ├── generator.py            # DeforumGenerator: Stable Diffusion video
│   ├── audio_sync.py           # AudioSyncEngine: Audio→animation mapping
│   ├── presets.py              # Style presets (Guitar Hero, Concert, etc.)
│   └── types.py                # Type definitions (AudioFeatures, VideoResult)
│
├── tests/                      # Comprehensive test suite
│   ├── conftest.py             # Pytest fixtures
│   ├── test_agents_types.py    # Tests for agent type definitions
│   ├── test_agents_utils.py    # Tests for utility functions
│   ├── test_tab_agent.py       # Tests for TabAgent
│   ├── test_ear_agent.py       # Tests for EarAgent
│   ├── test_suno_detector.py   # Tests for SunoDetector
│   ├── test_splitter_agent.py  # Tests for SplitterAgent
│   ├── test_audio_sync.py      # Tests for AudioSyncEngine
│   ├── test_deforum_types.py   # Tests for deforum types
│   ├── test_deforum_presets.py # Tests for style presets
│   ├── test_deforum_generator.py # Tests for DeforumGenerator
│   └── test_app.py             # Tests for main application
│
├── webflow/                    # Frontend integration assets
│   ├── api_client.js           # Gradio API client for Webflow
│   ├── embed_snippet.html      # Webflow embed code
│   ├── figma_tokens.json       # Design system tokens
│   └── WEBFLOW_DESIGN_GUIDE.md # Integration guide
│
├── TabAgent-MVP/               # Original CLI implementation
│   ├── main.py                 # Pipeline orchestrator
│   ├── agents.py               # Legacy agent implementations
│   ├── suno_postprocessor.py   # AI audio analysis
│   ├── test_pipeline.py        # Dependency verification
│   ├── setup.sh / setup.bat    # Automated setup scripts
│   └── user_memory/            # User preferences storage
│
└── TabAgent-Web/               # React 19 frontend ("Viral UI")
    ├── src/
    │   ├── App.tsx             # Main React application
    │   ├── main.tsx            # Entry point
    │   ├── index.css           # Tailwind directives
    │   ├── components/
    │   │   ├── features/       # Complex components (UploadZone, ResultsDashboard)
    │   │   ├── layout/         # Layout components (Navbar)
    │   │   └── ui/             # Primitive components (button, HeroBackground)
    │   └── lib/utils.ts        # Utility functions
    ├── package.json            # Frontend dependencies
    ├── vite.config.ts          # Vite configuration
    ├── tailwind.config.js      # Tailwind with neon colors
    └── tsconfig*.json          # TypeScript configs
```

## Technology Stack

### Backend (Python)
- **Framework:** Gradio 4.50+, HuggingFace Spaces (Zero GPU)
- **Audio:** PyTorch 2.0+, Librosa, Demucs 4.0, Basic Pitch 0.3+
- **Transcription:** Basic Pitch (fast) or YourMT3+ (accurate)
- **Video:** Stable Diffusion v1.5, Diffusers, OpenCV
- **Python Version:** 3.11

### Frontend (TypeScript)
- **Framework:** React 19, Vite 7.2
- **Styling:** Tailwind CSS, Framer Motion
- **Integration:** @gradio/client 2.0

## Development Workflows

### Python Backend (Gradio App)

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
# Opens at http://localhost:7860
```

### React Frontend

```bash
# Install dependencies (from root)
npm run install:web
# or: cd TabAgent-Web && npm install

# Development server with HMR
npm run dev
# or: cd TabAgent-Web && npm run dev

# Type checking and linting
cd TabAgent-Web && npm run lint

# Production build
npm run build
# Output: TabAgent-Web/dist/
```

### MVP CLI Testing

```bash
# Verify dependencies
python TabAgent-MVP/test_pipeline.py

# Automated setup
chmod +x TabAgent-MVP/setup.sh && ./TabAgent-MVP/setup.sh
```

## Key Code Patterns

### Agent Architecture (Python)

The codebase uses an agent-based pattern with clear separation of concerns:

```python
from agents import SplitterAgent, EarAgent, TabAgent, SunoDetector

# Each agent has a single responsibility:
splitter = SplitterAgent(output_dir="./stems")
stems = splitter.separate_stems(audio_path)

ear = EarAgent(model="basic_pitch", device="auto")
notes = ear.transcribe_stem(stem_path, target="guitar")

tab_agent = TabAgent(tuning=[40, 45, 50, 55, 59, 64], num_frets=24)
tab_notes = tab_agent.generate_tab(notes)
```

### Data Classes

```python
@dataclass
class Note:
    pitch: int
    start_time: float
    end_time: float
    velocity: int

@dataclass
class TabNote:
    string: int
    fret: int
    start_time: float
    end_time: float
    technique: str
    pitch: int
```

### Zero GPU Decorator

```python
# GPU functions use the @spaces.GPU decorator
if GPU_AVAILABLE:
    @spaces.GPU
    def process_audio(*args, **kwargs):
        return process_audio_impl(*args, **kwargs)
```

### React Component Structure

```typescript
// Functional components with TypeScript interfaces
interface Props {
  onUpload: (file: File) => void;
  isProcessing: boolean;
}

export function UploadZone({ onUpload, isProcessing }: Props) {
  // Hooks at top level
  const [isDragging, setIsDragging] = useState(false);
  // ...
}
```

### Gradio Client Integration

```typescript
import { Client } from "@gradio/client";

const client = await Client.connect("YOUR_SPACE_URL", {
  hf_token: import.meta.env.VITE_HF_TOKEN
});

const result = await client.predict("/process_audio", {
  audio_file: audioBlob,
  instrument: "Guitar",
  tuning: "Guitar (Standard)",
  // ...
});
```

## Configuration

### Main Configuration (config.yaml)

Key configuration sections:
- `tab_agent`: Transcription models, tunings, processing parameters
- `deforum`: Video generation settings, style presets
- `webflow`: API endpoints, CORS settings
- `export`: MIDI and video export settings

### Environment Variables

Frontend requires:
- `VITE_HF_TOKEN`: HuggingFace API token for Gradio client

### Tunings (MIDI note numbers)

```yaml
guitar_standard: [40, 45, 50, 55, 59, 64]  # E2-A2-D3-G3-B3-E4
guitar_drop_d: [38, 45, 50, 55, 59, 64]    # D2-A2-D3-G3-B3-E4
bass_4_string: [28, 33, 38, 43]            # E1-A1-D2-G2
bass_5_string: [23, 28, 33, 38, 43]        # B0-E1-A1-D2-G2
```

## Common Tasks

### Adding a New Tuning

1. Add to `config.yaml` under `tab_agent.tunings`
2. Add to `TUNINGS` dict in `app.py` (line ~42)
3. Update the Gradio dropdown choices if needed

### Adding a Video Style Preset

1. Add preset in `config.yaml` under `deforum.presets`
2. Add corresponding code in `deforum/presets.py`

### Modifying the Processing Pipeline

The main processing flow is in `app.py`:
- `process_audio_impl()` (line 54): Transcription pipeline
- `generate_video_impl()` (line 219): Video generation pipeline

### Updating Frontend Components

UI components are in `TabAgent-Web/src/components/`:
- `ui/`: Primitive, reusable components
- `features/`: Complex feature components
- `layout/`: Page layout components

## Important Files to Know

| File | Purpose |
|------|---------|
| `app.py` | Main Gradio application, API endpoints |
| `config.yaml` | Central configuration for all modules |
| `agents/ear.py` | Audio transcription (Basic Pitch/YourMT3+) |
| `agents/tab.py` | Tablature generation with Viterbi algorithm |
| `agents/splitter.py` | Demucs stem separation |
| `deforum/generator.py` | Stable Diffusion video generation |
| `deforum/audio_sync.py` | Audio-to-animation feature extraction |
| `TabAgent-Web/src/App.tsx` | React frontend main component |

## Code Style Conventions

### Python
- Type hints for function signatures
- Dataclasses for structured data
- Emoji-based logging (e.g., ✅ ❌ ⚠️ 🎵 🎸)
- Lazy model loading for performance
- Device auto-detection (cuda/mps/cpu)

### TypeScript/React
- Functional components with hooks
- Explicit interface/type definitions
- Tailwind CSS utility classes
- Framer Motion for animations
- Path alias: `@` → `./src`

### Design System (Frontend)
- Neon colors: purple `#b026ff`, cyan `#00f0ff`, green `#39ff14`
- Glassmorphism effects with backdrop blur
- Dark theme throughout

## Testing

The project includes a comprehensive pytest test suite with 200+ test cases.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_tab_agent.py

# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests

# Run with coverage
pytest --cov=agents --cov=deforum --cov-report=html
```

### Test Categories (Markers)

- `@pytest.mark.unit` - Fast unit tests, no external dependencies
- `@pytest.mark.integration` - Tests requiring models or external resources
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.gpu` - Tests requiring GPU

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures (audio samples, agents, etc.)
├── test_agents_types.py     # Note, TabNote, Tuning validation
├── test_agents_utils.py     # Utility function tests
├── test_tab_agent.py        # Tablature generation tests
├── test_ear_agent.py        # Transcription tests
├── test_suno_detector.py    # AI detection tests
├── test_splitter_agent.py   # Stem separation tests
├── test_audio_sync.py       # Audio analysis tests
├── test_deforum_*.py        # Video generation tests
└── test_app.py              # Application integration tests
```

### Key Fixtures

- `sample_audio_mono` - Mono sine wave WAV file
- `sample_audio_stereo` - Stereo audio file
- `sample_notes` - List of Note objects for testing
- `tab_agent` - Pre-configured TabAgent instance
- `ear_agent` - EarAgent in mock mode
- `audio_sync_engine` - AudioSyncEngine instance

## Deployment

### HuggingFace Spaces (Primary)
- Push to HF Space repository
- Auto-builds from git push
- Zero GPU (A10G) for inference

### Local Development
- Run `python app.py` for backend
- Run `npm run dev` for frontend

### Webflow Integration
- Embed via `webflow/api_client.js`
- Use data attributes for Webflow elements
- Connect to HF Space via @gradio/client

## Known Issues / Notes

1. `numpy<2.0` pinned for compatibility with older PyTorch versions
2. `xformers` excluded on macOS (`sys_platform != 'darwin'`)
3. YourMT3+ requires monkey-patching `torch.load` for checkpoint loading
4. Demucs may fall back to original audio if not installed

## Processing Pipeline Overview

```
Audio Input
    ↓
[Suno Detection] → AI artifact detection & preprocessing
    ↓
[Stem Separation] → Demucs v4 (guitar/bass stems)
    ↓
[Transcription] → Basic Pitch or YourMT3+ → MIDI notes
    ↓
[Tab Generation] → Viterbi algorithm → optimal fingering
    ↓
[Export] → MIDI, ASCII tabs, JSON
```

```
Video Pipeline:
Audio → [Librosa Analysis] → [Keyframe Generation] → [Stable Diffusion] → MP4
```

## Git Workflow

- Main branch contains stable code
- Feature branches for development
- Commit messages should be descriptive
- No pre-commit hooks configured
