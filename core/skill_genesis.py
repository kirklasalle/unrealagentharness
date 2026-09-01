r"""
UAH Skill Genesis & Self-Documenting Wisdom Synthesizer.
Automatically discovers, formalizes, and persists novel architectural techniques, CSG formulas,
and gametype configurations into the lifelong SQLite memory store.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logger import get_logger
from .memory_engine import MemoryEngine

logger = get_logger("SkillGenesis", "skill_genesis.log")


class SkillGenesis:
    """Discovers, refines, and registers novel procedural architectural skills and design patterns."""

    def __init__(self, memory_engine: Optional[MemoryEngine] = None):
        self.memory_engine = memory_engine or MemoryEngine()
        self._seed_standard_skills()

    def _seed_standard_skills(self) -> None:
        """Ensures foundational Unreal Agent skills are seeded and graph-indexed."""
        existing = self.memory_engine.query_wisdom("unrealed_viewport_setup", category="skill_viewport")
        if not existing:
            self.distill_and_register_skill(
                skill_name="unrealed_viewport_setup",
                category="viewport",
                description="World-class default 4-viewport layout: Top XY, Front XZ, Side YZ scaled to full extents above Dynamic Light 3D viewport.",
                parameters={
                    "layout": "3_top_ortho_1_bottom_dynamic_light",
                    "top_quadrants": ["top", "front", "side"],
                    "bottom_quadrant": "dynamic_light",
                },
                command_template=["MODE DYNAMICLIGHT", "CAMERA ALIGN", "VIEWPORT REDRAW"],
                tags="viewport,layout,dynamic_light,ortho,standards",
            )
            self.memory_engine.record_graph_node(
                "skill:unrealed_viewport_setup",
                "skill",
                "UnrealEd Standard 4-Viewport Setup",
                {"category": "viewport", "status": "active"},
            )

        existing_valley = self.memory_engine.query_wisdom("valley_fortress_synthesis", category="skill_world_design")
        if not existing_valley:
            self.distill_and_register_skill(
                skill_name="valley_fortress_synthesis",
                category="world_design",
                description="Synthesizes the complete Valley Fortress outdoor world with parallax skybox, mountain terraces, waterfalls, dual bridges, and fortified keep.",
                parameters={
                    "reference_image": "Builderbutton_valley_01.jpg",
                    "skybox_z": 4608,
                    "fortress_towers": 4,
                    "bridges": ["lower_stone_arch", "upper_timber_drawbridge"],
                },
                command_template=[
                    "BRUSH IMPORT FILE=ValleyMain.t3d",
                    "BRUSH SUBTRACT",
                    "BRUSH IMPORT FILE=CastleKeep.t3d",
                    "BRUSH ADD",
                    "MAP REBUILD",
                ],
                tags="valley,fortress,skybox,waterfall,bridges,castle",
            )
            self.memory_engine.record_graph_node(
                "skill:valley_fortress_synthesis",
                "skill",
                "Valley Fortress World Synthesis",
                {"category": "world_design", "reference": "Builderbutton_valley_01.jpg"},
            )

    def record_skill_training_event(
        self,
        skill_name: str,
        build_id: str,
        success: bool = True,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Records a continuous training event linking a build to an applied skill."""
        node_id = f"training:{skill_name}:{build_id}"
        payload = {
            "skill_name": skill_name,
            "build_id": build_id,
            "success": success,
            "metrics": metrics or {},
            "timestamp": time.time(),
        }
        ok = self.memory_engine.record_graph_node(node_id, "training_event", f"Training on {skill_name}", payload)
        ok = self.memory_engine.record_graph_edge(f"build:{build_id}", "trained_on_skill", f"skill:{skill_name}") and ok
        ok = self.memory_engine.record_graph_edge(node_id, "evaluates_skill", f"skill:{skill_name}") and ok
        return ok


    def distill_and_register_skill(
        self,
        skill_name: str,
        category: str,
        description: str,
        parameters: Dict[str, Any],
        command_template: List[str],
        tags: str = "",
        confidence: float = 1.0,
    ) -> bool:
        """Formalizes a newly generated level design technique into a persistent skill."""
        skill_payload = {
            "skill_name": skill_name,
            "category": category,
            "description": description,
            "parameters": parameters,
            "command_template": command_template,
            "created_at": time.time(),
        }

        content_str = json.dumps(skill_payload, indent=2)
        success = self.memory_engine.record_wisdom(
            category=f"skill_{category}",
            title=skill_name,
            content=content_str,
            tags=f"skill,{tags}",
            confidence=confidence,
        )

        if success:
            logger.info(f"SkillGenesis successfully recorded new skill: '{skill_name}' ({category})")
        else:
            logger.error(f"SkillGenesis failed to record skill: '{skill_name}'")

        return success

    def list_learned_skills(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Queries all learned and registered procedural skills."""
        query = f"skill_{category}" if category else "skill_"
        results = self.memory_engine.query_wisdom(query, limit=50)

        skills = []
        for r in results:
            try:
                data = json.loads(r["content"])
                data["id"] = r["id"]
                data["confidence"] = r["confidence"]
                skills.append(data)
            except Exception:
                pass
        return skills
