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

# create_octane_area_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_octane_area_light(file_path):
    """
    Creates an Octane area light (C4D area light + Octane Light tag) and assigns a texture.
    If an Octane area light is already selected, its texture is updated instead.
    """
    import c4d

    ID_OCTANE_LIGHT_TAG   = 1029526
    ID_OCTANE_IMAGE_TEXTURE = 1029508

    doc = c4d.documents.GetActiveDocument()

    # Update texture if an Octane area light is already selected
    for obj in doc.GetSelection():
        if obj.GetType() == c4d.Olight and obj[c4d.LIGHT_TYPE] == 8:
            tags = [t for t in obj.GetTags() if t.CheckType(ID_OCTANE_LIGHT_TAG)]
            if tags:
                image = tags[0][c4d.LIGHTTAG_EFFIC_OR_TEX]
                image[c4d.IMAGETEXTURE_FILE] = file_path
                c4d.EventAdd()
                return

    # Create new Octane area light
    light = c4d.BaseObject(c4d.Olight)
    light[c4d.LIGHT_TYPE] = 8  # area
    light.SetName("Octane Area Light")

    octag = c4d.BaseTag(ID_OCTANE_LIGHT_TAG)
    light.InsertTag(octag)
    octag[c4d.LIGHTTAG_POWER] = 4.0

    img_tex = c4d.BaseList2D(ID_OCTANE_IMAGE_TEXTURE)
    octag.InsertShader(img_tex)
    octag[c4d.LIGHTTAG_EFFIC_OR_TEX] = img_tex
    img_tex[c4d.IMAGETEXTURE_FILE] = file_path

    doc.InsertObject(light)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, light)
    c4d.EventAdd()
