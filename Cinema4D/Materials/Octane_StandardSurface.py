# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "material_name": "ArchPillar_Mat",
    "textures": {
        "base_color":   "/path/to/ArchPillar_BaseColor.png",
        "roughness":    "/path/to/ArchPillar_Roughness.png",
        "metalness":    "/path/to/ArchPillar_Metalness.png",
        "normal":       "/path/to/ArchPillar_Normal.png",
        "displacement": "/path/to/ArchPillar_Displacement.exr",  # optional
        "opacity":      "/path/to/ArchPillar_Opacity.png",       # optional
    },
}

# create_octane_standard_surface(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

import os

COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}

# OpenPBR identifier -> Octane Standard Surface SHADERLINK attribute ID
OCTANE_IDENTIFIER_MAP = {
    "base_weight":            "STDMAT_BASELAYER_WEIGHT_LINK",
    "base_color":             "STDMAT_BASELAYER_COLOR_LINK",
    "base_diffuse_roughness": "STDMAT_BASELAYER_DIFROUGH_LINK",
    "metalness":              "STDMAT_BASELAYER_METALNESS_LINK",
    "base_metalness":         "STDMAT_BASELAYER_METALNESS_LINK",
    "specular_weight":        "STDMAT_SPECULARLAYER_WEIGHT_LINK",
    "specular_color":         "STDMAT_SPECULARLAYER_COLOR_LINK",
    "specular_roughness":     "STDMAT_SPECULARLAYER_ROUGH_LINK",
    "roughness":              "STDMAT_SPECULARLAYER_ROUGH_LINK",
    "specular_ior":           "STDMAT_SPECULARLAYER_IOR_LINK",
    "transmission_weight":    "STDMAT_TRANSMLAYER_WEIGHT_LINK",
    "transmission_color":     "STDMAT_TRANSMLAYER_COLOR_LINK",
    "subsurface_weight":      "STDMAT_SUBSURFACE_LINK",
    "subsurface_color":       "STDMAT_SUBSURFACE_COLOR_LINK",
    "coat_weight":            "STDMAT_COATING_LINK",
    "coat_color":             "STDMAT_COATING_COLOR_LINK",
    "coat_roughness":         "STDMAT_COATING_ROUGHNESS_LINK",
    "fuzz_weight":            "STDMAT_SHEEN_LINK",
    "fuzz_color":             "STDMAT_SHEEN_COLOR_LINK",
    "emission_color":         "STDMAT_EMISSION_COLOR_LINK",
    "bump":                   "STDMAT_BUMP_LINK",
    "normal":                 "STDMAT_NORMAL_LINK",
    "geometry_normal":        "STDMAT_NORMAL_LINK",
    "displacement":           "STDMAT_DISPLACEMENT_LINK",
    "opacity":                "STDMAT_OPACITY_LINK",
}

COLORSPACE_NON_COLOR = 0
COLORSPACE_SRGB = 1


def create_octane_standard_surface(material_name, textures):
    """Builds an Octane Standard Surface material and connects all PBR texture channels."""
    import c4d

    ID_OCTANE_STANDARD_SURFACE = 1058763
    ID_OCTANE_IMAGE_TEXTURE    = 1029508

    doc = c4d.documents.GetActiveDocument()
    material = c4d.BaseMaterial(ID_OCTANE_STANDARD_SURFACE)
    material.SetName(material_name)
    doc.InsertMaterial(material)

    def add_image_texture(file_path, is_color=False):
        sha = c4d.BaseShader(ID_OCTANE_IMAGE_TEXTURE)
        sha[c4d.IMAGETEXTURE_FILE]    = file_path
        sha[c4d.IMAGETEXTURE_MODE]    = 0
        sha[c4d.IMAGETEX_BORDER_MODE] = 0
        sha[1118] = COLORSPACE_SRGB if is_color else COLORSPACE_NON_COLOR
        material.InsertShader(sha)
        return sha

    for identifier, file_path in textures.items():
        attr_name = OCTANE_IDENTIFIER_MAP.get(identifier)
        if not attr_name:
            continue

        octane_attr = getattr(c4d, attr_name, None)
        if octane_attr is None:
            continue

        is_color = identifier in COLOR_IDENTIFIERS
        node_name = os.path.splitext(os.path.basename(file_path))[0]
        img = add_image_texture(file_path, is_color=is_color)
        img.SetName(node_name)
        material[octane_attr] = img

    material.Message(c4d.MSG_UPDATE)
    material.Update(True, True)
    c4d.EventAdd()
