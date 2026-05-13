# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
#   LOP context → creates a materiallibrary containing a USD MaterialX subnet
#   OBJ / mat   → falls back to /mat
# This material renders with Karma XPU/CPU (Houdini's native renderer).
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "material_name": "ArchPillar_Mat",
    "textures": {
        "base_color":   "/path/to/ArchPillar_BaseColor.png",
        "roughness":    "/path/to/ArchPillar_Roughness.png",
        "metalness":    "/path/to/ArchPillar_Metalness.png",
        "normal":       "/path/to/ArchPillar_Normal.png",
        "displacement": "/path/to/ArchPillar_Displacement.exr",  # optional
        "opacity":      "/path/to/ArchPillar_Opacity.png",       # optional
    },
}

# create_materialx_openpbr(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

import os
import re

COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}


def create_materialx_openpbr(material_name, textures):
    import hou

    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_context = current_pane.pwd()
    is_lop = current_context.childTypeCategory() == hou.lopNodeTypeCategory()
    parent = None

    if is_lop:
        if current_context.type().name() == "materiallibrary":
            parent = current_context
        else:
            try:
                parent = current_context.createNode("materiallibrary")
                parent.moveToGoodPosition()
            except (hou.OperationFailed, hou.PermissionError):
                pass

    if not parent:
        parent = hou.node("/mat") or hou.node("/").createNode("mat")

    builder, out_surface, out_disp = _create_mtlx_subnet(parent, material_name)
    builder.moveToGoodPosition()

    # UV setup
    uv_reader = builder.createNode("usdprimvarreader", "UVAttrib")
    uv_reader.parm("signature").set("float2")
    uv_reader.parm("varname").set("st")

    uv_place = builder.createNode("mtlxplace2d", "UVControl")
    uv_place.setInput(0, uv_reader)

    surface = builder.createNode("mtlxopen_pbr_surface", "mtlxopen_pbr_surface")
    out_surface.setNamedInput("suboutput", surface, "out")

    for identifier, file_path in textures.items():
        is_color = identifier in COLOR_IDENTIFIERS
        file_node = builder.createNode("mtlximage")
        file_node.parm("filecolorspace").set("srgb_tx" if is_color else "Raw")
        file_node.parm("signature").set("color3" if is_color else "float")
        file_node.setNamedInput("texcoord", uv_place, "out")
        file_node.setName(_sanitize(os.path.basename(file_path)), unique_name=True)
        file_node.parm("file").set(file_path)

        if identifier in ("normal", "geometry_normal"):
            file_node.parm("signature").set("vector3")
            normal_node = builder.createNode("mtlxnormalmap")
            normal_node.setInput(0, file_node)
            try:
                surface.setNamedInput("geometry_normal", normal_node, 0)
            except hou.InvalidInput:
                pass
        elif identifier == "bump":
            file_node.parm("signature").set("float")
            bump_node = builder.createNode("mtlxheighttonormal")
            bump_node.setInput(0, file_node)
            try:
                surface.setNamedInput("geometry_normal", bump_node, 0)
            except hou.InvalidInput:
                pass
        elif identifier == "displacement":
            file_node.parm("signature").set("float")
            disp_node = builder.createNode("mtlxdisplacement")
            disp_node.setInput(0, file_node)
            if out_disp:
                out_disp.setNamedInput("suboutput", disp_node, "out")
        else:
            try:
                surface.setNamedInput(identifier, file_node, 0)
            except hou.InvalidInput:
                pass

    builder.layoutChildren()
    current_pane.cd(parent.path())
    builder.setSelected(True, clear_all_selected=True)
    current_pane.homeToSelection()


def _create_mtlx_subnet(parent, name):
    import hou
    builder = parent.createNode("subnet", name)
    builder.setMaterialFlag(True)

    ptg = builder.parmTemplateGroup()
    folder = hou.FolderParmTemplate("mtlxBuilder", "MaterialX+USD Builder",
                                    folder_type=hou.folderType.Collapsible)
    folder.addParmTemplate(hou.IntParmTemplate("inherit_ctrl", "Inherit from Class", 1,
                                               default_value=(2,), menu_items=["0", "1", "2"],
                                               menu_labels=["Never", "Always", "Material Flag"]))
    mask_pt = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1,
                                     default_value=["MaterialX USD parameter constant collect null genericshader subnet subnetconnector suboutput subinput"])
    folder.addParmTemplate(mask_pt)
    ptg.append(folder)
    ptg.append(hou.FloatParmTemplate("uvscale", "UV Scale", 2, default_value=(1, 1)))
    ptg.append(hou.FloatParmTemplate("uvoffset", "UV Offset", 2, default_value=(0, 0)))
    ptg.append(hou.FloatParmTemplate("uvrotate", "UV Rotate", 1))
    builder.setParmTemplateGroup(ptg)

    for c in builder.children():
        c.destroy()

    out_surface = builder.createNode("subnetconnector", "surface_output")
    out_surface.parm("connectorkind").set("output")
    out_surface.parm("parmname").set("surface")
    out_surface.parm("parmlabel").set("Surface")
    out_surface.parm("parmtype").set("surface")

    out_disp = builder.createNode("subnetconnector", "displacement_output")
    out_disp.parm("connectorkind").set("output")
    out_disp.parm("parmname").set("displacement")
    out_disp.parm("parmlabel").set("Displacement")
    out_disp.parm("parmtype").set("displacement")

    return builder, out_surface, out_disp


def _sanitize(name):
    name = os.path.splitext(name)[0]
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    return name or "texture"
