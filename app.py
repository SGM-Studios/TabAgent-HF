"""
Tab Agent Pro - Main Gradio Application
HuggingFace Space with Zero GPU support

Combines:
- Tab Agent: Audio-to-tablature transcription
- Deforum: Audio-reactive video generation
"""

import os
import sys
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

import gradio as gr
import numpy as np

# Zero GPU support
try:
    import spaces
    GPU_AVAILABLE = True
    print("✅ Zero GPU available")
except ImportError:
    GPU_AVAILABLE = False
    print("⚠️  Running without Zero GPU")

# Import Tab Agent modules
from agents import SplitterAgent, EarAgent, TabAgent, SunoDetector
from deforum import DeforumGenerator, AudioSyncEngine, STYLE_PRESETS, list_presets

# ============================================================================
# Configuration
# ============================================================================

TEMP_DIR = Path(tempfile.gettempdir()) / "tab_agent_pro"
TEMP_DIR.mkdir(exist_ok=True)

# Default tunings
TUNINGS = {
    "Guitar (Standard)": [40, 45, 50, 55, 59, 64],
    "Guitar (Drop D)": [38, 45, 50, 55, 59, 64],
    "Bass (4-String)": [28, 33, 38, 43],
    "Bass (5-String)": [23, 28, 33, 38, 43],
}


# ============================================================================
# Processing Functions
# ============================================================================

def process_audio_impl(
    audio_file: str,
    instrument: str,
    tuning: str,
    include_midi: bool,
    include_tab: bool,
    include_json: bool,
    detect_suno: bool,
    model_type: str = "Basic Pitch",  # New argument
    progress: gr.Progress = None
) -> Tuple[str, Optional[str], str]:
    """
    Main audio processing pipeline.
    
    Returns:
        Tuple of (status_message, zip_file_path, tab_preview)
    """
    if audio_file is None:
        return "❌ Please upload an audio file", None, ""
    
    try:
        # Create session directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = TEMP_DIR / f"session_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        audio_path = Path(audio_file)
        song_name = audio_path.stem
        
        if progress:
            progress(0.05, desc="🔍 Analyzing audio...")
        
        # Suno detection
        preprocessing_applied = False
        if detect_suno:
            detector = SunoDetector()
            analysis = detector.analyze(str(audio_path))
            
            if analysis.is_ai_generated:
                if progress:
                    progress(0.1, desc="🔧 Preprocessing AI audio...")
                processed_path = str(session_dir / f"{song_name}_processed.wav")
                audio_file = detector.preprocess(str(audio_path), processed_path)
                preprocessing_applied = True
        
        if progress:
            progress(0.15, desc="🎵 Separating stems (Demucs)...")
        
        # Stem separation
        splitter = SplitterAgent(output_dir=str(session_dir / "stems"))
        stems = splitter.separate_stems(audio_file)
        
        if progress:
            progress(0.3, desc="🎸 Processing instrument stems...")
        
        # Process stems based on instrument
        is_bass = "bass" in instrument.lower()
        
        if is_bass:
            processed_stems = {"bass": splitter.process_bass(stems["bass"])}
        else:
            guitar_stems = splitter.process_guitars(stems["guitar"])
            processed_stems = {
                "lead": guitar_stems["lead"],
                "rhythm_L": guitar_stems["left"],
                "rhythm_R": guitar_stems["right"]
            }
        
        if progress:
            progress(0.5, desc=f"🎧 Transcribing audio ({model_type})...")
        
        # Transcription
        # Map friendly name to internal model name
        internal_model = "yourmt3" if "YourMT3" in model_type else "basic_pitch"
        ear = EarAgent(model=internal_model, device="auto")
        tuning_notes = TUNINGS.get(tuning, TUNINGS["Guitar (Standard)"])
        
        results = {}
        tab_preview = ""
        
        for stem_name, stem_path in processed_stems.items():
            if progress:
                progress(0.5 + 0.2 * (len(results) / len(processed_stems)),
                        desc=f"🎸 Transcribing {stem_name}...")
            
            # Transcribe
            target = "bass" if is_bass else "guitar"
            notes = ear.transcribe_stem(stem_path, target=target)
            
            # Export MIDI
            if include_midi:
                midi_path = session_dir / f"{song_name}_{stem_name}.mid"
                ear.export_midi(notes, str(midi_path))
            
            results[stem_name] = notes
        
        if progress:
            progress(0.75, desc="📝 Generating tablature...")
        
        # Tablature generation
        tab_agent = TabAgent(
            tuning=tuning_notes,
            num_frets=24,
            instrument="bass" if is_bass else "guitar"
        )
        
        for stem_name, notes in results.items():
            tab_notes = tab_agent.generate_tab(notes)
            
            # Export ASCII tab
            if include_tab:
                tab_text = tab_agent.export_ascii(tab_notes, title=f"{song_name} - {stem_name}")
                tab_path = session_dir / f"{song_name}_{stem_name}.tab"
                tab_path.write_text(tab_text)
                
                # Use first stem as preview
                if not tab_preview:
                    tab_preview = tab_text
            
            # Export JSON
            if include_json:
                json_text = tab_agent.export_json(tab_notes, title=f"{song_name} - {stem_name}")
                json_path = session_dir / f"{song_name}_{stem_name}.json"
                json_path.write_text(json_text)
        
        if progress:
            progress(0.9, desc="📦 Creating download package...")
        
        # Create ZIP
        zip_path = session_dir / f"{song_name}_tablature.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in session_dir.rglob("*"):
                if file.is_file() and file != zip_path:
                    arcname = file.relative_to(session_dir)
                    zipf.write(file, arcname)
        
        if progress:
            progress(1.0, desc="✅ Complete!")
        
        # Status message
        file_count = len(list(session_dir.glob("*.*"))) - 1
        status = f"""
## ✅ Transcription Complete!

| Property | Value |
|----------|-------|
| **Song** | {song_name} |
| **Instrument** | {instrument} |
| **Tuning** | {tuning} |
| **Files Generated** | {file_count} |
| **AI Audio Detected** | {'Yes (preprocessed)' if preprocessing_applied else 'No'} |

📥 **Download the ZIP file below!**
        """
        
        return status, str(zip_path), tab_preview
        
    except Exception as e:
        import traceback
        error_msg = f"❌ **Error:**\n```\n{str(e)}\n\n{traceback.format_exc()}\n```"
        return error_msg, None, ""


def generate_video_impl(
    audio_file: str,
    style: str,
    custom_prompt: str,
    max_seconds: int,
    progress: gr.Progress = None
) -> Tuple[str, Optional[str]]:
    """
    Generate audio-reactive video with Deforum.
    
    Returns:
        Tuple of (status_message, video_path)
    """
    if audio_file is None:
        return "❌ Please upload an audio file", None
    
    try:
        if progress:
            progress(0.1, desc="🎵 Analyzing audio...")
        
        # Create session directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = TEMP_DIR / f"video_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        audio_path = Path(audio_file)
        song_name = audio_path.stem
        output_path = str(session_dir / f"{song_name}_video.mp4")
        
        # Initialize generator
        generator = DeforumGenerator(fps=15)
        
        if progress:
            progress(0.2, desc="🎬 Generating video...")
        
        # Use custom prompt if provided
        prompt = custom_prompt if custom_prompt.strip() else None
        
        # Calculate max frames (15 fps)
        max_frames = min(max_seconds * 15, 300)  # Cap at 20 seconds
        
        result = generator.generate(
            audio_path=str(audio_path),
            output_path=output_path,
            style=style,
            prompt=prompt,
            max_frames=max_frames
        )
        
        if progress:
            progress(1.0, desc="✅ Complete!")
        
        if result:
            status = f"""
## ✅ Video Generated!

| Property | Value |
|----------|-------|
| **Duration** | {result.duration_seconds:.1f}s |
| **Frames** | {result.frames_generated} |
| **FPS** | {result.fps} |
| **Style** | {result.style} |
            """
            return status, result.video_path
        else:
            return "❌ Video generation failed", None
            
    except Exception as e:
        import traceback
        error_msg = f"❌ **Error:**\n```\n{str(e)}\n\n{traceback.format_exc()}\n```"
        return error_msg, None


# Apply Zero GPU decorator if available
if GPU_AVAILABLE:
    @spaces.GPU
    def process_audio(*args, **kwargs):
        return process_audio_impl(*args, **kwargs)
    
    @spaces.GPU
    def generate_video(*args, **kwargs):
        return generate_video_impl(*args, **kwargs)
else:
    process_audio = process_audio_impl
    generate_video = generate_video_impl


# ============================================================================
# Gradio UI
# ============================================================================

def create_demo():
    """Create the Gradio demo interface."""
    
    with gr.Blocks(
        title="Tab Agent Pro - AI Tablature + Video",
        theme=gr.themes.Soft(
            primary_hue="purple",
            secondary_hue="blue"
        ),
        css="""
        .gradio-container { max-width: 1200px; margin: auto; }
        .tab-preview { font-family: monospace; white-space: pre; font-size: 12px; }
        """
    ) as demo:
        
        # Header
        gr.Markdown("""
# 🎸 Tab Agent Pro
        
**AI-Powered Tablature Transcription + Audio-Reactive Video Generation**

Upload your audio and get:
- 🎵 **Accurate tablature** for guitar and bass
- 🎬 **Audio-synced videos** with Deforum Stable Diffusion
- 📦 **Multiple formats**: MIDI, ASCII tabs, JSON

⚡ Powered by Zero GPU for fast processing
        """)
        
        with gr.Tabs():
            # ============================================================
            # Tab 1: Transcription
            # ============================================================
            with gr.TabItem("🎸 Transcribe Audio"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Upload Audio")
                        
                        audio_input = gr.Audio(
                            label="Audio File",
                            type="filepath",
                            sources=["upload"]
                        )
                        
                        instrument = gr.Radio(
                            label="Instrument",
                            choices=["Guitar", "Bass"],
                            value="Guitar"
                        )
                        
                        tuning = gr.Dropdown(
                            label="Tuning",
                            choices=list(TUNINGS.keys()),
                            value="Guitar (Standard)"
                        )
                        
                        model_selector = gr.Dropdown(
                            label="Transcription Model",
                            choices=["Basic Pitch (Fast)", "YourMT3+ (Best Accuracy)"],
                            value="YourMT3+ (Best Accuracy)",
                            info="YourMT3+ is slower but much more accurate for polyphonic audio."
                        )
                        
                        gr.Markdown("### Export Options")
                        
                        with gr.Row():
                            export_midi = gr.Checkbox(label="MIDI", value=True)
                            export_tab = gr.Checkbox(label="ASCII Tab", value=True)
                            export_json = gr.Checkbox(label="JSON", value=True)
                        
                        detect_suno = gr.Checkbox(
                            label="🤖 Detect & preprocess AI audio (Suno/Udio)",
                            value=True
                        )
                        
                        transcribe_btn = gr.Button(
                            "🎸 Transcribe Now",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Results")
                        
                        status_output = gr.Markdown(
                            value="Upload audio and click 'Transcribe' to begin."
                        )
                        
                        download_output = gr.File(
                            label="Download ZIP",
                            interactive=False
                        )
                        
                        gr.Markdown("### Tab Preview")
                        tab_preview = gr.Code(
                            label="Tablature",
                            language="text",
                            lines=15
                        )
                
                # Connect transcription
                transcribe_btn.click(
                    fn=process_audio,
                    inputs=[
                        audio_input,
                        instrument,
                        tuning,
                        export_midi,
                        export_tab,
                        export_json,
                        detect_suno,
                        model_selector
                    ],
                    outputs=[status_output, download_output, tab_preview]
                )
            
            # ============================================================
            # Tab 2: Video Generation
            # ============================================================
            with gr.TabItem("🎬 Generate Video"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Upload Audio")
                        
                        video_audio_input = gr.Audio(
                            label="Audio File",
                            type="filepath",
                            sources=["upload"]
                        )
                        
                        style_preset = gr.Dropdown(
                            label="Visual Style",
                            choices=list_presets(),
                            value="guitar_hero"
                        )
                        
                        custom_prompt = gr.Textbox(
                            label="Custom Prompt (optional)",
                            placeholder="Leave empty to use style preset...",
                            lines=2
                        )
                        
                        max_duration = gr.Slider(
                            label="Max Duration (seconds)",
                            minimum=5,
                            maximum=20,
                            value=10,
                            step=1
                        )
                        
                        generate_btn = gr.Button(
                            "🎬 Generate Video",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Results")
                        
                        video_status = gr.Markdown(
                            value="Upload audio and click 'Generate' to begin."
                        )
                        
                        video_output = gr.Video(
                            label="Generated Video",
                            interactive=False
                        )
                
                # Connect video generation
                generate_btn.click(
                    fn=generate_video,
                    inputs=[
                        video_audio_input,
                        style_preset,
                        custom_prompt,
                        max_duration
                    ],
                    outputs=[video_status, video_output]
                )
            
            # ============================================================
            # Tab 3: API Documentation
            # ============================================================
            with gr.TabItem("📚 API"):
                gr.Markdown("""
## API Documentation

This Gradio app exposes API endpoints for integration with external frontends (like Webflow).

### Transcription API

```javascript
const client = await Client.connect("YOUR_SPACE_URL");

const result = await client.predict("/transcribe", {
    audio: audioFile,
    instrument: "Guitar",
    tuning: "Guitar (Standard)",
    include_midi: true,
    include_tab: true,
    include_json: true,
    detect_suno: true
});

console.log(result.data);  // [status, zip_url, tab_preview]
```

### Video Generation API

```javascript
const result = await client.predict("/generate_video", {
    audio: audioFile,
    style: "guitar_hero",
    custom_prompt: "",
    max_seconds: 10
});

console.log(result.data);  // [status, video_url]
```

### Webflow Integration

See the `webflow/` directory for:
- Figma design tokens
- Embed snippet for Webflow
- JavaScript API client
                """)
        
        # Footer
        gr.Markdown("""
---

**Tab Agent Pro** | [GitHub](https://github.com/YOUR_USERNAME/TabAgent-HF) | Powered by 🤗 HuggingFace Zero GPU

Built with ❤️ using YourMT3+, Basic Pitch, Demucs, and Stable Diffusion
        """)
    
    return demo


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    demo = create_demo()
    demo.queue()
    demo.launch()
