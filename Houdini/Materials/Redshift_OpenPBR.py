# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================
#
# IMPORTANT — Houdini context:
# Works in both OBJ/mat and LOP contexts via rs_usd_material_builder.
# The node is created in the active context when possible; falls back to /mat.
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

# create_redshift_openpbr(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

import os
import re

COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}
ARM_CHANNELS = {"R": "ambient_occlusion", "G": "roughness", "B": "base_metalness"}


def create_redshift_openpbr(material_name, textures):
    import hou

    current_pane = hou.ui.curDesktop().paneTabOfType(hou.paneTabType.NetworkEditor)
    current_context = current_pane.pwd()
    is_lop = current_context.childTypeCategory() == hou.lopNodeTypeCategory()
    parent = None

    try:
        test = current_context.createNode("rs_usd_material_builder")
        test.destroy()
        parent = current_context
    except (hou.OperationFailed, hou.PermissionError):
        pass

    if not parent:
        if is_lop:
            try:
                parent = current_context.createNode("materiallibrary")
                parent.moveToGoodPosition()
            except (hou.OperationFailed, hou.PermissionError):
                pass
        if not parent:
            parent = hou.node("/mat") or hou.node("/").createNode("mat")

    builder = parent.createNode("rs_usd_material_builder")
    builder.setName(material_name, unique_name=True)
    builder.moveToGoodPosition()

    # Remove default shader nodes, keep output
    sg = None
    for child in builder.children():
        if child.type().name() in ("redshift_material", "redshift_usd_material"):
            sg = child
        else:
            child.destroy()

    shader = builder.createNode("redshift::OpenPBRMaterial")
    if sg:
        sg.setInput(0, shader)

    raw_space, srgb_space = _get_ocio_spaces()

    # ARM packed map
    if "arm_packed" in textures:
        tex = builder.createNode("redshift::TextureSampler")
        tex.setName(_sanitize(os.path.basename(textures["arm_packed"])), unique_name=True)
        tex.parm("tex0").set(textures["arm_packed"])
        tex.parm("tex0_colorSpace").set(raw_space)
        splitter = builder.createNode("redshift::RSColorSplitter")
        splitter.setInput(0, tex)
        channel_out = {"R": 0, "G": 1, "B": 2}
        for ch, identifier in ARM_CHANNELS.items():
            try:
                shader.setNamedInput(identifier, splitter, channel_out[ch])
            except hou.InvalidInput:
                pass

    for identifier, file_path in textures.items():
        if identifier == "arm_packed":
            continue
        is_color = identifier in COLOR_IDENTIFIERS
        tex = builder.createNode("redshift::TextureSampler")
        tex.setName(_sanitize(os.path.basename(file_path)), unique_name=True)
        tex.parm("tex0").set(file_path)
        tex.parm("tex0_colorSpace").set(srgb_space if is_color else raw_space)

        if identifier in ("normal", "geometry_normal"):
            normal_node = builder.createNode("redshift::BumpMap")
            normal_node.parm("inputType").set("1")  # tangent-space normal
            normal_node.setNamedInput("input", tex, 0)
            shader.setNamedInput("geometry_normal", normal_node, 0)
        elif identifier == "bump":
            bump_node = builder.createNode("redshift::BumpMap")
            bump_node.setNamedInput("input", tex, 0)
            if sg:
                sg.setNamedInput("Bump", bump_node, 0)
        elif identifier == "displacement":
            disp_node = builder.createNode("redshift::Displacement")
            disp_node.setNamedInput("texMap", tex, 0)
            if sg:
                sg.setNamedInput("Displacement", disp_node, 0)
        else:
            try:
                shader.setNamedInput(identifier, tex, 0)
            except hou.InvalidInput:
                pass

    # Shared UV context projection
    uv_proj = builder.createNode("redshift::UVContextProjection")
    shader.setNamedInput("rs_uv_context", uv_proj, 0)

    builder.layoutChildren()
    current_pane.cd(parent.path())
    builder.setSelected(True, clear_all_selected=True)
    current_pane.homeToSelection()


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
