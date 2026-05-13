# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/texture.png",
    "node_name": "ArchPillar_BaseColor",
    "is_sequence": False,  # set True for image sequences
}

# create_file_node(EXAMPLE["file_path"], EXAMPLE["node_name"], EXAMPLE["is_sequence"])
# -------------------------------------------------------------------------------

def create_file_node(file_path, node_name="fileNode", is_sequence=False):
    """Creates a file texture node wired to a place2dTexture, ready to connect to a shader."""
    import maya.cmds as cmds

    file_node = cmds.shadingNode("file", asTexture=True, n=node_name)
    cmds.setAttr(file_node + ".fileTextureName", file_path, type="string")

    if is_sequence:
        cmds.setAttr(file_node + ".useFrameExtension", 1)

    p2d = cmds.shadingNode("place2dTexture", asUtility=True)
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

    return file_node
