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
        # For ARM-packed textures (AO/Roughness/Metal in one file):
        # "arm_packed": "/path/to/ArchPillar_ARM.png",
    },
}

# create_redshift_openpbr(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}
ARM_CHANNELS = {"R": "ambient_occlusion", "G": "roughness", "B": "base_metalness"}


def create_redshift_openpbr(material_name, textures):
    """
    Builds a Redshift RedshiftOpenPBRMaterial and connects all PBR texture channels.

    textures: dict mapping OpenPBR identifier names to file paths.
              Use 'arm_packed' for a single ARM-packed texture (AO/Roughness/Metal).
    """
    import maya.cmds as cmds

    material = cmds.shadingNode("RedshiftOpenPBRMaterial", asShader=True, n=material_name)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=material_name + "_SG")
    cmds.connectAttr(material + ".outColor", sg + ".surfaceShader")

    file_nodes = []

    # ARM packed map
    if "arm_packed" in textures:
        arm_path = textures["arm_packed"]
        tex = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr(tex + ".fileTextureName", arm_path, type="string")
        cmds.setAttr(tex + ".colorSpace", "Raw", type="string")
        cmds.setAttr(tex + ".ignoreColorSpaceFileRules", 1)
        file_nodes.append(tex)
        channel_out = {"R": ".outColorR", "G": ".outColorG", "B": ".outColorB"}
        for ch, identifier in ARM_CHANNELS.items():
            try:
                cmds.connectAttr(tex + channel_out[ch], material + "." + identifier, force=True)
            except RuntimeError:
                pass

    for identifier, file_path in textures.items():
        if identifier == "arm_packed":
            continue

        is_color = identifier in COLOR_IDENTIFIERS
        tex = cmds.shadingNode("file", asTexture=True)
        cmds.setAttr(tex + ".fileTextureName", file_path, type="string")
        cmds.setAttr(tex + ".colorSpace", "sRGB" if is_color else "Raw", type="string")
        cmds.setAttr(tex + ".ignoreColorSpaceFileRules", 1)
        file_nodes.append(tex)

        if identifier in ("normal", "geometry_normal"):
            bump_node = cmds.shadingNode("RedshiftBumpMap", asTexture=True)
            cmds.setAttr(bump_node + ".inputType", 1)  # tangent-space normal
            cmds.connectAttr(tex + ".outColor", bump_node + ".input")
            cmds.connectAttr(bump_node + ".out", material + ".geometry_normal", force=True)

        elif identifier == "bump":
            bump_node = cmds.shadingNode("RedshiftBumpMap", asTexture=True)
            cmds.connectAttr(tex + ".outColor", bump_node + ".input")
            cmds.connectAttr(bump_node + ".out", material + ".geometry_normal", force=True)

        elif identifier == "displacement":
            disp_node = cmds.shadingNode("RedshiftDisplacement", asShader=True)
            cmds.connectAttr(tex + ".outColor", disp_node + ".texMap")
            cmds.connectAttr(disp_node + ".out", sg + ".rsDisplacementShader")

        else:
            # Redshift OpenPBR attribute names match OpenPBR identifiers directly
            src = ".outColor" if is_color else ".outAlpha"
            if not is_color:
                cmds.setAttr(tex + ".alphaIsLuminance", 1)
            try:
                cmds.connectAttr(tex + src, material + "." + identifier, force=True)
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
