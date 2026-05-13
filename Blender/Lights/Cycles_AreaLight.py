# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/light_texture.exr",
}

# create_area_light(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def create_area_light(file_path):
    """Creates a Cycles/EEVEE area light with a texture node driving its emission color."""
    import bpy

    bpy.ops.object.light_add(type="AREA", radius=1, align="WORLD", location=(0, 0, 2))
    light_obj = bpy.context.object
    light_obj.data.use_nodes = True

    node_tree = light_obj.data.node_tree
    nodes = node_tree.nodes
    links = node_tree.links

    tex_node = nodes.new("ShaderNodeTexImage")
    tex_node.image = bpy.data.images.load(file_path)
    tex_node.image.colorspace_settings.name = "Non-Color"

    emission_node = nodes.get("Emission")
    if emission_node:
        links.new(tex_node.outputs["Color"], emission_node.inputs["Color"])
