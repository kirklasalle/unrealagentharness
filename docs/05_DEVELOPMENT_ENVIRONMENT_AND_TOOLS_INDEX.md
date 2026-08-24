# Unreal Tournament & UTron: Development Environment & Tools Index

**Location:** `G:\UnrealTournament\docs\05_DEVELOPMENT_ENVIRONMENT_AND_TOOLS_INDEX.md`  
**Target:** Unreal Tournament Game of the Year Edition (v436 / OldUnreal v469)  

---

## 1. Master Toolset Overview

| Category | Tool | Location / Source | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **Compiler** | `UCC.exe make` | `G:\UnrealTournament\System\UCC.exe` | Native UnrealScript bytecode compiler |
| **Extractor** | `UCC.exe batchexport` | `G:\UnrealTournament\System\UCC.exe` | Extracts `.uc`, `.bmp`, `.wav`, `.it`, `.t3d` from packages |
| **Level Editor** | `UnrealEd.exe` | `G:\UnrealTournament\System\UnrealEd.exe` | Native CSG/BSP level designer, texture browser, actor inspector |
| **Automated Extractor** | `Extract_All_Scripts.bat` | `G:\UnrealTournament\Extract_All_Scripts.bat` | One-click extractor for all 1,967+ base and UTron classes |
| **Automated Builder** | `Build_UTron.bat` | `G:\UnrealTournament\Build_UTron.bat` | One-click recompiler for all UTron mod packages |
| **Mod Launcher** | `Launch_UTron.bat` | `G:\UnrealTournament\Launch_UTron.bat` | Launches UTron with custom INI & OldUnreal v469 runtime |
| **Editor Launcher** | `Launch_UTron_Editor.bat`| `G:\UnrealTournament\Launch_UTron_Editor.bat` | Launches UnrealEd preloaded with UTron assets |

---

## 2. Recommended Modern IDEs & Editors for UnrealScript

### Option 1: Visual Studio Code (Recommended Modern Workflow)
1. Install **Visual Studio Code**.
2. Open `G:\UnrealTournament` as the workspace root.
3. Install the **UnrealScript** extension (by *Eliot van Uytfanghe* or *dim-an*):
   - Syntax highlighting for `.uc` files.
   - Code folding, symbol indexing, and jump-to-definition across all extracted packages.
4. Set up a build task in `.vscode/tasks.json` pointing to `G:\UnrealTournament\Build_UTron.bat`.

### Option 2: WOTgreal (Classic Dedicated UnrealScript IDE)
- Historically the most popular UnrealScript IDE.
- Features: Class hierarchy tree, auto-complete, integrated `ucc make` compiler runner, INI configurator.

### Option 3: Notepad++
- Lightweight editor with user-defined UnrealScript language syntax highlighting (`UnrealScript.xml`).

---

## 3. Specialized Unreal Package & Asset Tools

1. **UE Viewer / UModel (by Konstantin Nosov / Gildor):**
   - Universal viewer and extractor for 3D meshes, textures, animations, and sound from all Unreal Engine versions.
   - URL: `https://www.gildor.org/en/projects/umodel`
2. **UTPT (Unreal Tournament Package Tool):**
   - In-depth reverse engineering and inspection tool for UE1 packages. Allows browsing raw bytecode, name tables, export objects, and texture mipmaps.
3. **OpenAL Soft Configuration Tool (`alsoft-config`):**
   - High-fidelity 3D binaural HRTF spatial audio configuration for OldUnreal `ALAudio.dll`.
4. **OldUnreal Community & Documentation Wiki:**
   - Central repository for Unreal Tournament v469 documentation, native patches, and Linux/Mac/Windows binaries:
   - URL: `https://www.oldunreal.com` and `https://ut99.org`

---

## 4. Useful UCC Commandlets Reference

| Commandlet | Syntax | Description |
| :--- | :--- | :--- |
| `make` | `ucc make [-option...]` | Compiles source `.uc` files into `.u` binaries. |
| `batchexport` | `ucc batchexport <pkg.ext> <class> <ext> <path>` | Bulk exports objects from packages. |
| `dumpint` | `ucc DumpInt <pkg.u>` | Generates/synchronizes `.int` localization files. |
| `compress` | `ucc compress <file.unr>` | Compresses files into `.uz` for HTTP server redirect downloading. |
| `decompress` | `ucc decompress <file.uz>` | Decompresses `.uz` packages back to `.unr`/`.utx`/`.u`. |
| `master` | `ucc master <master.ini>` | Builds `.umod` master installer packages. |
| `updateumod` | `ucc updateumod <file.umod>` | Inspects and extracts contents of `.umod` files. |
| `server` | `ucc server <map.unr>?game=<game> -ini=<ini>` | Launches a headless dedicated multiplayer server. |
