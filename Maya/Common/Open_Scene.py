# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/scene.mb",
}

# open_scene(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def open_scene(file_path):
    """Opens a Maya scene file (.ma or .mb), discarding unsaved changes."""
    import maya.cmds as cmds
    cmds.file(file_path, open=True, f=True)
