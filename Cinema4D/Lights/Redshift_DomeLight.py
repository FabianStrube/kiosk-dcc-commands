# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/environment.hdr",
}

# create_redshift_dome_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_redshift_dome_light(hdri_path):
    """
    Creates a Redshift dome light and assigns an HDRI.
    If a Redshift dome light is already selected, its texture is updated instead.
    """
    import c4d

    doc = c4d.documents.GetActiveDocument()

    texture_path_id = c4d.DescID(
        c4d.DescLevel(c4d.REDSHIFT_LIGHT_DOME_TEX0, 1036765, c4d.Orslight),
        c4d.DescLevel(c4d.REDSHIFT_FILE_PATH, c4d.DTYPE_STRING, 0)
    )

    # Update texture if a Redshift dome light is already selected
    for obj in doc.GetSelection():
        if obj.GetType() == 1036751 and obj[c4d.REDSHIFT_LIGHT_TYPE] == c4d.REDSHIFT_LIGHT_TYPE_DOME:
            obj[texture_path_id] = hdri_path
            c4d.EventAdd()
            return

    # Create new dome light
    light = c4d.BaseObject(c4d.Orslight)
    light.SetName("RS_DomeLight")
    light[c4d.REDSHIFT_LIGHT_TYPE] = c4d.REDSHIFT_LIGHT_TYPE_DOME
    light[texture_path_id] = hdri_path
    doc.InsertObject(light)
    c4d.EventAdd()
