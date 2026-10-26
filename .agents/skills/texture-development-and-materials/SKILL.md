---
name: texture-development-and-materials
description: World-class texture development, PBR material pipelines, Unreal UTX package architectures, procedural animated noise shaders, UV unwrapping, and S3TC/DXT texture compression.
---

# Texture Development & Materials Synthesis Skill

## Overview

The **Texture Development & Materials Synthesis Skill** establishes mastery over surface shading, texture package management, mathematical UV unwrapping, and real-time shader effects across both classic Unreal engines (UE1/UE2.5) and modern PBR pipelines (UE5). It ensures materials bind cleanly, render without stretching or missing texture placeholders, and maintain high framerates across viewports.

```
                              [ TEXTURE & MATERIAL PIPELINE ]
                ┌────────────────────────┼────────────────────────┐
                ▼                        ▼                        ▼
       [ MODERN PBR WORKFLOW ]   [ CLASSIC UTX ARCHITECTURE ] [ PROCEDURAL NOISE SHADERS ]
       • Albedo (Base Color)     • Dynamic OBJ LOAD Streaming • FireTexture (Flames)
       • Tangent Normal Maps     • Stock UTX Package Catalog  • WaterTexture (Cascades)
       • Roughness & Metallic    • 8-Bit Paletted Textures    • WaveTexture (Ripples)
                │                        │                        │
                └────────────────────────┼────────────────────────┘
                                         ▼
                             [ UV MAPPING & COMPRESSION ]
                        • Strict 1 Texel / UU Density Ratio
                        • S3TC / DXT1 - DXT5 Block Compression
                        • Non-Stretching Planar & Box Projections
```

---

## 🎨 Modern PBR (Physically Based Rendering) Workflow

Modern Unreal Engine materials adhere to physical laws of energy conservation:

1. **Albedo / Base Color**:
   * Pure reflectance without baked directional lighting, specular highlights, or ambient shadows.
   * Dielectric (non-metal) albedo values typically fall in the sRGB range [30, 240] (avoiding pure #000000 or #FFFFFF).
2. **Tangent-Space Normal Maps**:
   * Encodes surface micro-relief as 3D unit normal vectors perturbed relative to the polygonal tangent plane.
   * Format: Red channel = $X$ (tangent), Green channel = $Y$ (bitangent), Blue channel = $Z$ (surface normal).
3. **Roughness & Metallic**:
   * **Roughness**: Measures microfacet orientation scatter ($0.0 = \text{mirror smooth}$, $1.0 = \text{completely chalky/matte}$).
   * **Metallic**: Binary parameter ($0.0 = \text{dielectric/insulator}$, $1.0 = \text{conductor/raw metal}$). Dielectric specular reflectance is constant ($F_0 \approx 0.04$).
4. **Ambient Occlusion (AO)**:
   * Greyscale mask darkening crevice micro-shadows where diffuse ambient skylight cannot penetrate.

---

## 📦 Classic Unreal UTX Package Architecture & Dynamic Preloading

In Unreal Engine 1 and 2.5, textures reside inside compressed binary `.utx` package files. If an imported CSG brush references a texture from an unmounted package, UnrealEd either crashes or defaults the surface to flat gray or `DefaultTexture`.

### The Dynamic In-Editor Preload Rule
Before carving brushes or importing T3D geometry, always issue the native `OBJ LOAD` command via the UnrealEd console:
```text
OBJ LOAD FILE="..\Textures\<PackageName>.utx" PACKAGE=<PackageName>
```

### Canonical Stock UTX Texture Package Catalog:
| Package ID | Primary Architectural Theme | Representative Textures |
| :--- | :--- | :--- |
| `GenEarth.utx` | Outdoor Terrain, Cliffs, Rocks, Mud | `grasrok2`, `Rockfac1`, `Mud01`, `Ground3` |
| `NaliCast.utx` | Medieval Castles, Fortress Stone, Dungeons | `CblStn01`, `WoodFlr`, `Roof1`, `CastleDr` |
| `Ancient.utx` | Ancient Egyptian / Chizra Ruined Temples | `AncWall1`, `Hierogl1`, `SandStn2`, `Plinth` |
| `ShaneSky.utx` | Celestial Skies, Alpine Clouds, Mountains | `Sky_01`, `ShaneCloud`, `HorizonMtn` |
| `UTtech1.utx` | High-Tech Sci-Fi, Metal Plating, Conduits | `techw1`, `hatch01`, `vent_metal`, `floort1` |
| `UTtech2.utx` | Industrial Brutalism, Catwalks, Steel Trusses | `girder1`, `steelplate`, `conduit_rack` |
| `Coret_FX.utx` | High-Energy Neon, Sci-Fi Consoles, Glowing Grids | `NeonBlue`, `CoreLaser`, `Console_Glow` |
| `SpaceFX.utx` | Deep Space Starfields, Nebulae, Planets | `Starfield01`, `NebulaPink`, `MoonCrater` |

---

## 🌊 Procedural Animated Noise Shaders (`FireTexture`, `WaterTexture`)

Unreal Engine 1 pioneered CPU-driven procedural animated textures computed on the fly:
* **`FireTexture`**: Cellular automata simulating turbulent flame combustion, sparks, and hearth embers.
* **`WaterTexture`**: Damped wave propagation algorithm simulating rippling droplets, waterfalls, and river surfaces.
* **`WaveTexture`**: Directional sinusoidal waves for open lakes and surging oceans.
* **`WetTexture`**: High-specular reflective sheen simulating wet stones and rain-drenched pavement.

### Water Surface Poly Flags Formula:
To render transparent, buoyant water with moving ripples, apply:
$$\text{Flags} = \text{PF\_Translucent } (4) \;|\; \text{PF\_Semisolid } (32) = 36$$

---

## 📐 UV Mapping & Texel Density

Textures must maintain consistent visual scale throughout a map to avoid jarring visual seams:
* **Golden Texel Density**: `1 Texel per 1 Unreal Unit (UU)` for standard 256×256 textures across 256 UU surfaces.
* **Alignment Commands**:
  * `POLY ALIGN PLANAR`: Projects texture planar coordinates along the surface normal.
  * `POLY ALIGN WALLDIRECTION`: Wraps textures continuously around curved or octagonal perimeter walls.
  * `POLY TILING U=1 V=1`: Resets texture tiling to default 1:1 scale.

---

## 💾 Texture Compression Algorithms (S3TC / DXT)

* **DXT1 / BC1**: 4×4 pixel block compression with 1-bit punch-through alpha. Compression ratio `8:1` (0.5 bytes/pixel). Ideal for opaque stone, bedrock cliffs, and terrain.
* **DXT3 / BC2**: 4×4 block with explicit 4-bit uncompressed alpha. Ideal for sharp-edged decals, metal grating, and logos.
* **DXT5 / BC3**: 4×4 block with smoothly interpolated 8-bit alpha. Ideal for translucent glass, water cascades, and organic foliage leaves.
* **BC7 (Modern UE5)**: High-quality RGB/RGBA compression minimizing block compression artifacts on detailed normal and roughness maps.
