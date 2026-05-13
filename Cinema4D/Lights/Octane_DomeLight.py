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

# create_octane_dome_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_octane_dome_light(hdri_path):
    """
    Creates an Octane sky dome (C4D sky + Octane Environment tag) and assigns an HDRI.
    If an Octane sky is already selected, its texture is updated instead.
    """
    import c4d

    ID_OCTANE_ENVIRONMENT_TAG = 1029643
    ID_OCTANE_IMAGE_TEXTURE   = 1029508

    doc = c4d.documents.GetActiveDocument()

    # Update texture if an Octane sky is already selected
    for obj in doc.GetSelection():
        if obj.GetType() == c4d.Osky:
            tags = [t for t in obj.GetTags() if t.CheckType(ID_OCTANE_ENVIRONMENT_TAG)]
            if tags:
                image = tags[0][c4d.ENVIRONMENTTAG_TEXTURE]
                image[c4d.IMAGETEXTURE_FILE] = hdri_path
                c4d.EventAdd()
                return

    # Create new Octane sky
    osky = c4d.BaseObject(c4d.Osky)
    env = osky.MakeTag(ID_OCTANE_ENVIRONMENT_TAG)

    image = c4d.BaseList2D(ID_OCTANE_IMAGE_TEXTURE)
    image[1118] = 2               # HDR color space
    image[c4d.IMAGETEXTURE_GAMMA] = 1.0
    env.InsertShader(image)
    env[c4d.ENVIRONMENTTAG_TEXTURE] = image
    image[c4d.IMAGETEXTURE_FILE] = hdri_path

    doc.InsertObject(osky)
    doc.AddUndo(c4d.UNDOTYPE_NEWOBJ, osky)
    c4d.EventAdd()
