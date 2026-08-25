"""
Comprehensive test suite for the Standalone Multi-Engine Agent Harness.
Uses unittest with proper assertions for CI/verification.
"""

import sys
import unittest
from pathlib import Path

# Add AgentHarness parent directory and bootstrap for package imports
import core.bootstrap
from core.config_manager import ConfigManager
from core.engine_controller import EngineController
from core.formula_engine import FormulaEngine
from core.nexus_bridge import NexusBridge
from core.tools_schema import UNREALED_TOOLS
from core.logger import (
    get_logger,
    TRACE_LEVEL_NUM,
    set_global_log_level,
    flush_all_logs,
    write_crash_report,
    LOGS_DIR,
)


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
        expected = {"ut99_goty", "ut99_utron", "ut99_chaosut", "ut99_tacticalops", "ut2003", "ut2004", "ue5"}
        self.assertTrue(expected.issubset(set(profiles.keys())))

    def test_get_base_engines(self):
        base = self.cm.get_base_engines()
        self.assertIn("ut99_goty", base)
        self.assertIn("ut2004", base)
        self.assertNotIn("ut99_utron", base)

    def test_get_game_mods(self):
        mods = self.cm.get_game_mods()
        self.assertIn("ut99_utron", mods)
        self.assertIn("ut99_chaosut", mods)
        self.assertNotIn("ut99_goty", mods)

    def test_register_and_delete_custom_game_mod(self):
        mod_id = "test_custom_tc"
        mod_data = {
            "name": "Test Custom TC",
            "parent_engine": "ut99_goty",
            "generation": "UE1"
        }
        self.assertTrue(self.cm.register_game_mod(mod_id, mod_data))
        mods = self.cm.get_game_mods()
        self.assertIn(mod_id, mods)
        self.assertEqual(mods[mod_id]["category"], "Game Mod (Total Conversion)")

        # Cleanup
        self.assertTrue(self.cm.delete_game_mod(mod_id))
        self.assertNotIn(mod_id, self.cm.get_game_mods())

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

    def test_verify_and_initialize_engine(self):
        status = self.cm.verify_and_initialize_engine("ut99_goty", force_recheck=True)
        self.assertIsInstance(status, dict)
        self.assertTrue(status.get("initialized"))
        self.assertIn("verified", status)
        self.assertIn("summary", status)
        self.assertTrue(self.cm.is_engine_initialized("ut99_goty"))

    def test_active_engine_persists_across_instances(self):
        original = self.cm.get_active_engine_id()
        self.cm.set_active_engine_id("ut2004")

        # Create a fresh ConfigManager instance reading from disk
        new_cm = ConfigManager()
        self.assertEqual(new_cm.get_active_engine_id(), "ut2004")

        # Restore original
        self.cm.set_active_engine_id(original)

    def test_llm_engine_prompt_adapts_dynamically(self):
        from core.llm_engine import LLMEngine
        llm = LLMEngine(self.cm)

        # Test UT99 GOTY prompt
        self.cm.set_active_engine_id("ut99_goty")
        llm._refresh_context()
        prompt_goty = llm._build_system_prompt()
        self.assertIn("Botpack.ShockRifle", prompt_goty)
        self.assertNotIn("UTron.diffuser", prompt_goty)

        # Test UTron prompt
        self.cm.set_active_engine_id("ut99_utron")
        llm._refresh_context()
        prompt_utron = llm._build_system_prompt()
        self.assertIn("UTron.IdentityDisc", prompt_utron)
        self.assertIn("UTron.diffuser", prompt_utron)

        # Test UT2004 prompt
        self.cm.set_active_engine_id("ut2004")
        llm._refresh_context()
        prompt_ut2004 = llm._build_system_prompt()
        self.assertIn("XWeapons.ShockRiflePickup", prompt_ut2004)
        self.assertNotIn("UTron.diffuser", prompt_ut2004)

        # Restore
        self.cm.set_active_engine_id("ut99_goty")
        llm._refresh_context()


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

    def test_utron_mcp_core_generates_actors(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_utron_mcp_core(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            t3d_file = Path(tmp) / "MCPActors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("UTron.Central_Scrutiniser", content)
            self.assertIn("UTron.DeadlyDisc", content)
            self.assertIn("UTron.diffuser", content)

    def test_utron_tank_maze_grid_generates_actors(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_utron_tank_maze_grid(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            t3d_file = Path(tmp) / "TankMazeActors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("UTron.TankGun", content)
            self.assertIn("UTron.Recognizer", content)

    def test_utron_sarks_carrier_generates_actors(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_utron_sarks_carrier(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            t3d_file = Path(tmp) / "SarksCarrierActors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("UTron.RecoDrivable", content)
            self.assertIn("UTron.DeadlyDisc", content)

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
            # Verify continuous corridor and ramps
            corridor_file = Path(tmp) / "CastleCorridor.t3d"
            self.assertTrue(corridor_file.exists())
            ramp_file = Path(tmp) / "MountainRidgeRamp.t3d"
            self.assertTrue(ramp_file.exists())

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

    # -------------------------------------------------------------------------
    # UT2004 Procedural World & Component Tests
    # -------------------------------------------------------------------------
    def test_ut2004_tournament_colosseum_generates_valid_build(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut2004_tournament_colosseum(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            self.assertTrue(any("BRUSH SUBTRACT" in c for c in cmds))
            self.assertTrue(any("PATHS DEFINE" in c for c in cmds))
            t3d_file = Path(tmp) / "UT2k4_Colosseum_Actors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("XPickups.UDamagePack", content)
            self.assertIn("XWeapons.ShockRiflePickup", content)
            self.assertIn("XGame.xJumpPad", content)

    def test_ut2004_onslaught_canyon_outpost_generates_powercores_and_vehicles(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut2004_onslaught_canyon_outpost(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            self.assertTrue(any("OBJ LOAD" in c and "AntalusTextures" in c for c in cmds))
            t3d_file = Path(tmp) / "UT2k4_ONS_Canyon_Actors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("Onslaught.ONSPowerCore", content)
            self.assertIn("Onslaught.ONSPowerNodeNeutral", content)
            self.assertIn("Onslaught.ONSHoverCraftFactory", content)
            self.assertIn("Onslaught.ONSRVFactory", content)
            self.assertIn("Onslaught.ONSAttackCraftFactory", content)
            self.assertIn("Onslaught.ONSTankFactory", content)
            self.assertIn("Onslaught.ONSAVRiLPickup", content)
            self.assertIn("Engine.RoadPathNode", content)
            self.assertIn("Engine.FlyingPathNode", content)

    def test_ut2004_arctic_glacier_facility_generates_world_elements(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut2004_arctic_glacier_facility(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            self.assertTrue(any("OBJ LOAD" in c and "ArboreaArchitecture" in c for c in cmds))
            t3d_file = Path(tmp) / "UT2k4_Glacier_Actors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("Onslaught.ONSPRVFactory", content)
            self.assertIn("Onslaught.ONSHoverCraftFactory", content)
            self.assertIn("Onslaught.ONSPowerNodeNeutral", content)

    def test_ut2004_orbital_asteroid_mining_generates_world_elements(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut2004_orbital_asteroid_mining(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            t3d_file = Path(tmp) / "UT2k4_Space_Actors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("Engine.LevelInfo", content)
            self.assertIn("XWeapons.RedeemerPickup", content)
            self.assertIn("Space_Zone", content)

    def test_ut2004_volcanic_magma_foundry_generates_world_elements(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut2004_volcanic_magma_foundry(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            t3d_file = Path(tmp) / "UT2k4_Magma_Actors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("Engine.LevelInfo", content)
            self.assertIn("UDamage_Foundry", content)

    def test_ut2004_anubis_egyptian_temple_generates_world_elements(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut2004_anubis_egyptian_temple(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            t3d_file = Path(tmp) / "UT2k4_Anubis_Actors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("Engine.LevelInfo", content)
            self.assertIn("Anubis_UDamage", content)

    def test_ut2004_invasion_monster_arena_generates_skaarjpack_creatures(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            cmds = self.fe.generate_ut2004_invasion_monster_arena(system_dir=Path(tmp))
            self.assertIn("MAP NEW", cmds[0])
            t3d_file = Path(tmp) / "UT2k4_Invasion_Actors.t3d"
            self.assertTrue(t3d_file.exists())
            content = t3d_file.read_text(encoding="utf-8")
            self.assertIn("Engine.LevelInfo", content)
            self.assertIn("SkaarjPack.Skaarj", content)
            self.assertIn("SkaarjPack.Krall", content)
            self.assertIn("SkaarjPack.Titan", content)
            self.assertIn("SkaarjPack.Brute", content)
            self.assertIn("SkaarjPack.Pupae", content)

    def test_ut2004_palette_exhaustive_categories(self):
        from ui.palette_ut2004 import get_ut2004_palette
        palette = get_ut2004_palette()
        self.assertIsInstance(palette, list)
        self.assertGreaterEqual(len(palette), 8, "UT2004 palette should contain at least 8 rich categories")

        # Verify items in every category
        total_items = sum(len(cat.get("items", [])) for cat in palette)
        self.assertGreaterEqual(total_items, 30, "UT2004 palette should contain 30+ items")

        categories = [cat.get("category", "") for cat in palette]
        self.assertTrue(any("WORLD" in c.upper() for c in categories))
        self.assertTrue(any("VEHICLE" in c.upper() for c in categories))
        self.assertTrue(any("WEAPON" in c.upper() for c in categories))
        self.assertTrue(any("CREATURE" in c.upper() or "PEOPLE" in c.upper() for c in categories))


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

from core.pathing_engine import PathingEngine
from core.vision_inspector import VisionInspector


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
        from core.vision_inspector import VIEWPORT_QUADRANTS
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


class TestEngineScanner(unittest.TestCase):
    """Tests for the Universal Unreal Engine and Game Mod Auto-Discovery Engine."""

    def test_get_available_drives(self):
        from core.engine_scanner import EngineScanner
        drives = EngineScanner.get_available_drives()
        self.assertIsInstance(drives, list)
        self.assertTrue(len(drives) > 0)

    def test_inspect_directory_with_valid_ut99(self):
        import tempfile
        from core.engine_scanner import EngineScanner
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sys_dir = tmp_path / "System"
            sys_dir.mkdir()
            (sys_dir / "UnrealTournament.exe").touch()
            (sys_dir / "Botpack.u").touch()

            info = EngineScanner.inspect_directory(tmp_path)
            self.assertIsNotNone(info)
            self.assertEqual(info["id"], "ut99_goty")
            self.assertEqual(info["category"], "Base Game Engine")

    def test_inspect_mods_with_valid_utron(self):
        import tempfile
        from core.engine_scanner import EngineScanner
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            sys_dir = tmp_path / "System"
            sys_dir.mkdir()
            (sys_dir / "UTron.u").touch()

            mods = EngineScanner.inspect_mods_in_directory(tmp_path)
            self.assertTrue(any(m["id"] == "ut99_utron" for m in mods))

    def test_scan_all_finds_targets(self):
        from core.engine_scanner import EngineScanner
        res = EngineScanner.scan_all()
        self.assertIsInstance(res, dict)
        # Should detect local UT99 or UT2004 installation
        self.assertTrue(len(res) > 0)


class TestUpdateEngine(unittest.TestCase):
    """Tests for the UpdateEngine auto-updater and version management module."""

    def test_current_version_string(self):
        from core.update_engine import UpdateEngine
        ver = UpdateEngine.get_current_version()
        self.assertIsInstance(ver, str)
        self.assertTrue(len(ver) > 0)

    def test_parse_semver(self):
        from core.update_engine import UpdateEngine
        self.assertEqual(UpdateEngine.parse_semver("v2.10.0"), (2, 10, 0))
        self.assertEqual(UpdateEngine.parse_semver("2.9.1"), (2, 9, 1))
        self.assertEqual(UpdateEngine.parse_semver("3.0.0-beta"), (3, 0, 0))
        self.assertTrue(UpdateEngine.parse_semver("2.11.0") > UpdateEngine.parse_semver("2.10.0"))

    def test_is_git_repository(self):
        from core.update_engine import UpdateEngine
        is_git = UpdateEngine.is_git_repository()
        self.assertIsInstance(is_git, bool)
        if (Path(__file__).parent / ".git").exists():
            self.assertTrue(is_git)
        else:
            self.assertFalse(is_git)

    def test_check_for_updates_returns_dict(self):
        from core.update_engine import UpdateEngine
        res = UpdateEngine.check_for_updates(timeout=3.0)
        self.assertIsInstance(res, dict)
        self.assertIn("update_available", res)
        self.assertIn("current_version", res)
        self.assertIn("latest_version", res)


class TestLoggerAndDiagnostics(unittest.TestCase):
    """Tests for the world-class TRACE logging and crash capture system."""

    def test_trace_level_and_method(self):
        import logging
        self.assertEqual(logging.TRACE, 5)
        self.assertEqual(TRACE_LEVEL_NUM, 5)
        logger = get_logger("TestTraceLogger", "test_trace.log")
        self.assertTrue(hasattr(logger, "trace"))

    def test_log_file_written(self):
        logger = get_logger("TestFileLogger", "agent_harness.log")
        test_msg = "World-class trace logging test message"
        logger.info(test_msg)
        flush_all_logs()

        master_log = LOGS_DIR / "agent_harness.log"
        self.assertTrue(master_log.exists())
        with open(master_log, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        self.assertIn(test_msg, content)

    def test_crash_report_generation(self):
        try:
            raise ValueError("Simulated crash exception for diagnostic test")
        except ValueError as err:
            crash_file = write_crash_report(
                type(err), err, err.__traceback__, context="Unit Test Crash Test"
            )
            self.assertTrue(crash_file.exists())
            with open(crash_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.assertIn("Simulated crash exception for diagnostic test", content)
            self.assertIn("Unit Test Crash Test", content)
            self.assertIn("ENVIRONMENT DUMP", content)


class TestBootstrapDPI(unittest.TestCase):
    """Tests for the Win32 DPI awareness bootstrap (v2.15.0)."""

    def test_dpi_awareness_level_string(self):
        from core.bootstrap import get_dpi_awareness_level
        level = get_dpi_awareness_level()
        self.assertIsInstance(level, str)
        self.assertIn(
            level,
            {"per_monitor_v2", "per_monitor", "system_aware", "unavailable"},
        )

    def test_dpi_scale_factor_returns_float(self):
        from core.bootstrap import get_dpi_scale_factor
        scale = get_dpi_scale_factor(0)
        self.assertIsInstance(scale, float)
        # Scale should be at least 1.0 (96 DPI baseline)
        self.assertGreaterEqual(scale, 1.0)

    def test_dpi_scale_factor_with_invalid_hwnd(self):
        from core.bootstrap import get_dpi_scale_factor
        # An invalid hwnd should gracefully fall back to system DPI or 1.0
        scale = get_dpi_scale_factor(0xDEAD)
        self.assertIsInstance(scale, float)
        self.assertGreaterEqual(scale, 1.0)


class TestUpdateEngineResourceSafety(unittest.TestCase):
    """Tests for the UpdateEngine ResourceWarning fix (v2.15.0)."""

    def test_check_for_updates_no_resource_warning(self):
        import warnings
        from core.update_engine import UpdateEngine
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            UpdateEngine.check_for_updates(timeout=3.0)
            resource_warnings = [x for x in w if issubclass(x.category, ResourceWarning)]
            self.assertEqual(
                len(resource_warnings), 0,
                f"ResourceWarning raised during check_for_updates: {resource_warnings}",
            )

    def test_apply_update_source_uses_context_manager(self):
        """Verify apply_update's ZIP download path uses urllib.request.urlopen
        via a with-block rather than the deprecated urlretrieve."""
        import inspect
        from core.update_engine import UpdateEngine
        source = inspect.getsource(UpdateEngine.apply_update)
        # The old pattern was `urlretrieve(zip_url, ...)` — ensure it's gone
        self.assertNotIn(
            "urlretrieve",
            source,
            "apply_update still uses urlretrieve — expected urlopen with context manager",
        )
        # The new pattern should use `urlopen(req, ...)` inside a with-block
        self.assertIn("urlopen", source)


class TestTargetAndPaletteSystem(unittest.TestCase):
    """Audits the Target Engine profiles, tab mappings, and quick action Palettes."""

    def setUp(self):
        self.cm = ConfigManager()

    def test_engine_profiles_validity(self):
        profiles = self.cm.get_all_engine_profiles()
        self.assertGreaterEqual(len(profiles), 6)
        for p_id, p_data in profiles.items():
            self.assertIn("id", p_data)
            self.assertIn("name", p_data)
            self.assertIn("system_dir", p_data)

    def test_tab_map_coverage(self):
        tab_map = {
            "ut99_goty": 0,
            "ut99_chaosut": 0,
            "ut99_tacticalops": 0,
            "ut99_utron": 1,
            "ut2004": 2,
            "ut2003": 2,
        }
        for p_id in self.cm.get_all_engine_profiles():
            if p_id != "ue5":
                self.assertIn(p_id, tab_map, f"Engine {p_id} missing in palette tab map")

    def test_ut99_goty_palette_evaluation(self):
        from ui.palette_ut99_goty import get_ut99_goty_palette
        palette = get_ut99_goty_palette()
        self.assertIsInstance(palette, list)
        self.assertGreaterEqual(len(palette), 4)
        for cat in palette:
            self.assertIn("category", cat)
            for itm in cat.get("items", []):
                self.assertTrue(itm.get("title") or itm.get("name"))
                cf = itm.get("commands_factory")
                if cf:
                    cmds = cf()
                    self.assertIsInstance(cmds, list)
                    self.assertGreater(len(cmds), 0)

    def test_ut99_utron_palette_evaluation(self):
        from ui.palette_ut99_utron import get_ut99_utron_palette
        palette = get_ut99_utron_palette()
        self.assertIsInstance(palette, list)
        self.assertGreaterEqual(len(palette), 3)
        for cat in palette:
            for itm in cat.get("items", []):
                cf = itm.get("commands_factory")
                if cf:
                    cmds = cf()
                    self.assertIsInstance(cmds, list)
                    self.assertGreater(len(cmds), 0)

    def test_ut2004_palette_evaluation(self):
        from ui.palette_ut2004 import get_ut2004_palette
        palette = get_ut2004_palette()
        self.assertIsInstance(palette, list)
        self.assertGreaterEqual(len(palette), 8)
        for cat in palette:
            for itm in cat.get("items", []):
                cf = itm.get("commands_factory")
                if cf:
                    cmds = cf()
                    self.assertIsInstance(cmds, list)
                    self.assertGreater(len(cmds), 0)

    def test_ut2004_palette_vehicle_factory_safety(self):
        """Verifies no vehicle in the UT2004 palette spawns live pawns that crash USkeletalMeshInstance in editor."""
        import re
        from ui.palette_ut2004 import get_ut2004_palette
        palette = get_ut2004_palette()
        dangerous_pattern = re.compile(r"CLASS=(?:Onslaught|OnslaughtFull)\.(?:ONSHoverTank|ONSHoverBike|ONSRV|ONSPRV|ONSAttackCraft|ONSBomber|ONSPowerNode|ONSAVRiL)\b(?!(?:Factory|Pickup))")
        for cat in palette:
            for itm in cat.get("items", []):
                for cmd in itm.get("commands", []):
                    m = dangerous_pattern.search(cmd)
                    self.assertIsNone(m, f"Palette item '{itm.get('title')}' uses unsafe live vehicle/actor class: '{cmd}'")

    def test_ut2004_all_generators_preload_textures(self):
        """Verifies all UT2004 formula builders preload required texture packages via OBJ LOAD."""
        from core.formula_engine import FormulaEngine
        import tempfile
        generators = [
            FormulaEngine.generate_ut2004_tournament_colosseum,
            FormulaEngine.generate_ut2004_onslaught_canyon_outpost,
            FormulaEngine.generate_ut2004_arctic_glacier_facility,
            FormulaEngine.generate_ut2004_orbital_asteroid_mining,
            FormulaEngine.generate_ut2004_volcanic_magma_foundry,
            FormulaEngine.generate_ut2004_anubis_egyptian_temple,
            FormulaEngine.generate_ut2004_invasion_monster_arena,
            FormulaEngine.generate_ut2004_reactor_core_chamber,
            FormulaEngine.generate_ut2004_biohazard_quarantine_lab,
            FormulaEngine.generate_ut2004_fortified_forward_base,
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for gen in generators:
                cmds = gen(system_dir=Path(tmp))
                self.assertIn("MAP NEW", cmds[0])
                self.assertTrue(any(c.startswith("OBJ LOAD FILE=") for c in cmds), f"{gen.__name__} missing OBJ LOAD commands")

    def test_ut2004_navigation_nodes_have_no_duplicate_locations(self):
        """Verifies no two NavigationPoints/PlayerStarts share identical or near-identical coordinates (<50 UU)."""
        from core.formula_engine import FormulaEngine
        import tempfile
        import re
        generators = [
            FormulaEngine.generate_ut2004_tournament_colosseum,
            FormulaEngine.generate_ut2004_onslaught_canyon_outpost,
            FormulaEngine.generate_ut2004_arctic_glacier_facility,
            FormulaEngine.generate_ut2004_orbital_asteroid_mining,
            FormulaEngine.generate_ut2004_volcanic_magma_foundry,
            FormulaEngine.generate_ut2004_anubis_egyptian_temple,
            FormulaEngine.generate_ut2004_invasion_monster_arena,
            FormulaEngine.generate_ut2004_reactor_core_chamber,
            FormulaEngine.generate_ut2004_biohazard_quarantine_lab,
            FormulaEngine.generate_ut2004_fortified_forward_base,
        ]
        loc_pattern = re.compile(r"Location=\(X=([-\d.]+),Y=([-\d.]+),Z=([-\d.]+)\)")
        with tempfile.TemporaryDirectory() as tmp:
            for gen in generators:
                gen(system_dir=Path(tmp))
                for t3d in Path(tmp).glob("*.t3d"):
                    content = t3d.read_text(encoding="utf-8")
                    actors = content.split("Begin Actor")
                    nav_locs = []
                    for act in actors:
                        if any(k in act for k in ["PathNode", "PlayerStart", "JumpPad", "RoadPathNode", "FlyingPathNode"]):
                            m = loc_pattern.search(act)
                            if m:
                                x, y, z = float(m.group(1)), float(m.group(2)), float(m.group(3))
                                for (ox, oy, oz) in nav_locs:
                                    dist = ((x - ox)**2 + (y - oy)**2 + (z - oz)**2)**0.5
                                    self.assertGreater(dist, 10.0, f"Generator {gen.__name__} produced overlapping nav nodes in {t3d.name} at ({x}, {y}, {z}) vs ({ox}, {oy}, {oz})")
                                nav_locs.append((x, y, z))

    def test_tools_schema_detail_level_presence(self):
        tool_names = {t["function"]["name"]: t["function"] for t in UNREALED_TOOLS}
        self.assertIn("build_tournament_arena", tool_names)
        self.assertIn("detail_level", tool_names["build_tournament_arena"]["parameters"]["properties"])
        self.assertIn("build_unreal1_sanctuary", tool_names)
        self.assertIn("build_outdoor_world", tool_names)


class TestFormulaEngineUltraGeometry(unittest.TestCase):
    """Tests for the Ultra Geometry Detail Engine, Semi-Solid Brushes, and Unreal 1 RPG generators."""

    def test_detail_presets_structure(self):
        from core.formula_engine import DETAIL_PRESETS
        self.assertIn("standard", DETAIL_PRESETS)
        self.assertIn("high", DETAIL_PRESETS)
        self.assertIn("ultra", DETAIL_PRESETS)
        self.assertEqual(DETAIL_PRESETS["ultra"]["pillar_sides"], 32)
        self.assertEqual(DETAIL_PRESETS["ultra"]["tower_sides"], 24)
        self.assertTrue(DETAIL_PRESETS["ultra"]["semisolid_decoration"])
        self.assertTrue(DETAIL_PRESETS["ultra"]["rich_story_elements"])

    def test_primitive_shapes_generate_polylists(self):
        from core.formula_engine import _generate_brush_polylist_t3d
        shapes = ["BeveledBox", "Arch", "Buttress", "TrimStrip", "Cylinder", "HexColumn"]
        for s in shapes:
            t3d = _generate_brush_polylist_t3d((256.0, 256.0, 256.0), shape=s, sides=12)
            self.assertIn("Begin PolyList", t3d)
            self.assertIn("End PolyList", t3d)
            self.assertIn("Vertex", t3d)

    def test_semisolid_flag_output(self):
        from core.formula_engine import _generate_brush_polylist_t3d
        t3d_solid = _generate_brush_polylist_t3d((128.0, 128.0, 128.0), shape="Box", is_semisolid=False)
        t3d_semi = _generate_brush_polylist_t3d((128.0, 128.0, 128.0), shape="Box", is_semisolid=True)
        self.assertNotIn("Flags=32", t3d_solid)
        self.assertIn("Flags=32", t3d_semi)

    def test_unreal1_sp_sanctuary_generation(self):
        cmds = FormulaEngine.generate_unreal1_sp_sanctuary(detail_level="ultra")
        self.assertIsInstance(cmds, list)
        self.assertGreater(len(cmds), 15)
        cmd_str = "\n".join(cmds)
        self.assertIn("MAP NEW", cmd_str)
        self.assertIn("MAP REBUILD", cmd_str)
        self.assertIn("NaliCast", cmd_str)

    def test_verdant_mountain_valley_ultra_generation(self):
        cmds = FormulaEngine.generate_ut99_verdant_mountain_valley(detail_level="ultra")
        self.assertIsInstance(cmds, list)
        self.assertGreater(len(cmds), 20)
        cmd_str = "\n".join(cmds)
        self.assertIn("BridgeArchRib.t3d", cmd_str)
        self.assertIn("CastleButtress.t3d", cmd_str)

    def test_tournament_arena_ultra_vs_standard(self):
        cmds_standard = FormulaEngine.generate_ut99_tournament_arena(detail_level="standard")
        cmds_ultra = FormulaEngine.generate_ut99_tournament_arena(detail_level="ultra")
        # Ultra adds fluted semi-solid columns, perimeter moldings, crown cornices, and alcoves (56 vs 26 commands)
        self.assertGreater(len(cmds_ultra), len(cmds_standard))
        self.assertGreaterEqual(len(cmds_ultra), 50)
        self.assertLessEqual(len(cmds_standard), 30)


class TestMemoryEngine(unittest.TestCase):
    """Tests for the SQLite Persistent Memory, Wisdom Recorder, and Dynamic RAG Engine."""

    def setUp(self):
        import tempfile
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_db = Path(self.tmp_dir.name) / "test_memory.db"
        from core.memory_engine import MemoryEngine
        self.memory = MemoryEngine(db_path=str(self.tmp_db))

    def tearDown(self):
        self.memory = None
        import gc
        gc.collect()
        try:
            self.tmp_dir.cleanup()
        except Exception:
            pass

    def test_database_initialization_and_seeding(self):
        wisdom = self.memory.query_wisdom("", limit=10)
        self.assertGreaterEqual(len(wisdom), 5)
        titles = [w["title"] for w in wisdom]
        self.assertTrue(any("Watertight Brush" in t for t in titles))
        self.assertTrue(any("UT2004 Navigation" in t for t in titles))

    def test_record_and_query_wisdom(self):
        ok = self.memory.record_wisdom(
            category="custom_test",
            title="Custom Lighting Philosophy",
            content="Use amber key lights at hue 32 with violet shadows at hue 210.",
            tags="lighting,philosophy,colors",
        )
        self.assertTrue(ok)

        results = self.memory.query_wisdom("lighting amber", limit=5)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Custom Lighting Philosophy")

    def test_record_and_get_build_telemetry(self):
        ok = self.memory.record_build_event(
            engine_id="ut99_goty",
            build_type="Verdant Mountain Valley",
            command_count=42,
            entity_count=28,
            details="Successfully synthesized valley fortress with 20 path nodes."
        )
        self.assertTrue(ok)

        recent = self.memory.get_recent_builds(limit=5)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["engine_id"], "ut99_goty")
        self.assertEqual(recent[0]["command_count"], 42)

    def test_knowledge_base_indexing_and_search(self):
        docs_dir = Path(__file__).resolve().parent / "docs"
        if docs_dir.exists():
            count = self.memory.index_documentation_directory(str(docs_dir))
            self.assertGreater(count, 0)

            results = self.memory.search_knowledge_base("UnrealScript syntax", limit=3)
            self.assertIsInstance(results, list)

    def test_build_augmented_context(self):
        ctx = self.memory.build_augmented_context("How do I build lights and path nodes?", "ut99_goty")
        self.assertIsInstance(ctx, str)
        self.assertIn("RETRIEVED ARCHITECTURAL WISDOM", ctx)


class TestLLMNativeToolFormatters(unittest.TestCase):
    """Tests for multi-provider native tool schema formatting."""

    def test_gemini_schema_formatter(self):
        from core.llm_engine import _tools_to_gemini_schema
        from core.tools_schema import UNREALED_TOOLS

        gemini_tools = _tools_to_gemini_schema(UNREALED_TOOLS)
        self.assertIsInstance(gemini_tools, list)
        self.assertEqual(len(gemini_tools), 1)
        self.assertIn("functionDeclarations", gemini_tools[0])

        decls = gemini_tools[0]["functionDeclarations"]
        self.assertGreater(len(decls), 5)
        names = [d["name"] for d in decls]
        self.assertIn("execute_unrealed_commands", names)
        self.assertIn("build_outdoor_world", names)
        self.assertIn("build_tournament_arena", names)

    def test_anthropic_schema_formatter(self):
        from core.llm_engine import _tools_to_anthropic_schema
        from core.tools_schema import UNREALED_TOOLS

        claude_tools = _tools_to_anthropic_schema(UNREALED_TOOLS)
        self.assertIsInstance(claude_tools, list)
        self.assertGreater(len(claude_tools), 5)

        for ct in claude_tools:
            self.assertIn("name", ct)
            self.assertIn("description", ct)
            self.assertIn("input_schema", ct)


class TestMindSynthesizer(unittest.TestCase):
    """Tests for the SOTA Mind-to-World Neuro-Symbolic Synthesizer."""

    def test_intent_analysis(self):
        from core.mind_synthesizer import MindSynthesizer
        intent = MindSynthesizer.analyze_design_intent("Huge ancient gothic temple with snipers and jump pads")
        self.assertEqual(intent["theme"], "ancient")
        self.assertEqual(intent["scale"], "large")
        self.assertTrue(intent["has_jump_pad"])
        self.assertTrue(intent["has_sniper_perch"])

    def test_synthesize_level_from_mind(self):
        from core.mind_synthesizer import MindSynthesizer
        cmds = MindSynthesizer.synthesize_level_from_mind("Cybernetic neon combat arena with central dais")
        self.assertIsInstance(cmds, list)
        self.assertGreater(len(cmds), 10)
        cmd_str = "\n".join(cmds)
        self.assertIn("MAP NEW", cmd_str)
        self.assertIn("OBJ LOAD", cmd_str)
        self.assertIn("BRUSH SUBTRACT", cmd_str)
        self.assertIn("MAP REBUILD", cmd_str)

    def test_generate_procedural_compound(self):
        from core.mind_synthesizer import MindSynthesizer
        cmds = MindSynthesizer.generate_procedural_compound(room_count=3)
        self.assertIsInstance(cmds, list)
        self.assertGreater(len(cmds), 12)
        cmd_str = "\n".join(cmds)
        self.assertIn("HubRoom.t3d", cmd_str)
        self.assertIn("EastRoom.t3d", cmd_str)
        self.assertIn("WestRoom.t3d", cmd_str)


class TestSkillGenesis(unittest.TestCase):
    """Tests for lifelong autonomous skill discovery and registration."""

    def setUp(self):
        import tempfile
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_db = Path(self.tmp_dir.name) / "test_skills.db"
        from core.memory_engine import MemoryEngine
        from core.skill_genesis import SkillGenesis
        self.memory = MemoryEngine(db_path=str(self.tmp_db))
        self.genesis = SkillGenesis(self.memory)

    def tearDown(self):
        self.memory = None
        self.genesis = None
        import gc
        gc.collect()
        try:
            self.tmp_dir.cleanup()
        except Exception:
            pass

    def test_distill_and_list_skills(self):
        ok = self.genesis.distill_and_register_skill(
            skill_name="TestCathedralVault",
            category="geometry",
            description="Vaulted cathedral ceiling with fluted buttresses.",
            parameters={"vault_height": 1024, "arch_radius": 512},
            command_template=["BRUSH IMPORT FILE=Vault.t3d", "BRUSH SUBTRACT"],
            tags="cathedral,vault,gothic",
        )
        self.assertTrue(ok)

        skills = self.genesis.list_learned_skills()
        self.assertGreaterEqual(len(skills), 1)
        self.assertEqual(skills[0]["skill_name"], "TestCathedralVault")


class TestUnrealWizardBuilder(unittest.TestCase):
    """Tests for the Unreal Architect Wizard Builder dual-mode generator."""

    def test_unreal1_campaign_level_generation(self):
        from core.wizard_builder import UnrealWizardBuilder
        cmds = UnrealWizardBuilder.build_unreal1_rpg_campaign_level(
            preset_key="chizra_temple",
            include_secret_crypt=True,
            detail_level="ultra",
        )
        self.assertIsInstance(cmds, list)
        self.assertGreater(len(cmds), 15)
        cmd_str = "\n".join(cmds)
        self.assertIn("MAP NEW", cmd_str)
        self.assertIn("WizNave.t3d", cmd_str)
        self.assertIn("WizActors.t3d", cmd_str)
        self.assertIn("MAP REBUILD", cmd_str)

    def test_inject_wing_into_existing_map(self):
        from core.wizard_builder import UnrealWizardBuilder
        cmds = UnrealWizardBuilder.inject_wing_into_existing_map(
            anchor_location=(1000.0, 500.0, 0.0),
            wing_type="secret_crypt",
            direction="North",
        )
        self.assertIsInstance(cmds, list)
        self.assertGreater(len(cmds), 8)
        cmd_str = "\n".join(cmds)
        # Injection MUST NOT wipe the existing map with MAP NEW
        self.assertNotIn("MAP NEW", cmd_str)
        self.assertIn("InjectHall.t3d", cmd_str)
        self.assertIn("InjectWing.t3d", cmd_str)
        self.assertIn("MAP REBUILD", cmd_str)


if __name__ == "__main__":
    unittest.main(verbosity=2)


