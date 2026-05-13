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
    """Imports an OBJ, FBX, or Alembic file into the active Cinema 4D document."""
    import c4d
    import os

    extension = os.path.splitext(file_path)[1].lstrip(".").lower()
    supported = ("obj", "fbx", "abc")

    if extension in supported:
        doc = c4d.documents.GetActiveDocument()
        c4d.documents.MergeDocument(
            doc, file_path,
            c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS
        )
        c4d.EventAdd()
    else:
        c4d.gui.MessageDialog(f"Unsupported import format: {extension}")
