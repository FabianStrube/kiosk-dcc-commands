# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
#   OBJ context → creates an rslightdome::2.0 node
#   LOP context → creates a domelight::2.0 LOP node (USD, render-delegate agnostic)
# If a dome light is already selected, its texture is updated instead.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/environment.hdr",
}

# create_redshift_dome_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_redshift_dome_light(file_path):
    import hou

    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_context = current_pane.pwd()
    is_lop = current_context.childTypeCategory() == hou.lopNodeTypeCategory()
    sel = hou.selectedNodes()
    found = None

    if not is_lop:
        for node in sel:
            try:
                if node.type().name() == "rslightdome::2.0":
                    found = node
                    break
            except (AttributeError, hou.OperationFailed):
                pass

        if found:
            found.parm("env_map").set(file_path)
        else:
            dome = current_context.createNode("rslightdome::2.0")
            dome.parm("env_map").set(file_path)
            dome.moveToGoodPosition()

    else:
        for node in sel:
            try:
                if node.type().name() == "domelight::2.0":
                    found = node
                    break
            except (AttributeError, hou.OperationFailed):
                pass

        if found:
            found.parm("xn__inputstexturefile_r3ah").set(file_path)
        else:
            dome = current_context.createNode("domelight::2.0")
            dome.parm("xn__inputstexturefile_r3ah").set(file_path)
            lop_sel = [n for n in sel if n.parent() == current_context]
            if lop_sel:
                dome.setInput(0, lop_sel[-1])
            dome.moveToGoodPosition()
