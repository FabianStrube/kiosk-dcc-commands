# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
# This script targets the OBJ context and creates a pxrdomelight::3.0 node.
# If a PxrDomeLight is already selected, its texture is updated instead.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/environment.hdr",
}

# create_renderman_dome_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_renderman_dome_light(file_path):
    import hou

    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_context = current_pane.pwd()
    sel = hou.selectedNodes()
    found = None

    for node in sel:
        try:
            if node.type().name() == "pxrdomelight::3.0":
                found = node
                break
        except (AttributeError, hou.OperationFailed):
            pass

    if found:
        found.parm("lightColorMap").set(file_path)
    else:
        dome = current_context.createNode("pxrdomelight::3.0", node_name="pxrdomelight")
        dome.parm("lightColorMap").set(file_path)
        dome.moveToGoodPosition()
