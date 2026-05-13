# Kiosk DCC Commands

> Open-source pipeline commands for Maya, Houdini, Cinema 4D & Blender  
> Created by **[Kiosk Library](https://www.kiosk-library.com)**

---

## What is this?

These are the Python scripts that power the DCC integrations inside **Kiosk Library** — a 3D asset management app for artists working across Maya, Houdini, Cinema 4D, and Blender.

We're releasing them as a free, standalone reference for the community. Whether you're building your own pipeline tools, writing a studio connector, or just curious how things like Redshift material creation or USD stage importing work in Python — grab what's useful and adapt it.

Every file is self-contained. No extra dependencies, no app required.

---

## Repository Structure

```
kiosk-dcc-commands/
├── Maya/
│   ├── Common/         # Import, open, reference, image plane
│   ├── Lights/         # Area lights & dome lights per renderer
│   └── Materials/      # PBR material builders per renderer
├── Houdini/
│   ├── Common/         # Import, open, USD, reference image
│   ├── Lights/         # Area lights & dome lights per renderer
│   └── Materials/      # PBR material builders per renderer
├── Cinema4D/
│   ├── Common/         # Import, open, XRef
│   ├── Lights/         # Area lights & dome lights per renderer
│   └── Materials/      # PBR material builders per renderer
└── Blender/
    ├── Common/         # Import, open
    ├── Lights/         # Area light & HDRI world setup
    └── Materials/      # Principled BSDF builder
```

---

## Supported DCCs & Renderers

| | Arnold | Redshift | V-Ray | RenderMan | Octane | Cycles / Karma (MaterialX) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Maya** | ✓ | ✓ | ✓ | ✓ | — | — |
| **Houdini** | ✓ | ✓ | — | ✓ | — | ✓ |
| **Cinema 4D** | — | ✓ | — | — | ✓ | — |
| **Blender** | — | — | — | — | — | ✓ |

---

## How to Use

Each script is self-contained — copy it into your pipeline or paste it directly into the DCC's Python console.

Every file has an **EXAMPLE dict** at the top that shows the expected inputs. Swap the paths for your own files and call the function.

**Asset import example (Maya):**
```python
from Import_Asset import import_asset
import_asset("/path/to/asset.fbx")
```

**PBR material example (Redshift in Maya):**
```python
from Redshift_OpenPBR import create_redshift_openpbr

create_redshift_openpbr("ArchPillar_Mat", {
    "base_color":   "/path/to/BaseColor.png",
    "roughness":    "/path/to/Roughness.png",
    "metalness":    "/path/to/Metalness.png",
    "normal":       "/path/to/Normal.png",
    "displacement": "/path/to/Displacement.exr",
})
```

**ARM-packed texture (single map for AO / Roughness / Metal):**
```python
create_redshift_openpbr("ArchPillar_Mat", {
    "base_color": "/path/to/BaseColor.png",
    "arm_packed": "/path/to/ARM.png",   # R=AO  G=Roughness  B=Metalness
    "normal":     "/path/to/Normal.png",
})
```

**Houdini — context matters:**  
Scripts detect whether you are in an OBJ, SOP, or LOP (Solaris/USD) network and create the correct node type. Check the header comment of each Houdini file for the context it targets.

---

## About Kiosk Library

**Kiosk Library** is a 3D asset management app designed for 3D artists who work across multiple DCCs. It lets you browse, organize, and instantly send assets — models, textures, HDRIs, and materials — directly into your active scene.

→ **[www.kiosk-library.com](https://www.kiosk-library.com)**

---

## License

MIT — do whatever you want with it. Attribution appreciated but not required.
