# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/asset.fbx",
}

# import_asset(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def import_asset(file_path):
    import maya.cmds as cmds
    import os

    extension = os.path.splitext(file_path)[1].lstrip(".").lower()

    maya_import_types = {
        "ma":   "MayaAscii",
        "mb":   "MayaBinary",
        "obj":  "OBJ",
        "fbx":  "FBX",
        "abc":  "Alembic",
        "usd":  "USD Import",
        "usda": "USD Import",
        "usdc": "USD Import",
        "usdz": "USD Import",
    }

    if extension in ("usd", "usda", "usdc", "usdz"):
        try:
            if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
                cmds.loadPlugin("mayaUsdPlugin")
        except RuntimeError:
            cmds.warning("mayaUsdPlugin could not be loaded. USD import is unavailable.")
            return

    if extension in maya_import_types:
        cmds.file(file_path, i=True, type=maya_import_types[extension],
                  ignoreVersion=True, ra=True, mergeNamespacesOnClash=False,
                  namespace=":", options="v=0;", pr=True)
    else:
        cmds.warning(f"Unknown import format: {extension}")
