# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
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

# create_principled_bsdf(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}

# OpenPBR identifier -> Principled BSDF input socket name
IDENTIFIER_TO_BSDF = {
    "base_color":         "Base Color",
    "diffuse":            "Base Color",
    "metalness":          "Metallic",
    "base_metalness":     "Metallic",
    "metallic":           "Metallic",
    "specular_roughness": "Roughness",
    "roughness":          "Roughness",
    "specular_ior":       "IOR",
    "ior":                "IOR",
    "opacity":            "Alpha",
    "transmission_weight":"Transmission Weight",
    "emission_color":     "Emission Color",
    "coat_weight":        "Coat Weight",
    "coat_roughness":     "Coat Roughness",
    "coat_normal":        "Coat Normal",
    "specular_weight":    "Specular IOR Level",
    "specular_color":     "Specular Tint",
    "subsurface_weight":  "Subsurface Weight",
}


def create_principled_bsdf(material_name, textures):
    """
    Builds a Cycles/EEVEE Principled BSDF material and connects all PBR texture channels.
    The material is automatically assigned to any currently selected mesh objects.

    textures: dict mapping OpenPBR identifier names to file paths.
    """
    import bpy

    material = bpy.data.materials.new(name=material_name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    for node in list(nodes):
        nodes.remove(node)

    output_node = nodes.new("ShaderNodeOutputMaterial")
    output_node.location = (1600, 0)

    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.location = (1200, 0)
    links.new(principled.outputs["BSDF"], output_node.inputs["Surface"])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-200, 0)
    mapping = nodes.new("ShaderNodeMapping")
    mapping.location = (0, 0)
    links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])

    normal_map_node = None
    bump_node = None
    y = 0

    for identifier, file_path in textures.items():
        is_color = identifier in COLOR_IDENTIFIERS
        tex = nodes.new("ShaderNodeTexImage")
        tex.location = (400, y)
        tex.image = bpy.data.images.load(file_path)
        tex.image.colorspace_settings.name = "sRGB" if is_color else "Non-Color"
        links.new(mapping.outputs["Vector"], tex.inputs["Vector"])

        if identifier in ("normal", "geometry_normal"):
            tex.image.colorspace_settings.name = "Non-Color"
            normal_map_node = nodes.new("ShaderNodeNormalMap")
            normal_map_node.location = (800, y)
            links.new(tex.outputs["Color"], normal_map_node.inputs["Color"])

        elif identifier == "bump":
            tex.image.colorspace_settings.name = "Non-Color"
            bump_node = nodes.new("ShaderNodeBump")
            bump_node.location = (800, y)
            links.new(tex.outputs["Color"], bump_node.inputs["Height"])

        elif identifier == "displacement":
            tex.image.colorspace_settings.name = "Non-Color"
            disp_node = nodes.new("ShaderNodeDisplacement")
            disp_node.location = (700, y)
            links.new(tex.outputs["Color"], disp_node.inputs["Height"])
            links.new(disp_node.outputs["Displacement"], output_node.inputs["Displacement"])

        else:
            bsdf_input = IDENTIFIER_TO_BSDF.get(identifier)
            if bsdf_input and bsdf_input in principled.inputs:
                links.new(tex.outputs["Color"], principled.inputs[bsdf_input])

        y -= 400

    # Chain normal and bump
    if normal_map_node and bump_node:
        links.new(normal_map_node.outputs["Normal"], bump_node.inputs["Normal"])
        links.new(bump_node.outputs["Normal"], principled.inputs["Normal"])
    elif normal_map_node:
        links.new(normal_map_node.outputs["Normal"], principled.inputs["Normal"])
    elif bump_node:
        links.new(bump_node.outputs["Normal"], principled.inputs["Normal"])

    # Assign to selected mesh objects
    for obj in bpy.context.selected_objects:
        if obj.type == "MESH":
            if obj.data.materials:
                obj.data.materials[0] = material
            else:
                obj.data.materials.append(material)
