"""
Standardized Multi-Engine Tool Calling Schemas for Standalone Agent Harness.
Compatible with OpenAI, Gemini, Claude, and Ollama tool-calling formats.
"""

from typing import Any, Dict, List

UNREALED_TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "execute_unrealed_commands",
            "description": "Executes one or more raw UnrealEd console/exec commands directly in UEditorEngine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of commands in execution order (e.g. ['BRUSH BUILD BOX X=1024 Y=1024 Z=512', 'BRUSH SUBTRACT', 'MAP REBUILD'])",
                    }
                },
                "required": ["commands"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_bsp_room",
            "description": "Parametrically creates subtractive rooms or additive brushes in UnrealEd.",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["Subtract", "Add"],
                        "description": "CSG operation: 'Subtract' to carve hollow space, 'Add' to place solid geometry (pillars, platforms).",
                    },
                    "shape": {
                        "type": "string",
                        "enum": ["Box", "Cylinder", "Cone", "Stairs"],
                        "description": "Brush geometry shape.",
                    },
                    "dimensions": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Dimensions [X, Y, Z] in Unreal Units (e.g. [2048, 2048, 512]).",
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Center 3D coordinates [X, Y, Z] in Unreal Units.",
                    },
                    "add_light": {
                        "type": "boolean",
                        "description": "If true, automatically places a Light actor in the room center.",
                    },
                },
                "required": ["operation", "shape", "dimensions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "spawn_actor",
            "description": "Spawns an actor of a given class at exact 3D coordinates in the active level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "actor_class": {
                        "type": "string",
                        "description": "Actor class name (e.g. 'UTron.IdentityDisc', 'UTron.diffuser', 'UTron.wirenode', 'Botpack.ShockRifle', 'Engine.PlayerStart', 'Engine.Light').",
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Position [X, Y, Z] in Unreal Units.",
                    },
                    "properties": {
                        "type": "object",
                        "description": "Key-value dictionary of actor properties (e.g. {'LightBrightness': 200, 'Tag': 'RedBase'}).",
                    },
                },
                "required": ["actor_class", "location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_utron_arena",
            "description": "Procedurally builds a UTron Cyber-Grid combat arena, Diffuser tile network, or Light Cycle track.",
            "parameters": {
                "type": "object",
                "properties": {
                    "archetype": {
                        "type": "string",
                        "enum": ["disc_arena", "diffuser_bus", "wirenode_circuit", "lightcycle_grid"],
                        "description": "UTron archetype to construct.",
                    },
                    "radius": {
                        "type": "number",
                        "description": "Arena radius or size in Unreal Units.",
                    },
                    "diffuser_count": {
                        "type": "integer",
                        "description": "Number of diffuser tiles for a bus array.",
                    },
                },
                "required": ["archetype"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_tournament_arena",
            "description": "Procedurally builds a tournament deathmatch arena with multi-tier mezzanines, semi-solid fluted columns, crown moldings, weapon layouts, and path nodes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "width": {"type": "number", "description": "Width X in Unreal Units (default 3072)."},
                    "length": {"type": "number", "description": "Length Y in Unreal Units (default 3072)."},
                    "height": {"type": "number", "description": "Height Z in Unreal Units (default 1024)."},
                    "detail_level": {
                        "type": "string",
                        "enum": ["standard", "high", "ultra"],
                        "description": "Architectural detail level. 'ultra' adds semi-solid fluted columns, perimeter moldings, crown cornices, recessed lighting alcoves, and 44 path nodes.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_unreal1_sanctuary",
            "description": "Procedurally builds an authentic Unreal 1 Single-Player narrative RPG dungeon sanctuary with vaulted nave, arched ceilings, semi-solid fluted columns, TranslatorEvent lore tablets, Nali monks, Brutes, Skaarj, and sacred crypts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "detail_level": {
                        "type": "string",
                        "enum": ["standard", "high", "ultra"],
                        "description": "Architectural detail level ('ultra' enables 24-sided fluted columns, alcove moldings, and sacred pool crypts).",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_outdoor_world",
            "description": "Procedurally builds a premier outdoor world: mountain valley fortress, arid desert canyon ruins, or orbital asteroid outpost.",
            "parameters": {
                "type": "object",
                "properties": {
                    "world_type": {
                        "type": "string",
                        "enum": ["mountain_valley", "desert_canyon", "asteroid_outpost"],
                        "description": "World environment archetype to construct.",
                    },
                    "detail_level": {
                        "type": "string",
                        "enum": ["standard", "high", "ultra"],
                        "description": "Architectural detail level ('ultra' enables 24-sided towers/lookouts, semi-solid flying buttresses, stepped cliff shelves, bridge arch ribs, and TranslatorEvent lore).",
                    },
                },
                "required": ["world_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "rebuild_level",
            "description": "Executes full BSP CSG geometry compilation, lighting calculations, and bot AI path grid building.",
            "parameters": {
                "type": "object",
                "properties": {
                    "build_paths": {
                        "type": "boolean",
                        "description": "If true, builds bot navigation path network.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "switch_engine_profile",
            "description": "Dynamically switches the active engine target (e.g. 'ut99_utron', 'ut99_goty', 'ut2003', 'ut2004').",
            "parameters": {
                "type": "object",
                "properties": {
                    "engine_id": {
                        "type": "string",
                        "enum": ["ut99_utron", "ut99_goty", "ut2003", "ut2004"],
                        "description": "Target engine profile identifier.",
                    }
                },
                "required": ["engine_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "capture_viewport",
            "description": "Captures the active UnrealEd 3D perspective viewport for multimodal visual inspection.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    # ── Phase 2: Bot Pathing & Navigation Tools ──────────────────────
    {
        "type": "function",
        "function": {
            "name": "build_path_lattice",
            "description": "Generates a uniform grid of PathNode actors covering a bounding box for bot AI navigation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bounds": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Bounding box [min_x, min_y, min_z, max_x, max_y, max_z] in Unreal Units.",
                    },
                    "spacing": {
                        "type": "number",
                        "description": "Distance between PathNodes in Unreal Units (default 512).",
                    },
                    "z_floor": {
                        "type": "number",
                        "description": "Override Z floor height for all nodes.",
                    },
                },
                "required": ["bounds"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_perimeter_nodes",
            "description": "Generates a ring of PathNodes around a center point for circular arenas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "center": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Center position [X, Y, Z] in Unreal Units.",
                    },
                    "radius": {
                        "type": "number",
                        "description": "Ring radius in Unreal Units (default 1024).",
                    },
                    "count": {
                        "type": "integer",
                        "description": "Number of PathNodes in the ring (default 8).",
                    },
                },
                "required": ["center"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wire_jumppad",
            "description": "Creates a JumpPad (Kicker) at the launch position and a LiftExit at the landing position for bot vertical navigation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "launch_pos": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Launch position [X, Y, Z].",
                    },
                    "landing_pos": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Landing position [X, Y, Z].",
                    },
                    "tag": {
                        "type": "string",
                        "description": "Tag name for wiring the pair.",
                    },
                },
                "required": ["launch_pos", "landing_pos"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wire_teleporter",
            "description": "Creates a bidirectional Teleporter pair with matching URL tags for bot navigation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entry_pos": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Entry teleporter position [X, Y, Z].",
                    },
                    "exit_pos": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Exit teleporter position [X, Y, Z].",
                    },
                    "url_tag": {
                        "type": "string",
                        "description": "Matching URL tag for the pair.",
                    },
                },
                "required": ["entry_pos", "exit_pos"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "audit_pathing",
            "description": "Runs PATHS BUILD and MAP CHECK, then parses Editor.log to produce a reachability audit report with recommendations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fix_gaps": {
                        "type": "boolean",
                        "description": "If true, automatically inserts bridging PathNodes where gaps exceed max reachability distance.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_viewport",
            "description": "Captures a specific UnrealEd viewport (perspective, top, front, side) and returns a base64-encoded PNG for multimodal spatial analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "viewport": {
                        "type": "string",
                        "enum": ["perspective", "top", "front", "side", "all"],
                        "description": "Which viewport to capture.",
                    },
                    "add_grid": {
                        "type": "boolean",
                        "description": "If true, overlays a reference grid on the capture.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "synthesize_mind_level",
            "description": "SOTA Mind-to-World Synthesizer: Compiles a free-form human conceptual idea into a watertight, illuminated, and fully pathed UnrealEd level within 75% engine budget limits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "Natural language creative prompt describing desired level theme, lore, combat topology, and mood.",
                    },
                },
                "required": ["prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_procedural_compound",
            "description": "Synthesizes an interconnected multi-chamber compound with central hub, connecting corridors, airlocks, and vistas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "room_count": {
                        "type": "integer",
                        "description": "Number of interconnected rooms to carve (e.g. 3, 5).",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "distill_and_register_skill",
            "description": "Formalizes a novel architectural design pattern or CSG formula into a reusable, persistent .uah_skill stored in lifelong memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {"type": "string", "description": "Unique descriptive name for the learned skill."},
                    "category": {"type": "string", "description": "Skill category (e.g. geometry, lighting, pathing, gametype)."},
                    "description": {"type": "string", "description": "Detailed explanation of what the skill constructs."},
                    "parameters": {"type": "object", "description": "Parametric inputs used by the skill."},
                },
                "required": ["skill_name", "category", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wizard_build_level",
            "description": "Unreal Architect Wizard: Generates an expansive clean-slate level (Unreal 1 SP RPG Campaign, UT99 Arena/CTF, UTron, UT2004) with TranslatorEvents, Nali NPCs, Skaarj enemies, and full lighting/pathing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "preset_key": {
                        "type": "string",
                        "enum": ["chizra_temple", "skaarj_mothership", "bluff_eversmoking"],
                        "description": "Campaign narrative preset.",
                    },
                    "include_secret_crypt": {
                        "type": "boolean",
                        "description": "Whether to carve a hidden subterranean crypt wing with monster guard and reward.",
                    },
                    "detail_level": {
                        "type": "string",
                        "enum": ["standard", "high", "ultra"],
                        "description": "Architectural detail level (75% budget optimization).",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wizard_inject_extension",
            "description": "Unreal Architect Wizard (In-Situ Mode): Injects a non-destructive wing, crypt, or tower into the currently open active map in UnrealEd without resetting existing geometry.",
            "parameters": {
                "type": "object",
                "properties": {
                    "anchor_location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Anchor [X, Y, Z] coordinate in current map where the new wing will connect.",
                    },
                    "wing_type": {
                        "type": "string",
                        "enum": ["secret_crypt", "sniper_overlook", "armory_hall", "powernode_substation"],
                        "description": "Type of wing/room to inject.",
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["North", "South", "East", "West"],
                        "description": "Direction relative to anchor where the new wing should extend.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_unreal_academy",
            "description": "Unreal Academy Knowledge Engine: Searches master tutorials, 3D optical illusions, FX tricks, little-known engine quirks, and classic U1-U5 map deconstructions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword or topic (e.g. 'forced perspective skybox', 'warpzone portal', 'Deck16 slime vat', '75 percent rule').",
                    },
                    "category": {
                        "type": "string",
                        "enum": ["tutorials", "tips_and_tricks", "little_known_facts", "artistic_illusions_fx", "classic_map_deconstructions", "engine_secrets"],
                        "description": "Optional category filter.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ingest_master_insight",
            "description": "Autonomous Training & Ingestion: Records a new master level design technique, 3D illusion, engine quirk fix, or map review into lifelong SQLite memory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Descriptive title of the technique or trick."},
                    "category": {
                        "type": "string",
                        "enum": ["tutorials", "tips_and_tricks", "little_known_facts", "artistic_illusions_fx", "classic_map_deconstructions", "engine_secrets"],
                        "description": "Category.",
                    },
                    "summary": {"type": "string", "description": "Conceptual summary and rationale."},
                    "step_by_step": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Step-by-step implementation instructions.",
                    },
                    "technical_trick": {"type": "string", "description": "The key technical secret or gotcha."},
                },
                "required": ["title", "category", "summary"],
            },
        },
    },
]


