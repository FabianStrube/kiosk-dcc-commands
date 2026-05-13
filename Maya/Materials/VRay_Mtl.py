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

# create_vray_mtl(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}

# OpenPBR identifier -> VRayMtl attribute
IDENTIFIER_TO_VRAY = {
    "base_color":                    "color",
    "base_weight":                   "diffuseColorAmount",
    "base_diffuse_roughness":        "roughnessAmount",
    "base_metalness":                "metalness",
    "metalness":                     "metalness",
    "specular_color":                "reflectionColor",
    "specular_weight":               "reflectionColorAmount",
    "specular_roughness":            "reflectionGlossiness",
    "roughness":                     "reflectionGlossiness",
    "specular_roughness_anisotropy": "anisotropy",
    "specular_ior":                  "fresnelIOR",
    "transmission_weight":           "refractionColorAmount",
    "transmission_color":            "refractionColor",
    "subsurface_weight":             "translucencyAmount",
    "subsurface_color":              "translucencyColor",
    "coat_color":                    "coatColor",
    "coat_weight":                   "coatColorAmount",
    "coat_roughness":                "coatGlossiness",
    "coat_ior":                      "coatIOR",
    "fuzz_color":                    "sheenColor",
    "fuzz_weight":                   "sheenColorAmount",
    "fuzz_roughness":                "sheenGlossiness",
    "emission_color":                "illumColor",
    "geometry_opacity":              "opacityMap",
    "opacity":                       "opacityMap",
}

# VRayMtl attributes that expect a scalar (connect .outAlpha instead of .outColor)
SCALAR_VRAY_ATTRS = {
    "diffuseColorAmount", "roughnessAmount", "metalness",
    "reflectionColorAmount", "reflectionGlossiness", "anisotropy", "fresnelIOR",
    "refractionColorAmount", "coatColorAmount", "coatGlossiness", "coatIOR",
    "sheenColorAmount", "sheenGlossiness",
}


def create_vray_mtl(material_name, textures):
    """Builds a V-Ray VRayMtl and connects all PBR texture channels."""
    import maya.cmds as cmds

    material = cmds.shadingNode("VRayMtl", asShader=True, n=material_name)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=material_name + "_SG")
    cmds.connectAttr(material + ".outColor", sg + ".surfaceShader")
    cmds.setAttr(material + ".shadingModel", 1)

    file_nodes = []
    vray_normal_node = None
    bump_node_ref = None

    for identifier, file_path in textures.items():
        is_color = identifier in COLOR_IDENTIFIERS
        tex = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr(tex + ".fileTextureName", file_path, type="string")
        cmds.setAttr(tex + ".colorSpace", "sRGB" if is_color else "Raw", type="string")
        cmds.setAttr(tex + ".ignoreColorSpaceFileRules", 1)
        file_nodes.append(tex)

        if identifier in ("normal", "geometry_normal"):
            cmds.setAttr(tex + ".colorSpace", "Raw", type="string")
            vray_normal_node = cmds.shadingNode("VRayNormalMap", asTexture=True)
            cmds.connectAttr(tex + ".outColor", vray_normal_node + ".map")
            cmds.setAttr(vray_normal_node + ".mapType", 1)  # tangent-space
            if bump_node_ref:
                cmds.connectAttr(bump_node_ref + ".outColor", vray_normal_node + ".additionalBump")
            cmds.connectAttr(vray_normal_node + ".outColor", material + ".bumpMap")

        elif identifier == "bump":
            cmds.setAttr(tex + ".colorSpace", "Raw", type="string")
            bump_node_ref = tex
            if vray_normal_node:
                cmds.connectAttr(tex + ".outColor", vray_normal_node + ".additionalBump")
            else:
                vray_normal_node = cmds.shadingNode("VRayNormalMap", asTexture=True)
                cmds.connectAttr(tex + ".outColor", vray_normal_node + ".map")
                cmds.connectAttr(vray_normal_node + ".outColor", material + ".bumpMap")

        elif identifier in ("coat_normal", "geometry_coat_normal"):
            cmds.setAttr(tex + ".colorSpace", "Raw", type="string")
            coat_node = cmds.shadingNode("VRayNormalMap", asTexture=True)
            cmds.connectAttr(tex + ".outColor", coat_node + ".map")
            cmds.setAttr(coat_node + ".mapType", 1)
            cmds.connectAttr(coat_node + ".outColor", material + ".coat_bump_map")

        elif identifier == "displacement":
            cmds.setAttr(tex + ".colorSpace", "Raw", type="string")
            disp_node = cmds.shadingNode("displacementShader", asShader=True)
            cmds.connectAttr(tex + ".outAlpha", disp_node + ".displacement")
            cmds.connectAttr(disp_node + ".displacement", sg + ".displacementShader")

        else:
            vray_attr = IDENTIFIER_TO_VRAY.get(identifier, identifier)
            src = ".outAlpha" if vray_attr in SCALAR_VRAY_ATTRS else (
                ".outColor" if is_color else ".outAlpha"
            )
            try:
                cmds.connectAttr(tex + src, material + "." + vray_attr, force=True)
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
