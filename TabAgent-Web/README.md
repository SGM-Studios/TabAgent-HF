# 🎸 Tab Agent PRO (Web Frontend)

**Version 1.0 "Viral"**

This is the high-performance React frontend for Tab Agent Pro. It features a "Dark Glass & Neon" design language, magnetic interactions, and real-time integration with the Hugging Face backend.

## 🚀 Tech Stack
- **Framework**: React 19 + Vite
- **Styling**: TailwindCSS 4 (via PostCSS)
- **Animation**: Framer Motion (Spring physics, Layout animations)
- **Icons**: Lucide React
- **Integration**: `@gradio/client` (Connects to HF Space)

## 🛠️ Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Environment Setup**
   Create a `.env` file in this directory:
   ```bash
   VITE_HF_TOKEN=hf_... # Your Hugging Face Read Token
   ```

3. **Run Locally**
   ```bash
   npm run dev
   ```

## 📦 Deployment Options

### Option A: Vercel (Recommended for Speed)
This frontend is optimized for edge deployment.
1. Push this folder to GitHub.
2. Import project into Vercel.
3. Add `VITE_HF_TOKEN` to Vercel Environment Variables.
4. **Build Command**: `npm run build`
5. **Output Directory**: `dist`

### Option B: Hugging Face Space (Integrated)
This frontend can be served directly by the Python backend.
1. Run `npm run build`.
2. Ensure the `dist/` folder is committed or generated in the Dockerfile.
3. The `app.py` in the parent directory is configured to serve these static files.

## 📂 Project Structure
```
src/
├── components/
│   ├── features/       # Complex functionality (UploadZone, Results)
│   ├── layout/         # Structural components (Navbar)
│   └── ui/             # Primitive UI elements (Button, MagneticWrapper)
├── App.tsx             # Main application composition
└── index.css           # Global styles & Tailwind directives
```

## 🎨 Design System
- **Colors**: Neon Purple (`#b026ff`), Cyan (`#00f0ff`), Green (`#00ff9d`)
- **Effects**: Glassmorphism (`backdrop-blur-xl`), Noise Textures, Mesh Gradients
- **Typography**: Outfit (Headings), Inter (Body), JetBrains Mono (Code/Tabs)
