# Tab Agent Pro - Webflow Design Guide

## 🎨 Figma → Webflow Workflow

This guide helps you create the Tab Agent Pro frontend in Webflow using the provided design tokens.

---

## 1. Setup Webflow Project

### Create New Project
1. Create new Webflow project: "Tab Agent Pro"
2. Set up custom fonts:
   - Go to Project Settings → Fonts
   - Add Google Fonts: **Inter** (400, 500, 600, 700, 800)
   - Add Google Fonts: **JetBrains Mono** (for tab preview)

### Global Styles
Add these as Webflow CSS variables in Project Settings → Custom Code → Head:

```html
<style>
  :root {
    --color-primary: #9333ea;
    --color-primary-light: #a855f7;
    --color-secondary: #3b82f6;
    --color-accent: #10b981;
    --color-bg: #09090b;
    --color-card: #18181b;
    --color-border: rgba(255, 255, 255, 0.1);
    --font-sans: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
  }
</style>
```

---

## 2. Page Structure

### Navbar
- **Height**: 64px
- **Background**: rgba(0, 0, 0, 0.8) with backdrop-filter: blur(12px)
- **Border-bottom**: 1px solid var(--color-border)
- **Position**: Fixed, full width, z-index: 50

**Elements**:
- Logo (gradient purple icon + "Tab Agent" text)
- Sign In button (ghost style)

### Hero Section
- **Padding**: 128px top, 64px bottom
- **Max-width**: 800px, centered
- **Text-align**: center

**Elements**:
1. **H1 Headline** (gradient text):
   ```
   Turn Audio into
   Perfect Guitar Tabs
   ```
   - Font: Inter, 4.5rem (desktop), 2.5rem (mobile)
   - Weight: 800
   - Gradient: white → gray-200 → gray-500

2. **Subtitle**:
   ```
   The world's most advanced AI transcriber...
   ```
   - Font: Inter, 1.125rem
   - Color: #71717a
   - Max-width: 640px

### Upload Zone
- **Background**: rgba(255, 255, 255, 0.05)
- **Border**: 2px dashed var(--color-border)
- **Border-radius**: 24px
- **Padding**: 48px 32px
- **Hover**: border-color → purple-500, bg → rgba(255, 255, 255, 0.1)

**Elements**:
- Upload icon (64px circle, centered)
- "Drop your audio file here" heading
- "or click to browse" subtitle
- Hidden file input (triggered by click)

### Results Card
- **Background**: gradient from #27272a to #18181b
- **Border**: 1px solid var(--color-border)
- **Border-radius**: 24px
- **Padding**: 32px

**Elements**:
- Success badge (green)
- Status message
- Tab preview (monospace, green text on dark bg)
- Download button (primary gradient)

### Features Section
Three-column grid with feature cards:
1. 🎸 Multi-Track Transcription
2. 🤖 Suno AI Detection
3. 🎬 Video Generation

---

## 3. Component Classes

### Buttons

**.btn-primary**
```css
background: linear-gradient(135deg, #9333ea 0%, #7c3aed 100%);
color: white;
padding: 12px 24px;
border-radius: 12px;
font-weight: 600;
box-shadow: 0 4px 6px -1px rgba(147, 51, 234, 0.3);
transition: all 0.2s;
```

**.btn-secondary**
```css
background: transparent;
color: #a1a1aa;
border: 1px solid rgba(255, 255, 255, 0.1);
padding: 12px 24px;
border-radius: 12px;
```

### Cards

**.card-default**
```css
background: linear-gradient(180deg, #27272a 0%, #18181b 100%);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 24px;
padding: 32px;
```

**.card-glass**
```css
background: rgba(24, 24, 27, 0.8);
backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 24px;
```

### Tab Preview

**.tab-preview**
```css
font-family: 'JetBrains Mono', monospace;
font-size: 12px;
line-height: 1.4;
color: #10b981;
background: rgba(0, 0, 0, 0.4);
border: 1px solid rgba(255, 255, 255, 0.05);
border-radius: 12px;
padding: 16px;
white-space: pre;
overflow-x: auto;
```

---

## 4. Interactions

### Upload Zone Hover
- Border color animates to purple-500
- Background brightens slightly
- Icon scales to 1.1

### Button Hover
- Transform: translateY(-2px)
- Box-shadow increases
- Background lightens (for primary)

### Loading State
- Spinner animation (rotate 360deg, 1s, infinite)
- Pulse animation on text
- Overlay with blur backdrop

### Success Animation
- Fade in + slide up (opacity 0→1, translateY 20px→0)
- Duration: 0.5s
- Easing: cubic-bezier(0.4, 0, 0.2, 1)

---

## 5. Webflow Custom Attributes

Add these custom attributes for JavaScript targeting:

| Element | Attribute |
|---------|-----------|
| Upload dropzone | `data-dropzone` |
| File input (transcribe) | `data-transcribe-input` |
| File input (video) | `data-video-input` |
| Results container | `data-results` |
| Status message | `data-status` |
| Tab preview | `data-tab-preview` |
| Download button | `data-download` |
| Video player | `data-video-player` |
| Loader | `data-loader` |
| Instrument select | `data-instrument` |
| Tuning select | `data-tuning` |
| Style select | `data-style` |
| Duration slider | `data-duration` |

---

## 6. Responsive Breakpoints

| Breakpoint | Width | Changes |
|------------|-------|---------|
| Desktop | 1280px+ | Full layout |
| Tablet | 768px-1279px | Stack columns, reduce padding |
| Mobile | <768px | Single column, smaller fonts |

### Mobile Adjustments
- H1: 2.5rem → 1.875rem
- Section padding: 48px → 24px
- Card padding: 32px → 16px
- Features: 3-col → 1-col

---

## 7. Custom Code Integration

### Footer Code (before `</body>`)

Paste the contents of `embed_snippet.html` into:
**Page Settings → Custom Code → Before </body> tag**

### Head Code

Add to **Page Settings → Custom Code → Inside <head> tag**:

```html
<!-- Gradio Client for API calls -->
<script type="module">
  import { Client } from "https://cdn.jsdelivr.net/npm/@gradio/client@latest/+esm";
  window.GradioClient = Client;
</script>

<!-- Tab Agent Configuration -->
<script>
  window.TAB_AGENT_CONFIG = {
    spaceUrl: "https://YOUR_USERNAME-tab-agent-pro.hf.space",
    // Update with your actual Space URL
  };
</script>
```

---

## 8. Publishing Checklist

- [ ] Update SPACE_URL in embed_snippet.html
- [ ] Add Google Fonts (Inter, JetBrains Mono)
- [ ] Set page background to #09090b
- [ ] Test file upload on mobile
- [ ] Verify CORS settings on HuggingFace Space
- [ ] Test all breakpoints
- [ ] Add meta tags (title, description, OG image)
- [ ] Add favicon (guitar icon)
- [ ] Set up custom domain
- [ ] Enable SSL

---

## 9. Figma File References

The design tokens in `figma_tokens.json` can be imported into Figma using:
- **Tokens Studio for Figma** plugin
- Or manually apply styles from the JSON

Key Figma frames to create:
1. **Landing Page** - Hero, upload, features
2. **Results View** - Tab preview, download
3. **Video Generator** - Style picker, player
4. **Mobile Views** - Responsive layouts

---

## 10. Need Help?

- **Design Tokens**: `webflow/figma_tokens.json`
- **API Client**: `webflow/api_client.js`
- **Embed Code**: `webflow/embed_snippet.html`
- **Backend Docs**: See `app.py` API tab

For the HuggingFace Space backend, deploy the `TabAgent-HF` folder to your Space.
