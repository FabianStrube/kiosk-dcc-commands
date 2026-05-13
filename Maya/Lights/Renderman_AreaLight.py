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

# create_renderman_area_light(EXAMPLE["file_path"], EXAMPLE["light_name"])
# -------------------------------------------------------------------------------

def create_renderman_area_light(file_path, light_name="PxrRectLight"):
    """Creates a RenderMan PxrRectLight and assigns a texture to its lightColorMap."""
    import sys
    import maya.cmds as cmds

    try:
        if not cmds.pluginInfo("RenderMan_for_Maya", query=True, loaded=True):
            cmds.warning("RenderMan plugin is not loaded. Enable it via Windows > Plug-in Manager.")
            return
    except RuntimeError:
        cmds.warning("RenderMan plugin is not loaded.")
        return

    # rfm2.api.nodes must be used from the already-initialized plugin module.
    # Re-importing gives a partially-initialized copy that is missing runtime functions.
    rman_nodes = sys.modules.get("rfm2.api.nodes")
    if rman_nodes is None:
        cmds.warning("rfm2.api.nodes is not available — ensure the RenderMan plugin is active.")
        return

    rman_nodes.create_and_select("PxrRectLight")
    selected = cmds.ls(selection=True)[0]
    parent = cmds.listRelatives(selected, parent=True)
    tnode = parent[0] if parent else selected
    tnode = cmds.rename(tnode, light_name)
    snode = cmds.listRelatives(tnode, shapes=True)[0]
    cmds.setAttr(snode + ".lightColorMap", file_path, type="string")
