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

# create_renderman_pxrsurface(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}

# OpenPBR identifier -> PxrSurface input name.
# List values connect the same texture to multiple inputs.
IDENTIFIER_MAP = {
    "base_color":          "diffuseColor",
    "base_metalness":      "metallic",
    "metalness":           "metallic",
    "specular_roughness":  "specularRoughness",
    "roughness":           "specularRoughness",
    "specular_color":      ["specularFaceColor", "specularEdgeColor"],
    "specular_ior":        "specularIor",
    "transmission_weight": "refractionGain",
    "transmission_color":  "refractionColor",
    "subsurface_color":    "subsurfaceColor",
    "emission_color":      "glowColor",
    "coat_weight":         "coatGain",
    "coat_color":          "coatColor",
    "coat_roughness":      "coatRoughness",
    "opacity":             "presence",
}


def create_renderman_pxrsurface(material_name, textures):
    """Builds a RenderMan PxrSurface material and connects all PBR texture channels."""
    import maya.cmds as cmds

    material = cmds.shadingNode("PxrSurface", asShader=True, n=material_name)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=material_name + "_SG")
    cmds.connectAttr(material + ".outColor", sg + ".surfaceShader")

    file_nodes = []
    bump_node = None

    for identifier, file_path in textures.items():
        is_color = identifier in COLOR_IDENTIFIERS
        tex = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr(tex + ".fileTextureName", file_path, type="string")
        cmds.setAttr(tex + ".colorSpace", "sRGB" if is_color else "Raw", type="string")
        cmds.setAttr(tex + ".ignoreColorSpaceFileRules", 1)
        file_nodes.append(tex)

        if identifier in ("normal", "geometry_normal"):
            cmds.setAttr(tex + ".colorSpace", "Raw", type="string")
            normal_node = cmds.shadingNode("PxrNormalMap", asTexture=True)
            cmds.connectAttr(tex + ".outColor", normal_node + ".inputRGB")
            if bump_node:
                cmds.connectAttr(normal_node + ".resultN", bump_node + ".inputN", force=True)
            else:
                cmds.connectAttr(normal_node + ".resultN", material + ".bumpNormal", force=True)

        elif identifier == "bump":
            cmds.setAttr(tex + ".colorSpace", "Raw", type="string")
            bump_node = cmds.shadingNode("PxrBump", asTexture=True)
            cmds.connectAttr(tex + ".outColorR", bump_node + ".inputBump")
            cmds.connectAttr(bump_node + ".resultN", material + ".bumpNormal", force=True)

        elif identifier == "displacement":
            cmds.setAttr(tex + ".colorSpace", "Raw", type="string")
            disp_node = cmds.shadingNode("displacementShader", asShader=True)
            cmds.connectAttr(tex + ".outColorR", disp_node + ".displacement")
            cmds.connectAttr(disp_node + ".displacement", sg + ".displacementShader")

        else:
            pxr_attrs = IDENTIFIER_MAP.get(identifier)
            if pxr_attrs:
                if isinstance(pxr_attrs, str):
                    pxr_attrs = [pxr_attrs]
                src = ".outColor" if is_color else ".outColorR"
                for pxr_attr in pxr_attrs:
                    try:
                        cmds.connectAttr(tex + src, material + "." + pxr_attr, force=True)
                    except RuntimeError:
                        pass

    if file_nodes:
        p2d = cmds.shadingNode("place2dTexture", asUtility=True)
        for tex in file_nodes:
            _connect_p2d(p2d, tex)


def _connect_p2d(p2d, file_node):
    import maya.cmds as cmds
    attrs = [
        ("outUV", "uvCoord"), ("outUvFilterSize", "uvFilterSize"),
        ("vertexCameraOne", "vertexCameraOne"), ("vertexUvOne", "vertexUvOne"),
        ("vertexUvThree", "vertexUvThree"), ("vertexUvTwo", "vertexUvTwo"),
        ("coverage", "coverage"), ("mirrorU", "mirrorU"), ("mirrorV", "mirrorV"),
        ("noiseUV", "noiseUV"), ("offset", "offset"), ("repeatUV", "repeatUV"),
        ("rotateFrame", "rotateFrame"), ("rotateUV", "rotateUV"),
        ("stagger", "stagger"), ("translateFrame", "translateFrame"),
        ("wrapU", "wrapU"), ("wrapV", "wrapV"),
    ]
    for src, tgt in attrs:
        cmds.connectAttr(p2d + "." + src, file_node + "." + tgt)
