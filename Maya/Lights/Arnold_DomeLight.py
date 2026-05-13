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

# create_arnold_dome_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_arnold_dome_light(hdri_path):
    """
    Creates an Arnold aiSkyDomeLight with the given HDRI.
    If an aiSkyDomeLight is already selected, updates its texture instead.
    """
    import maya.cmds as cmds
    import os

    try:
        if not cmds.pluginInfo("mtoa", query=True, loaded=True):
            cmds.warning("Arnold (mtoa) plugin is not loaded. Enable it via Windows > Plug-in Manager.")
            return
    except RuntimeError:
        cmds.warning("Arnold (mtoa) plugin is not loaded.")
        return

    # Check if an Arnold dome light is selected
    for each in cmds.ls(selection=True):
        try:
            shape = cmds.listRelatives(each, shapes=True)[0]
            if cmds.objectType(shape) == "aiSkyDomeLight":
                connections = cmds.listConnections(shape + ".color") or []
                for c in connections:
                    if cmds.objectType(c) == "file":
                        cmds.setAttr(c + ".fileTextureName", hdri_path, type="string")
                        return
        except (RuntimeError, TypeError):
            pass

    # Create new dome light
    dome_light = cmds.shadingNode("aiSkyDomeLight", asLight=True)
    dome_light = cmds.rename(dome_light, "aiSkyDomeLight")

    file_node = cmds.shadingNode("file", asTexture=True, n=os.path.basename(hdri_path))
    cmds.setAttr(file_node + ".colorSpace", "Raw", type="string")
    cmds.setAttr(file_node + ".ignoreColorSpaceFileRules", 1)
    cmds.setAttr(file_node + ".fileTextureName", hdri_path, type="string")
    cmds.connectAttr(file_node + ".outColor", dome_light + ".color")
    _connect_place2d(file_node)


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
