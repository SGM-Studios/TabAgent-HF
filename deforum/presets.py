"""
Deforum Style Presets - Visual styles for audio-reactive video generation
"""

from typing import Dict, Any

# Style preset definitions
STYLE_PRESETS: Dict[str, Dict[str, Any]] = {
    "guitar_hero": {
        "name": "Guitar Hero",
        "description": "Neon-lit concert stage with dramatic lighting",
        "prompt_base": "electric guitar, neon lights, concert stage, dramatic lighting, music visualization, purple and blue glow, high energy, rock concert",
        "negative_prompt": "blurry, low quality, deformed, ugly, cartoon",
        "color_coherence": "LAB",
        "motion_scale": 1.5,
        "strength_base": 0.65,
        "guidance_scale": 7.5
    },
    
    "concert": {
        "name": "Live Concert",
        "description": "Crowd silhouettes with stage lights and smoke",
        "prompt_base": "live concert, crowd silhouette, stage lights, smoke effects, rock music atmosphere, spotlights, professional photography",
        "negative_prompt": "blurry, low quality, cartoon, anime",
        "color_coherence": "HSV",
        "motion_scale": 1.0,
        "strength_base": 0.55,
        "guidance_scale": 7.0
    },
    
    "abstract": {
        "name": "Abstract Visualization",
        "description": "Psychedelic patterns and flowing colors",
        "prompt_base": "abstract art, flowing colors, musical waveforms, digital art, psychedelic patterns, fractals, gradient, synthwave aesthetic",
        "negative_prompt": "realistic, photograph, text",
        "color_coherence": "None",
        "motion_scale": 2.0,
        "strength_base": 0.7,
        "guidance_scale": 8.0
    },
    
    "acoustic": {
        "name": "Acoustic Session",
        "description": "Warm, intimate setting with natural lighting",
        "prompt_base": "acoustic guitar, warm lighting, intimate setting, wooden textures, folk music vibes, cozy atmosphere, soft shadows, vintage",
        "negative_prompt": "neon, digital, high contrast",
        "color_coherence": "LAB",
        "motion_scale": 0.5,
        "strength_base": 0.5,
        "guidance_scale": 6.5
    },
    
    "metal": {
        "name": "Heavy Metal",
        "description": "Dark, intense visuals with fire and skulls",
        "prompt_base": "heavy metal, fire, skulls, dark atmosphere, intense red lighting, black metal aesthetic, chains, dramatic shadows",
        "negative_prompt": "cute, bright, cheerful, pastel",
        "color_coherence": "LAB",
        "motion_scale": 1.8,
        "strength_base": 0.7,
        "guidance_scale": 8.5
    },
    
    "jazz": {
        "name": "Jazz Club",
        "description": "Smoky jazz club with warm amber lighting",
        "prompt_base": "jazz club, smoky atmosphere, amber lighting, silhouette, saxophone, double bass, vintage feel, noir aesthetic, elegant",
        "negative_prompt": "neon, bright colors, modern",
        "color_coherence": "LAB",
        "motion_scale": 0.6,
        "strength_base": 0.45,
        "guidance_scale": 6.0
    },
    
    "synthwave": {
        "name": "Synthwave",
        "description": "Retro-futuristic 80s aesthetic with grid and sunset",
        "prompt_base": "synthwave, retrowave, neon grid, sunset, chrome, 80s aesthetic, vaporwave, outrun, purple and pink gradient, palm trees",
        "negative_prompt": "realistic, natural, organic",
        "color_coherence": "HSV",
        "motion_scale": 1.2,
        "strength_base": 0.6,
        "guidance_scale": 7.5
    },
    
    "nature": {
        "name": "Nature Scene",
        "description": "Beautiful landscapes synced to music",
        "prompt_base": "beautiful nature, landscape, mountains, sunset, clouds, dramatic sky, cinematic, epic, peaceful, 4k photography",
        "negative_prompt": "artificial, urban, text",
        "color_coherence": "LAB",
        "motion_scale": 0.4,
        "strength_base": 0.5,
        "guidance_scale": 7.0
    }
}


def get_preset(style: str) -> Dict[str, Any]:
    """
    Get a style preset by name.
    
    Args:
        style: Preset name (case-insensitive)
        
    Returns:
        Preset dictionary
    """
    style_lower = style.lower().replace(" ", "_")
    return STYLE_PRESETS.get(style_lower, STYLE_PRESETS["guitar_hero"])


def list_presets() -> list:
    """List all available preset names."""
    return list(STYLE_PRESETS.keys())


def get_preset_description(style: str) -> str:
    """Get the description for a preset."""
    preset = get_preset(style)
    return preset.get("description", "No description available")
