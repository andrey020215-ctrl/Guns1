"""Render a muzzle-origin icy tracer on the original CS2 AK mesh. Blender preview, not CS2 evidence.
Requires tools/build_cs2_frost.py outputs; run: blender -b --python tools/preview_icy_tracer.py
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'assets/icy_tracers'; OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/cs2_local/ak47.blend'))
bpy.data.orphans_purge(do_recursive=True)
settings=json.loads((ROOT/'config/icy_tracers.json').read_text())
weapon=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name!='Studio floor']
points=[o.matrix_world@v.co for o in weapon for v in o.data.vertices]
xmax=max(p.x for p in points); tips=[p for p in points if p.x>xmax-.002]
muzzle=sum(tips,Vector())/len(tips); muzzle.x=xmax+.001
end=muzzle+Vector((1.55,0,0))

def material(name,rgb,power):
 m=bpy.data.materials.new(name); m.use_nodes=True; m.node_tree.nodes.clear(); out=m.node_tree.nodes.new('ShaderNodeOutputMaterial'); emit=m.node_tree.nodes.new('ShaderNodeEmission'); emit.inputs['Color'].default_value=(*[c/255 for c in rgb],1); emit.inputs['Strength'].default_value=power
 if 'glow' in name:
  transparent=m.node_tree.nodes.new('ShaderNodeBsdfTransparent'); mix=m.node_tree.nodes.new('ShaderNodeMixShader'); mix.inputs[0].default_value=.25; m.node_tree.links.new(transparent.outputs[0],mix.inputs[1]); m.node_tree.links.new(emit.outputs[0],mix.inputs[2]); m.node_tree.links.new(mix.outputs[0],out.inputs[0])
 else: m.node_tree.links.new(emit.outputs[0],out.inputs[0])
 return m

def beam(name,width,rgb,power):
 direction=end-muzzle
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=width*.0254/2,depth=direction.length,location=(end+muzzle)/2)
 o=bpy.context.object; o.name=name; o.rotation_euler=direction.to_track_quat('Z','Y').to_euler(); o.data.materials.append(material(name,rgb,power))
beam('ICY / cyan glow',settings['glowWidth'],settings['glowRgb'],1.1)
beam('ICY / white cyan core',settings['coreWidth'],settings['coreRgb'],14)
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=False
cam=scene.camera; target=Vector((.65,0,.0)); cam.location=(.5,-4,1.05); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.ortho_scale=2.85
scene.use_nodes=True; nt=scene.node_tree; nt.nodes.clear(); source=nt.nodes.new('CompositorNodeRLayers'); glow=nt.nodes.new('CompositorNodeGlare'); glow.glare_type='FOG_GLOW'; glow.quality='HIGH'; glow.threshold=1.5; glow.size=8; out=nt.nodes.new('CompositorNodeComposite'); nt.links.new(source.outputs['Image'],glow.inputs['Image']); nt.links.new(glow.outputs['Image'],out.inputs[0])
scene.render.resolution_x=1600; scene.render.resolution_y=800; scene.render.resolution_percentage=100
# A readable overlay explicitly distinguishes this render from an in-game capture.
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
for body,x,y,size in [('PEGASUS / ICY TRACER',-1.25,.60,.065),('Blender preview / not tested in CS2',-1.25,-.60,.035)]:
 bpy.ops.object.text_add(); text=bpy.context.object; text.data.body=body; text.data.size=size
 if Path(font).exists(): text.data.font=bpy.data.fonts.load(font,check_existing=True)
 text.rotation_euler=cam.rotation_euler
 text.location=cam.location+cam.rotation_euler.to_quaternion()@Vector((x,y,-2))
 text.data.materials.append(material('Overlay', [190,220,235],1))
scene.render.filepath=str(OUT/'icy-tracer-preview.png'); scene.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True)
(OUT/'preview-source.json').write_text(json.dumps({'weapon':'ak47','source_mesh':'official Valve CS2 Workshop geometry','muzzle_world_metres':list(muzzle),'impact_world_metres':list(end),'style':settings,'runtime_tested':False,'preview':'Blender Cycles, not a CS2 capture'},indent=2))
