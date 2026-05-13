# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/scene.blend",
}

# open_scene(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def open_scene(file_path):
    """Opens a Blender scene file (.blend), discarding unsaved changes."""
    import bpy
    bpy.ops.wm.open_mainfile(filepath=file_path)
