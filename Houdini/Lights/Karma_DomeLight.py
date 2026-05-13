# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
# Karma uses LOP (Solaris/USD) nodes exclusively.
# This script always operates inside /stage, redirecting there if needed.
# If a domelight::2.0 LOP node is already selected, its texture is updated instead.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/environment.hdr",
}

# create_karma_dome_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_karma_dome_light(file_path):
    import hou

    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_context = current_pane.pwd()
    is_lop = current_context.childTypeCategory() == hou.lopNodeTypeCategory()

    # Karma always lives in LOP — redirect to /stage if needed
    if not is_lop:
        stage = hou.node("/stage") or hou.node("/").createNode("stage")
        current_context = stage
        current_pane.cd(stage.path())

    sel = hou.selectedNodes()
    found = None

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
