# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/scene.hip",
}

# open_scene(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def open_scene(file_path):
    """Opens a Houdini scene file (.hip, .hiplc, .hipnc)."""
    import hou
    hou.hipFile.load(file_path)
