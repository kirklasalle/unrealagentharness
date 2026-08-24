# UnrealScript Language Reference & Programming Manual

**Engine Target:** Unreal Engine 1 (UT GOTY / v436 & v469)  
**Location:** `G:\UnrealTournament\docs\02_UNREALSCRIPT_LANGUAGE_REFERENCE.md`  
**Audience:** Kirk LaSalle & UTron Developers  

---

## 1. UnrealScript Overview

UnrealScript (often abbreviated **UScript**) is a strongly-typed, object-oriented, event-driven programming language designed by Tim Sweeney specifically for the Unreal Engine.

Key Language Characteristics:
- **Java/C++ Syntax Familiarity:** Uses familiar syntax (`class`, `extends`, `var`, `function`, `if/else`, `while`, `for`, `switch`).
- **Built-in State Machine Architecture:** First-class support for finite state machines (`state`, `state code`, `latent functions`).
- **Native Network Replication:** Built-in network replication definitions (`replication {}`).
- **Time and Latent Execution:** Built-in execution suspension (`Sleep(t)`, `FinishAnim()`, `MoveTo()`).
- **Vector & Rotator Mathematics:** Native primitives for 3D game mathematics (`vector`, `rotator`, `coords`).

---

## 2. Class Declaration & Modifiers

Every UnrealScript file defines exactly one class and must be named `<ClassName>.uc` located inside `<PackageName>\Classes\<ClassName>.uc`.

```unrealscript
class IdentityDisc extends Weapon
    abstract
    native
    config(UTronProject);
```

### Class Modifiers:
- `abstract`: Class cannot be instantiated directly (serves as a base class).
- `native`: Portions of the class or its vtable are implemented in native C++ (`.dll`).
- `config(ConfigName)`: Class variables marked with `config` are persisted to `<ConfigName>.ini`.
- `transient`: Objects of this class are not serialized when saving games.
- `nousercreate`: Level designers cannot place this actor manually in UnrealEd.

---

## 3. Variable Types & Declarations

### Primitive Data Types:
- `bool`: `true` or `false` (1 bit packed).
- `byte`: 8-bit unsigned integer (`0` to `255`).
- `int`: 32-bit signed integer.
- `float`: 32-bit single-precision floating point.
- `string`: Dynamic ASCII/Unicode string.
- `name`: Case-insensitive identifier token referencing the global Name Table.

### Built-in Geometric Types:
- `vector`: 3D position or direction `vect(X, Y, Z)`. Supports operators `+`, `-`, `*`, `/`, `Dot` (`dot`), `Cross` (`cross`), `VSize(v)`, `Normal(v)`.
- `rotator`: 3D orientation `rot(Pitch, Yaw, Roll)` measured in Unreal units (65536 units = 360 degrees).

### Variable Modifiers:
- `var()`: Exposes variable in the UnrealEd property inspector under the class name category.
- `var(CategoryName)`: Exposes variable under a custom category header in UnrealEd.
- `var config`: Loads/saves value automatically from the configured `.ini` file.
- `var localized`: Localized string loaded from `.int` / `.det` / `.frt` files.
- `var transient`: Excluded from binary save files.
- `var const`: Read-only in UnrealScript (written by native engine code).

---

## 4. Functions & Execution Modifiers

```unrealscript
function float CalculateDiscTrajectory(vector TargetLoc, out vector OutVelocity)
{
    local vector Dir;
    Dir = TargetLoc - Location;
    OutVelocity = Normal(Dir) * 1200.0;
    return VSize(Dir);
}
```

### Function Modifiers:
- `final`: Cannot be overridden in subclasses (enables faster VM dispatch).
- `simulated`: Executes on network clients (simulated proxies) as well as the server.
- `singular`: Prevents re-entrant recursion of the same function on the same actor.
- `exec`: Can be invoked directly from the player in-game console (e.g. `mutate`, `firedisc`).
- `latent`: State-only function that suspends execution over multiple frames (`Sleep`, `FinishAnim`).
- `iterator`: Generator function used in `foreach` loops (`AllActors`, `RadiusActors`).

---

## 5. State Machines in UnrealScript

State machines allow actors to alter their behavior, event handlers, and execution flow dynamically without nested `if/switch` checks.

```unrealscript
auto state Active
{
    function Touch(Actor Other)
    {
        if (Other.IsA('Pawn') && Other != Instigator)
        {
            Other.TakeDamage(Damage, Instigator, Location, MomentumTransfer * Velocity, MyDamageType);
            GotoState('Returning');
        }
    }

Begin:
    PlaySound(DiscHumSound, SLOT_Misc);
    Sleep(2.5);
    GotoState('Returning');
}

state Returning
{
    function Tick(float DeltaTime)
    {
        Velocity = Normal(Instigator.Location - Location) * ReturnSpeed;
    }

Begin:
    PlaySound(DiscRecallSound, SLOT_Misc);
}
```

---

## 6. Built-in Iterators (Actor Queries)

UE1 provides high-performance spatial iterators:

- `foreach AllActors(class'Pawn', P)`: Iterates over every spawned pawn in the level.
- `foreach RadiusActors(class'Actor', A, BlastRadius, ExplodeLocation)`: Iterates over actors within a spherical radius.
- `foreach VisibleActors(class'Pawn', P, ViewDistance)`: Iterates over actors with direct line of sight.
- `foreach TouchingActors(class'Pawn', P)`: Iterates over actors currently colliding with this actor.
- `foreach ChildActors(class'Actor', A)`: Iterates over actors owned by this actor.

---

## 7. DefaultProperties Block

Placed at the very bottom of the `.uc` file, `defaultproperties` sets initial values for all instances:

```unrealscript
defaultproperties
{
    ItemName="Identity Disc"
    PlayerViewOffset=(X=3.000000,Y=-1.500000,Z=-2.000000)
    PlayerViewMesh=Mesh'UTron.DiscViewMesh'
    PickupMesh=Mesh'UTron.DiscPickupMesh'
    ThirdPersonMesh=Mesh'UTron.Disc3rdMesh'
    StatusIcon=Texture'UTronHUD.Icons.DiscIcon'
    AutoSwitchPriority=10
    InventoryGroup=1
    PickupSound=Sound'UTron.Sounds.DiscPickup'
    Physics=PHYS_Falling
    CollisionRadius=20.000000
    CollisionHeight=10.000000
    bCollideActors=True
}
```
