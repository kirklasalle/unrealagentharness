# UnrealEd 3.0 Master Console & Exec Command Reference

This document is the comprehensive reference for all console commands supported by **UnrealEd 3.0** (`UEditorEngine::Exec`) in Unreal Tournament 2004. These commands can be entered via the editor command bar, in `.exec` batch scripts, or dispatched via the **Agent Bridge API**.

---

## 1. Level & Map Operations

| Command | Syntax / Parameters | Description |
| :--- | :--- | :--- |
| `MAP NEW` | `MAP NEW` | Clears the workspace and creates a new empty level. |
| `MAP LOAD` | `MAP LOAD FILE="<path.ut2>"` | Loads an existing map file into the editor. |
| `MAP SAVE` | `MAP SAVE FILE="<path.ut2>"` | Saves the active map to disk. |
| `MAP IMPORT` | `MAP IMPORT FILE="<path.t3d>"` | Imports level geometry and actors from an Unreal Text (`.t3d`) file. |
| `MAP EXPORT` | `MAP EXPORT FILE="<path.t3d>"` | Exports all level actors, brushes, and properties to `.t3d`. |
| `MAP CHECK` | `MAP CHECK` | Runs the map error scanner (orphaned nodes, missing materials, collision errors). |
| `MAP SCALE` | `MAP SCALE FACTOR=<float>` | Uniformly scales the entire map by the specified multiplier. |
| `MAP SENDTO` | `MAP SENDTO [FIRST/LAST/SWAP]` | Reorders the brush list hierarchy for CSG evaluation. |

---

## 2. Actor Manipulation & Spawning

| Command | Syntax / Parameters | Description |
| :--- | :--- | :--- |
| `ACTOR ADD` | `ACTOR ADD CLASS=<ClassName>` | Spawns an actor of type `<ClassName>` at the current Red Builder Brush position (e.g. `ACTOR ADD CLASS=Light`). |
| `ACTOR DELETE` | `ACTOR DELETE` | Deletes all currently selected actors. |
| `ACTOR SELECT ALL` | `ACTOR SELECT ALL` | Selects every actor in the active level. |
| `ACTOR SELECT NONE` | `ACTOR SELECT NONE` | Deselects all actors. |
| `ACTOR SELECT OFCLASS`| `ACTOR SELECT OFCLASS CLASS=<ClassName>` | Selects all actors matching the given class (e.g. `PathNode`). |
| `ACTOR DUPLICATE` | `ACTOR DUPLICATE` | Clones all selected actors in-place. |
| `ACTOR MOVE` | `ACTOR MOVE X=<float> Y=<float> Z=<float>` | Translates selected actors by relative delta coordinates. |
| `EDITACTOR NAME` | `EDITACTOR NAME=<ActorName>` | Opens the properties dialog for the specified actor (e.g. `EDITACTOR NAME=Light0`). |
| `EDITACTOR CLASS` | `EDITACTOR CLASS=<ClassName>` | Opens properties for the nearest actor of that class. |
| `ACTOR REPLACE` | `ACTOR REPLACE CLASS=<NewClass>` | Replaces selected actors with an instance of `<NewClass>`. |
| `ACTOR HIDE` | `ACTOR HIDE SELECTED` / `UNHIDE` | Toggles actor visibility in the viewports. |

---

## 3. CSG (Constructive Solid Geometry) & Brush Building

| Command | Syntax / Parameters | Description |
| :--- | :--- | :--- |
| `BRUSH BUILD BOX` | `BRUSH BUILD BOX X=<size> Y=<size> Z=<size>` | Builds a box builder brush with the specified dimensions (e.g. `BRUSH BUILD BOX X=1024 Y=1024 Z=512`). |
| `BRUSH BUILD CYLINDER` | `BRUSH BUILD CYLINDER HEIGHT=<h> RADIUS=<r> SIDES=<s>` | Builds a cylindrical builder brush. |
| `BRUSH BUILD CONE` | `BRUSH BUILD CONE HEIGHT=<h> RADIUS=<r> SIDES=<s>` | Builds a conical builder brush. |
| `BRUSH BUILD STAIRS` | `BRUSH BUILD LINEARSTAIRS NUMSTEPS=<s> STEPHEIGHT=<h> STEPWIDTH=<w>` | Builds a staircase builder brush. |
| `BRUSH ADD` | `BRUSH ADD` | Adds the builder brush as a solid additive CSG brush. |
| `BRUSH SUBTRACT` | `BRUSH SUBTRACT` | Subtracts the builder brush from the world to carve out rooms/corridors. |
| `BRUSH INTERSECT` | `BRUSH INTERSECT` | Intersects builder brush against surrounding solid geometry. |
| `BRUSH DEINTERSECT` | `BRUSH DEINTERSECT` | De-intersects builder brush against solid geometry. |
| `BRUSH MERGEPOLYS` | `BRUSH MERGEPOLYS` | Merges coplanar polygons on selected brushes to reduce poly count. |
| `BRUSH SEPARATEPOLYS`| `BRUSH SEPARATEPOLYS` | Splits merged polygons into basic triangles. |
| `BRUSH IMPORT` | `BRUSH IMPORT FILE="<file.t3d>"` | Loads a custom brush shape from `.t3d`. |
| `BRUSH EXPORT` | `BRUSH EXPORT FILE="<file.t3d>"` | Saves the current builder brush to `.t3d`. |

---

## 4. Surface & Polygon Management

| Command | Syntax / Parameters | Description |
| :--- | :--- | :--- |
| `POLY SELECT ALL` | `POLY SELECT ALL` | Selects all BSP surfaces in the level. |
| `POLY SELECT NONE` | `POLY SELECT NONE` | Deselects all surfaces. |
| `POLY SELECT MATCHING`| `POLY SELECT MATCHING TEXTURE` | Selects all surfaces sharing the same texture as the active selection. |
| `POLY SELECT ADJACENT`| `POLY SELECT ADJACENT [ALL/FLOORS/WALLS/CEILINGS/COPLANARS]` | Selects contiguous or coplanar surfaces. |
| `POLY SET TEXTURE` | `POLY SET TEXTURE="<Package.Group.Name>"` | Applies the specified texture material to selected surfaces. |
| `POLY DEFAULT` | `POLY DEFAULT` | Resets texture alignment, scaling, and panning to defaults. |

---

## 5. Rebuilding & System Compilers

| Command | Syntax / Parameters | Description |
| :--- | :--- | :--- |
| `MAP REBUILD` | `MAP REBUILD [GEOMETRY=1] [LIGHTING=1] [PATHS=1]` | Runs a complete level build (BSP + Lighting + Navigation). |
| `GEOMETRY REBUILD` | `GEOMETRY REBUILD` | Computes BSP cuts, polygon splitting, and visibility zones. |
| `LIGHT APPLY` | `LIGHT APPLY [SELECTED=0]` | Calculates direct raytraced lighting, radiosity, and shadow maps. |
| `PATHS BUILD` | `PATHS BUILD` | Computes reachability matrices between all navigation nodes (`PathNode`, `PlayerStart`, etc.). |
| `PATHS REVIEW` | `PATHS REVIEW` | Opens the path review diagnostic panel. |
| `FLUID REBUILD` | `FLUID REBUILD` | Rebuilds dynamic fluid surface simulation tables. |
| `FLUSH` | `FLUSH` | Flushes Direct3D texture/vertex caches and forces a full viewport redraw. |

---

## 6. Transactions, Viewports & Batching

| Command | Syntax / Parameters | Description |
| :--- | :--- | :--- |
| `TRANSACTION BEGIN` | `TRANSACTION BEGIN` | Starts a multi-step undoable transaction. |
| `TRANSACTION END` | `TRANSACTION END` | Commits the open transaction buffer. |
| `TRANSACTION UNDO` | `TRANSACTION UNDO` | Reverts the last transaction. |
| `TRANSACTION REDO` | `TRANSACTION REDO` | Replays the last reverted transaction. |
| `CAMERA ALIGN` | `CAMERA ALIGN` | Aligns all viewport cameras to focus on the selected actor. |
| `JUMPTO` | `JUMPTO X=<float> Y=<float> Z=<float>` | Moves viewport cameras to exact 3D coordinates. |
| `EXEC` | `EXEC "<script.txt>"` | Executes an external batch file of UnrealEd commands sequentially. |
| `OBJ CLASSES` | `OBJ CLASSES` | Lists all loaded classes in memory to the editor log. |
| `OBJ GARBAGE` | `OBJ GARBAGE` | Triggers the engine garbage collector to purge unreferenced objects. |
