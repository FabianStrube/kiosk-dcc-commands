# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/asset.fbx",
}

# import_asset(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def import_asset(file_path):
    """Imports a 3D asset into Blender. Supports: FBX, GLTF, OBJ, DAE, ABC, USD."""
    import bpy
    import os

    ext = os.path.splitext(file_path)[1].lstrip(".").lower()

    importers = {
        "fbx":  lambda: bpy.ops.import_scene.fbx(filepath=file_path),
        "gltf": lambda: bpy.ops.import_scene.gltf(filepath=file_path),
        "glb":  lambda: bpy.ops.import_scene.gltf(filepath=file_path),
        "obj":  lambda: bpy.ops.wm.obj_import(filepath=file_path),
        "dae":  lambda: bpy.ops.wm.collada_import(filepath=file_path),
        "abc":  lambda: bpy.ops.wm.alembic_import(filepath=file_path),
        "usd":  lambda: bpy.ops.wm.usd_import(filepath=file_path),
        "usdc": lambda: bpy.ops.wm.usd_import(filepath=file_path),
        "usda": lambda: bpy.ops.wm.usd_import(filepath=file_path),
    }

    importer = importers.get(ext)
    if importer:
        importer()
    else:
        print(f"[kiosk-dcc-commands] Unsupported format: {ext}")
