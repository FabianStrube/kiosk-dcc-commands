# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
# This script targets the OBJ context and creates a pxrrectlight::3.0 node.
# If a PxrRectLight is already selected, its texture is updated instead.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/light_texture.exr",
}

# create_renderman_area_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_renderman_area_light(file_path):
    import hou

    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_context = current_pane.pwd()
    sel = hou.selectedNodes()

    for node in sel:
        try:
            if node.type().name() == "pxrrectlight::3.0":
                node.parm("lightColorMap").set(file_path)
                return
        except (AttributeError, hou.OperationFailed):
            pass

    light = current_context.createNode("pxrrectlight::3.0", node_name="area_light")
    light.parm("lightColorMap").set(file_path)
    light.moveToGoodPosition()
