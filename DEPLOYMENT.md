# Tab Agent Pro - Deployment Guide

## 🚀 Deploy to HuggingFace Spaces

### Prerequisites
- HuggingFace account with Pro subscription (for Zero GPU)
- Git installed locally

### Step 1: Create New Space

1. Go to https://huggingface.co/new-space
2. Name: `tab-agent-pro` (or your preferred name)
3. SDK: **Gradio**
4. Hardware: **Zero GPU (A10G)** ⚡
5. Visibility: Public or Private

### Step 2: Clone and Push

```bash
# Clone your new Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/tab-agent-pro
cd tab-agent-pro

# Copy files from TabAgent-HF
# (On Windows)
xcopy /E /I "c:\hivyr\TabAgent-HF\*" .

# Or on Mac/Linux
cp -r /path/to/TabAgent-HF/* .

# Add all files
git add .
git commit -m "Initial deployment"

# Push to HuggingFace
git push
```

### Step 3: Wait for Build

- HuggingFace will automatically build and deploy
- Check the "Building" status in your Space
- First build takes ~5-10 minutes (downloading models)

### Step 4: Test

1. Visit your Space URL
2. Upload a test audio file
3. Verify transcription works
4. Test video generation

---

## 🌐 Connect to Webflow

### Step 1: Get Your Space URL

Your Space URL format:
```
https://YOUR_USERNAME-tab-agent-pro.hf.space
```

### Step 2: Update Webflow Code

1. Open `webflow/embed_snippet.html`
2. Replace `YOUR_USERNAME` with your actual username
3. Copy the entire contents

### Step 3: Add to Webflow

1. Open your Webflow project
2. Go to **Page Settings** → **Custom Code**
3. Paste in **Before </body> tag** section

### Step 4: Add HTML Elements

In Webflow Designer, add elements with these data attributes:
- `data-dropzone` - Upload zone
- `data-transcribe-input` - File input
- `data-results` - Results container
- `data-tab-preview` - Tab display
- `data-download` - Download button

See `WEBFLOW_DESIGN_GUIDE.md` for complete styling.

---

## 🎨 Figma Integration

### Import Design Tokens

1. Install **Tokens Studio** plugin in Figma
2. Import `webflow/figma_tokens.json`
3. Apply tokens to your design

### Key Design Elements

- **Colors**: Purple primary, blue secondary, emerald accent
- **Fonts**: Inter (UI), JetBrains Mono (tabs)
- **Cards**: Glassmorphism with subtle borders
- **Buttons**: Gradient with glow effects

---

## 🔧 Local Development

### Setup

```bash
cd TabAgent-HF

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Locally

```bash
python app.py
```

Opens at http://localhost:7860

### Test Pipeline

```bash
# Test transcription
python -c "from agents import EarAgent; print(EarAgent())"

# Test Deforum
python -c "from deforum import DeforumGenerator; print(DeforumGenerator())"
```

---

## 🐛 Troubleshooting

### "No module named 'spaces'"
- Only available on HuggingFace Spaces
- Local runs work without Zero GPU (CPU mode)

### "CUDA out of memory"
- Reduce video max_frames
- Use CPU fallback for transcription

### Webflow CORS errors
- Check Space is public
- Verify URL is correct
- Try with `/` at end of URL

### Slow first request
- Normal: models download on first use
- Subsequent requests are faster

---

## 📁 File Structure

```
TabAgent-HF/
├── README.md              # HuggingFace Space README
├── app.py                 # Main Gradio application
├── requirements.txt       # Python dependencies
├── config.yaml            # Configuration
│
├── agents/                # Tab Agent core
│   ├── __init__.py
│   ├── splitter.py        # Demucs separation
│   ├── ear.py             # Basic Pitch transcription
│   ├── tab.py             # Viterbi tablature
│   └── suno_detector.py   # AI audio detection
│
├── deforum/               # Video generation
│   ├── __init__.py
│   ├── generator.py       # Stable Diffusion
│   ├── audio_sync.py      # Beat/onset sync
│   └── presets.py         # Style presets
│
├── webflow/               # Frontend assets
│   ├── figma_tokens.json  # Design tokens
│   ├── api_client.js      # JavaScript client
│   ├── embed_snippet.html # Webflow embed
│   └── WEBFLOW_DESIGN_GUIDE.md
│
└── DEPLOYMENT.md          # This file
```

---

## 🔐 Security Notes

- Don't expose API keys in frontend code
- Use environment variables for secrets
- Consider rate limiting for production
- Add authentication for paid features

---

## 📈 Scaling

For high traffic:
1. Upgrade to persistent GPU hardware
2. Add Redis queue for long jobs
3. Implement user authentication
4. Add Stripe for monetization

---

**Good luck with your deployment! 🎸🚀**
