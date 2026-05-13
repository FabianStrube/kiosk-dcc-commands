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
        # For ARM-packed textures (AO/Roughness/Metal in one file):
        # "arm_packed": "/path/to/ArchPillar_ARM.png",
    },
}

# create_redshift_openpbr(EXAMPLE["material_name"], EXAMPLE["textures"])
# -------------------------------------------------------------------------------

import os

COLOR_IDENTIFIERS = {"base_color", "emission_color", "coat_color", "specular_color", "subsurface_color"}
ARM_CHANNELS = {"R": "base_metalness", "G": "roughness", "B": "ambient_occlusion"}


def create_redshift_openpbr(material_name, textures):
    """
    Builds a Redshift OpenPBR material using Cinema 4D's node graph API.

    textures: dict mapping OpenPBR identifier names to file paths.
              Use 'arm_packed' for a single ARM-packed texture (AO/Roughness/Metal).
    """
    import c4d
    import maxon

    doc = c4d.documents.GetActiveDocument()

    id_texture     = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.texturesampler")
    id_openpbr     = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.openpbrmaterial")
    id_standard    = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.standardmaterial")
    id_bump        = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.bumpmap")
    id_bump_blend  = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.bumpblender")
    id_displacement = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.displacement")
    id_splitter    = maxon.Id("com.redshift3d.redshift4c4d.nodes.core.rscolorsplitter")
    rs_node_space  = maxon.Id("com.redshift3d.redshift4c4d.class.nodespace")

    material = c4d.BaseMaterial(c4d.Mmaterial)
    material.SetName(material_name)
    doc.InsertMaterial(material)

    node_mat = material.GetNodeMaterialReference()
    graph = node_mat.CreateDefaultGraph(rs_node_space)
    if graph.IsNullValue():
        raise RuntimeError("Could not create Redshift node graph.")

    c4d.EventAdd()

    root = graph.GetRoot()
    out_node = None
    for node in root.GetChildren():
        if str(node.GetId()).startswith("output"):
            out_node = node
            break

    std_nodes = []
    maxon.GraphModelHelper.FindNodesByAssetId(graph, id_standard, True, std_nodes)

    bump_ref = None
    normal_ref = None
    connected_ids = set()

    with graph.BeginTransaction() as transaction:

        for node in std_nodes:
            node.Remove()

        openpbr = graph.AddChild(maxon.Id(), id_openpbr)

        # Connect OpenPBR -> output
        openpbr_out = openpbr.GetOutputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.openpbrmaterial.outcolor"
        )
        out_surface = out_node.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.node.output.surface"
        )
        if openpbr_out and out_surface:
            openpbr_out.Connect(out_surface, modes=maxon.WIRE_MODE.NORMAL, reverse=False)

        # Pass 1: regular (non-packed) channels
        for identifier, file_path in textures.items():
            if identifier == "arm_packed":
                continue

            is_color = identifier in COLOR_IDENTIFIERS
            node_name = os.path.splitext(os.path.basename(file_path))[0]

            tex = graph.AddChild(maxon.Id(), id_texture)
            tex.SetValue(maxon.NODE.BASE.NAME, node_name)

            if not is_color:
                cs_port = tex.GetInputs().FindChild(
                    "com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0"
                ).FindChild("colorspace")
                cs_port.SetPortValue("RS_INPUT_COLORSPACE_RAW")

            tex.GetInputs().FindChild(
                "com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0"
            ).FindChild("path").SetPortValue(file_path)

            tex_out = tex.GetOutputs().FindChild(
                "com.redshift3d.redshift4c4d.nodes.core.texturesampler.outcolor"
            )

            if identifier in ("normal", "geometry_normal"):
                n_node = graph.AddChild(maxon.Id(), id_bump)
                n_node.GetInputs().FindChild(
                    "com.redshift3d.redshift4c4d.nodes.core.bumpmap.inputtype"
                ).SetPortValue(maxon.Int64(1))  # tangent-space normal
                n_in  = n_node.GetInputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.bumpmap.input")
                n_out = n_node.GetOutputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.bumpmap.out")
                tex_out.Connect(n_in, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
                normal_ref = (n_node, n_out)
                connected_ids.add(identifier)

            elif identifier == "bump":
                b_node = graph.AddChild(maxon.Id(), id_bump)
                b_in  = b_node.GetInputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.bumpmap.input")
                b_out = b_node.GetOutputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.bumpmap.out")
                tex_out.Connect(b_in, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
                bump_ref = (b_node, b_out)
                connected_ids.add(identifier)

            elif identifier == "displacement":
                d_node  = graph.AddChild(maxon.Id(), id_displacement)
                d_in    = d_node.GetInputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.displacement.texmap")
                d_out   = d_node.GetOutputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.displacement.out")
                out_disp = out_node.GetInputs().FindChild("com.redshift3d.redshift4c4d.node.output.displacement")
                tex_out.Connect(d_in,   modes=maxon.WIRE_MODE.NORMAL, reverse=False)
                d_out.Connect(out_disp, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
                connected_ids.add(identifier)

            else:
                mat_in = openpbr.GetInputs().FindChild(
                    f"com.redshift3d.redshift4c4d.nodes.core.openpbrmaterial.{identifier}"
                )
                if mat_in and not mat_in.IsNullValue():
                    tex_out.Connect(mat_in, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
                    connected_ids.add(identifier)

        # Pass 2: ARM packed map
        if "arm_packed" in textures:
            arm_path = textures["arm_packed"]
            node_name = os.path.splitext(os.path.basename(arm_path))[0]
            tex = graph.AddChild(maxon.Id(), id_texture)
            tex.SetValue(maxon.NODE.BASE.NAME, node_name)
            cs_port = tex.GetInputs().FindChild(
                "com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0"
            ).FindChild("colorspace")
            cs_port.SetPortValue("RS_INPUT_COLORSPACE_RAW")
            tex.GetInputs().FindChild(
                "com.redshift3d.redshift4c4d.nodes.core.texturesampler.tex0"
            ).FindChild("path").SetPortValue(arm_path)
            tex_out = tex.GetOutputs().FindChild(
                "com.redshift3d.redshift4c4d.nodes.core.texturesampler.outcolor"
            )
            splitter = graph.AddChild(maxon.Id(), id_splitter)
            splitter_in = splitter.GetInputs().FindChild(
                "com.redshift3d.redshift4c4d.nodes.core.rscolorsplitter.input"
            )
            tex_out.Connect(splitter_in, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
            channel_port = {
                "R": "com.redshift3d.redshift4c4d.nodes.core.rscolorsplitter.outr",
                "G": "com.redshift3d.redshift4c4d.nodes.core.rscolorsplitter.outg",
                "B": "com.redshift3d.redshift4c4d.nodes.core.rscolorsplitter.outb",
            }
            for ch, identifier in ARM_CHANNELS.items():
                if identifier in connected_ids:
                    continue
                ch_out = splitter.GetOutputs().FindChild(channel_port[ch])
                mat_in = openpbr.GetInputs().FindChild(
                    f"com.redshift3d.redshift4c4d.nodes.core.openpbrmaterial.{identifier}"
                )
                if ch_out and mat_in and not mat_in.IsNullValue():
                    ch_out.Connect(mat_in, modes=maxon.WIRE_MODE.NORMAL, reverse=False)

        # Wire bump/normal to geometry_normal port
        bump_port = openpbr.GetInputs().FindChild(
            "com.redshift3d.redshift4c4d.nodes.core.openpbrmaterial.geometry_normal"
        )
        if bump_ref and normal_ref:
            blender = graph.AddChild(maxon.Id(), id_bump_blend)
            blender.GetInputs().FindChild(
                "com.redshift3d.redshift4c4d.nodes.core.bumpblender.bumpweight0"
            ).SetPortValue(1.0)
            blender.GetInputs().FindChild(
                "com.redshift3d.redshift4c4d.nodes.core.bumpblender.additive"
            ).SetPortValue(True)
            base_in   = blender.GetInputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.bumpblender.baseinput")
            layer_in  = blender.GetInputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.bumpblender.bumpinput0")
            blend_out = blender.GetOutputs().FindChild("com.redshift3d.redshift4c4d.nodes.core.bumpblender.outdisplacementvector")
            bump_ref[1].Connect(base_in,   modes=maxon.WIRE_MODE.NORMAL, reverse=False)
            normal_ref[1].Connect(layer_in, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
            blend_out.Connect(bump_port,    modes=maxon.WIRE_MODE.NORMAL, reverse=False)
        elif normal_ref:
            normal_ref[1].Connect(bump_port, modes=maxon.WIRE_MODE.NORMAL, reverse=False)
        elif bump_ref:
            bump_ref[1].Connect(bump_port, modes=maxon.WIRE_MODE.NORMAL, reverse=False)

        transaction.Commit()

    c4d.EventAdd()
