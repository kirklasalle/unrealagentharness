# UnrealScript Extraction, Compilation & Total Conversion Guide
### Unreal Tournament 2004 (Unreal Engine 2.5)

---

## 1. UnrealScript Source Extraction (Decompilation)

UnrealScript code packages (`.u` files) contain compiled virtual machine bytecode. To inspect, extend, or study stock and mod classes, use the built-in `batchexport` commandlet in `UCC.exe`.

### 1.1 Using `UCC batchexport`
Navigate to the `System\` directory and execute:

```powershell
# Syntax:
# UCC.exe batchexport <PackageName.u> class uc <DestinationDirectory>

# Example 1: Extract GUI2K4 User Interface classes
cd G:\UnrealTournament2004\System
.\UCC.exe batchexport GUI2K4.u class uc ..\GUI2K4_Export

# Example 2: Extract XWeapons weapon & projectile classes
.\UCC.exe batchexport XWeapons.u class uc ..\XWeapons_Export

# Example 3: Extract Onslaught vehicle & node classes
.\UCC.exe batchexport Onslaught.u class uc ..\Onslaught_Export
```

### 1.2 Automated Batch Extraction Script
Run `Extract_All_Source.bat` from the repository root to decompile all stock packages into `UT2004_ExtractedSource\`:

```cmd
.\Extract_All_Source.bat
```

The script extracts all 34 core packages in strict dependency order:
`Core`, `Engine`, `Fire`, `Editor`, `UnrealEd`, `IpDrv`, `UWeb`, `GamePlay`, `UnrealGame`, `XGame_rc`, `XEffects`, `XWeapons_rc`, `XPickups_rc`, `XPickups`, `XGame`, `XWeapons`, `XInterface`, `XAdmin`, `XWebAdmin`, `Vehicles`, `BonusPack`, `SkaarjPack_rc`, `SkaarjPack`, `UTClassic`, `UT2k4Assault`, `Onslaught`, `GUI2K4`, `UT2k4AssaultFull`, `OnslaughtFull`, `xVoting`, `OnslaughtBP`, `StreamlineFX`, `UTV2004c`, `UTV2004s`, and `AssaultBP`.

---

## 2. The `UCC make` Compilation Pipeline

The UnrealScript compiler is built into `UCC.exe`. It compiles `.uc` source files from disk into binary `.u` packages in `System\`.

```
                              COMPILATION STEPS
                              
   Step 1: Check System\<Package>.u
           ├──► File exists? ────► Skip compilation (Up-to-date)
           └──► File deleted? ───► Proceed to Step 2
                     │
                     ▼
   Step 2: Read Classes in <RootDir>\<Package>\Classes\*.uc
                     │
                     ▼
   Step 3: Two-Pass Compiler (Pass 1: Structs/Enums/Headers; Pass 2: Bytecode)
                     │
                     ▼
   Step 4: Emit System\<Package>.u
                     │
                     ▼
   Step 5: Run 'UCC.exe dumpint <Package>.u' to export localization (.int)
```

### 2.1 The Critical Rule of `EditPackages`
In `UT2004.ini` (or your mod's `.ini`), packages listed under `[Editor.EditorEngine]` are compiled sequentially from top to bottom. A package can **only reference classes from packages declared above it**.

Always place custom Total Conversion packages at the bottom of the list:

```ini
[Editor.EditorEngine]
EditPackages=Core
EditPackages=Engine
EditPackages=Fire
EditPackages=Editor
EditPackages=UnrealEd
EditPackages=IpDrv
EditPackages=UWeb
EditPackages=GamePlay
EditPackages=UnrealGame
EditPackages=XGame_rc
EditPackages=XEffects
EditPackages=XWeapons_rc
EditPackages=XPickups_rc
EditPackages=XPickups
EditPackages=XGame
EditPackages=XWeapons
EditPackages=XInterface
EditPackages=XAdmin
EditPackages=XWebAdmin
EditPackages=Vehicles
EditPackages=BonusPack
EditPackages=SkaarjPack_rc
EditPackages=SkaarjPack
EditPackages=UTClassic
EditPackages=UT2k4Assault
EditPackages=Onslaught
EditPackages=GUI2K4
EditPackages=UT2k4AssaultFull
EditPackages=OnslaughtFull
EditPackages=xVoting
EditPackages=OnslaughtBP
EditPackages=StreamlineFX
EditPackages=UTV2004c
EditPackages=UTV2004s
EditPackages=AssaultBP

; Custom Mod Packages
EditPackages=UTron2004
```

### 2.2 Clean Rebuild Command Line
Because `UCC make` will skip any package whose `.u` file exists, your build script must delete the existing `.u` before invoking the compiler:

```bat
@echo off
cd /d "%~dp0System"
if exist UTron2004.u del UTron2004.u
if exist UTron2004.ucl del UTron2004.ucl
UCC.exe make
UCC.exe dumpint UTron2004.u
```

---

## 3. Total Conversion Architecture (`UTron2004`)

A Total Conversion (TC) completely replaces the gameplay, HUD, menus, characters, and weapons while maintaining engine stability.

### 3.1 Directory Organization
```
G:\UnrealTournament2004\
├── UTron2004\
│   ├── Classes\               <-- .uc source files
│   ├── Maps\                  <-- .ut2 maps
│   ├── Textures\              <-- .utx texture packages
│   ├── StaticMeshes\          <-- .usx geometry packages
│   ├── Animations\            <-- .ukx skeletal animation packages
│   ├── Sounds\                <-- .uax audio packages
│   └── Music\                 <-- .ogg music tracks
├── System\
│   ├── UTron2004.ini          <-- Dedicated engine config
│   ├── UTron2004User.ini      <-- Dedicated keybindings
│   └── UTron2004.u            <-- Compiled mod package
├── Build_UTron2004.bat        <-- Compiler wrapper
└── Launch_UTron2004.bat       <-- Total Conversion launcher
```

### 3.2 Key Classes for a Total Conversion

1. **`GameInfo` (`UTronArcadeClassic.uc` / `UTronDiscArena.uc`)**:
   ```unrealscript
   class UTronArcadeClassic extends DeathMatch;

   defaultproperties
   {
       DefaultPlayerClassName="UTron2004.UTronPawn"
       PlayerControllerClassName="UTron2004.UTronPlayerController"
       HUDType="UTron2004.UTronHUD"
       GameName="UTron 2004 Arcade"
       Description="Tron Arena Total Conversion Game Type."
   }
   ```

2. **`Pawn` / `xPawn` (`UTronPawn.uc` / `UTronLightCycle.uc`)**:
   Controls player mesh, collision cylinder, physics states (`PHYS_Walking`, `PHYS_Hovering`), health, and animations.

3. **`Weapon` & `WeaponFire` (`UTronIdentityDisc.uc`, `UTronIdentityDiscFire.uc`)**:
   Controls projectile launching, fire rates, muzzle effects, and damage types (`UTronDamTypeDisc.uc`).

4. **`HUD` (`UTronHUD.uc`)**:
   Renders custom 2D/3D Canvas elements:
   ```unrealscript
   function DrawHUD(Canvas C)
   {
       Super.DrawHUD(C);
       C.SetPos(32, C.ClipY - 64);
       C.SetDrawColor(0, 255, 255, 255); // Tron Cyan
       C.DrawText("UTRON 2004 SHIELD: " $ PawnOwner.Health);
   }
   ```

5. **`GUI2K4` Custom Main Menu (`UTronMainMenu.uc`)**:
   Extends `UT2K4GUIPage` to provide a dedicated fullscreen menu system with customized buttons, background imagery, and music playback.
