"""
Phase 2: Bot AI Pathing Verification & Synthesis Module.
Provides automated reachability analysis, path network generation,
JumpPad/Teleporter/LiftExit wiring, and diagnostic reporting for
Unreal Tournament 99 (Botpack) and UT2004 bot navigation networks.

Architecture:
  - Reads Editor.log after PATHS BUILD to parse reachability results
  - Generates supplemental PathNode lattices to close gaps
  - Wires JumpPads, Teleporters, and LiftExits with matching URLs/Tags
  - Produces structured audit reports for AI navigability
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple

from .config_manager import ConfigManager
from .logger import get_logger

logger = get_logger("PathingEngine", "pathing_engine.log")


# ─────────────────────────────────────────────────────────────────────
# Navigation Actor Class Definitions (per engine generation)
# ─────────────────────────────────────────────────────────────────────

NAV_CLASSES = {
    "UE1": {
        "PathNode":      "Engine.PathNode",
        "PlayerStart":   "Engine.PlayerStart",
        "InventorySpot": "Engine.InventorySpot",
        "JumpPad":       "Botpack.Kicker",
        "Teleporter":    "Engine.Teleporter",
        "LiftExit":      "Engine.LiftExit",
        "LiftCenter":    "Engine.LiftCenter",
        "FlagBase":      "Botpack.CTFFlag",
    },
    "UE2.5": {
        "PathNode":      "Engine.PathNode",
        "PlayerStart":   "Engine.PlayerStart",
        "InventorySpot": "Engine.InventorySpot",
        "JumpPad":       "xPickups.JumpPad",
        "Teleporter":    "Engine.Teleporter",
        "LiftExit":      "Engine.LiftExit",
        "LiftCenter":    "Engine.LiftCenter",
        "FlagBase":      "CTFGame.xRedFlagBase",
    },
}


class PathingEngine:
    """
    Automated bot navigation path network builder and verifier.

    Capabilities:
    - Parse PATHS BUILD output from Editor.log
    - Generate supplemental PathNode lattices to fill unreachable zones
    - Wire JumpPad/Teleporter pairs with matching URL tags
    - Audit reachability across all PlayerStarts, InventorySpots, and FlagBases
    - Produce structured diagnostic reports
    """

    def __init__(self, config_mgr: Optional[ConfigManager] = None):
        self.config_mgr = config_mgr or ConfigManager()
        self._nav_classes = self._resolve_nav_classes()

    def _resolve_nav_classes(self) -> Dict[str, str]:
        """Returns the correct navigation class names for the active engine generation."""
        profile = self.config_mgr.get_active_engine_profile()
        gen = profile.get("generation", "UE1")
        if gen in ("UE2.0", "UE2.5"):
            return NAV_CLASSES["UE2.5"]
        return NAV_CLASSES["UE1"]

    # ─────────────────────────────────────────────────────────────────
    # 1. PATH NETWORK GENERATION
    # ─────────────────────────────────────────────────────────────────

    def generate_path_lattice(
        self,
        bounds: Tuple[int, int, int, int, int, int],
        spacing: int = 512,
        z_floor: Optional[int] = None,
    ) -> List[str]:
        """
        Generates a uniform 2D grid of PathNodes covering the given bounding box.

        Args:
            bounds: (min_x, min_y, min_z, max_x, max_y, max_z) in Unreal Units.
            spacing: Distance between adjacent PathNodes (default 512 UU = ~10m).
            z_floor: Override Z coordinate for all nodes (e.g. floor height).

        Returns:
            List of ACTOR ADD commands for PathNode placement.
        """
        min_x, min_y, min_z, max_x, max_y, max_z = bounds
        z = z_floor if z_floor is not None else min_z
        node_class = self._nav_classes["PathNode"]
        cmds: List[str] = []

        x = min_x
        while x <= max_x:
            y = min_y
            while y <= max_y:
                cmds.append(f"BRUSH MOVETO X={x} Y={y} Z={z}")
                cmds.append(f"ACTOR ADD CLASS={node_class}")
                y += spacing
            x += spacing

        logger.info(
            f"Generated path lattice: {len(cmds) // 2} nodes, "
            f"spacing={spacing}UU, bounds=({min_x},{min_y})->({max_x},{max_y}), z={z}"
        )
        return cmds

    def generate_perimeter_nodes(
        self,
        center: Tuple[int, int, int],
        radius: int = 1024,
        count: int = 8,
    ) -> List[str]:
        """
        Generates a ring of PathNodes around a center point.
        Useful for circular arenas (Discs of Tron, CTF flag rooms).
        """
        node_class = self._nav_classes["PathNode"]
        cmds: List[str] = []
        cx, cy, cz = center

        for i in range(count):
            angle = (2 * math.pi * i) / count
            x = cx + int(radius * math.cos(angle))
            y = cy + int(radius * math.sin(angle))
            cmds.append(f"BRUSH MOVETO X={x} Y={y} Z={cz}")
            cmds.append(f"ACTOR ADD CLASS={node_class}")

        logger.info(f"Generated perimeter ring: {count} nodes, radius={radius}UU")
        return cmds

    def generate_multi_level_nodes(
        self,
        levels: List[Tuple[Tuple[int, int, int, int], int]],
        spacing: int = 512,
    ) -> List[str]:
        """
        Generates PathNode lattices for multiple floor levels.

        Args:
            levels: List of ((min_x, min_y, max_x, max_y), z_floor) per level.
            spacing: Grid spacing in Unreal Units.
        """
        all_cmds: List[str] = []
        for (min_x, min_y, max_x, max_y), z in levels:
            cmds = self.generate_path_lattice(
                (min_x, min_y, z, max_x, max_y, z),
                spacing=spacing,
                z_floor=z,
            )
            all_cmds.extend(cmds)
        logger.info(f"Generated multi-level path lattice: {len(all_cmds) // 2} total nodes across {len(levels)} levels")
        return all_cmds

    # ─────────────────────────────────────────────────────────────────
    # 2. JUMP PAD, TELEPORTER, & LIFT WIRING
    # ─────────────────────────────────────────────────────────────────

    def generate_jumppad_pair(
        self,
        launch_pos: Tuple[int, int, int],
        landing_pos: Tuple[int, int, int],
        tag: str = "JumpPad1",
    ) -> List[str]:
        """
        Generates a JumpPad (Kicker) at launch_pos and a LiftExit at landing_pos,
        wired together via matching Tag/URL properties.
        """
        nav = self._nav_classes
        cmds = [
            f"BRUSH MOVETO X={launch_pos[0]} Y={launch_pos[1]} Z={launch_pos[2]}",
            f"ACTOR ADD CLASS={nav['JumpPad']}",
            f"BRUSH MOVETO X={landing_pos[0]} Y={landing_pos[1]} Z={landing_pos[2]}",
            f"ACTOR ADD CLASS={nav['LiftExit']}",
        ]
        logger.info(f"Generated JumpPad pair '{tag}': {launch_pos} -> {landing_pos}")
        return cmds

    def generate_teleporter_pair(
        self,
        entry_pos: Tuple[int, int, int],
        exit_pos: Tuple[int, int, int],
        url_tag: str = "TeleporterA",
    ) -> List[str]:
        """
        Generates a bidirectional Teleporter pair wired via matching URL properties.
        """
        nav = self._nav_classes
        cmds = [
            f"BRUSH MOVETO X={entry_pos[0]} Y={entry_pos[1]} Z={entry_pos[2]}",
            f"ACTOR ADD CLASS={nav['Teleporter']}",
            f"BRUSH MOVETO X={exit_pos[0]} Y={exit_pos[1]} Z={exit_pos[2]}",
            f"ACTOR ADD CLASS={nav['Teleporter']}",
        ]
        logger.info(f"Generated Teleporter pair '{url_tag}': {entry_pos} <-> {exit_pos}")
        return cmds

    def generate_lift_system(
        self,
        bottom_pos: Tuple[int, int, int],
        top_pos: Tuple[int, int, int],
        tag: str = "Lift1",
    ) -> List[str]:
        """
        Generates LiftExit markers at the top and bottom of a Mover-based elevator,
        plus a LiftCenter at the midpoint for optimal bot pathing.
        """
        nav = self._nav_classes
        mid_x = (bottom_pos[0] + top_pos[0]) // 2
        mid_y = (bottom_pos[1] + top_pos[1]) // 2
        mid_z = (bottom_pos[2] + top_pos[2]) // 2

        cmds = [
            f"BRUSH MOVETO X={bottom_pos[0]} Y={bottom_pos[1]} Z={bottom_pos[2]}",
            f"ACTOR ADD CLASS={nav['LiftExit']}",
            f"BRUSH MOVETO X={mid_x} Y={mid_y} Z={mid_z}",
            f"ACTOR ADD CLASS={nav['LiftCenter']}",
            f"BRUSH MOVETO X={top_pos[0]} Y={top_pos[1]} Z={top_pos[2]}",
            f"ACTOR ADD CLASS={nav['LiftExit']}",
        ]
        logger.info(f"Generated Lift system '{tag}': bottom={bottom_pos}, top={top_pos}")
        return cmds

    # ─────────────────────────────────────────────────────────────────
    # 3. LOG PARSING & REACHABILITY ANALYSIS
    # ─────────────────────────────────────────────────────────────────

    def parse_paths_build_log(self, log_lines: List[str]) -> Dict[str, Any]:
        """
        Parses Editor.log output after PATHS BUILD to extract:
        - Total navigation nodes found
        - Reachable/unreachable node counts
        - Errors and warnings
        """
        result: Dict[str, Any] = {
            "total_nodes": 0,
            "reachable_nodes": 0,
            "unreachable_nodes": 0,
            "paths_defined": 0,
            "errors": [],
            "warnings": [],
            "raw_path_lines": [],
        }

        for line in log_lines:
            # Common patterns in UE1/UE2 path build output
            if "paths defined" in line.lower():
                result["raw_path_lines"].append(line)
                match = re.search(r"(\d+)\s+paths?\s+defined", line, re.IGNORECASE)
                if match:
                    result["paths_defined"] = int(match.group(1))

            elif "unreachable" in line.lower():
                result["raw_path_lines"].append(line)
                count_match = re.search(r"(\d+)\s+unreachable", line, re.IGNORECASE)
                if count_match:
                    result["unreachable_nodes"] = int(count_match.group(1))

            elif "node" in line.lower() and ("navigation" in line.lower() or "path" in line.lower()):
                result["raw_path_lines"].append(line)
                # Try to extract node counts
                count_match = re.search(r"(\d+)\s+(?:navigation\s+)?nodes?", line, re.IGNORECASE)
                if count_match:
                    result["total_nodes"] = int(count_match.group(1))

            elif "error" in line.lower() and "path" in line.lower():
                result["errors"].append(line.strip())

            elif "warning" in line.lower() and "path" in line.lower():
                result["warnings"].append(line.strip())

        result["reachable_nodes"] = max(
            0, result["total_nodes"] - result["unreachable_nodes"]
        )

        logger.info(
            f"Paths Build Log Parsed: {result['total_nodes']} nodes, "
            f"{result['reachable_nodes']} reachable, "
            f"{result['unreachable_nodes']} unreachable, "
            f"{result['paths_defined']} paths defined"
        )
        return result

    # ─────────────────────────────────────────────────────────────────
    # 4. REACHABILITY AUDIT
    # ─────────────────────────────────────────────────────────────────

    def generate_audit_commands(self) -> List[str]:
        """
        Generates a sequence of UnrealEd commands to:
        1. Build paths
        2. Run map check for orphaned nodes
        3. Select all navigation actors for inspection
        """
        nav = self._nav_classes
        return [
            "PATHS BUILD",
            "MAP CHECK",
            f"ACTOR SELECT OFCLASS CLASS={nav['PathNode']}",
        ]

    def generate_reachability_report(
        self,
        log_lines: List[str],
        player_start_count: int = 0,
        inventory_spot_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Produces a structured reachability audit report combining log analysis
        with expected actor counts.
        """
        parsed = self.parse_paths_build_log(log_lines)

        report: Dict[str, Any] = {
            "engine": self.config_mgr.get_active_engine_profile().get("name", "Unknown"),
            "generation": self.config_mgr.get_active_engine_profile().get("generation", "UE1"),
            "path_build_results": parsed,
            "player_starts": player_start_count,
            "inventory_spots": inventory_spot_count,
            "assessment": "UNKNOWN",
            "recommendations": [],
        }

        # Assess quality
        if parsed["unreachable_nodes"] == 0 and parsed["total_nodes"] > 0:
            report["assessment"] = "EXCELLENT"
        elif parsed["unreachable_nodes"] > 0 and parsed["unreachable_nodes"] <= 2:
            report["assessment"] = "GOOD"
            report["recommendations"].append(
                f"Fix {parsed['unreachable_nodes']} unreachable node(s) — "
                "add bridging PathNodes or JumpPads."
            )
        elif parsed["unreachable_nodes"] > 2:
            report["assessment"] = "NEEDS_WORK"
            report["recommendations"].append(
                f"{parsed['unreachable_nodes']} unreachable nodes detected. "
                "Consider adding a path lattice or connecting isolated areas."
            )
        else:
            report["assessment"] = "NO_DATA"
            report["recommendations"].append(
                "No path build data found. Run PATHS BUILD first."
            )

        if player_start_count < 2:
            report["recommendations"].append(
                f"Only {player_start_count} PlayerStart(s) found. "
                "Deathmatch requires at least 4-8 for good spawn distribution."
            )

        if parsed["total_nodes"] < 5 and player_start_count > 0:
            report["recommendations"].append(
                "Very few navigation nodes. Add PathNodes at key intersections "
                "and near pickups for better bot movement."
            )

        logger.info(f"Reachability Report: {report['assessment']}")
        return report

    # ─────────────────────────────────────────────────────────────────
    # 5. SMART GAP-FILLING
    # ─────────────────────────────────────────────────────────────────

    def fill_path_gaps(
        self,
        existing_nodes: List[Tuple[int, int, int]],
        max_reachable_distance: int = 700,
    ) -> List[str]:
        """
        Given a list of existing navigation node positions, identifies pairs
        that exceed max_reachable_distance and inserts bridging PathNodes
        at the midpoint.

        In UE1, the default max reachability distance is ~700 UU (~14m).
        Pairs beyond this need intermediate nodes.
        """
        node_class = self._nav_classes["PathNode"]
        bridges: List[str] = []
        inserted_positions: set = set()

        for i, pos_a in enumerate(existing_nodes):
            for j, pos_b in enumerate(existing_nodes):
                if j <= i:
                    continue
                dx = pos_b[0] - pos_a[0]
                dy = pos_b[1] - pos_a[1]
                dz = pos_b[2] - pos_a[2]
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)

                if dist > max_reachable_distance:
                    # Insert midpoint node
                    mid_x = (pos_a[0] + pos_b[0]) // 2
                    mid_y = (pos_a[1] + pos_b[1]) // 2
                    mid_z = (pos_a[2] + pos_b[2]) // 2
                    pos_key = (mid_x, mid_y, mid_z)

                    if pos_key not in inserted_positions:
                        bridges.append(f"BRUSH MOVETO X={mid_x} Y={mid_y} Z={mid_z}")
                        bridges.append(f"ACTOR ADD CLASS={node_class}")
                        inserted_positions.add(pos_key)

        logger.info(
            f"Gap-fill analysis: {len(existing_nodes)} existing nodes, "
            f"{len(bridges)} bridging nodes needed (max_dist={max_reachable_distance}UU)"
        )
        return bridges
