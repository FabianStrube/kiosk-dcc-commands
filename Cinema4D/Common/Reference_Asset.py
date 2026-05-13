# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/asset.c4d",
    "object_name": "ArchPillar",
}

# reference_asset(EXAMPLE["file_path"], EXAMPLE["object_name"])
# -------------------------------------------------------------------------------

def reference_asset(file_path, object_name="XRef"):
    """Creates a Cinema 4D XRef object pointing to the given file."""
    import c4d
    import os

    if not os.path.exists(file_path):
        c4d.gui.MessageDialog(f"File not found: {file_path}")
        return

    doc = c4d.documents.GetActiveDocument()
    xref = c4d.BaseObject(1025766)  # Oxref
    xref[c4d.ID_CA_XREF_FILE] = file_path
    xref.SetName(object_name)
    doc.InsertObject(xref)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, xref)
    c4d.EventAdd()
