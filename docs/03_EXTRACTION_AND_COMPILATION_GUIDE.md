# UnrealScript Extraction & Compilation Complete Guide

**Location:** `G:\UnrealTournament\docs\03_EXTRACTION_AND_COMPILATION_GUIDE.md`  
**Applicable Engine:** Unreal Engine 1 (UT99 / UT GOTY / v436 & v469)  
**Author:** Antigravity AI Engineering  
**Prepared For:** Kirk LaSalle  

---

## 1. Introduction: The Two Essential Operations

In Unreal Engine 1, working with UnrealScript source code requires two foundational operations:
1. **Extraction (Decompilation/Unpacking):** Extracting bytecode and text buffers from binary `.u` packages into human-readable `.uc` classes in a directory tree.
2. **Compilation (Building):** Compiling `.uc` class files back into binary `.u` packages using the native Unreal Commandlet Compiler (`UCC.exe make`).

---

## 2. UnrealScript Extraction Methods

### Method 1: The Native UCC BatchExport Commandlet (Fastest & Most Accurate)

The Unreal Engine execution environment includes `UCC.exe` in `G:\UnrealTournament\System`.

#### Command Syntax:
```cmd
ucc batchexport <PackageName.u> class uc <DestinationDirectory>
```

#### Examples:
```cmd
cd G:\UnrealTournament\System
ucc batchexport Botpack.u class uc ..\Botpack\Classes
ucc batchexport UTron.u class uc ..\UTronProject\UTron\Classes
ucc batchexport UTronMenu.u class uc ..\UTronProject\UTronMenu\Classes
ucc batchexport UTronMedia.u class uc ..\UTronProject\UTronMedia\Classes
ucc batchexport UTronBrowser.u class uc ..\UTronProject\UTronBrowser\Classes
```

#### Exporting Other Asset Types via UCC:
`ucc batchexport` can also extract non-script assets from packages:
- **Textures:** `ucc batchexport Package.utx texture bmp ..\ExportedTextures`
- **Sounds:** `ucc batchexport Package.uax sound wav ..\ExportedSounds`
- **Music:** `ucc batchexport Package.umx music it ..\ExportedMusic` (or `s3m`, `xm`)
- **Maps / Geometry:** `ucc batchexport MapName.unr level t3d ..\ExportedMaps`

---

### Method 2: UnrealEd GUI Export

1. Launch Unreal Tournament Editor (`UnrealEd.exe` or `Launch_UTron_Editor.bat`).
2. In the right-hand panel, switch to the **Actor Class Browser**.
3. Click **File** -> **Export All Scripts**.
4. UnrealEd will unpack all loaded packages and write `.uc` files directly into each package's `Classes\` folder in the root directory.

---

### Method 3: Third-Party Modding Tools & Decompilers

If you prefer external GUI suites, the following established community tools are available:
- **WOTgreal:** Full-featured IDE designed for UnrealScript with syntax highlighting, IntelliSense, package browsing, and automated compilation integration.
- **UTPT (Unreal Tournament Package Tool):** In-depth binary package explorer capable of inspecting bytecodes, mesh headers, import/export tables, and raw assets.
- **UE Viewer (UModel by Gildor):** Modern tool for extracting skeletal meshes, textures, animations, and sounds from all Unreal Engine generations.
- **UnrealPackage (C# / CLI):** Modern open-source .NET package reader and decompiler.

---

## 3. How `UCC make` Compiles UnrealScript

### 3.1 The Compilation Process Explained

1. `UCC.exe make` looks at the active INI file (`UnrealTournament.ini`, `UTronProject.ini`, or `UTronEditor.ini`).
2. It navigates to the `[Editor.EditorEngine]` section and reads the `EditPackages=` entries sequentially.
3. **Crucial Rule:** If `<PackageName>.u` **already exists** in `System/`, `ucc make` **skips** it and loads it as a compiled dependency.
4. If `<PackageName>.u` **does NOT exist**, `ucc make` navigates to `<Root>\<PackageName>\Classes\*.uc`, parses all classes, verifies dependencies, resolves imports, compiles bytecode, and generates a fresh `<PackageName>.u` binary in `System/`.

### 3.2 Required Package Dependency Order for UTron

Unreal packages MUST be compiled strictly in dependency order:
```ini
[Editor.EditorEngine]
EditPackages=Core
EditPackages=Engine
EditPackages=Editor
EditPackages=UWindow
EditPackages=Fire
EditPackages=IpDrv
EditPackages=UWeb
EditPackages=UBrowser
EditPackages=UnrealShare
EditPackages=UnrealI
EditPackages=UMenu
EditPackages=IpServer
EditPackages=Botpack
EditPackages=UTServerAdmin
EditPackages=UTMenu
EditPackages=UTBrowser
; UTron Mod Packages:
EditPackages=UTronMedia
EditPackages=UTron
EditPackages=UTronMenu
EditPackages=UTronBrowser
```

### 3.3 Rebuilding a Package Step-by-Step

To rebuild `UTron.u` after modifying `UTron\Classes\*.uc`:
1. Delete (or backup) the old binary: `del G:\UnrealTournament\UTronProject\System\UTron.u` (and `del G:\UnrealTournament\System\UTron.u` if present).
2. Ensure the source folder exists at `G:\UnrealTournament\UTron\Classes` (or configured search path).
3. Run:
   ```cmd
   cd G:\UnrealTournament\System
   ucc make
   ```
4. `UCC` will detect that `UTron.u` is missing, compile `UTron\Classes\*.uc`, and output the new `UTron.u`.

---

## 4. Automated Extraction & Compilation Scripts Included

We have created one-click automated tools in your repository:

### 1. `G:\UnrealTournament\Extract_All_Scripts.bat`
Extracts all base engine packages and all UTron packages into their respective `Classes\` directories.

### 2. `G:\UnrealTournament\Build_UTron.bat`
Backs up old UTron packages, sets up compilation paths, and runs `ucc make` with clean logging.

### 3. `G:\UnrealTournament\Launch_UTron.bat`
Launches the UTron Total Conversion mod with custom INI and user configurations on the modern OldUnreal engine.

### 4. `G:\UnrealTournament\Launch_UTron_Editor.bat`
Launches UnrealEd configured with all UTron actor classes, texture palettes, and map packages ready for level design.
