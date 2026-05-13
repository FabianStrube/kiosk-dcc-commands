# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
#   OBJ context → creates an rslight node
#   LOP context → creates a light::2.0 LOP node (USD, render-delegate agnostic)
# If a Redshift area light is already selected, its texture is updated instead.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/light_texture.exr",
}

# create_redshift_area_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_redshift_area_light(file_path):
    import hou

    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_context = current_pane.pwd()
    is_lop = current_context.childTypeCategory() == hou.lopNodeTypeCategory()
    sel = hou.selectedNodes()

    if not is_lop:
        for node in sel:
            try:
                if node.type().name() == "rslight":
                    node.parm("TextureSampler1_tex0").set(file_path)
                    return
            except (AttributeError, hou.OperationFailed):
                pass

        light = current_context.createNode("rslight", node_name="area_light")
        light.parm("RSColorLayer1_layer1_enable").set(1)
        light.parm("TextureSampler1_tex0").set(file_path)
        light.parm("TextureSampler1_tex0_colorSpace").set("Raw")
        light.moveToGoodPosition()

    else:
        for node in sel:
            try:
                if node.type().name() == "light::2.0" and node.parent() == current_context:
                    node.parm("xn__inputstexturefile_r3ah").set(file_path)
                    return
            except (AttributeError, hou.OperationFailed):
                pass

        light = current_context.createNode("light::2.0", node_name="area_light")
        light.parm("lighttype").set(4)
        light.parm("xn__inputstexturefile_r3ah").set(file_path)
        lop_sel = [n for n in sel if n.parent() == current_context]
        if lop_sel:
            light.setInput(0, lop_sel[-1])
        light.moveToGoodPosition()
