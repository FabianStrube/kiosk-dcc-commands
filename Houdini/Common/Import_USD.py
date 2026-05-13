# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
# These functions target the LOP (Solaris/USD) network inside /stage.
# Run them when the active network editor is inside a LOP network.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/scene.usd",
    "asset_name": "ArchPillar",
}

# As a sublayer (adds the USD file as a layer on top of the current stage):
# import_usd_sublayer(EXAMPLE["file_path"], EXAMPLE["asset_name"])

# As a reference (scenegraph reference, preserves hierarchy):
# import_usd_reference(EXAMPLE["file_path"], EXAMPLE["asset_name"])
# -------------------------------------------------------------------------------

def import_usd_sublayer(file_path, asset_name="sublayer"):
    """Adds a USD file as a sublayer inside the active LOP context."""
    import hou
    stage = hou.node("/stage") or hou.node("/").createNode("stage")
    node = stage.createNode("sublayer")
    node.parm("filepath1").set(file_path)
    node.setName("sublayer_" + asset_name, unique_name=True)
    node.moveToGoodPosition()


def import_usd_reference(file_path, asset_name="reference"):
    """Adds a USD file as a scene-graph reference inside the active LOP context."""
    import hou
    stage = hou.node("/stage") or hou.node("/").createNode("stage")
    node = stage.createNode("reference::2.0")
    node.parm("filepath1").set(file_path)
    node.setName("reference_" + asset_name, unique_name=True)
    node.moveToGoodPosition()
