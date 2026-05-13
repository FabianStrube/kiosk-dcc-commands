# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/scene.usd",
    "asset_name": "ArchPillar",
}

# import_usd_stage(EXAMPLE["file_path"], EXAMPLE["asset_name"])
# -------------------------------------------------------------------------------

def import_usd_stage(file_path, asset_name):
    """Creates a mayaUsdProxyShape that streams the USD file as a live stage."""
    import maya.cmds as cmds
    import os

    extension = os.path.splitext(file_path)[1].lstrip(".").lower()

    if extension not in ("usd", "usda", "usdc", "usdz"):
        cmds.warning(f"Unsupported format for USD stage: {extension}")
        return

    try:
        if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
            cmds.loadPlugin("mayaUsdPlugin")

        shape_node = cmds.createNode('mayaUsdProxyShape', name=f"{asset_name}Shape")
        transform_node = cmds.listRelatives(shape_node, parent=True)[0]
        cmds.rename(transform_node, asset_name)
        cmds.setAttr(f"{shape_node}.filePath", file_path, type="string")
    except RuntimeError:
        cmds.warning("mayaUsdPlugin could not be loaded. USD import is unavailable.")
