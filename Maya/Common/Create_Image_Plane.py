# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/reference.png",
    "is_sequence": False,  # set True for image sequences (e.g. frame_####.png)
}

# create_image_plane(EXAMPLE["file_path"], EXAMPLE["is_sequence"])
# -------------------------------------------------------------------------------

def create_image_plane(file_path, is_sequence=False):
    """Creates an image plane attached to the persp camera."""
    import maya.cmds as cmds

    results = cmds.imagePlane(fileName=file_path, camera="persp", showInAllViews=True)

    if results:
        ip_node = results[1]  # shape node
        if is_sequence:
            cmds.setAttr(f"{ip_node}.useFrameExtension", 1)
