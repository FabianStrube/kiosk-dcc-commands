# ==============================================================================
# Kiosk Library — DCC Commands Collection
# www.kiosk-library.com
#
# Free & open-source contribution to the 3D community.
# Feel free to use, adapt, and share — attribution appreciated.
# ==============================================================================

# Example -----------------------------------------------------------------------
EXAMPLE = {
    "file_path": "/path/to/environment.hdr",
}

# set_hdri_world(EXAMPLE["file_path"])
# -------------------------------------------------------------------------------

def set_hdri_world(hdri_path):
    """
    Sets the world environment to the given HDRI for Cycles or EEVEE.
    If an Environment Texture node already exists in the world, its image is updated.
    Creates the world node tree if it does not already exist.
    """
    import bpy
    import os

    if not os.path.exists(hdri_path):
        print(f"[kiosk-dcc-commands] HDRI file not found: {hdri_path}")
        return

    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    bg_shader = nodes.get("Background") or nodes.new("ShaderNodeBackground")
    output_node = nodes.get("World Output") or nodes.new("ShaderNodeOutputWorld")

    if not output_node.inputs["Surface"].is_linked:
        links.new(bg_shader.outputs["Background"], output_node.inputs["Surface"])

    image = bpy.data.images.load(hdri_path, check_existing=True)

    # Reuse existing environment texture node if present
    env_node = next((n for n in nodes if n.type == "TEX_ENVIRONMENT"), None)
    if env_node:
        env_node.image = image
    else:
        env_node = nodes.new("ShaderNodeTexEnvironment")
        env_node.name = "Environment Texture"
        env_node.image = image
        links.new(env_node.outputs["Color"], bg_shader.inputs["Color"])

    bpy.context.scene.world = world
