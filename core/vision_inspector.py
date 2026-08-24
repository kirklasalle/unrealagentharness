"""
Phase 2: Multimodal Vision Inspector for UnrealEd Viewports.
Captures UnrealEd viewport framebuffers and provides structured
analysis interfaces for LLM-based spatial reasoning.

Supports:
  - Viewport screenshot capture via Win32 + PIL
  - Viewport region extraction (3D perspective, top/front/side ortho)
  - Screenshot annotation with grid overlays
  - Image encoding for multimodal LLM dispatch (base64 PNG)
"""

import base64
import io
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont, ImageGrab
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import win32gui
    HAS_PYWIN32 = True
except ImportError:
    HAS_PYWIN32 = False

from .bootstrap import get_dpi_scale_factor
from .logger import get_logger

logger = get_logger("VisionInspector", "vision_inspector.log")

# OldUnreal 469e UnrealEd viewport layout constants (approximate)
# The main window has 4 quadrant viewports:
# ┌──────────┬──────────┐
# │  3D Persp │  Top XY  │
# ├──────────┼──────────┤
# │ Front XZ │ Side YZ  │
# └──────────┴──────────┘

VIEWPORT_QUADRANTS = {
    "perspective": (0.0, 0.0, 0.5, 0.5),   # top-left (x%, y%, w%, h%)
    "top":         (0.5, 0.0, 0.5, 0.5),   # top-right
    "front":       (0.0, 0.5, 0.5, 0.5),   # bottom-left
    "side":        (0.5, 0.5, 0.5, 0.5),   # bottom-right
}


class VisionInspector:
    """
    Multimodal viewport capture and analysis for UnrealEd.
    Provides screenshot acquisition, viewport region extraction,
    and base64 encoding for LLM vision dispatch.
    """

    def __init__(self, screenshots_dir: Optional[str] = None):
        if screenshots_dir:
            self.screenshots_dir = Path(screenshots_dir)
        else:
            self.screenshots_dir = Path(__file__).resolve().parent.parent / "logs" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def capture_full_window(self, hwnd: int) -> Optional[Image.Image]:
        """
        Captures the full UnrealEd window content as a PIL Image.

        Uses DPI-aware coordinates so that captures on 4K / multi-monitor
        setups produce pixel-accurate images rather than virtualised blurry
        screenshots.  DPI awareness is initialised at bootstrap import-time.

        Args:
            hwnd: Win32 window handle for the UnrealEd main frame.

        Returns:
            PIL Image or None if capture fails.
        """
        if not HAS_PIL or not HAS_PYWIN32:
            logger.warning("PIL or pywin32 not available for viewport capture.")
            return None

        try:
            rect = win32gui.GetWindowRect(hwnd)
            # GetWindowRect returns physical pixels when DPI awareness is
            # active (set in bootstrap.py).  ImageGrab.grab() also expects
            # physical pixels, so the bbox can be passed through directly.
            bbox = (rect[0], rect[1], rect[2], rect[3])
            img = ImageGrab.grab(bbox=bbox)
            dpi_scale = get_dpi_scale_factor(hwnd)
            logger.info(
                f"Captured full window: {img.size[0]}x{img.size[1]}px "
                f"(DPI scale: {dpi_scale:.2f}x)"
            )
            return img
        except Exception as e:
            logger.error(f"Full window capture failed: {e}")
            return None

    def capture_viewport(
        self,
        hwnd: int,
        viewport: str = "perspective",
    ) -> Optional[Image.Image]:
        """
        Captures a specific viewport quadrant from the UnrealEd window.

        Args:
            hwnd: Win32 window handle.
            viewport: One of 'perspective', 'top', 'front', 'side'.

        Returns:
            Cropped PIL Image of the viewport region, or None.
        """
        full_img = self.capture_full_window(hwnd)
        if full_img is None:
            return None

        if viewport not in VIEWPORT_QUADRANTS:
            logger.warning(f"Unknown viewport '{viewport}', defaulting to full window.")
            return full_img

        x_pct, y_pct, w_pct, h_pct = VIEWPORT_QUADRANTS[viewport]
        img_w, img_h = full_img.size

        # Account for title bar and toolbars (approximate offsets).
        # These physical-pixel constants are measured at 96 DPI (100%).
        # On HiDPI displays the OS scales chrome proportionally, so we
        # multiply by the DPI scale factor for pixel-accurate cropping.
        dpi_scale = get_dpi_scale_factor(hwnd)
        toolbar_height = int(80 * dpi_scale)   # toolbar + menu bar
        status_height  = int(24 * dpi_scale)    # status bar
        content_h = img_h - toolbar_height - status_height

        left = int(x_pct * img_w)
        top = toolbar_height + int(y_pct * content_h)
        right = left + int(w_pct * img_w)
        bottom = top + int(h_pct * content_h)

        cropped = full_img.crop((left, top, right, bottom))
        logger.info(
            f"Captured '{viewport}' viewport: {cropped.size[0]}x{cropped.size[1]}px "
            f"(DPI scale: {dpi_scale:.2f}x)"
        )
        return cropped

    def save_screenshot(
        self,
        image: Image.Image,
        name: str = "viewport",
    ) -> str:
        """Saves a screenshot to the logs/screenshots directory. Returns the file path."""
        import time
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        image.save(str(filepath), format="PNG")
        logger.info(f"Screenshot saved: {filepath}")
        return str(filepath)

    def image_to_base64(self, image: Image.Image, max_width: int = 1024) -> str:
        """
        Encodes a PIL Image as a base64 PNG string for multimodal LLM dispatch.
        Optionally resizes to max_width to stay within token limits.
        """
        # Resize if needed
        if image.size[0] > max_width:
            ratio = max_width / image.size[0]
            new_size = (max_width, int(image.size[1] * ratio))
            image = image.resize(new_size, Image.LANCZOS)

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        logger.info(f"Encoded image to base64: {len(b64)} chars, {image.size[0]}x{image.size[1]}px")
        return b64

    def annotate_with_grid(
        self,
        image: Image.Image,
        grid_size: int = 64,
        color: str = "cyan",
        opacity: int = 80,
    ) -> Image.Image:
        """
        Overlays a reference grid on a viewport screenshot.
        Useful for spatial orientation in multimodal vision analysis.
        """
        annotated = image.copy().convert("RGBA")
        overlay = Image.new("RGBA", annotated.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Parse color
        color_map = {
            "cyan": (0, 255, 255, opacity),
            "green": (0, 255, 0, opacity),
            "red": (255, 0, 0, opacity),
            "yellow": (255, 255, 0, opacity),
            "white": (255, 255, 255, opacity),
        }
        rgba = color_map.get(color.lower(), (0, 255, 255, opacity))

        w, h = annotated.size
        for x in range(0, w, grid_size):
            draw.line([(x, 0), (x, h)], fill=rgba, width=1)
        for y in range(0, h, grid_size):
            draw.line([(0, y), (w, y)], fill=rgba, width=1)

        result = Image.alpha_composite(annotated, overlay)
        return result.convert("RGB")

    def build_vision_context(
        self,
        hwnd: int,
        viewports: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Captures specified viewports and packages them as a structured
        multimodal context payload for LLM dispatch.

        Args:
            hwnd: UnrealEd window handle.
            viewports: List of viewport names to capture.
                       Defaults to ['perspective'] for minimal token cost.

        Returns:
            Dict with base64-encoded images and metadata.
        """
        if viewports is None:
            viewports = ["perspective"]

        context: Dict[str, Any] = {
            "type": "unrealed_viewport_capture",
            "viewports": {},
            "available": HAS_PIL and HAS_PYWIN32,
        }

        if not context["available"]:
            context["error"] = "PIL or pywin32 not installed"
            return context

        for vp_name in viewports:
            img = self.capture_viewport(hwnd, vp_name)
            if img is not None:
                context["viewports"][vp_name] = {
                    "base64_png": self.image_to_base64(img),
                    "width": img.size[0],
                    "height": img.size[1],
                }

        logger.info(f"Built vision context: {len(context['viewports'])} viewport(s) captured")
        return context
