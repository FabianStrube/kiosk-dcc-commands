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

# create_arnold_openpbr(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

# Texture identifiers that carry color data (sRGB). All others are treated as linear/raw.
COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}

# ARM packed channel layout: R=ambient_occlusion, G=roughness, B=base_metalness
ARM_CHANNELS = {"R": "ambient_occlusion", "G": "roughness", "B": "base_metalness"}


def create_arnold_openpbr(material_name, textures):
    """
    Builds an Arnold openPBRSurface material and connects all PBR texture channels.

    textures: dict mapping OpenPBR identifier names to file paths.
              Use 'arm_packed' for a single ARM-packed texture (AO/Roughness/Metal).
    """
    import maya.cmds as cmds

    material = cmds.shadingNode("openPBRSurface", asShader=True, n=material_name)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=material_name + "_SG")
    cmds.connectAttr(material + ".outColor", sg + ".surfaceShader")

    file_nodes = []

    # ARM packed map
    if "arm_packed" in textures:
        arm_path = textures["arm_packed"]
        tex = cmds.shadingNode("aiImage", asTexture=True)
        cmds.setAttr(tex + ".filename", arm_path, type="string")
        cmds.setAttr(tex + ".colorSpace", "Raw", type="string")
        cmds.setAttr(tex + ".ignoreColorSpaceFileRules", 1)
        file_nodes.append(tex)
        channel_out = {"R": ".outColorR", "G": ".outColorG", "B": ".outColorB"}
        for ch, identifier in ARM_CHANNELS.items():
            attr = "." + _to_camel(identifier)
            try:
                cmds.connectAttr(tex + channel_out[ch], material + attr, force=True)
            except RuntimeError:
                pass

    for identifier, file_path in textures.items():
        if identifier == "arm_packed":
            continue

        is_color = identifier in COLOR_IDENTIFIERS
        tex = cmds.shadingNode("aiImage", asTexture=True)
        cmds.setAttr(tex + ".filename", file_path, type="string")
        cmds.setAttr(tex + ".colorSpace", "sRGB" if is_color else "Raw", type="string")
        cmds.setAttr(tex + ".ignoreColorSpaceFileRules", 1)
        file_nodes.append(tex)

        if identifier in ("normal", "geometry_normal"):
            normal_node = cmds.shadingNode("aiNormalMap", asTexture=True)
            cmds.connectAttr(tex + ".outColor", normal_node + ".input")
            cmds.connectAttr(normal_node + ".outValue", material + ".normalCamera", force=True)

        elif identifier == "bump":
            bump_node = cmds.shadingNode("aiBump2d", asTexture=True)
            cmds.connectAttr(tex + ".outColor", bump_node + ".bumpMap")
            cmds.connectAttr(bump_node + ".outValue", material + ".normalCamera", force=True)

        elif identifier == "displacement":
            disp_node = cmds.shadingNode("displacementShader", asShader=True)
            cmds.connectAttr(tex + ".outColorR", disp_node + ".displacement")
            cmds.connectAttr(disp_node + ".displacement", sg + ".displacementShader")

        else:
            attr = "." + _to_camel(identifier)
            src = ".outColor" if is_color else ".outColorR"
            try:
                cmds.connectAttr(tex + src, material + attr, force=True)
            except RuntimeError:
                pass

    # Shared place2dTexture for all Arnold image nodes
    if file_nodes:
        p2d = cmds.shadingNode("place2dTexture", asUtility=True)
        for tex in file_nodes:
            try:
                cmds.connectAttr(p2d + ".outUV", tex + ".uvcoords")
                cmds.connectAttr(p2d + ".offset.offsetU", tex + ".soffset")
                cmds.connectAttr(p2d + ".offset.offsetV", tex + ".toffset")
                cmds.connectAttr(p2d + ".repeatUV.repeatU", tex + ".sscale")
                cmds.connectAttr(p2d + ".repeatUV.repeatV", tex + ".tscale")
                cmds.connectAttr(p2d + ".mirrorU", tex + ".sflip")
                cmds.connectAttr(p2d + ".mirrorV", tex + ".tflip")
            except RuntimeError:
                pass


def _to_camel(snake_str):
    parts = snake_str.split("_")
    return parts[0] + "".join(x.title() for x in parts[1:])
