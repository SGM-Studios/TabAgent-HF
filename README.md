---
title: Tab Agent Pro
emoji: 🎸
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: "4.50.0"
app_file: app.py
pinned: true
license: mit
hardware: zero-a10g
suggested_hardware: zero-a10g
suggested_storage: large
tags:
  - music
  - audio
  - transcription
  - guitar
  - bass
  - tablature
  - video-generation
  - deforum
  - stable-diffusion
  - basic-pitch
  - demucs
models:
  - runwayml/stable-diffusion-v1-5
datasets: []
---

# 🎸 Tab Agent Pro

**AI-Powered Tablature Transcription + Audio-Reactive Video Generation**

Upload your audio and get:
- 🎵 **Accurate tablature** for guitar and bass
- 🎬 **Audio-synced videos** with Deforum Stable Diffusion
- 📦 **Multiple formats**: MIDI, ASCII tabs, JSON

## 📋 Repository Overview

This repository contains a complete AI-powered music transcription and video generation platform. It combines multiple cutting-edge technologies to convert audio files into guitar/bass tablatures and generate synchronized videos.

### Project Structure
- `app.py`: Main Gradio application
- `agents/`: Audio processing agents (Splitter, Ear, Tab, SunoDetector)
- `deforum/`: Video generation components
- `tests/`: Unit tests for all major components
- `webflow/`: Webflow integration assets
- `TabAgent-MVP/`: Minimum viable product implementation
- `TabAgent-Web/`: Web-based frontend components

## ✨ Features

### Tab Agent (Audio Transcription)
- ✅ Multi-instrument: Lead, rhythm (L/R), bass
- ✅ Demucs stem separation
- ✅ Basic Pitch / YourMT3+ transcription
- ✅ Viterbi optimal fingering algorithm
- ✅ Suno/Udio AI audio detection & preprocessing
- ✅ Export: MIDI, ASCII Tab, JSON

### Deforum Integration (Visual Generation)
- ✅ Audio-reactive video with Stable Diffusion
- ✅ Note onset → keyframe triggers
- ✅ BPM sync with camera motion
- ✅ Multiple style presets

## 🚀 How to Use

### Transcription
1. Upload an audio file (WAV, MP3, FLAC)
2. Select instrument type (Guitar/Bass)
3. Choose export formats
4. Click "Transcribe Now"
5. Download the ZIP with all outputs

### Video Generation
1. Upload an audio file
2. Select a visual style preset
3. Set max duration
4. Click "Generate Video"
5. Watch your audio-reactive video!

## 📊 Processing Times (Zero GPU)

| Duration | Transcription | Video (10s) |
|----------|---------------|-------------|
| 30 sec   | ~1-2 min      | ~3-5 min    |
| 60 sec   | ~2-4 min      | ~5-8 min    |

## 🔗 API Usage

Connect from your web app:

```javascript
import { Client } from "@gradio/client";

const client = await Client.connect("YOUR_SPACE_URL");

// Transcribe
const result = await client.predict("/process_audio", {
    audio_file: audioBlob,
    instrument: "Guitar",
    // ... options
});

// Generate video
const video = await client.predict("/generate_video", {
    video_audio_input: audioBlob,
    style_preset: "guitar_hero"
});
```

## 📄 License

MIT License - Free for personal and commercial use.

## 🙏 Acknowledgments

- **Spotify** - Basic Pitch transcription
- **Meta AI** - Demucs source separation
- **Stability AI** - Stable Diffusion
- **HuggingFace** - Zero GPU infrastructure

---

**Made with ❤️ and 🤖 AI**
