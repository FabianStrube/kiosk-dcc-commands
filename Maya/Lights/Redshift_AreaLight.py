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

# create_redshift_area_light(EXAMPLE["file_path"], EXAMPLE["light_name"])
# -------------------------------------------------------------------------------

def create_redshift_area_light(file_path, light_name="RSAreaLight"):
    """Creates a Redshift Physical Light and connects a texture to its color input."""
    import maya.cmds as cmds

    try:
        if not cmds.pluginInfo("redshift4maya", query=True, loaded=True):
            cmds.warning("Redshift plugin is not loaded. Enable it via Windows > Plug-in Manager.")
            return
    except RuntimeError:
        cmds.warning("Redshift plugin is not loaded.")
        return

    file_node = cmds.shadingNode("file", asTexture=True, n=light_name + "_tex")
    cmds.setAttr(file_node + ".fileTextureName", file_path, type="string")
    cmds.setAttr(file_node + ".colorSpace", "Raw", type="string")
    cmds.setAttr(file_node + ".ignoreColorSpaceFileRules", 1)
    _connect_place2d(file_node)

    area_light = cmds.shadingNode("RedshiftPhysicalLight", asLight=True)
    area_light = cmds.rename(area_light, light_name)
    cmds.connectAttr(file_node + ".outColor", area_light + ".color")


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
