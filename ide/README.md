# UnrealScript IDE Tools & WOTgreal Integration

This directory contains reference installers and guidelines for third-party UnrealScript Integrated Development Environments (IDEs) supported by the **Unreal Agent Harness (UAH)**.

---

## 🛠️ WOTgreal (Wormbo's UnrealScript IDE)

**WOTgreal** is the classic, premier IDE for UnrealScript development across Unreal Engine 1, 2, and 2.5 (Unreal Tournament 99, UT2003, UT2004, Deus Ex, Postal 2, and total conversions like UTron).

### Key Features:
- **IntelliSense & Syntax Highlighting**: Full parsing of `.uc` classes, states, replication blocks, and native functions.
- **Package Hierarchy Browser**: Live tree view of parent and child classes across all loaded packages.
- **One-Click UCC Compilation**: Integrates directly with `UCC.exe make` and output log parsing.

### Official Community Resources & Downloads:
- **Official Portal**: [BeyondUnreal Wiki - WOTgreal](https://wiki.beyondunreal.com/Legacy:WOTgreal)
- **OldUnreal Community**: [OldUnreal Forums & Modding](https://www.oldunreal.com)

---

## 🚀 Recommended Modern VS Code Setup

For modern multi-engine development, you can also use **Visual Studio Code** with the following community extensions:
1. **UnrealScript (by Eliot van Uytfanghe)**: Syntax highlighting and package indexing.
2. **UnrealScript Language Support**: Autocompletion and symbol definitions.
3. **UAH PowerShell Scripts**: Use `tools/Compile-UnrealScript.ps1` and `tools/Extract-UnrealScript.ps1` for automated background compilation and extraction.
