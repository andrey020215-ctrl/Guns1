"""Texture Valve's official CS2 Workshop OBJ meshes, preserving geometry and UVs.
Usage: blender -b --python tools/build_cs2_frost.py -- --source /path/to/objs [--ids ak47,deagle]
Valve meshes/derived mesh exports stay local; own textures, recipes and renders may be versioned.
"""
import argparse, bpy, json, math, os, sys, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
p=argparse.ArgumentParser(); p.add_argument('--source',required=True); p.add_argument('--ids',default=''); p.add_argument('--samples',type=int,default=48); p.add_argument('--size',type=int,default=2048); opts=p.parse_args(args)
ART=ROOT/'assets/frost_cs2'; LOCAL=ROOT/'assets/cs2_local'; RENDERS=ART/'renders'; TEX=ART/'textures'
for folder in [LOCAL,RENDERS,TEX]: folder.mkdir(parents=True,exist_ok=True)
RECIPES=[
 ('mp9','weapon_smg_mp9.obj','MP9 «Снегири и рябина»',1,'red',0,.32),
 ('famas','weapon_rif_famas.obj','FAMAS «Еловая сказка»',1,'green',0,.32),
 ('nova','weapon_shot_nova.obj','Nova «Сапфировые снежинки»',1,'blue',0,.34),
 ('glock18','weapon_pist_glock18.obj','Glock-18 «Рождественская лента»',1,'red',0,.20),
 ('ak47','weapon_rif_ak47.obj','AK-47 «Кобальт и рубин»',2,'blue',-.025,.35),
 ('m4a1s','weapon_rif_m4a1_silencer.obj','M4A1-S «Изумрудное Рождество»',2,'red',0,.34),
 ('ssg08','weapon_snip_ssg08.obj','SSG 08 «Бирюзовое созвездие»',2,'pegasus',-.04,.35),
 ('usp_s','weapon_pist_usp_silencer.obj','USP-S «Зимнее кружево»',2,'blue',.12,.25),
 ('awp','weapon_snip_awp.obj','AWP «Сапфировая филигрань»',3,'blue',.015,.38),
 ('xm1014','weapon_shot_xm1014.obj','XM1014 «Гранатовый узор»',3,'red',-.04,.34),
 ('negev','weapon_mach_negev.obj','Negev «Малахитовый орнамент»',3,'green',.015,.35),
 ('deagle','weapon_pist_deagle.obj','Desert Eagle «Звёздный Пегас»',3,'pegasus',.025,.23),
]
OFFSETS={'red':(0,.5),'green':(.5,.5),'blue':(0,0),'pegasus':(.5,0)}

def node(nt,kind,name=None):
 n=nt.nodes.new(kind)
 if name: n.name=name; n.label=name
 return n

def ornament(atlas,recipe):
 ident,_,_,tier,palette,hue,period=recipe
 mat=bpy.data.materials.new('PEGASUS / '+ident); mat.use_nodes=True
 nt=mat.node_tree; nt.nodes.clear(); L=nt.links
 out=node(nt,'ShaderNodeOutputMaterial'); shader=node(nt,'ShaderNodeBsdfPrincipled'); L.new(shader.outputs['BSDF'],out.inputs['Surface'])
 shader.inputs['Metallic'].default_value=.45; shader.inputs['Roughness'].default_value=.3
 texcoord=node(nt,'ShaderNodeTexCoord'); scale=node(nt,'ShaderNodeVectorMath'); scale.operation='SCALE'; scale.inputs['Scale'].default_value=1/period; L.new(texcoord.outputs['Object'],scale.inputs[0])
 separate=node(nt,'ShaderNodeSeparateXYZ'); L.new(scale.outputs['Vector'],separate.inputs[0])
 geom=node(nt,'ShaderNodeNewGeometry'); normal=node(nt,'ShaderNodeVectorTransform'); normal.vector_type='NORMAL'; normal.convert_from='WORLD'; normal.convert_to='OBJECT'; L.new(geom.outputs['Normal'],normal.inputs[0])
 ab=node(nt,'ShaderNodeVectorMath'); ab.operation='ABSOLUTE'; L.new(normal.outputs[0],ab.inputs[0]); ns=node(nt,'ShaderNodeSeparateXYZ'); L.new(ab.outputs[0],ns.inputs[0])
 colors=[]; weights=[]; ox,oy=OFFSETS[palette]
 for a,b,axis in [('Y','Z','X'),('X','Z','Y'),('X','Y','Z')]:
  combine=node(nt,'ShaderNodeCombineXYZ'); L.new(separate.outputs[a],combine.inputs['X']); L.new(separate.outputs[b],combine.inputs['Y'])
  frac=node(nt,'ShaderNodeVectorMath'); frac.operation='FRACTION'; L.new(combine.outputs[0],frac.inputs[0])
  atlasmap=node(nt,'ShaderNodeVectorMath'); atlasmap.operation='MULTIPLY_ADD'; L.new(frac.outputs[0],atlasmap.inputs[0]); atlasmap.inputs[1].default_value=(.496,.496,1); atlasmap.inputs[2].default_value=(ox+.002,oy+.002,0)
  image=node(nt,'ShaderNodeTexImage'); image.image=atlas; image.extension='EXTEND'; L.new(atlasmap.outputs[0],image.inputs['Vector'])
  weight=node(nt,'ShaderNodeMath'); weight.operation='POWER'; L.new(ns.outputs[axis],weight.inputs[0]); weight.inputs[1].default_value=6
  colors.append(image.outputs['Color']); weights.append(weight.outputs[0])
 # Normalized triplanar blending avoids stretching on the barrel/top/end faces.
 add1=node(nt,'ShaderNodeMath'); add1.operation='ADD'; L.new(weights[0],add1.inputs[0]); L.new(weights[1],add1.inputs[1])
 add2=node(nt,'ShaderNodeMath'); add2.operation='ADD'; L.new(add1.outputs[0],add2.inputs[0]); L.new(weights[2],add2.inputs[1])
 weighted=[]
 for color,weight in zip(colors,weights):
  div=node(nt,'ShaderNodeMath'); div.operation='DIVIDE'; L.new(weight,div.inputs[0]); L.new(add2.outputs[0],div.inputs[1])
  mul=node(nt,'ShaderNodeVectorMath'); mul.operation='SCALE'; L.new(color,mul.inputs[0]); L.new(div.outputs[0],mul.inputs['Scale']); weighted.append(mul.outputs[0])
 sum1=node(nt,'ShaderNodeVectorMath'); sum1.operation='ADD'; L.new(weighted[0],sum1.inputs[0]); L.new(weighted[1],sum1.inputs[1])
 sum2=node(nt,'ShaderNodeVectorMath'); sum2.operation='ADD'; L.new(sum1.outputs[0],sum2.inputs[0]); L.new(weighted[2],sum2.inputs[1])
 hue_node=node(nt,'ShaderNodeHueSaturation'); hue_node.inputs['Hue'].default_value=.5+hue; hue_node.inputs['Saturation'].default_value=.95; L.new(sum2.outputs[0],hue_node.inputs['Color']); L.new(hue_node.outputs[0],shader.inputs['Base Color'])
 return mat,shader

def setup_scene():
 scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=opts.samples; scene.cycles.use_denoising=False
 scene.render.bake.use_pass_direct=False; scene.render.bake.use_pass_indirect=False; scene.render.bake.use_pass_color=True; scene.render.bake.margin=12
 scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.17,.25,1); scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 scene.render.resolution_x=1440; scene.render.resolution_y=810; scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
 scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'
 return scene

manifest=[]
for recipe in RECIPES:
 ident,filename,title,tier,palette,hue,period=recipe
 if opts.ids and ident not in opts.ids.split(','): continue
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 bpy.data.orphans_purge(do_recursive=True)
 scene=setup_scene(); bpy.context.preferences.filepaths.save_version=0
 src=Path(opts.source)/filename
 bpy.ops.wm.obj_import(filepath=str(src),forward_axis="Y",up_axis="Z")
 meshes=[o for o in bpy.context.selected_objects if o.type=='MESH']; assert meshes
 # Official OBJ uses X=width, Y=up, Z=barrel. Rigid rotation and inch-to-metre conversion only.
 transform=Matrix(((0,0,1),(1,0,0),(0,1,0)))
 for obj in meshes:
  bpy.context.view_layer.objects.active=obj
  bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
  for v in obj.data.vertices: v.co=(transform@v.co)*.0254
  obj.data.update()
 points=[v.co for o in meshes for v in o.data.vertices]
 low=Vector(tuple(min(v[i] for v in points) for i in range(3))); high=Vector(tuple(max(v[i] for v in points) for i in range(3))); center=(high+low)*.5
 for o in meshes:
  for v in o.data.vertices: v.co-=center
  o.data.update()
 dim=high-low; uv_count=sum(len(o.data.uv_layers) for o in meshes); assert uv_count==len(meshes)
 atlas=bpy.data.images.load(str(TEX/'ornament_atlas.png'),check_existing=True)
 mat,shader=ornament(atlas,recipe)
 target=bpy.data.images.new(ident+'_basecolor',width=opts.size,height=opts.size,alpha=False); target.filepath_raw=str(TEX/(ident+'_basecolor.png')); target.file_format='PNG'
 bake=mat.node_tree.nodes.new('ShaderNodeTexImage'); bake.name='Original CS2 UV bake'; bake.image=target; mat.node_tree.nodes.active=bake; bake.select=True
 for o in meshes: o.data.materials.clear(); o.data.materials.append(mat)
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes: o.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0]
 scene.cycles.samples=1
 bpy.ops.object.bake(type='DIFFUSE')
 scene.cycles.samples=opts.samples
 target.save()
 # Replace the procedural projection with its baked result in original Valve UVs.
 uv=mat.node_tree.nodes.new('ShaderNodeUVMap'); mat.node_tree.links.new(uv.outputs[0],bake.inputs['Vector']); mat.node_tree.links.new(bake.outputs['Color'],shader.inputs['Base Color'])
 bw=mat.node_tree.nodes.new('ShaderNodeRGBToBW'); mat.node_tree.links.new(bake.outputs['Color'],bw.inputs[0])
 bump=mat.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.00012; mat.node_tree.links.new(bw.outputs[0],bump.inputs['Height']); mat.node_tree.links.new(bump.outputs['Normal'],shader.inputs['Normal'])
 # Export static PBR first; animated Blender finish is added afterwards.
 bpy.ops.export_scene.gltf(filepath=str(LOCAL/(ident+'.glb')),export_format='GLB',use_selection=True,export_apply=False)
 # Autonomous soft light in ornament highlights, Blender preview only (not a Source 2 material).
 nt=mat.node_tree; tc=node(nt,'ShaderNodeTexCoord'); wave=node(nt,'ShaderNodeTexWave'); wave.wave_type='BANDS'; wave.bands_direction='X'; wave.inputs['Scale'].default_value=4; wave.inputs['Distortion'].default_value=1.5; nt.links.new(tc.outputs['Generated'],wave.inputs['Vector'])
 duration={1:5,2:3.5,3:4}[tier]; scene.render.fps=24; scene.frame_end=int(duration*24)
 for frame,val in [(1,0),(scene.frame_end,math.tau)]: wave.inputs['Phase Offset'].default_value=val; wave.inputs['Phase Offset'].keyframe_insert('default_value',frame=frame)
 if nt.animation_data and nt.animation_data.action:
  for fc in nt.animation_data.action.fcurves:
   for k in fc.keyframe_points: k.interpolation='LINEAR'
 highlight=node(nt,'ShaderNodeMath'); highlight.operation='MULTIPLY'; nt.links.new(wave.outputs['Fac'],highlight.inputs[0]); nt.links.new(bw.outputs[0],highlight.inputs[1])
 strength=node(nt,'ShaderNodeMath'); strength.operation='MULTIPLY'; strength.inputs[1].default_value=.12; nt.links.new(highlight.outputs[0],strength.inputs[0]); nt.links.new(strength.outputs[0],shader.inputs['Emission Strength']); shader.inputs['Emission Color'].default_value=(.3,.75,1,1)
 floor_z=-dim.z/2-.018
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,floor_z)); floor=bpy.context.object; floor.name='Studio floor'
 fm=bpy.data.materials.new('Midnight navy studio'); fm.diffuse_color=(.009,.019,.03,1); fm.use_nodes=True; fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.009,.019,.03,1); fm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85; floor.data.materials.append(fm)
 scale=max(dim.x,dim.z*1.6)
 for name,loc,power,size in [('Key',(-.2,-.8,1.2),65,.8),('Fill',(.7,-.2,.5),30,.65),('Rim',(.1,.6,.9),90,.65)]:
  bpy.ops.object.light_add(type='AREA',location=Vector(loc)*scale); lamp=bpy.context.object; lamp.name=name; lamp.data.energy=power*scale**2; lamp.data.shape='DISK'; lamp.data.size=size*scale; lamp.rotation_euler=(-lamp.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=Vector((.08,-3,.52))*scale); camera=bpy.context.object; camera.rotation_euler=(-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=scale*1.15; scene.camera=camera
 scene.render.filepath=str(RENDERS/(ident+'.png')); scene.frame_set(1)
 bpy.ops.file.pack_all(); bpy.ops.wm.save_as_mainfile(filepath=str(LOCAL/(ident+'.blend')))
 bpy.ops.render.render(write_still=True)
 manifest.append({'id':ident,'reference_name':title,'vip':tier,'palette':palette,'source_obj':filename,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'vertices':sum(len(o.data.vertices) for o in meshes),'triangles':sum(len(o.data.loop_triangles) for o in meshes),'uv_layers':uv_count,'status':'implemented','geometry':'Valve official CS2 Workshop OBJ; rigid transform and unit conversion only','basecolor':f'textures/{ident}_basecolor.png','render':f'renders/{ident}.png','local_glb':f'assets/cs2_local/{ident}.glb','blender_preview_cycle_seconds':duration,'cs2_tested':False})
 (ART/('manifest-partial.json' if opts.ids else 'manifest.json')).write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 print('FROST_COMPLETED',ident,flush=True)
print('ALL_COMPLETE',len(manifest),flush=True)
