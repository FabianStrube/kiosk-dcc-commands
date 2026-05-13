# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context sensitivity:
# This script detects the active network editor context and creates different
# node types accordingly:
#   OBJ context  → creates a geo container with a file/alembic SOP inside
#   SOP context  → creates a file or alembic SOP directly
#   LOP context  → creates an assetreference LOP node (USD)
#   FBX (any)    → always imports via hou.hipFile.importFBX into /obj
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/asset.fbx",
    "asset_name": "ArchPillar",
}

# import_asset(EXAMPLE["file_path"], EXAMPLE["asset_name"])
# -------------------------------------------------------------------------------

import os
import re


def import_asset(file_path, asset_name=None):
    import hou

    if asset_name is None:
        asset_name = _sanitize(os.path.splitext(os.path.basename(file_path))[0])

    ext = os.path.splitext(file_path)[1].lower()

    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_context = current_pane.pwd()

    is_lop = current_context.childTypeCategory() == hou.lopNodeTypeCategory()
    is_sop = current_context.childTypeCategory() == hou.sopNodeTypeCategory()
    is_obj = current_context.childTypeCategory() == hou.objNodeTypeCategory()

    # FBX always uses the dedicated importer which lands nodes in /obj
    if ext == ".fbx":
        if is_sop:
            node = current_context.createNode("file")
            node.setName(asset_name, unique_name=True)
            node.parm("file").set(file_path)
            node.moveToGoodPosition()
        else:
            obj_context = hou.node("/obj")
            before = {c.path() for c in obj_context.children()}
            hou.hipFile.importFBX(file_path)
            new_nodes = [c for c in obj_context.children() if c.path() not in before]
            if new_nodes:
                new_nodes[0].setName(asset_name, unique_name=True)
                current_pane.cd(obj_context.path())
        return

    # LOP (Solaris / USD stage) — assetreference node
    if is_lop:
        node = current_context.createNode("assetreference")
        node.setName(asset_name, unique_name=True)
        node.parm("filepath").set(file_path)
        lop_sel = [n for n in hou.selectedNodes() if n.parent() == current_context]
        if lop_sel:
            node.setInput(0, lop_sel[-1])
        node.moveToGoodPosition()
        return

    # SOP context — file or alembic SOP directly inside the current geo node
    if is_sop:
        node_type = "alembic" if ext == ".abc" else "file"
        parm_name = "fileName" if ext == ".abc" else "file"
        node = current_context.createNode(node_type)
        node.setName(asset_name, unique_name=True)
        node.parm(parm_name).set(file_path)
        node.moveToGoodPosition()
        return

    # OBJ context (or fallback) — wrap inside a geo container
    parent = current_context if is_obj else hou.node("/obj")
    geo = parent.createNode("geo")
    geo.setName(asset_name, unique_name=True)
    for child in geo.children():
        child.destroy()
    node_type = "alembic" if ext == ".abc" else "file"
    parm_name = "fileName" if ext == ".abc" else "file"
    inner = geo.createNode(node_type)
    inner.setName(asset_name, unique_name=True)
    inner.parm(parm_name).set(file_path)
    inner.moveToGoodPosition()
    geo.moveToGoodPosition()


def _sanitize(name):
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if name and name[0].isdigit():
        name = "_" + name
    return name or "asset"
