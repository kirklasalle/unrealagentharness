"""
Comprehensive test suite for the Standalone Multi-Engine Agent Harness.
Uses unittest with proper assertions for CI/verification.
"""

import sys
import unittest
from pathlib import Path

# Add AgentHarness parent directory for package imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from AgentHarness.core.config_manager import ConfigManager
from AgentHarness.core.engine_controller import EngineController
from AgentHarness.core.formula_engine import FormulaEngine
from AgentHarness.core.nexus_bridge import NexusBridge
from AgentHarness.core.tools_schema import UNREALED_TOOLS


class TestConfigManager(unittest.TestCase):
    """Tests for the ConfigManager profile loading and switching."""

    def setUp(self):
        self.cm = ConfigManager()

    def test_active_engine_id_is_string(self):
        engine_id = self.cm.get_active_engine_id()
        self.assertIsInstance(engine_id, str)
        self.assertIn(engine_id, self.cm.get_all_engine_profiles())

    def test_active_engine_profile_has_required_keys(self):
        profile = self.cm.get_active_engine_profile()
        required_keys = ["id", "name", "generation", "root_dir", "system_dir", "editor_exe"]
        for key in required_keys:
            self.assertIn(key, profile, f"Engine profile missing required key: {key}")

    def test_all_engine_profiles_present(self):
        profiles = self.cm.get_all_engine_profiles()
        expected = {"ut99_goty", "ut99_utron", "ut2003", "ut2004", "ue5"}
        self.assertEqual(set(profiles.keys()), expected)

    def test_active_llm_profile_id_is_string(self):
        profile_id = self.cm.get_active_llm_profile_id()
        self.assertIsInstance(profile_id, str)
        self.assertTrue(len(profile_id) > 0)

    def test_active_personality_id_is_string(self):
        personality_id = self.cm.get_active_personality_id()
        self.assertIsInstance(personality_id, str)
        self.assertTrue(len(personality_id) > 0)

    def test_engine_profile_switch_valid(self):
        original = self.cm.get_active_engine_id()
        self.assertTrue(self.cm.set_active_engine_id("ut99_goty"))
        self.assertEqual(self.cm.get_active_engine_id(), "ut99_goty")
        # Restore original
        self.cm.set_active_engine_id(original)

    def test_engine_profile_switch_invalid(self):
        self.assertFalse(self.cm.set_active_engine_id("nonexistent_engine"))


class TestFormulaEngine(unittest.TestCase):
    """Tests for the FormulaEngine procedural level generators."""

    def setUp(self):
        self.fe = FormulaEngine()

    def test_utron_disc_arena_generates_commands(self):
        cmds = self.fe.generate_utron_disc_arena()
        self.assertIsInstance(cmds, list)
        self.assertIn("MAP NEW", cmds[0])
        self.assertTrue(any("MAP IMPORT" in c for c in cmds))
        self.assertIn("PATHS BUILD", cmds)

    def test_utron_diffuser_bus_generates_commands(self):
        cmds = self.fe.generate_utron_diffuser_bus((0, 0, -200), count=8)
        self.assertIsInstance(cmds, list)
        self.assertGreater(len(cmds), 0, "Diffuser bus should generate at least 1 command")

    def test_ut99_tournament_arena_generates_commands(self):
        cmds = self.fe.generate_ut99_tournament_arena()
        self.assertIsInstance(cmds, list)
        self.assertIn("MAP NEW", cmds[0])
        self.assertTrue(any("MAP IMPORT" in c for c in cmds))
        self.assertIn("PATHS BUILD", cmds)

    def test_ut99_ctf_base_generates_commands(self):
        for color in ["Red", "Blue"]:
            cmds = self.fe.generate_ut99_ctf_base(base_color=color)
            self.assertIsInstance(cmds, list)
            self.assertTrue(any("MAP IMPORT" in c for c in cmds))

    def test_ue5_modular_arena_generates_actors(self):
        actors = self.fe.generate_ue5_modular_arena()
        self.assertIsInstance(actors, list)
        self.assertGreater(len(actors), 0, "UE5 arena should generate at least 1 actor")

    def test_disc_arena_contains_player_starts(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_utron_disc_arena(system_dir=Path(tmp))
            t3d_file = Path(tmp) / "UTronDiscActors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("PlayerStart", content)

    def test_ut99_arena_contains_weapons(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut99_tournament_arena(system_dir=Path(tmp))
            t3d_file = Path(tmp) / "ArenaActors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("Botpack.ShockRifle", content)
            self.assertIn("Botpack.UT_FlakCannon", content)

    def test_ut99_verdant_mountain_valley_generates_world_elements(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut99_verdant_mountain_valley(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            self.assertTrue(any("OBJ LOAD" in c for c in cmds))
            t3d_file = Path(tmp) / "ValleyActors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("UnrealShare.Tree1", content)
            self.assertIn("UnrealI.BigRock", content)
            self.assertIn("Botpack.ShockRifle", content)
            self.assertIn("Engine.PathNode", content)

    def test_ut99_desert_canyon_ruins_generates_world_elements(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut99_desert_canyon_ruins(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            t3d_file = Path(tmp) / "DesertActors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("UnrealShare.Plant5", content)
            self.assertIn("UnrealShare.MonkStatue", content)
            self.assertIn("Botpack.UT_FlakCannon", content)

    def test_ut99_orbital_asteroid_outpost_generates_world_elements(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut99_orbital_asteroid_outpost(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            t3d_file = Path(tmp) / "AsteroidActors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("ZoneGravity", content)
            self.assertIn("UnrealI.BigRock", content)
            self.assertIn("Botpack.WarheadLauncher", content)


class TestToolsSchema(unittest.TestCase):
    """Tests for the LLM tool-calling schema definitions."""

    def test_tools_schema_is_list(self):
        self.assertIsInstance(UNREALED_TOOLS, list)
        self.assertGreater(len(UNREALED_TOOLS), 0)

    def test_each_tool_has_function_definition(self):
        for tool in UNREALED_TOOLS:
            self.assertIn("type", tool)
            self.assertEqual(tool["type"], "function")
            self.assertIn("function", tool)
            self.assertIn("name", tool["function"])
            self.assertIn("parameters", tool["function"])

    def test_core_tools_present(self):
        tool_names = {t["function"]["name"] for t in UNREALED_TOOLS}
        expected = {"execute_unrealed_commands", "create_bsp_room", "spawn_actor"}
        self.assertTrue(expected.issubset(tool_names),
                        f"Missing core tools: {expected - tool_names}")


class TestNexusBridge(unittest.TestCase):
    """Tests for the .nexus Post Office integration bridge."""

    def test_nexus_bridge_initializes(self):
        nb = NexusBridge()
        self.assertIsInstance(nb.is_available, bool)

    def test_nexus_bridge_detects_nexus_dir(self):
        nb = NexusBridge()
        # On Kirk's machine, .nexus should exist at d:\projects\.nexus
        if nb.nexus_root.exists():
            self.assertTrue(nb.is_available)
        else:
            self.assertFalse(nb.is_available)

    def test_nexus_bridge_has_agent_identity(self):
        nb = NexusBridge()
        self.assertIsInstance(nb.agent_name, str)
        self.assertIsInstance(nb.agent_address, str)
        self.assertTrue(len(nb.agent_name) > 0)


class TestEngineController(unittest.TestCase):
    """Tests for the Win32 engine controller (non-destructive, no live UnrealEd needed)."""

    def setUp(self):
        self.cm = ConfigManager()
        self.ctrl = EngineController(self.cm)

    def test_system_dir_is_valid_path(self):
        self.assertIsInstance(self.ctrl.system_dir, (str, Path))
        # Should point to a System directory
        self.assertTrue(str(self.ctrl.system_dir).endswith("System"))

    def test_is_connected_returns_bool(self):
        result = self.ctrl.is_connected()
        self.assertIsInstance(result, bool)


# ═══════════════════════════════════════════════════════════════════════
# PHASE 2: Bot Pathing & Multimodal Vision Tests
# ═══════════════════════════════════════════════════════════════════════

from AgentHarness.core.pathing_engine import PathingEngine
from AgentHarness.core.vision_inspector import VisionInspector


class TestPathingEngine(unittest.TestCase):
    """Tests for the Phase 2 PathingEngine bot navigation module."""

    def setUp(self):
        self.pe = PathingEngine()

    def test_path_lattice_generates_correct_node_count(self):
        # 3x3 grid at spacing 512 in a 1024x1024 box = 9 nodes (18 commands: MOVETO + ADD)
        cmds = self.pe.generate_path_lattice(
            bounds=(-512, -512, -200, 512, 512, -200),
            spacing=512,
        )
        self.assertIsInstance(cmds, list)
        self.assertEqual(len(cmds), 18)
        actor_adds = [c for c in cmds if "ACTOR ADD CLASS=Engine.PathNode" in c]
        self.assertEqual(len(actor_adds), 9)

    def test_path_lattice_single_node(self):
        cmds = self.pe.generate_path_lattice(
            bounds=(0, 0, 0, 0, 0, 0), spacing=512
        )
        self.assertEqual(len(cmds), 2)
        self.assertIn("ACTOR ADD CLASS=Engine.PathNode", cmds[1])

    def test_perimeter_nodes_count(self):
        cmds = self.pe.generate_perimeter_nodes(
            center=(0, 0, -200), radius=1024, count=8
        )
        self.assertEqual(len(cmds), 16)
        actor_adds = [c for c in cmds if "PathNode" in c]
        self.assertEqual(len(actor_adds), 8)

    def test_jumppad_pair_generates_two_actors(self):
        cmds = self.pe.generate_jumppad_pair(
            launch_pos=(0, 0, -200),
            landing_pos=(0, 0, 400),
        )
        self.assertEqual(len(cmds), 4)

    def test_teleporter_pair_generates_two_actors(self):
        cmds = self.pe.generate_teleporter_pair(
            entry_pos=(0, 0, 0),
            exit_pos=(2000, 2000, 0),
        )
        self.assertEqual(len(cmds), 4)
        actor_adds = [c for c in cmds if "Teleporter" in c]
        self.assertEqual(len(actor_adds), 2)

    def test_lift_system_generates_three_actors(self):
        cmds = self.pe.generate_lift_system(
            bottom_pos=(0, 0, -200),
            top_pos=(0, 0, 600),
        )
        self.assertEqual(len(cmds), 6)

    def test_parse_paths_build_log_empty(self):
        result = self.pe.parse_paths_build_log([])
        self.assertEqual(result["total_nodes"], 0)
        self.assertEqual(result["paths_defined"], 0)

    def test_parse_paths_build_log_with_data(self):
        log_lines = [
            "Log: 47 navigation nodes",
            "Log: 142 paths defined",
            "Warning: 3 unreachable navigation nodes found",
        ]
        result = self.pe.parse_paths_build_log(log_lines)
        self.assertEqual(result["total_nodes"], 47)
        self.assertEqual(result["paths_defined"], 142)
        self.assertEqual(result["unreachable_nodes"], 3)
        self.assertEqual(result["reachable_nodes"], 44)

    def test_reachability_report_excellent(self):
        log = ["Log: 20 navigation nodes", "Log: 45 paths defined"]
        report = self.pe.generate_reachability_report(log, player_start_count=4)
        self.assertEqual(report["assessment"], "EXCELLENT")

    def test_reachability_report_needs_work(self):
        log = ["Log: 20 navigation nodes", "Warning: 5 unreachable"]
        report = self.pe.generate_reachability_report(log, player_start_count=4)
        self.assertEqual(report["assessment"], "NEEDS_WORK")
        self.assertTrue(len(report["recommendations"]) > 0)

    def test_fill_path_gaps_identifies_gaps(self):
        # Two nodes 1500 UU apart should need a bridge (2 cmds: MOVETO + ADD)
        nodes = [(0, 0, 0), (1500, 0, 0)]
        bridges = self.pe.fill_path_gaps(nodes, max_reachable_distance=700)
        self.assertEqual(len(bridges), 2)
        self.assertIn("750", bridges[0])  # midpoint MOVETO

    def test_fill_path_gaps_no_gaps(self):
        # Two nodes 400 UU apart should NOT need a bridge
        nodes = [(0, 0, 0), (400, 0, 0)]
        bridges = self.pe.fill_path_gaps(nodes, max_reachable_distance=700)
        self.assertEqual(len(bridges), 0)

    def test_audit_commands_include_paths_build(self):
        cmds = self.pe.generate_audit_commands()
        self.assertIn("PATHS BUILD", cmds)
        self.assertIn("MAP CHECK", cmds)

    def test_multi_level_nodes(self):
        levels = [
            ((-512, -512, 512, 512), -200),
            ((-512, -512, 512, 512), 200),
        ]
        cmds = self.pe.generate_multi_level_nodes(levels, spacing=512)
        # 3x3 per level x 2 levels = 18 nodes = 36 commands
        self.assertEqual(len(cmds), 36)


class TestVisionInspector(unittest.TestCase):
    """Tests for the Phase 2 VisionInspector module (no live UnrealEd required)."""

    def test_vision_inspector_initializes(self):
        vi = VisionInspector()
        self.assertTrue(vi.screenshots_dir.exists())

    def test_viewport_quadrants_defined(self):
        from AgentHarness.core.vision_inspector import VIEWPORT_QUADRANTS
        self.assertIn("perspective", VIEWPORT_QUADRANTS)
        self.assertIn("top", VIEWPORT_QUADRANTS)
        self.assertIn("front", VIEWPORT_QUADRANTS)
        self.assertIn("side", VIEWPORT_QUADRANTS)

    def test_build_vision_context_without_window(self):
        vi = VisionInspector()
        # With an invalid hwnd, should return empty viewports
        context = vi.build_vision_context(hwnd=0, viewports=["perspective"])
        self.assertIn("viewports", context)
        # Won't capture anything since hwnd=0 is invalid
        self.assertEqual(len(context["viewports"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

