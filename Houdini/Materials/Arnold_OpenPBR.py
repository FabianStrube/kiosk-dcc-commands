# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
#   OBJ / mat context → builds an arnold_materialbuilder with an arnold::openpbr_surface
#   LOP context       → builds a USD MaterialX subnet (arnold::mtlximage nodes)
# The active network editor context determines which branch runs.
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
        # For ARM-packed textures (AO/Roughness/Metal in one file):
        # "arm_packed": "/path/to/ArchPillar_ARM.png",
    },
}

# create_arnold_openpbr(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

import os
import re

COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}
ARM_CHANNELS = {"R": "ambient_occlusion", "G": "roughness", "B": "base_metalness"}


def create_arnold_openpbr(material_name, textures):
    import hou
    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_context = current_pane.pwd()
    is_lop = (current_context.childTypeCategory() == hou.lopNodeTypeCategory()
              or "stage" in current_context.path().lower())

    if is_lop:
        _build_lop(material_name, textures, current_context, current_pane)
    else:
        _build_obj(material_name, textures, current_context, current_pane)


# ---------------------------------------------------------------------------
# OBJ / mat context — arnold_materialbuilder + arnold::openpbr_surface
# ---------------------------------------------------------------------------

def _build_obj(material_name, textures, current_context, current_pane):
    import hou

    parent = None
    try:
        test = current_context.createNode("arnold_materialbuilder")
        test.destroy()
        parent = current_context
    except (hou.OperationFailed, hou.PermissionError):
        pass

    if not parent:
        parent = hou.node("/mat") or hou.node("/").createNode("mat")

    builder = parent.createNode("arnold_materialbuilder")
    builder.setName(material_name, unique_name=True)
    builder.moveToGoodPosition()

    shader = builder.createNode("arnold::openpbr_surface")
    out_material = hou.node(f"{builder.path()}/OUT_material")
    out_material.setNamedInput("surface", shader, 0)

    uv_transform = builder.createNode("arnold::uv_transform")
    uv_transform.setName("uv_transform", unique_name=True)
    bump_node = None

    raw_space, srgb_space = _get_ocio_spaces()

    # ARM packed map
    if "arm_packed" in textures:
        tex = builder.createNode("arnold::image")
        tex.setName(_sanitize(os.path.basename(textures["arm_packed"])), unique_name=True)
        tex.parm("filename").set(textures["arm_packed"])
        tex.setNamedInput("uvcoords", uv_transform, 0)
        hou.hscript(f"opparm {tex.path()} color_family (Utility)")
        tex.parm("color_space").set(raw_space)
        channel_out = {"R": 1, "G": 2, "B": 3}
        for ch, identifier in ARM_CHANNELS.items():
            try:
                shader.setNamedInput(identifier, tex, channel_out[ch])
            except hou.InvalidInput:
                pass

    for identifier, file_path in textures.items():
        if identifier == "arm_packed":
            continue
        is_color = identifier in COLOR_IDENTIFIERS
        tex = builder.createNode("arnold::image")
        tex.setName(_sanitize(os.path.basename(file_path)), unique_name=True)
        tex.parm("filename").set(file_path)
        tex.setNamedInput("uvcoords", uv_transform, 0)
        hou.hscript(f"opparm {tex.path()} color_family (Utility)")
        tex.parm("color_space").set(srgb_space if is_color else raw_space)

        if identifier in ("normal", "geometry_normal"):
            normal_node = builder.createNode("arnold::normal_map")
            normal_node.setInput(0, tex)
            if bump_node:
                bump_node.setNamedInput("geometry_normal", normal_node, 0)
            else:
                shader.setNamedInput("geometry_normal", normal_node, 0)
        elif identifier == "bump":
            bump_node = builder.createNode("arnold::bump2d")
            bump_node.setInput(0, tex)
            shader.setNamedInput("normal", bump_node, 0)
        elif identifier == "displacement":
            out_material.setNamedInput("displacement", tex, 0)
        else:
            try:
                shader.setNamedInput(identifier, tex, 0)
            except hou.InvalidInput:
                pass

    builder.layoutChildren()
    current_pane.cd(parent.path())
    builder.setSelected(True, clear_all_selected=True)
    current_pane.homeToSelection()


# ---------------------------------------------------------------------------
# LOP context — USD MaterialX subnet with arnold::mtlximage nodes
# ---------------------------------------------------------------------------

def _build_lop(material_name, textures, current_context, current_pane):
    import hou

    if current_context.type().name() == "materiallibrary":
        parent = current_context
    else:
        try:
            parent = current_context.createNode("materiallibrary")
            parent.moveToGoodPosition()
        except (hou.OperationFailed, hou.PermissionError):
            parent = hou.node("/mat") or hou.node("/").createNode("mat")

    builder, out_surface, out_disp = _create_arnold_lop_subnet(parent, material_name)
    builder.moveToGoodPosition()

    uv_reader = builder.createNode("usdprimvarreader", "UVAttrib")
    uv_reader.parm("signature").set("float2")
    uv_reader.parm("varname").set("st")

    surface = builder.createNode("mtlxopen_pbr_surface", "mtlxopen_pbr_surface")
    out_surface.setNamedInput("suboutput", surface, "out")

    raw_space, srgb_space = _get_ocio_spaces()

    if "arm_packed" in textures:
        file_node = builder.createNode("arnold::mtlximage")
        file_node.parm("filenamecolorspace").set("Raw")
        file_node.parm("signature").set("color3")
        file_node.setNamedInput("uvcoords", uv_reader, 0)
        file_node.setName(_sanitize(os.path.basename(textures["arm_packed"])), unique_name=True)
        file_node.parm("filename").set(textures["arm_packed"])
        splitter = builder.createNode("mtlxseparate3c")
        splitter.setInput(0, file_node)
        channel_out = {"R": "outr", "G": "outg", "B": "outb"}
        for ch, identifier in ARM_CHANNELS.items():
            try:
                surface.setNamedInput(identifier, splitter, channel_out[ch])
            except hou.InvalidInput:
                pass

    for identifier, file_path in textures.items():
        if identifier == "arm_packed":
            continue
        is_color = identifier in COLOR_IDENTIFIERS
        file_node = builder.createNode("arnold::mtlximage")
        file_node.parm("filenamecolorspace").set(srgb_space if is_color else "Raw")
        file_node.parm("signature").set("color3" if is_color else "float")
        file_node.setNamedInput("uvcoords", uv_reader, 0)
        file_node.setName(_sanitize(os.path.basename(file_path)), unique_name=True)
        file_node.parm("filename").set(file_path)

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


def _create_arnold_lop_subnet(parent, name):
    import hou
    builder = parent.createNode("subnet", name)
    builder.setMaterialFlag(True)

    ptg = builder.parmTemplateGroup()
    folder = hou.FolderParmTemplate("folder1", "USD MaterialX Builder (Arnold)",
                                    folder_type=hou.folderType.Collapsible)
    folder.addParmTemplate(hou.IntParmTemplate("inherit_ctrl", "Inherit from Class", 1,
                                               default_value=(2,), menu_items=["0", "1", "2"],
                                               menu_labels=["Never", "Always", "Material Flag"]))
    arc_pt = hou.StringParmTemplate("shader_referencetype", "Class Arc", 1, default_value=["inherit"],
                                    menu_items=["reference", "inherit", "specialize", "represent"],
                                    menu_labels=["Reference", "Inherit", "Specialize", "Represent"])
    arc_pt.setTags({"spare_category": "Shader", "shader_isparm": "0"})
    folder.addParmTemplate(arc_pt)
    base_pt = hou.StringParmTemplate("shader_baseprimpath", "Class Prim Path", 1,
                                     default_value=["/__class_mtl__/`$OS`"])
    base_pt.setTags({"spare_category": "Shader", "shader_isparm": "0"})
    folder.addParmTemplate(base_pt)
    mask_pt = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1,
                                     default_value=["ArnoldMaterialX MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"])
    mask_pt.setTags({"spare_category": "Tab Menu"})
    folder.addParmTemplate(mask_pt)
    ctx_pt = hou.StringParmTemplate("shader_rendercontextname", "Render Context Name", 1,
                                    default_value=["mtlx"])
    ctx_pt.setTags({"spare_category": "Shader", "shader_isparm": "0"})
    folder.addParmTemplate(ctx_pt)
    ptg.append(folder)
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


def _get_ocio_spaces():
    try:
        import PyOpenColorIO as OCIO
        import hou
        config = OCIO.Config.CreateFromFile(hou.Color.ocio_configPath())
        raw = config.getColorSpace("data")
        raw_name = raw.getName() if raw else "Raw"
        for candidate in ("sRGB - Texture", "srgb_texture", "Utility - sRGB - Texture", "sRGB"):
            space = config.getColorSpace(candidate)
            if space and "acescc" not in space.getName().lower():
                return raw_name, space.getName()
        return raw_name, "sRGB"
    except Exception:
        return "Raw", "sRGB"


def _sanitize(name):
    name = os.path.splitext(name)[0]
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    return name or "texture"
