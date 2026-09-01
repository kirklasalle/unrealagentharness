"""Reference-image analysis primitives for the approval-gated world builder.

This module is intentionally deterministic and dependency-light. It separates
operator red markup from source pixels, extracts a useful edge map, and emits a
normalized Valley Fortress scene graph that can be reviewed before generation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from PIL import Image, ImageFilter
    HAS_PIL = True
except ImportError:  # pragma: no cover - exercised on minimal installations
    HAS_PIL = False

from .logger import get_logger

logger = get_logger("ReferenceAnalyzer", "reference_analyzer.log")


class ReferenceAnalyzer:
    """Extracts annotation masks, edges, and normalized world landmarks."""

    def __init__(self, artifact_dir: Optional[Path] = None):
        self.artifact_dir = Path(artifact_dir or Path(__file__).resolve().parent.parent / "logs" / "reference_artifacts")
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _red_mask(image: "Image.Image") -> "Image.Image":
        """Returns a binary mask for saturated red operator markup."""
        hsv = image.convert("HSV")
        pixels = hsv.load()
        mask = Image.new("L", image.size, 0)
        out = mask.load()
        for y in range(image.height):
            for x in range(image.width):
                hue, saturation, value = pixels[x, y]
                # PIL hue is [0,255], red wraps around both ends.
                red_hue = hue <= 18 or hue >= 238
                if red_hue and saturation >= 120 and value >= 90:
                    out[x, y] = 255
        return mask.filter(ImageFilter.MaxFilter(5))

    @staticmethod
    def _edge_map(image: "Image.Image", annotation_mask: "Image.Image") -> "Image.Image":
        """Creates a clean grayscale edge map with markup excluded."""
        clean = image.convert("RGB").copy()
        clean.paste((128, 128, 128), mask=annotation_mask)
        edges = clean.convert("L").filter(ImageFilter.FIND_EDGES)
        # Suppress residual annotation pixels after filtering.
        edges.paste(0, mask=annotation_mask)
        return edges

    @staticmethod
    def _mask_bounds(mask: "Image.Image") -> Optional[Tuple[float, float, float, float]]:
        """Returns the normalized bounds of a non-empty binary mask."""
        bbox = mask.getbbox()
        if not bbox:
            return None
        left, top, right, bottom = bbox
        return (
            left / max(mask.width, 1), top / max(mask.height, 1),
            right / max(mask.width, 1), bottom / max(mask.height, 1),
        )

    @staticmethod
    def _image_density(image: "Image.Image", threshold: int = 48) -> float:
        """Calculates a bounded edge-density metric for QA and confidence."""
        histogram = image.convert("L").histogram()
        active = sum(histogram[threshold:])
        return round(active / max(image.width * image.height, 1), 6)

    @staticmethod
    def _column_edge_profile(edges: "Image.Image", buckets: int = 12) -> List[float]:
        """Returns normalized edge density per image column bucket."""
        grayscale = edges.convert("L")
        result: List[float] = []
        for bucket in range(buckets):
            left = bucket * grayscale.width // buckets
            right = (bucket + 1) * grayscale.width // buckets
            values = [grayscale.getpixel((x, y)) for x in range(left, right) for y in range(grayscale.height)]
            result.append(round(sum(1 for value in values if value >= 48) / max(len(values), 1), 6))
        return result

    @staticmethod
    def _region(name: str, bounds: Tuple[float, float, float, float], priority: int, material: str, elevation: str, kind: str) -> Dict[str, Any]:
        return {
            "id": name,
            "bounds": {"left": bounds[0], "top": bounds[1], "right": bounds[2], "bottom": bounds[3]},
            "priority": priority,
            "material_family": material,
            "elevation_band": elevation,
            "geometry_kind": kind,
        }

    def build_scene_graph(self, image_path: Path, annotation_regions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Builds a reviewable normalized graph from a reference image."""
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        if not HAS_PIL:
            raise RuntimeError("Pillow is required for reference image analysis")

        with Image.open(image_path) as source:
            image = source.convert("RGB")
            red_mask = self._red_mask(image)
            edges = self._edge_map(image, red_mask)
            stem = image_path.stem
            mask_path = self.artifact_dir / f"{stem}_annotation_mask.png"
            edge_path = self.artifact_dir / f"{stem}_clean_edges.png"
            red_mask.save(mask_path)
            edges.save(edge_path)
            width, height = image.size
            annotation_bounds = self._mask_bounds(red_mask)
            edge_density = self._image_density(edges)

        graph = {
            "schema": "uah.valley_scene_graph.v1",
            "source": {
                "path": str(image_path.resolve()),
                "sha256": self.sha256(image_path),
                "width": width,
                "height": height,
                "annotation_mask": str(mask_path),
                "clean_edge_map": str(edge_path),
                "annotation_bounds": annotation_bounds,
                "clean_edge_density": edge_density,
                "edge_column_profile": self._column_edge_profile(edges),
            },
            "annotation_regions": annotation_regions or {
                "skybox_dome": {"description": "operator-marked sky/backdrop region"},
                "east_fortress_mass": {"description": "operator-marked castle region"},
            },
            "landmarks": [
                self._region("skybox_dome", (0.02, 0.02, 0.98, 0.39), 100, "cloud_mountain_sky", "far_above", "skybox"),
                self._region("far_valley_horizon", (0.22, 0.22, 0.78, 0.52), 95, "distant_rock", "far_ridge", "skybox_detail"),
                self._region("west_cliff_mass", (0.00, 0.18, 0.46, 0.78), 90, "granite_rock", "high_to_low", "structural_bsp"),
                self._region("east_fortress_mass", (0.53, 0.18, 1.00, 0.62), 100, "castle_masonry", "high_ridge", "structural_bsp"),
                self._region("river_axis", (0.34, 0.35, 0.67, 1.00), 100, "river_water", "descending_center", "structural_bsp"),
                self._region("upper_drawbridge", (0.44, 0.43, 0.68, 0.62), 90, "weathered_timber", "castle_gate", "structural_bsp"),
                self._region("lower_stone_bridge", (0.20, 0.62, 0.86, 0.76), 95, "castle_masonry", "foreground_crossing", "structural_bsp"),
                self._region("tree_line_west", (0.00, 0.30, 0.35, 0.95), 80, "pine_foliage", "layered_slope", "actor_foliage"),
                self._region("tree_line_east", (0.70, 0.34, 1.00, 0.95), 80, "pine_foliage", "layered_slope", "actor_foliage"),
                self._region("foreground_boulder_field", (0.00, 0.68, 1.00, 1.00), 75, "granite_boulder", "foreground", "actor_detail"),
            ],
            "routes": [
                {"id": "castle_route", "from": "upper_drawbridge", "to": "east_fortress_mass"},
                {"id": "river_route", "from": "far_valley_horizon", "to": "lower_stone_bridge"},
                {"id": "lookout_route", "from": "river_route", "to": "west_cliff_mass"},
            ],
            "validation_views": ["perspective", "top", "front", "side"],
        }
        return graph

    def analyze_to_json(self, image_path: Path, output_path: Optional[Path] = None) -> Path:
        graph = self.build_scene_graph(Path(image_path))
        target = Path(output_path or self.artifact_dir / f"{Path(image_path).stem}_scene_graph.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(graph, indent=2), encoding="utf-8")
        logger.info("Wrote reference scene graph: %s", target)
        return target
