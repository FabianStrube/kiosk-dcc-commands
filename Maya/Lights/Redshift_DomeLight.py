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

# create_redshift_dome_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_redshift_dome_light(hdri_path):
    """
    Creates a Redshift dome light with the given HDRI.
    If a RedshiftDomeLight is already selected, updates its texture instead.
    """
    import maya.cmds as cmds

    try:
        if not cmds.pluginInfo("redshift4maya", query=True, loaded=True):
            cmds.warning("Redshift plugin is not loaded. Enable it via Windows > Plug-in Manager.")
            return
    except RuntimeError:
        cmds.warning("Redshift plugin is not loaded.")
        return

    # Check if a Redshift dome light is already selected
    for each in cmds.ls(selection=True):
        try:
            shape = cmds.listRelatives(each, shapes=True)[0]
            if cmds.objectType(shape) == "RedshiftDomeLight":
                cmds.setAttr(shape + ".tex0", hdri_path, type="string")
                return
        except (RuntimeError, TypeError):
            pass

    # Create new dome light
    dome_light = cmds.shadingNode("RedshiftDomeLight", asLight=True)
    cmds.setAttr(dome_light + ".tex0", hdri_path, type="string")
