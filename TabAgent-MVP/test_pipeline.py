"""
Quick test script to verify Tab Agent works end-to-end
"""

import os
import sys
import codecs

# Fix Windows encoding for emojis
if sys.platform == "win32":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# Check dependencies
print("=" * 60)
print("🧪 TAB AGENT - DEPENDENCY CHECK")
print("=" * 60)

missing_deps = []

# Test Basic Pitch
try:
    from basic_pitch.inference import predict
    print("✅ Basic Pitch installed")
except ImportError:
    print("❌ Basic Pitch NOT installed")
    print("   Install: pip install basic-pitch")
    missing_deps.append("basic-pitch")

# Test Demucs
try:
    from demucs.pretrained import get_model
    print("✅ Demucs installed")
except ImportError:
    print("❌ Demucs NOT installed")
    print("   Install: pip install demucs")
    missing_deps.append("demucs")

# Test librosa
try:
    import librosa
    print("✅ Librosa installed")
except ImportError:
    print("❌ Librosa NOT installed")
    print("   Install: pip install librosa")
    missing_deps.append("librosa")

# Test note_seq
try:
    import note_seq
    print("✅ note-seq installed")
except ImportError:
    print("❌ note-seq NOT installed")
    print("   Install: pip install note-seq")
    missing_deps.append("note-seq")

# Test soundfile
try:
    import soundfile
    print("✅ soundfile installed")
except ImportError:
    print("❌ soundfile NOT installed")
    print("   Install: pip install soundfile")
    missing_deps.append("soundfile")

print()

if missing_deps:
    print("=" * 60)
    print("❌ MISSING DEPENDENCIES")
    print("=" * 60)
    print("\nInstall all missing packages:")
    print(f"pip install {' '.join(missing_deps)}")
    print()
    sys.exit(1)

# Test agents
print("=" * 60)
print("🧪 TAB AGENT - MODULE CHECK")
print("=" * 60)

try:
    from agents import SplitterAgent, EarAgent, TabAgent
    print("✅ agents.py imports successfully")
except Exception as e:
    print(f"❌ Failed to import agents: {e}")
    sys.exit(1)

# Test initialization
try:
    ear = EarAgent()
    print("✅ EarAgent initializes successfully")
except Exception as e:
    print(f"❌ Failed to initialize EarAgent: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL CHECKS PASSED")
print("=" * 60)
print()
print("Ready to run:")
print("  python main.py <your_audio_file.wav>")
print()
print("Test with a short audio clip (10-30 seconds recommended)")
print()
