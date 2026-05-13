# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/asset.mb",
}

# reference_asset(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def reference_asset(file_path):
    """Prompts for a namespace and references the file into the current scene."""
    import maya.cmds as cmds

    result = cmds.promptDialog(
        title='Namespace',
        message='Enter namespace for the reference:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel'
    )

    if result == 'OK':
        namespace = cmds.promptDialog(query=True, text=True)
        cmds.file(file_path, reference=True, namespace=namespace)
