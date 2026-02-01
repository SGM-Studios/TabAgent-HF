"""
DeforumGenerator - Audio-Reactive Video Generation with Stable Diffusion
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

import numpy as np
from PIL import Image

from .audio_sync import AudioSyncEngine, AudioFeatures, AnimationKeyframe


@dataclass
class VideoResult:
    """Result from video generation."""
    video_path: str
    frames_generated: int
    duration_seconds: float
    fps: int
    style: str


class DeforumGenerator:
    """
    Generate audio-reactive videos using Stable Diffusion.
    
    Features:
    - Audio feature extraction and sync
    - Keyframe-based animation
    - Multiple style presets
    - Zero GPU compatible
    """
    
    def __init__(
        self,
        model_id: str = "runwayml/stable-diffusion-v1-5",
        device: str = "auto",
        width: int = 512,
        height: int = 512,
        fps: int = 15
    ):
        """
        Initialize DeforumGenerator.
        
        Args:
            model_id: HuggingFace model ID
            device: "cuda", "cpu", or "auto"
            width: Output video width
            height: Output video height
            fps: Frames per second
        """
        self.model_id = model_id
        self.width = width
        self.height = height
        self.fps = fps
        self.device = self._detect_device(device)
        
        self.audio_sync = AudioSyncEngine(fps=fps)
        self.pipe = None
        self._model_loaded = False
        
        print(f"🎬 DeforumGenerator initialized ({width}x{height} @ {fps}fps)")
    
    def _detect_device(self, device: str) -> str:
        """Detect best available device."""
        if device != "auto":
            return device
        
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
        except ImportError:
            pass
        return "cpu"
    
    def _load_model(self):
        """Lazy load the diffusion model."""
        if self._model_loaded:
            return
        
        try:
            import torch
            from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
            
            print(f"   Loading Stable Diffusion: {self.model_id}")
            
            self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                safety_checker=None
            )
            
            # Use faster scheduler
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config
            )
            
            self.pipe.to(self.device)
            
            if self.device == "cuda":
                self.pipe.enable_attention_slicing()
            
            self._model_loaded = True
            print("   ✅ Model loaded")
            
        except ImportError as e:
            print(f"   ⚠️  Diffusers not installed: {e}")
            self.pipe = None
        except Exception as e:
            print(f"   ❌ Model loading failed: {e}")
            self.pipe = None
    
    def generate(
        self,
        audio_path: str,
        output_path: str = None,
        style: str = "guitar_hero",
        prompt: str = None,
        max_frames: int = 120,
        num_inference_steps: int = 25,
        guidance_scale: float = 7.5
    ) -> Optional[VideoResult]:
        """
        Generate audio-reactive video.
        
        Args:
            audio_path: Path to audio file
            output_path: Output video path (None = auto-generate)
            style: Style preset ("guitar_hero", "concert", "abstract", "acoustic")
            prompt: Custom prompt (overrides style preset)
            max_frames: Maximum number of frames
            num_inference_steps: Diffusion steps per frame
            guidance_scale: CFG scale
            
        Returns:
            VideoResult with output path and metadata
        """
        print(f"🎬 Generating video: {Path(audio_path).name}")
        print(f"   Style: {style}, Max frames: {max_frames}")
        
        # Load model
        self._load_model()
        
        if self.pipe is None:
            print("   ❌ No model available, generating placeholder video")
            return self._generate_placeholder(audio_path, output_path, max_frames)
        
        # Analyze audio
        features = self.audio_sync.analyze_audio(audio_path)
        
        # Generate keyframes
        keyframes = self.audio_sync.generate_keyframes(
            features, max_frames=max_frames, style=style
        )
        
        # Get prompt from preset or use custom
        if prompt is None:
            from .presets import get_preset
            preset = get_preset(style)
            prompt = preset.get('prompt_base', 'abstract art, flowing colors')
        
        # Generate frames
        frames = self._generate_frames(
            prompt=prompt,
            keyframes=keyframes,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale
        )
        
        # Compile video
        if output_path is None:
            output_path = str(Path(audio_path).with_suffix('.mp4'))
        
        video_path = self._compile_video(frames, audio_path, output_path)
        
        return VideoResult(
            video_path=video_path,
            frames_generated=len(frames),
            duration_seconds=len(frames) / self.fps,
            fps=self.fps,
            style=style
        )
    
    def _generate_frames(
        self,
        prompt: str,
        keyframes: List[AnimationKeyframe],
        num_inference_steps: int,
        guidance_scale: float
    ) -> List[Image.Image]:
        """Generate video frames using img2img."""
        import torch
        
        frames = []
        
        # Start with a generated image
        print(f"   Generating {len(keyframes)} frames...")
        
        # Generate initial frame (txt2img-style)
        from diffusers import StableDiffusionPipeline
        
        # Use a simple noise image as starting point
        init_image = Image.new('RGB', (self.width, self.height), color=(128, 128, 128))
        init_image = self._add_noise(init_image, amount=0.5)
        
        prev_image = init_image
        
        for i, kf in enumerate(keyframes):
            if i % 10 == 0:
                print(f"   Frame {i}/{len(keyframes)}...")
            
            # Apply transformations based on keyframe
            warped_image = self._warp_image(prev_image, kf)
            
            # Generate new frame
            try:
                result = self.pipe(
                    prompt=prompt,
                    image=warped_image,
                    strength=kf.strength,
                    guidance_scale=guidance_scale,
                    num_inference_steps=num_inference_steps
                )
                
                frame = result.images[0]
                frames.append(frame)
                prev_image = frame
                
            except Exception as e:
                print(f"   ⚠️  Frame {i} failed: {e}")
                frames.append(prev_image)
        
        print(f"   ✅ Generated {len(frames)} frames")
        return frames
    
    def _warp_image(self, image: Image.Image, kf: AnimationKeyframe) -> Image.Image:
        """Apply zoom, rotation, and translation to image."""
        import cv2
        import numpy as np
        
        # Convert to numpy
        img_np = np.array(image)
        h, w = img_np.shape[:2]
        center = (w // 2, h // 2)
        
        # Create transformation matrix
        # Zoom
        zoom_matrix = cv2.getRotationMatrix2D(center, 0, kf.zoom)
        
        # Rotation
        rot_matrix = cv2.getRotationMatrix2D(center, kf.angle, 1.0)
        
        # Apply transformations
        warped = cv2.warpAffine(img_np, zoom_matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
        warped = cv2.warpAffine(warped, rot_matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
        
        # Translation
        trans_matrix = np.float32([[1, 0, kf.translation_x], [0, 1, kf.translation_y]])
        warped = cv2.warpAffine(warped, trans_matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
        
        return Image.fromarray(warped)
    
    def _add_noise(self, image: Image.Image, amount: float = 0.3) -> Image.Image:
        """Add noise to image."""
        img_np = np.array(image).astype(float)
        noise = np.random.randn(*img_np.shape) * 255 * amount
        noisy = np.clip(img_np + noise, 0, 255).astype(np.uint8)
        return Image.fromarray(noisy)
    
    def _compile_video(
        self,
        frames: List[Image.Image],
        audio_path: str,
        output_path: str
    ) -> str:
        """Compile frames into video with audio."""
        import imageio
        
        print(f"   Compiling video: {Path(output_path).name}")
        
        # Create temporary video without audio
        temp_video = output_path + ".temp.mp4"
        
        # Write frames
        with imageio.get_writer(temp_video, fps=self.fps, codec='libx264') as writer:
            for frame in frames:
                writer.append_data(np.array(frame))
        
        # Add audio with ffmpeg
        try:
            import subprocess
            
            cmd = [
                'ffmpeg', '-y',
                '-i', temp_video,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Clean up temp file
            os.remove(temp_video)
            
            print(f"   ✅ Video saved: {output_path}")
            
        except Exception as e:
            print(f"   ⚠️  Failed to add audio: {e}")
            # Rename temp file as output
            os.rename(temp_video, output_path)
        
        return output_path
    
    def _generate_placeholder(
        self,
        audio_path: str,
        output_path: str,
        max_frames: int
    ) -> VideoResult:
        """Generate a placeholder video when no model is available."""
        import imageio
        
        if output_path is None:
            output_path = str(Path(audio_path).with_suffix('.mp4'))
        
        # Create simple animated gradient frames
        frames = []
        for i in range(min(max_frames, 60)):
            # Create gradient that shifts over time
            img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
            hue_shift = (i * 3) % 256
            for y in range(self.height):
                for x in range(self.width):
                    img[y, x] = [
                        (x + hue_shift) % 256,
                        (y + hue_shift) % 256,
                        128
                    ]
            
            frames.append(img)
        
        # Write video
        with imageio.get_writer(output_path, fps=self.fps, codec='libx264') as writer:
            for frame in frames:
                writer.append_data(frame)
        
        return VideoResult(
            video_path=output_path,
            frames_generated=len(frames),
            duration_seconds=len(frames) / self.fps,
            fps=self.fps,
            style="placeholder"
        )
