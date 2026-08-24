# Unreal Tournament: GOTY Edition & The UTron Project
## Master Documentation & Development Portal

**Game:** Unreal Tournament: Game of the Year Edition  
**Engine:** Unreal Engine 1 (v436 / OldUnreal v469 Maintenance Series)  
**Total Conversion Mod:** UTron (1999–2003) by Kirk LaSalle & Contributors  
**Root Workspace:** `G:\UnrealTournament`  

---

## 📚 Documentation Index

| Document | Description |
| :--- | :--- |
| **[01. Engine Architecture Audit](file:///g:/UnrealTournament/docs/01_UNREAL_ENGINE_ARCHITECTURE_AUDIT.md)** | In-depth technical breakdown of Unreal Engine 1, Object hierarchy, tick lifecycle, networking/replication, BSP geometry, rendering drivers, and audio subsystems. |
| **[02. UnrealScript Language Reference](file:///g:/UnrealTournament/docs/02_UNREALSCRIPT_LANGUAGE_REFERENCE.md)** | Complete syntax, state machine programming, latent execution, variable modifiers, networking blocks, built-in iterators, and defaultproperties guide. |
| **[03. Extraction & Compilation Guide](file:///g:/UnrealTournament/docs/03_EXTRACTION_AND_COMPILATION_GUIDE.md)** | How to decompile `.u` packages into `.uc` source trees using `ucc batchexport`, how `ucc make` compiles packages, dependency ordering, and automated tooling. |
| **[04. UTron Project Audit & Dev Guide](file:///g:/UnrealTournament/docs/04_UTRON_PROJECT_AUDIT_AND_DEV_GUIDE.md)** | Complete analysis of the UTron total conversion mod (Discs of Tron, Light Cycles, Recognizers, Tanks, Diffuser Tiles), maps, textures, sounds, and the fix for the launcher entry point error. |
| **[05. Tools & Dev Environment Index](file:///g:/UnrealTournament/docs/05_DEVELOPMENT_ENVIRONMENT_AND_TOOLS_INDEX.md)** | Master list of development tools, UCC commandlets, VS Code setup, WOTgreal, UTPT, UModel, and community links. |
| **[06. UT2004 Porting & Compatibility Guide](file:///g:/UnrealTournament/docs/06_UTRON_UT2004_PORTING_AND_COMPATIBILITY_GUIDE.md)** | Technical breakdown of porting UTron from UT99 (UE1) to UT2004 (UE2.5), asset migration, vehicle physics, shaders, and Karma mechanics. |

---

## ⚡ Quick-Start Automation Scripts

In the root directory `G:\UnrealTournament\`, you will find one-click scripts for your workflow:

1. **[Launch_UTron.bat](file:///g:/UnrealTournament/Launch_UTron.bat)**: Launches the UTron total conversion mod directly on the modern OldUnreal engine.
2. **[Launch_UTron_Editor.bat](file:///g:/UnrealTournament/Launch_UTron_Editor.bat)**: Launches UnrealEd pre-configured for UTron level design and asset editing.
3. **[Build_UTron.bat](file:///g:/UnrealTournament/Build_UTron.bat)**: Recompiles all modified UTron UnrealScript classes into `.u` binary packages using `ucc make`.
4. **[Extract_All_Scripts.bat](file:///g:/UnrealTournament/Extract_All_Scripts.bat)**: Automatically extracts all 1,967+ UnrealScript source files from base packages and UTron packages into clean folder trees.
