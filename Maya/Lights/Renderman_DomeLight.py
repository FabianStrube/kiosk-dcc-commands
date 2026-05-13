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

# create_renderman_dome_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_renderman_dome_light(hdri_path):
    """
    Creates a RenderMan PxrDomeLight with the given HDRI.
    If a PxrDomeLight is already selected, updates its lightColorMap instead.
    """
    import sys
    import maya.cmds as cmds

    try:
        if not cmds.pluginInfo("RenderMan_for_Maya", query=True, loaded=True):
            cmds.warning("RenderMan plugin is not loaded. Enable it via Windows > Plug-in Manager.")
            return
    except RuntimeError:
        cmds.warning("RenderMan plugin is not loaded.")
        return

    # Check if a PxrDomeLight is already selected
    for each in cmds.ls(selection=True):
        try:
            shape = cmds.listRelatives(each, shapes=True)[0]
            if cmds.objectType(shape) == "PxrDomeLight":
                cmds.setAttr(shape + ".lightColorMap", hdri_path, type="string")
                return
        except (RuntimeError, TypeError):
            pass

    # rfm2.api.nodes must be used from the already-initialized plugin module.
    rman_nodes = sys.modules.get("rfm2.api.nodes")
    if rman_nodes is None:
        cmds.warning("rfm2.api.nodes is not available — ensure the RenderMan plugin is active.")
        return

    rman_nodes.create_and_select("PxrDomeLight")
    selected = cmds.ls(selection=True)[0]
    parent = cmds.listRelatives(selected, parent=True)
    tnode = parent[0] if parent else selected
    dome_shape = cmds.listRelatives(tnode, shapes=True)[0]
    cmds.setAttr(dome_shape + ".lightColorMap", hdri_path, type="string")
