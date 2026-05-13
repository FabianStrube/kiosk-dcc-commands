# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
#   LOP context → creates a materiallibrary containing a RenderMan subnet
#   OBJ / mat   → creates the subnet directly in /mat or the active context
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

# create_renderman_pxrsurface(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

import os
import re

COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}

# OpenPBR identifier -> PxrSurface input name (same parameter names as the Maya version)
IDENTIFIER_MAP = {
    "base_color":          "diffuseColor",
    "base_metalness":      "metallic",
    "metalness":           "metallic",
    "specular_roughness":  "specularRoughness",
    "roughness":           "specularRoughness",
    "specular_color":      ["specularFaceColor", "specularEdgeColor"],
    "specular_ior":        "specularIor",
    "transmission_weight": "refractionGain",
    "transmission_color":  "refractionColor",
    "subsurface_color":    "subsurfaceColor",
    "emission_color":      "glowColor",
    "coat_weight":         "coatGain",
    "coat_color":          "coatColor",
    "coat_roughness":      "coatRoughness",
    "opacity":             "presence",
}


def create_renderman_pxrsurface(material_name, textures):
    import hou

    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_context = current_pane.pwd()
    is_lop = current_context.childTypeCategory() == hou.lopNodeTypeCategory()
    parent = None

    if current_context.type().name() == "materiallibrary":
        parent = current_context
    elif is_lop:
        try:
            parent = current_context.createNode("materiallibrary")
            parent.moveToGoodPosition()
        except (hou.OperationFailed, hou.PermissionError):
            pass

    if not parent:
        parent = hou.node("/mat") or hou.node("/").createNode("mat")

    builder = parent.createNode("subnet", material_name)
    builder.setMaterialFlag(True)
    builder.moveToGoodPosition()

    # Tag the subnet as a RenderMan material builder
    ptg = builder.parmTemplateGroup()
    folder = hou.FolderParmTemplate("folder1", "RenderMan Material Builder",
                                    folder_type=hou.folderType.Collapsible)
    folder.setTags({"sidefx::shader_isparm": "0"})
    mask_pt = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1,
                                     default_value=["risnet USD ^hmtlx* MaterialX collect parameter subnet null"])
    mask_pt.setTags({"spare_category": "Tab Menu Parameter"})
    folder.addParmTemplate(mask_pt)
    ctx_pt = hou.StringParmTemplate("shader_rendercontextname", "Render Context Name", 1,
                                    default_value=["ri"])
    ctx_pt.setTags({"spare_category": "Shader", "sidefx::shader_isparm": "0"})
    folder.addParmTemplate(ctx_pt)
    ptg.append(folder)
    builder.setParmTemplateGroup(ptg)

    shader = builder.createNode("pxrsurface::3.0", "PxrSurface")
    suboutput = builder.node("suboutput1")
    if suboutput:
        try:
            suboutput.setInput(0, shader)
        except hou.InvalidInput:
            pass

    manifold = builder.createNode("pxrmanifold2d::3.0", "UVManifold")
    bump_node = None

    for identifier, file_path in textures.items():
        is_color = identifier in COLOR_IDENTIFIERS
        tex = builder.createNode("pxrtexture::3.0")
        tex.setName(_sanitize(os.path.basename(file_path)), unique_name=True)
        tex.parm("filename").set(file_path)
        tex.parm("linearize").set(1 if is_color else 0)
        tex.setNamedInput("manifold", manifold, 0)

        if identifier in ("normal", "geometry_normal"):
            normal_node = builder.createNode("pxrnormalmap::3.0")
            normal_node.setNamedInput("inputRGB", tex, "resultRGB")
            if bump_node:
                bump_node.setNamedInput("inputN", normal_node, "resultN")
            else:
                shader.setNamedInput("bumpNormal", normal_node, "resultN")
        elif identifier == "bump":
            bump_node = builder.createNode("pxrbump::3.0")
            bump_node.setNamedInput("inputBump", tex, "resultR")
            shader.setNamedInput("bumpNormal", bump_node, "resultN")
        elif identifier == "displacement":
            disp_node = builder.createNode("pxrdisplace::3.0")
            disp_node.setNamedInput("dispScalar", tex, "resultR")
            if suboutput:
                try:
                    suboutput.setInput(1, disp_node)
                except hou.InvalidInput:
                    pass
        else:
            pxr_inputs = IDENTIFIER_MAP.get(identifier)
            if pxr_inputs:
                if isinstance(pxr_inputs, str):
                    pxr_inputs = [pxr_inputs]
                src = "resultRGB" if is_color else "resultR"
                for pxr_input in pxr_inputs:
                    try:
                        shader.setNamedInput(pxr_input, tex, src)
                    except hou.InvalidInput:
                        pass

    builder.layoutChildren()
    current_pane.cd(parent.path())
    builder.setSelected(True, clear_all_selected=True)
    current_pane.homeToSelection()


def _sanitize(name):
    name = os.path.splitext(name)[0]
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    return name or "texture"
