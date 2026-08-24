# UTron: Unreal Tournament 2004 (UE2.5) Porting & Compatibility Guide

**Source Engine:** Unreal Engine 1 (UT99 / UT GOTY - v436 / v469)  
**Target Engine:** Unreal Engine 2.5 (Unreal Tournament 2004 / v3369+)  
**Source Package:** `G:\utronarcadebeta1x\UTronArcadebeta1.umod`  
**Target Directory:** `G:\UnrealTournament2004`  
**Author:** Antigravity AI Engineering  
**Prepared For:** Kirk LaSalle  

---

## 1. Direct Compatibility Assessment

### Can `UTronArcadebeta1.umod` be installed directly into UT2004?
**No.** Directly running the UMOD installer or copying the `.u` / `.unr` files from UT99 into UT2004 will fail with package version mismatches and missing base classes.

### Technical Differences Between UT99 (UE1) and UT2004 (UE2.5)

| Subsystem | Unreal Tournament (UT99 / UE1) | Unreal Tournament 2004 (UT2004 / UE2.5) |
| :--- | :--- | :--- |
| **Engine Generation** | Unreal Engine 1 (Build 436 / 469) | Unreal Engine 2.5 (Build 3369) |
| **Package Format** | Version 68–69 | Version 118–128 |
| **Player Pawn Base** | `Botpack.TournamentPlayer` | `XGame.xPawn` |
| **Weapon Base** | `Botpack.TournamentWeapon` | `XWeapons.Weapon` / `Engine.Weapon` |
| **GameType Base** | `Botpack.TournamentGameInfo` / `DeathMatchPlus` | `Engine.GameInfo` / `XGame.xDeathMatch` |
| **Physics Engine** | Simple collision cylinder + trace physics | **Karma Physics Engine** (`KarmaData`) + Ragdolls |
| **Vehicles** | Custom pawn hacks / scripted morphs | **Native Vehicle Physics** (`ONSVehicle`, `KVehicle`) |
| **3D Models** | Vertex Animated Meshes (`.3d` / `_d.3d` / `_a.3d`) | **Static Meshes** (`.usx`) + **Skeletal Meshes** (`.ukx`) |
| **GUI Framework** | `UWindow` / `UMenu` / `UTMenu` | `GUIComponent` / `UT2K4GUIController` |
| **Audio Pipeline** | Galaxy / OpenAL (`.uax` PCM WAV + `.umx` Tracker) | DirectSound / OpenAL (`.uax` WAV + `.ogg` Vorbis + Tracker) |

---

## 2. Why UT2004 is the Ultimate Engine for a TRON Mod

While direct drop-in binary execution is not possible, **UT2004 is significantly more capable of realizing the full vision of UTron** than UT99 was:

1. **Native Vehicle Framework (Onslaught / SVehicles):**
   - In UT99, your Light Cycles and Recognizers had to be scripted using custom player pawn morphs (`cycleMorph.uc`, `RecoDrivable.uc`).
   - In UT2004, you have `ONSVehicle` and `KVehicle` with true multi-part chassis, angular velocity dampening, steering, headlights, and Karma collision volumes.
2. **Static Meshes & Lighting:**
   - UT2004 supports hardware-accelerated Static Meshes (`.usx`) with glowing materials, unlit shaders, and complex neon vector architecture without BSP geometry errors.
3. **Karma Ragdolls & Derez Physics:**
   - Defeated programs can fracture into glowing volumetric voxels or ragdoll before derezzing.
4. **Karma Physics Discs:**
   - Identity Discs can utilize Karma rigid body collision physics for ultra-realistic ricochets and trajectory deflection.

---

## 3. Step-by-Step Asset Migration & Porting Roadmap

### Phase 1: Audio Migration
- **Sound Effects (`.uax`):** Export all audio from `G:\UnrealTournament\UTronProject\Sounds\*.uax` to `.wav` using `UCC.exe batchexport` and import into UT2004 sound packages.
- **Voice Packs:** Re-map voice cues (MCP, Bit, Flynn, Sark, Tron) to UT2004's `TeamVoicePack` / `xVoicePack`.
- **Music:** Copy `1-Alive.umx` and `Anthem.umx` or convert tracker modules to `.ogg` and place in `G:\UnrealTournament2004\Music\`.

### Phase 2: Texture & Material Migration
- **Neon Textures:** Export `Tron2002.utx`, `UTron_Grids-Lines.utx`, `UTron_Floors-Walls.utx` to 32-bit TGA/BMP.
- **UT2004 Shaders:** Create UT2004 Shaders with `SelfIllumination` and `Combiner` materials to make the neon lines glow vividly in modern renderers.

### Phase 3: 3D Models & Meshes
- Convert vertex meshes (`_d.3d`, `_a.3d`) of the Identity Disc, Recognizer, and Light Cycle into 3D formats (OBJ / FBX / ASE) and import as UT2004 Static Meshes (`.usx`) and Skeletal Meshes (`.ukx`).

### Phase 4: UnrealScript Code Adaptation
- **Identity Disc:** Re-implement `IdentityDisc` extending `XWeapons.Weapon` and `WeaponFire`.
- **Light Cycle:** Create `UTronLightCycle` extending `ONSVehicle` with custom trail emitters generating deadly collision barriers.
- **Recognizer:** Create `UTronRecognizer` extending `ONSHoverCraft` or `ONSVehicle`.
- **Discs of Tron Gametype:** Create `UTronDiscArena` extending `xDeathMatch`.

---

## 4. Current Working Environment Recommendation

- **For Immediate Gameplay & Modding:** Continue using the fully functional, fixed installation in **`G:\UnrealTournament`** using **[`Launch_UTron.bat`](file:///g:/UnrealTournament/Launch_UTron.bat)**.
- **For Future Porting to UT2004:** Use the extracted source files in [`G:\UnrealTournament\UTronProject`](file:///g:/UnrealTournament/UTronProject) and the exported textures/sounds as the source asset library.
## 5. Dedicated 1980s Retro Terminal GUI & Total Conversion Setup

The UT2004 port of UTron features a dedicated custom GUI system mirroring the classic 1982 film's green-on-black phosphor terminal computers:

- **Custom Menu (`UTronMainMenu.uc`):** Retro CRT terminal header `>> ENCOM MAINFRAME OS [VERSION 4.1.82] -- MCP SECURITY ONLINE <<` with terminal command prompts in green text.
- **Background Music:** Plays the original UTron tracker soundtrack module (`1-Alive.umx`).
- **Dedicated Configuration:** `G:\UnrealTournament2004\System\UTron2004.ini` and `UTron2004User.ini`.
- **Launcher:** `G:\UnrealTournament2004\Launch_UTron2004.bat` launches UT2004 directly into the full UTron Total Conversion environment.
### 5.1 UTron Arcade Subsystem Structure

```
[ MAIN TERMINAL MENU ]
  ??? > 1. UTRON ARCADE ?????????????? [ UTRON ARCADE SUBSYSTEM ]
  ?                                      ??? > [ 1 ] DISCS OF UTRON (Platform Disc Combat)
  ?                                      ??? > [ 2 ] UTRON ARCADE CLASSIC (90? Light Cycles & Recognizers)
  ?                                      ??? > [ 3 ] RETURN TO SYSTEM ROOT
  ??? > 2. MULTIPLAYER NETWORK GRID
  ??? > 3. HOST MCP ARENA SERVER
  ??? > 4. CUSTOM MATCH CONFIG (INSTANT ACTION)
  ??? > 5. USER ARCHIVES & COMMUNITY
  ??? > 6. TERMINAL CONFIGURATION (SETTINGS)
  ??? > 7. DEREZ & TERMINATE PROGRAM (QUIT)
```
### 5.2 Registered UTron Gametypes in UT2004

The following gametypes are registered and selectable in Instant Action, Host Game, and Server Browser:

1. **UTron Arcade: Discs of UTron (`UTron2004.UTronDiscArena`)**:
   - Focuses on 1-on-1 and FFA platform disc combat.
   - Weapons: Ricocheting Identity Discs and deflector shields.
   - Kill Multipliers: DecapaTron headshots.

2. **UTron Arcade: Classic (`UTron2004.UTronArcadeClassic`)**:
   - 1982 Arcade Simulation.
   - Vehicles: 90-degree orthogonal Light Cycles and Recognizers.
   - Hazard: Continuous fatal light wall trails.
