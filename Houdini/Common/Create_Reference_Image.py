# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
# refimage is a SOP node. This script creates the SOP inside the currently
# active context. If the active context is at OBJ level, a new geo container
# is created first.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/reference.png",
    "is_sequence": False,  # set True for image sequences (e.g. frame_0001.png)
}

# create_reference_image(EXAMPLE["file_path"], EXAMPLE["is_sequence"])
# -------------------------------------------------------------------------------

import os
import re


def create_reference_image(file_path, is_sequence=False):
    """Creates a refimage SOP and handles image sequences with $F padding tokens."""
    import hou

    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    context_node = current_pane.pwd()

    # refimage is a SOP — wrap in a geo container if we are at OBJ level
    if context_node.childTypeCategory() == hou.objNodeTypeCategory():
        node_name = os.path.splitext(os.path.basename(file_path))[0].replace(".", "_")
        geo_node = context_node.createNode("geo", node_name=node_name)
        parent = geo_node
    else:
        parent = context_node

    try:
        ref_node = parent.createNode("refimage", node_name="ref_image")
    except Exception as e:
        hou.ui.displayMessage(f"Could not create refimage node: {e}", severity=hou.severityType.Error)
        return

    # Convert sequence path to Houdini $F token (e.g. frame_0001.png -> frame_$F4.png)
    final_path = file_path
    if is_sequence:
        basename = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        match = re.match(r"^(.*?)(\d+)(\.\w+)$", basename)
        if match:
            prefix, frame_num, ext = match.group(1), match.group(2), match.group(3)
            padding = len(frame_num)
            token = f"$F{padding}" if padding > 1 else "$F"
            final_path = os.path.join(directory, f"{prefix}{token}{ext}").replace("\\", "/")

    ref_node.parm("file").set(final_path)
    ref_node.setDisplayFlag(True)
    ref_node.setRenderFlag(True)
    ref_node.moveToGoodPosition()
