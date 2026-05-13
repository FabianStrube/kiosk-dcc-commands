# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/scene.c4d",
}

# open_scene(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def open_scene(file_path):
    """Opens a Cinema 4D scene file (.c4d)."""
    import c4d

    if not c4d.documents.LoadFile(file_path):
        c4d.gui.MessageDialog("Failed to open the scene file.")
