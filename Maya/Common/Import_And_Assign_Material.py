# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/material.mb",
}

# Select the mesh objects you want to receive the material, then run:
# import_and_assign_material(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def import_and_assign_material(file_path):
    """Imports a Maya Binary material file and assigns it to the current selection."""
    import maya.cmds as cmds

    selected_objects = cmds.ls(selection=True)

    imported_nodes = cmds.file(
        file_path, i=True, type="mayaBinary",
        ignoreVersion=True, ra=True,
        mergeNamespacesOnClash=False, returnNewNodes=True
    )
    materials = cmds.ls(imported_nodes, materials=True)

    if not materials:
        cmds.warning("No materials found in the imported file.")
        return

    if not selected_objects:
        selected_objects = cmds.ls(type="transform")

    material = materials[0]
    shading_group = cmds.listConnections(material + '.outColor', type='shadingEngine')[0]

    def has_valid_shape(obj):
        shapes = cmds.listRelatives(obj, shapes=True)
        return shapes and cmds.nodeType(shapes[0]) != "defaultGeometry"

    for obj in selected_objects:
        if not has_valid_shape(obj):
            cmds.warning(f"Object {obj} has no shape node. Skipping.")
            continue
        cmds.sets(obj, edit=True, forceElement=shading_group)
