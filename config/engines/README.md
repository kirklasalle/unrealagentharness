# Unreal Agent Harness (UAH) — Pluggable TOML Engine Profiles

This directory allows community modders, level designers, and studio engineers to add or customize Unreal Engine integration profiles without writing any Python code.

## Available Shipped Profiles:
- **`ue1_ut99.toml`**: Unreal Tournament 99 GOTY & OldUnreal 469e (supports classic Unreal 1 games including *Deus Ex*, *Rune*, *The Wheel of Time*, *Klingon Honor Guard*).
- **`ue2_ut2004.toml`**: Unreal Tournament 2004 & UE2.5 (supports *Postal 2*, *SWAT 4*, *Land of the Dead*, *Tom Clancy's Splinter Cell*).
- **`ue5_modern.toml`**: Unreal Engine 5.4 / 5.5 Next-Gen Editor Automation.

## How to Add a Custom Total Conversion / Game Engine Profile:
1. Copy one of the sample `.toml` files matching your game's engine generation.
2. Name your file `[game_id].toml` (e.g. `deusex.toml`, `postal2.toml`, `custom_ue5.toml`).
3. Fill in the paths, window classes, process names, actor signatures, and CSG grid metrics:
   ```toml
   [engine]
   id = "deusex"
   name = "Deus Ex (UE1)"
   generation = "UE1"
   icon = "🕶"

   [paths]
   default_root = "C:\\DeusEx"
   system_subpath = "System"
   editor_exe = "DeusExEd.exe"
   game_exe = "DeusEx.exe"
   ```
4. Launch Unreal Agent Harness: it will automatically discover your profile and expose it in the engine selector HUD!
