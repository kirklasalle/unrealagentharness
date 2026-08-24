"""
Unreal Tournament 2004 (UE2.5 / v3369+) Exhaustive World-Class Quick Action Palette.
Provides instant 1-click procedural worlds, full exterior outposts, complex interiors,
combat vehicles, Onslaught/Assault objectives, weapon armory, powerups, interactive things,
SkaarjPack creature spawners, and bot/vehicle path navigation networks.
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from core.formula_engine import FormulaEngine


def get_ut2004_palette(
    on_execute_prompt: Optional[Callable[[str], None]] = None,
    system_dir: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Returns an exhaustive, world-class category grouping of UT2004 blueprints and quick action commands."""

    return [
        # ---------------------------------------------------------------------
        # 1. PREMIER FULL WORLD ENVIRONMENTS
        # ---------------------------------------------------------------------
        {
            "category": "🏆 PREMIER FULL WORLD ENVIRONMENTS",
            "items": [
                {
                    "title": "🏜️ Onslaught Canyon Outpost (Torlan)",
                    "desc": "8192x8192 outdoor canyon expanse with Red & Blue PowerCores, Neutral PowerNodes, Manta/Scorpion/Raptor/Goliath vehicle bays, AVRiL armory, and full road/air path lattice.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_onslaught_canyon_outpost(system_dir=system_dir),
                    "prompt": "Construct a massive Torlan-style Onslaught Desert Canyon world with Red and Blue PowerCores, Neutral PowerNodes, vehicle bays (Manta, Scorpion, Raptor, Goliath), AVRiL weapon stations, jump pads, and full bot pathing.",
                },
                {
                    "title": "❄️ Arctic Glacial Research Facility",
                    "desc": "6144x6144 sub-zero ice chasm with suspension bridge, Hellbender & Manta vehicle bays, East/West research complexes, defense towers, and power nodes.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_arctic_glacier_facility(system_dir=system_dir),
                    "prompt": "Construct an Arctic Glacial Research Facility outdoor world with frozen ravine, suspension bridge, Hellbender & Manta vehicle bays, research domes, and defense towers.",
                },
                {
                    "title": "🪐 Orbital Asteroid Mining Station",
                    "desc": "5120x5120 low-gravity asteroid crater with industrial mining gantry, Redeemer apex, high-velocity jump pads, space skybox, and reduced gravity.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_orbital_asteroid_mining(system_dir=system_dir),
                    "prompt": "Construct an Orbital Asteroid Mining Station with low-gravity crater, mining crane gantry, Redeemer apex, high-velocity jump pads, and deep space starfield.",
                },
                {
                    "title": "🌋 Volcanic Magma Foundry (Abaddon)",
                    "desc": "4096x4096 industrial smelting complex over molten magma with suspended steel catwalks, extreme heat lighting, hazard zones, and UDamage.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_volcanic_magma_foundry(system_dir=system_dir),
                    "prompt": "Construct a Volcanic Magma Foundry level with molten lava excavations, suspended metal platforms, extreme heat pulsating lighting, and high-tier weapons.",
                },
                {
                    "title": "🏛️ Ancient Egyptian Temple (Anubis)",
                    "desc": "4096x4096 sandstone temple with grand hypostyle colonnade, golden sacrificial altar, UDamage apex, and underground crypt.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_anubis_egyptian_temple(system_dir=system_dir),
                    "prompt": "Construct an ancient Egyptian Sandstone Temple world with grand hypostyle hall, massive stone pillars, gold altar with UDamage, and torch lighting.",
                },
            ],
        },

        # ---------------------------------------------------------------------
        # 2. EXTERIOR STRUCTURES & OUTPOSTS
        # ---------------------------------------------------------------------
        {
            "category": "🏰 EXTERIOR STRUCTURES & OUTPOSTS",
            "items": [
                {
                    "title": "🛡️ Fortified Forward Base (FOB)",
                    "desc": "4096x4096 fortified bunker outpost with perimeter defense walls, command post, vehicle repair dock, sniper mast, and Scorpion buggy.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_fortified_forward_base(system_dir=system_dir),
                    "prompt": "Construct a Fortified Forward Operating Base with perimeter barrier walls, command bunker, vehicle repair dock, sniper mast, and Scorpion buggy.",
                },
                {
                    "title": "🚜 Heavy Vehicle Dropzone & Pad",
                    "desc": "Spawns heavy vehicle staging pad with Goliath Tank Factory, Manta Factory, and AVRiL weapon locker.",
                    "commands": [
                        "ACTOR ADD CLASS=Onslaught.ONSTankFactory",
                        "ACTOR ADD CLASS=Onslaught.ONSHoverCraftFactory",
                        "ACTOR ADD CLASS=Onslaught.ONSAVRiLPickup",
                        "FLUSH",
                    ],
                    "prompt": "Construct a heavy vehicle staging area with Goliath Battle Tank Factory, Manta Factory, and AVRiL weapon station.",
                },
                {
                    "title": "📡 Deep Space Radar Relay Tower",
                    "desc": "Spawns communications tower with high-elevation sniper aerie, Lightning Gun, and searchlight.",
                    "commands": [
                        "ACTOR ADD CLASS=XWeapons.SniperRiflePickup",
                        "ACTOR ADD CLASS=Engine.Light",
                        "ACTOR ADD CLASS=Engine.PathNode",
                        "FLUSH",
                    ],
                    "prompt": "Construct a deep space radar relay mast with sniper aerie, Lightning Gun, and spotlight.",
                },
            ],
        },

        # ---------------------------------------------------------------------
        # 3. INTERIOR COMPLEXES & ARENAS
        # ---------------------------------------------------------------------
        {
            "category": "🏛️ INTERIOR COMPLEXES & ARENAS",
            "items": [
                {
                    "title": "🏟️ Grand Colosseum Tournament Arena",
                    "desc": "3072x3072 multi-level gladiatorial deathmatch arena with center UDamage dais, 4 weapon alcoves, 4 xJumpPads, and 8 PlayerStarts.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_tournament_colosseum(system_dir=system_dir),
                    "prompt": "Construct a premier UT2004 Tournament Colosseum Deathmatch arena with Shock Rifle, Flak Cannon, Body Armor, jump pads, and full Botpack pathing.",
                },
                {
                    "title": "⚛️ Sub-Level Reactor Core Chamber",
                    "desc": "3072x3072 high-tech nuclear reactor chamber with magnetic containment rings, coolant pipes, hazard walkways, and pulsing plasma light.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_reactor_core_chamber(system_dir=system_dir),
                    "prompt": "Construct a high-tech Nuclear Reactor Core Chamber with central reactor core, magnetic containment rings, coolant pipes, and hazard walkways.",
                },
                {
                    "title": "☣️ Bio-Hazard Containment Laboratory",
                    "desc": "3072x3072 quarantine laboratory with specimen containment vats, decontamination airlocks, Bio Rifle arsenal, and amber alert strobes.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_biohazard_quarantine_lab(system_dir=system_dir),
                    "prompt": "Construct a Bio-Hazard Containment & Quarantine Laboratory with specimen vats, decontamination airlocks, and Bio Rifle stations.",
                },
            ],
        },

        # ---------------------------------------------------------------------
        # 4. VEHICLES & COMBAT CAVALRY (ONSLAUGHT & ASSAULT)
        # ---------------------------------------------------------------------
        {
            "category": "🚜 VEHICLES & HEAVY CAVALRY (ONS & AS)",
            "items": [
                {
                    "title": "🏍️ ONSHoverCraftFactory (Manta)",
                    "desc": "Spawns Onslaught.ONSHoverCraftFactory vehicle spawner with agile Manta hovercraft.",
                    "commands": ["ACTOR ADD CLASS=Onslaught.ONSHoverCraftFactory", "FLUSH"],
                    "prompt": "Spawn an Onslaught.ONSHoverCraftFactory Manta spawner here.",
                },
                {
                    "title": "🚙 ONSRVFactory (Scorpion)",
                    "desc": "Spawns Onslaught.ONSRVFactory vehicle spawner with light attack Scorpion buggy.",
                    "commands": ["ACTOR ADD CLASS=Onslaught.ONSRVFactory", "FLUSH"],
                    "prompt": "Spawn an Onslaught.ONSRVFactory Scorpion buggy spawner here.",
                },
                {
                    "title": "✈️ ONSAttackCraftFactory (Raptor)",
                    "desc": "Spawns Onslaught.ONSAttackCraftFactory vehicle spawner with Raptor aerial VTOL fighter.",
                    "commands": ["ACTOR ADD CLASS=Onslaught.ONSAttackCraftFactory", "FLUSH"],
                    "prompt": "Spawn an Onslaught.ONSAttackCraftFactory Raptor VTOL aircraft spawner here.",
                },
                {
                    "title": "🚜 ONSTankFactory (Goliath)",
                    "desc": "Spawns Onslaught.ONSTankFactory vehicle spawner with Goliath heavy battle tank.",
                    "commands": ["ACTOR ADD CLASS=Onslaught.ONSTankFactory", "FLUSH"],
                    "prompt": "Spawn an Onslaught.ONSTankFactory Goliath battle tank spawner here.",
                },
                {
                    "title": "🚛 ONSPRVFactory (Hellbender)",
                    "desc": "Spawns Onslaught.ONSPRVFactory vehicle spawner with Hellbender 3-person combat rover.",
                    "commands": ["ACTOR ADD CLASS=Onslaught.ONSPRVFactory", "FLUSH"],
                    "prompt": "Spawn an Onslaught.ONSPRVFactory Hellbender 3-person combat rover spawner here.",
                },
                {
                    "title": "🛸 ONSBomberFactory (Cicada)",
                    "desc": "Spawns OnslaughtFull.ONSBomberFactory vehicle spawner with Cicada dual-pilot VTOL gunship.",
                    "commands": ["ACTOR ADD CLASS=OnslaughtFull.ONSBomberFactory", "FLUSH"],
                    "prompt": "Spawn an OnslaughtFull.ONSBomberFactory Cicada rocket gunship spawner here.",
                },
                {
                    "title": "🛞 ONSShockTankFactory (Paladin)",
                    "desc": "Spawns OnslaughtBP.ONSShockTankFactory vehicle spawner with Paladin directional plasma shield vehicle.",
                    "commands": ["ACTOR ADD CLASS=OnslaughtBP.ONSShockTankFactory", "FLUSH"],
                    "prompt": "Spawn an OnslaughtBP.ONSShockTankFactory Paladin vehicle spawner here.",
                },
                {
                    "title": "🤖 ONSMASFactory (Leviathan)",
                    "desc": "Spawns OnslaughtFull.ONSMASFactory vehicle spawner with Leviathan colossal 5-man mobile super fortress.",
                    "commands": ["ACTOR ADD CLASS=OnslaughtFull.ONSMASFactory", "FLUSH"],
                    "prompt": "Spawn an OnslaughtFull.ONSMASFactory Leviathan super fortress vehicle spawner here.",
                },
            ],
        },

        # ---------------------------------------------------------------------
        # 5. ONSLAUGHT & ASSAULT OBJECTIVES
        # ---------------------------------------------------------------------
        {
            "category": "⚡ ONSLAUGHT & ASSAULT OBJECTIVES",
            "items": [
                {
                    "title": "🔴 ONSPowerCore (Red Base)",
                    "desc": "Spawns Onslaught.ONSPowerCore with Red Team defense ownership (TeamIndex=0).",
                    "commands": ["ACTOR ADD CLASS=Onslaught.ONSPowerCore DefenderTeamIndex=0", "FLUSH"],
                    "prompt": "Place a Red Team ONSPowerCore master base core here.",
                },
                {
                    "title": "🔵 ONSPowerCore (Blue Base)",
                    "desc": "Spawns Onslaught.ONSPowerCore with Blue Team defense ownership (TeamIndex=1).",
                    "commands": ["ACTOR ADD CLASS=Onslaught.ONSPowerCore DefenderTeamIndex=1", "FLUSH"],
                    "prompt": "Place a Blue Team ONSPowerCore master base core here.",
                },
                {
                    "title": "🔷 ONSPowerNodeNeutral (Neutral)",
                    "desc": "Spawns Onslaught.ONSPowerNodeNeutral capturable tactical network link hub.",
                    "commands": ["ACTOR ADD CLASS=Onslaught.ONSPowerNodeNeutral", "FLUSH"],
                    "prompt": "Place an Onslaught.ONSPowerNodeNeutral capturable network link node here.",
                },
                {
                    "title": "🎯 Assault Objective (Destroyable)",
                    "desc": "Spawns UT2k4Assault.ASTurret or destroyable goal objective for Assault scenarios.",
                    "commands": ["ACTOR ADD CLASS=UT2k4Assault.ASTurret", "FLUSH"],
                    "prompt": "Place an Assault defensive turret objective here.",
                },
            ],
        },

        # ---------------------------------------------------------------------
        # 6. WEAPONS & COMBAT ARSENAL
        # ---------------------------------------------------------------------
        {
            "category": "🔫 UT2004 WEAPONS & ARSENAL",
            "items": [
                {
                    "title": "⚡ Shock Rifle Pickup",
                    "desc": "Spawns XWeapons.ShockRiflePickup (photon beam + plasma ball combo).",
                    "commands": ["ACTOR ADD CLASS=XWeapons.ShockRiflePickup", "FLUSH"],
                    "prompt": "Place an XWeapons.ShockRiflePickup at the current location.",
                },
                {
                    "title": "💥 Flak Cannon Pickup",
                    "desc": "Spawns XWeapons.FlakCannonPickup (shrapnel spread & bouncy explosive shell).",
                    "commands": ["ACTOR ADD CLASS=XWeapons.FlakCannonPickup", "FLUSH"],
                    "prompt": "Place an XWeapons.FlakCannonPickup at the current location.",
                },
                {
                    "title": "🚀 Rocket Launcher Pickup",
                    "desc": "Spawns XWeapons.RocketLauncherPickup (triple spiral/grenade volley).",
                    "commands": ["ACTOR ADD CLASS=XWeapons.RocketLauncherPickup", "FLUSH"],
                    "prompt": "Place an XWeapons.RocketLauncherPickup at the current location.",
                },
                {
                    "title": "🎯 Lightning Gun Pickup",
                    "desc": "Spawns XWeapons.SniperRiflePickup (high-voltage sniper headshot).",
                    "commands": ["ACTOR ADD CLASS=XWeapons.SniperRiflePickup", "FLUSH"],
                    "prompt": "Place an XWeapons.SniperRiflePickup (Lightning Gun) at the current location.",
                },
                {
                    "title": "🌪️ Minigun Pickup",
                    "desc": "Spawns XWeapons.MinigunPickup (rapid rotary bullet stream).",
                    "commands": ["ACTOR ADD CLASS=XWeapons.MinigunPickup", "FLUSH"],
                    "prompt": "Place an XWeapons.MinigunPickup at the current location.",
                },
                {
                    "title": "💚 Link Gun Pickup",
                    "desc": "Spawns XWeapons.LinkGunPickup (plasma bolts & vehicle repair/boost beam).",
                    "commands": ["ACTOR ADD CLASS=XWeapons.LinkGunPickup", "FLUSH"],
                    "prompt": "Place an XWeapons.LinkGunPickup at the current location.",
                },
                {
                    "title": "🧪 Bio Rifle Pickup",
                    "desc": "Spawns XWeapons.BioRiflePickup (toxic GES sludge shooter).",
                    "commands": ["ACTOR ADD CLASS=XWeapons.BioRiflePickup", "FLUSH"],
                    "prompt": "Place an XWeapons.BioRiflePickup at the current location.",
                },
                {
                    "title": "🎯 ONSAVRiLPickup (Anti-Vehicle Rocket)",
                    "desc": "Spawns Onslaught.ONSAVRiLPickup laser-guided anti-vehicle rocket launcher.",
                    "commands": ["ACTOR ADD CLASS=Onslaught.ONSAVRiLPickup", "FLUSH"],
                    "prompt": "Place an Onslaught.ONSAVRiLPickup Anti-Vehicle Rocket Launcher at the current location.",
                },
                {
                    "title": "☢️ Redeemer Pickup",
                    "desc": "Spawns XWeapons.RedeemerPickup (fly-by-wire thermonuclear missile).",
                    "commands": ["ACTOR ADD CLASS=XWeapons.RedeemerPickup", "FLUSH"],
                    "prompt": "Place an XWeapons.RedeemerPickup thermonuclear super weapon at the current location.",
                },
            ],
        },

        # ---------------------------------------------------------------------
        # 7. POWERUPS, HEALTH & ADRENALINE
        # ---------------------------------------------------------------------
        {
            "category": "🛡️ POWERUPS, HEALTH & ADRENALINE",
            "items": [
                {
                    "title": "🛡️ Super Shield Pack (+100 Armor)",
                    "desc": "Spawns XPickups.SuperShieldPack heavy armor protection.",
                    "commands": ["ACTOR ADD CLASS=XPickups.SuperShieldPack", "FLUSH"],
                    "prompt": "Place an XPickups.SuperShieldPack (+100 Armor) here.",
                },
                {
                    "title": "🦺 Shield Pack (+50 Armor)",
                    "desc": "Spawns XPickups.ShieldPack medium armor protection.",
                    "commands": ["ACTOR ADD CLASS=XPickups.ShieldPack", "FLUSH"],
                    "prompt": "Place an XPickups.ShieldPack (+50 Armor) here.",
                },
                {
                    "title": "🧪 Super Health Pack (+100 HP)",
                    "desc": "Spawns XPickups.SuperHealthPack (Keg of Health).",
                    "commands": ["ACTOR ADD CLASS=XPickups.SuperHealthPack", "FLUSH"],
                    "prompt": "Place an XPickups.SuperHealthPack (+100 HP) here.",
                },
                {
                    "title": "💊 Health Pack (+25 HP)",
                    "desc": "Spawns XPickups.HealthPack medical kit.",
                    "commands": ["ACTOR ADD CLASS=XPickups.HealthPack", "FLUSH"],
                    "prompt": "Place an XPickups.HealthPack (+25 HP) here.",
                },
                {
                    "title": "🟣 Damage Amplifier (UDamage)",
                    "desc": "Spawns XPickups.UDamagePack 2x lethal damage amplifier.",
                    "commands": ["ACTOR ADD CLASS=XPickups.UDamagePack", "FLUSH"],
                    "prompt": "Place an XPickups.UDamagePack amplifier here.",
                },
                {
                    "title": "⚡ Adrenaline Pill (+3 Adrenaline)",
                    "desc": "Spawns XPickups.AdrenalinePickup for combo powers (Speed, Booster, Berserk, Invisible).",
                    "commands": ["ACTOR ADD CLASS=XPickups.AdrenalinePickup", "FLUSH"],
                    "prompt": "Place an XPickups.AdrenalinePickup pill here.",
                },
            ],
        },

        # ---------------------------------------------------------------------
        # 8. THINGS, MOVERS, EMITTERS & INTERACTIVES
        # ---------------------------------------------------------------------
        {
            "category": "🌀 THINGS, MOVERS & EMITTERS",
            "items": [
                {
                    "title": "🌀 xJumpPad (High-Velocity)",
                    "desc": "Spawns XGame.xJumpPad ballistic trajectory launch pad.",
                    "commands": ["ACTOR ADD CLASS=XGame.xJumpPad", "FLUSH"],
                    "prompt": "Place an XGame.xJumpPad launch pad here.",
                },
                {
                    "title": "💡 Sunlight / Sky Atmosphere",
                    "desc": "Spawns Engine.Sunlight for realistic directional sky illumination.",
                    "commands": ["ACTOR ADD CLASS=Engine.Sunlight", "FLUSH"],
                    "prompt": "Place an Engine.Sunlight actor for outdoor illumination.",
                },
                {
                    "title": "🚨 Emergency Strobe Light",
                    "desc": "Spawns Engine.Light configured for pulsating red emergency warning.",
                    "commands": ["ACTOR ADD CLASS=Engine.Light LightBrightness=250 LightHue=0 LightSaturation=250 LightType=LT_Strobe", "FLUSH"],
                    "prompt": "Place an emergency red strobe warning light here.",
                },
                {
                    "title": "🌌 SkyZoneInfo (Skybox Anchor)",
                    "desc": "Spawns Engine.SkyZoneInfo for 3D parallax skybox background projection.",
                    "commands": ["ACTOR ADD CLASS=Engine.SkyZoneInfo", "FLUSH"],
                    "prompt": "Place an Engine.SkyZoneInfo skybox anchor actor.",
                },
                {
                    "title": "💧 Water / Slime ZoneInfo",
                    "desc": "Spawns Engine.ZoneInfo configured for fluid buoyant physics.",
                    "commands": ["ACTOR ADD CLASS=Engine.ZoneInfo", "FLUSH"],
                    "prompt": "Place an Engine.ZoneInfo fluid physics volume.",
                },
            ],
        },

        # ---------------------------------------------------------------------
        # 9. PEOPLE, BOTS & CREATURES (SKAARJPACK / INVASION)
        # ---------------------------------------------------------------------
        {
            "category": "👾 PEOPLE, BOTS & CREATURES",
            "items": [
                {
                    "title": "🚩 PlayerStart (Tournament)",
                    "desc": "Spawns Engine.PlayerStart for Deathmatch or Team spawning.",
                    "commands": ["ACTOR ADD CLASS=Engine.PlayerStart", "FLUSH"],
                    "prompt": "Place an Engine.PlayerStart spawn point here.",
                },
                {
                    "title": "👾 Skaarj Warrior",
                    "desc": "Spawns SkaarjPack.Skaarj deadly clawed alien warrior with projectile dodges.",
                    "commands": ["ACTOR ADD CLASS=SkaarjPack.Skaarj", "FLUSH"],
                    "prompt": "Spawn a SkaarjPack.Skaarj alien warrior here.",
                },
                {
                    "title": "👹 Warlord Boss",
                    "desc": "Spawns SkaarjPack.WarLord flying winged boss with homing rocket launcher.",
                    "commands": ["ACTOR ADD CLASS=SkaarjPack.WarLord", "FLUSH"],
                    "prompt": "Spawn a SkaarjPack.WarLord flying boss creature here.",
                },
                {
                    "title": "🦣 Titan Giant",
                    "desc": "Spawns SkaarjPack.Titan colossal boulder-throwing prehistoric behemoth.",
                    "commands": ["ACTOR ADD CLASS=SkaarjPack.Titan", "FLUSH"],
                    "prompt": "Spawn a SkaarjPack.Titan boulder-throwing giant here.",
                },
                {
                    "title": "🦎 Krall Warrior",
                    "desc": "Spawns SkaarjPack.Krall staff-wielding alien shock trooper.",
                    "commands": ["ACTOR ADD CLASS=SkaarjPack.Krall", "FLUSH"],
                    "prompt": "Spawn a SkaarjPack.Krall alien guard here.",
                },
                {
                    "title": "🦍 Brute Behemoth",
                    "desc": "Spawns SkaarjPack.Brute heavy armor-plated alien with arm rocket launchers.",
                    "commands": ["ACTOR ADD CLASS=SkaarjPack.Brute", "FLUSH"],
                    "prompt": "Spawn a SkaarjPack.Brute heavy guard here.",
                },
                {
                    "title": "🕷️ Skaarj Pupae",
                    "desc": "Spawns SkaarjPack.Pupae fast-swarming arachnid predator.",
                    "commands": ["ACTOR ADD CLASS=SkaarjPack.Pupae", "FLUSH"],
                    "prompt": "Spawn a SkaarjPack.Pupae insect swarm creature here.",
                },
                {
                    "title": "🦇 Razorfly",
                    "desc": "Spawns SkaarjPack.Fly buzzing aerial stinger pest.",
                    "commands": ["ACTOR ADD CLASS=SkaarjPack.Fly", "FLUSH"],
                    "prompt": "Spawn a SkaarjPack.Fly razorfly creature here.",
                },
                {
                    "title": "🛡️ Invasion Monster Wave Spawner",
                    "desc": "Constructs a complete multi-tier survival arena with Skaarj, Krall, Titan, and Warlord encounters.",
                    "commands_factory": lambda: FormulaEngine.generate_ut2004_invasion_monster_arena(system_dir=system_dir),
                    "prompt": "Construct an Invasion Survival Arena with full SkaarjPack creature spawners, weapon lockers, and adrenaline stations.",
                },
            ],
        },

        # ---------------------------------------------------------------------
        # 10. BOT NAVIGATION & AI PATHING
        # ---------------------------------------------------------------------
        {
            "category": "🧭 BOT NAVIGATION & VEHICLE PATHING",
            "items": [
                {
                    "title": "🌐 PathNode (Infantry)",
                    "desc": "Spawns Engine.PathNode standard AI bot navigation point.",
                    "commands": ["ACTOR ADD CLASS=Engine.PathNode", "PATHS BUILD", "FLUSH"],
                    "prompt": "Place an Engine.PathNode navigation node here.",
                },
                {
                    "title": "🚗 RoadPathNode (Vehicles)",
                    "desc": "Spawns Engine.RoadPathNode high-radius road navigation node for tanks and buggies.",
                    "commands": ["ACTOR ADD CLASS=Engine.RoadPathNode", "PATHS BUILD", "FLUSH"],
                    "prompt": "Place an Engine.RoadPathNode vehicle road navigation node here.",
                },
                {
                    "title": "✈️ FlyingPathNode (Raptor / Cicada)",
                    "desc": "Spawns Engine.FlyingPathNode 3D aerial navigation node for aircraft.",
                    "commands": ["ACTOR ADD CLASS=Engine.FlyingPathNode", "PATHS BUILD", "FLUSH"],
                    "prompt": "Place an Engine.FlyingPathNode aerial navigation node here.",
                },
                {
                    "title": "🔄 Complete Level Rebuild & Path Compile",
                    "desc": "Executes full CSG BSP compilation, lighting calculation, and AI bot path network build.",
                    "commands": ["MAP REBUILD", "LIGHT APPLY", "PATHS BUILD", "FLUSH"],
                    "prompt": "Rebuild geometry, apply lighting, and build AI path network for this level.",
                },
            ],
        },
    ]
