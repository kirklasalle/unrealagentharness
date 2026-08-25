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
