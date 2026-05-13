# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/light_texture.exr",
}

# create_redshift_area_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_redshift_area_light(file_path):
    """
    Creates a Redshift Physical area light and assigns a texture to it.
    If a Redshift area light is already selected, its texture is updated instead.
    """
    import c4d

    doc = c4d.documents.GetActiveDocument()

    texture_path_id = c4d.DescID(
        c4d.DescLevel(c4d.REDSHIFT_LIGHT_PHYSICAL_TEXTURE, 1036765, c4d.Orslight),
        c4d.DescLevel(c4d.REDSHIFT_FILE_PATH, c4d.DTYPE_STRING, 0)
    )

    # Update texture if a Redshift area light is already selected
    for obj in doc.GetSelection():
        if obj.GetType() == 1036751 and obj[c4d.REDSHIFT_LIGHT_TYPE] == 3:
            obj[texture_path_id] = file_path
            c4d.EventAdd()
            return

    # Create new area light
    light = c4d.BaseObject(c4d.Orslight)
    light[c4d.REDSHIFT_LIGHT_TYPE] = 3  # area
    light[texture_path_id] = file_path
    doc.InsertObject(light)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, light)
    c4d.EventAdd()
