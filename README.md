# Kiosk DCC Commands

**Open-source Python commands for Maya, Houdini, Cinema 4D & Blender.**  
Built for TDs. Free for everyone.

Made by **[Kiosk Library](https://www.kiosk-library.com)** - the asset management app for 3D artists.

---

## What's in here?

The actual Python scripts that run inside Kiosk Library every time an artist sends an asset, material, or light into their DCC. Ripped out of the app, cleaned up, and dropped here for anyone to use.

Copy a file. Paste it in your DCC's script editor. Done.

No dependencies. No boilerplate. No app required.

---

## Structure

```
kiosk-dcc-commands/
├── Maya/
│   ├── Common/       import, open, reference, USD stage, image plane
│   ├── Lights/       area lights + dome lights, one file per renderer
│   └── Materials/    PBR material builders, one file per renderer
├── Houdini/
│   ├── Common/       import, open, USD sublayer/reference, refimage
│   ├── Lights/       area lights + dome lights, one file per renderer
│   └── Materials/    PBR material builders, one file per renderer
├── Cinema4D/
│   ├── Common/       import, open, XRef
│   ├── Lights/       area lights + dome lights, one file per renderer
│   └── Materials/    PBR material builders, one file per renderer
└── Blender/
    ├── Common/       import, open
    ├── Lights/       area light, HDRI world setup
    └── Materials/    Principled BSDF builder
```

---

## Renderer Support

|              | Arnold | Redshift | V-Ray | RenderMan | Octane | Karma / Cycles |
|:-------------|:------:|:--------:|:-----:|:---------:|:------:|:--------------:|
| **Maya**     |   ✓    |    ✓     |   ✓   |     ✓     |        |                |
| **Houdini**  |   ✓    |    ✓     |       |     ✓     |        |       ✓        |
| **Cinema 4D**|        |    ✓     |       |           |   ✓    |                |
| **Blender**  |        |          |       |           |        |       ✓        |

---

## How to Use

Every file has an `EXAMPLE` dict at the top with paths you can swap out. Call the function directly.

**Import an asset into Maya:**
```python
from Import_Asset import import_asset
import_asset("/path/to/asset.fbx")
```

**Build a Redshift material in Maya:**
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

**Houdini: context matters**  
Scripts detect whether you are in an OBJ, SOP, or LOP (Solaris/USD) network and create the right node type. Each Houdini file has a note at the top about which context it targets.

---

## About Kiosk Library

Kiosk Library is an asset management app for 3D artists. Browse your library, click an asset, and it lands in your scene - textures connected, material built, light ready to render.

**[www.kiosk-library.com](https://www.kiosk-library.com)**

---

## License

MIT. Take it, use it, change it.
