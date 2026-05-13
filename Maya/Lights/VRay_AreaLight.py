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
    "light_name": "KeyLight",
}

# create_vray_area_light(EXAMPLE["file_path"], EXAMPLE["light_name"])
# -------------------------------------------------------------------------------

def create_vray_area_light(file_path, light_name="VRayAreaLight"):
    """Creates a V-Ray rect light and connects a texture to its rect texture input."""
    import maya.cmds as cmds

    try:
        if not cmds.pluginInfo("vrayformaya", query=True, loaded=True):
            cmds.warning("V-Ray plugin is not loaded. Enable it via Windows > Plug-in Manager.")
            return
    except RuntimeError:
        cmds.warning("V-Ray plugin is not loaded.")
        return

    file_node = cmds.shadingNode("file", asTexture=True, n=light_name + "_tex")
    cmds.setAttr(file_node + ".fileTextureName", file_path, type="string")
    cmds.setAttr(file_node + ".colorSpace", "Raw", type="string")
    cmds.setAttr(file_node + ".ignoreColorSpaceFileRules", 1)
    _connect_place2d(file_node)

    area_light = cmds.shadingNode("VRayLightRectShape", asLight=True)
    area_light = cmds.rename(area_light, light_name)
    area_light_shape = cmds.listRelatives(area_light, shapes=True, fullPath=True)[0]
    cmds.setAttr(area_light_shape + ".useRectTex", 1)
    cmds.connectAttr(file_node + ".outColor", area_light_shape + ".rectTex")


def _connect_place2d(file_node):
    import maya.cmds as cmds
    p2d = cmds.shadingNode("place2dTexture", asUtility=True)
    attrs = [
        "outUV", "outUvFilterSize", "vertexCameraOne",
        "vertexUvOne", "vertexUvThree", "vertexUvTwo",
        "coverage", "mirrorU", "mirrorV", "noiseUV",
        "offset", "repeatUV", "rotateFrame", "rotateUV",
        "stagger", "translateFrame", "wrapU", "wrapV",
    ]
    targets = [
        "uvCoord", "uvFilterSize", "vertexCameraOne",
        "vertexUvOne", "vertexUvThree", "vertexUvTwo",
        "coverage", "mirrorU", "mirrorV", "noiseUV",
        "offset", "repeatUV", "rotateFrame", "rotateUV",
        "stagger", "translateFrame", "wrapU", "wrapV",
    ]
    for src, tgt in zip(attrs, targets):
        cmds.connectAttr(p2d + "." + src, file_node + "." + tgt)
