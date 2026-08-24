# UnrealScript Development & Compilation Master Guide
### Complete Technical Reference: Writing, Debugging, and Compiling UnrealScript in UnrealEd / UE1 (469e)

**Author:** Kirk LaSalle & Antigravity AI Architect  
**Engine Version:** Unreal Engine 1 (UT99 GOTY / OldUnreal 469e)  
**Target Mod:** UTron Total Conversion & Custom Mods  
**Workspace:** `G:\UnrealTournament`

---

## 🛠️ 1. UnrealScript Directory & Package Architecture

To write and compile UnrealScript packages in Unreal Engine 1:

```
 G:\UnrealTournament\
 ├── System\
 │   ├── ucc.exe                    # The Commandlet Compiler
 │   ├── UnrealTournament.ini       # Package registration (EditPackages)
 │   └── MyPackage.u                # Compiled binary package
 └── MyPackage\
     ├── Classes\
     │   ├── MyPawn.uc              # UnrealScript source files
     │   ├── MyWeapon.uc
     │   └── MyMutator.uc
     ├── Models\                    # Optional 3D vertex mesh definitions
     └── Textures\                  # Optional source graphic textures
```

---

## ⚙️ 2. Package Registration (`UnrealTournament.ini`)

To enable UnrealEd and the `ucc make` compiler to recognize a package, it must be listed under `[Editor.EditorEngine]` in `System/UnrealTournament.ini`:

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
EditPackages=Botpack
EditPackages=UTron
EditPackages=UTronMedia
EditPackages=UTronMenu
EditPackages=UTronBrowser
```

> [!IMPORTANT]
> **Compilation Order**: Packages are compiled strictly in the order they appear in `EditPackages`. If `PackageB` references classes in `PackageA`, `PackageA` must appear before `PackageB`.

---

## 🔨 3. Compiling with `ucc make`

To compile modified or newly written `.uc` source files:

1.  **Delete the old binary package** in `G:\UnrealTournament\System\` (e.g. `del System\MyPackage.u`). `ucc make` will only compile packages whose `.u` file is missing.
2.  **Execute the compiler commandlet**:
    ```powershell
    cd G:\UnrealTournament\System
    .\ucc.exe make
    ```
3.  **Commandlet Flags**:
    *   `ucc.exe make -nobind`: Skips native C++ binding generation.
    *   `ucc.exe make -silent`: Suppresses interactive prompts.

---

## 📝 4. UnrealScript Syntax & Core Class Hierarchy

### 4.1 Class Declaration
```unrealscript
class MyLaserGun extends TournamentWeapon;

#exec TEXTURE IMPORT NAME=LaserTex FILE=Textures\Laser.pcx GROUP=Skins
#exec AUDIO IMPORT FILE=Sounds\LaserFire.wav NAME=LaserFire GROUP=Weapons

var() int BeamIntensity;
var() color BeamColor;

function Fire(float Value)
{
    if (AmmoType.UseAmmo(1))
    {
        PlaySound(Sound'LaserFire', SLOT_Misc, 2.0);
        TraceFire(Value);
    }
}

defaultproperties
{
    BeamIntensity=100
    ItemName="Precision Laser Rifle"
    PickupMessage="You got the Precision Laser Rifle."
    PlayerViewOffset=(X=30.0,Y=10.0,Z=-10.0)
    FireSound=Sound'LaserFire'
    Mesh=Mesh'Botpack.ShockRifleM'
}
```

### 4.2 State Machines & Latent Functions
```unrealscript
auto state Active
{
    function BeginState()
    {
        bHidden = False;
    }

Begin:
    Sleep(2.0);
    GotoState('Patrol');
}
```

### 4.3 Network Replication
```unrealscript
replication
{
    reliable if (Role == ROLE_Authority)
        BeamIntensity, BeamColor;
}
```

---

## 🤖 5. Agent Assistance & Pair Programming Capabilities

The **Antigravity AI Architect** is equipped to assist with:
*   Writing new weapons, projectiles, mutators, game types, and HUD interfaces.
*   Debugging script compilation warnings, parse errors, and type mismatches.
*   Generating `#exec` import macros for textures, skeletal meshes, and audio clips.
*   Refactoring Bot AI logic, path weights, and behavior trees.
