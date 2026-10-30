"""Original stylized mesh prototypes. Run with Blender --background --python this_file."""
import bpy, math, json, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,'assets','prototypes')
os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color,metal=.6,rough=.3,glow=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 if glow:
  p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=glow
 return m
black=mat('Graphite',( .035,.06,.09)); silver=mat('Frost ceramic',(.68,.85,.92)); blue=mat('Sapphire',(.035,.19,.34)); cyan=mat('Glacial cyan',(.06,.65,.9),.45,.22,.45); purple=mat('Aurora violet',(.37,.12,.8),.5,.25,.35); red=mat('Rowan red',(.7,.025,.055)); steel=mat('Brushed steel',(.22,.3,.37)); white=mat('Typography',(.65,.8,.9),0,.6)
current=[]
def finish(o,name,m):
 o.name=name; o.data.materials.append(m); current.append(o)
 if o.type=='MESH':
  b=o.modifiers.new('Machined edges','BEVEL'); b.width=.035; b.segments=2
  o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o

def box(n,loc,size,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return finish(o,n,m)
def profile(n,pts,w,m):
 verts=[(x,y,z) for y in [-w/2,w/2] for x,z in pts]; k=len(pts)
 faces=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)]
 mesh=bpy.data.meshes.new(n); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(n,mesh); bpy.context.collection.objects.link(o); return finish(o,n,m)
def cyl(n,x,z,length,r,m,y=0):
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=length,location=(x,y,z),rotation=(0,math.pi/2,0)); return finish(bpy.context.object,n,m)
def line(n,a,b,r,m):
 a,b=Vector(a),Vector(b); d=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=d.length,location=(a+b)/2); o=bpy.context.object; o.rotation_euler=d.to_track_quat('Z','Y').to_euler(); return finish(o,n,m)
def stock(m):
 profile('Shoulder stock',[(-2.9,.2),(-2.9,.85),(-1.35,.65),(-1.25,.28),(-2,.05)],.32,m)
 box('Butt pad',(-2.94,0,.5),(.12,.4,.8),black)
def grip(x=-.65):
 profile('Pistol grip',[(x-.25,.35),(x+.15,.3),(x-.05,-.65),(x-.48,-.55)],.32,black)
def trigger(x=-.2):
 for a,b in [((x-.4,-.18,.2),(x-.35,-.18,-.25)),((x-.35,-.18,-.25),(x+.18,-.18,-.25)),((x+.18,-.18,-.25),(x+.25,-.18,.2))]: line('Trigger guard',a,b,.035,steel)
 line('Trigger',(x-.08,-.05,.15),(x-.16,-.05,-.1),.045,black)
def mag(x=.3,curved=False):
 pts=[(x-.2,.25),(x+.22,.25),(x+.35,-.45),(x+.65,-1.0),(x+.25,-1.12),(x-.02,-.6)] if curved else [(x-.22,.25),(x+.22,.25),(x+.15,-.85),(x-.3,-.85)]
 profile('Magazine',pts,.3,black)
 for i in range(3): box('Magazine ribs',(x,-.166,-.3-i*.16),(.29,.025,.035),steel)
def scope(x=-.1):
 for sx in [x-.5,x+.45]: box('Optic mount',(sx,0,.95),(.17,.25,.25),black)
 cyl('Scope tube',x,1.23,1.6,.15,black); cyl('Objective',x+.75,1.23,.4,.25,steel); cyl('Blue lens',x+.96,1.23,.015,.205,cyan); cyl('Eyepiece',x-.8,1.23,.25,.2,steel)
 box('Elevation turret',(x,0,1.43),(.22,.22,.2),black)
def decorate(tier,pistol=False):
 for side in [-1,1]:
  yy=side*(.205 if pistol else .235)
  for j in range(4):
   x=-.75+j*.35
   line('Ice vein',(x,yy,.46),(x+.15,yy,.67),.018,cyan)
   line('Ice vein fork',(x+.15,yy,.67),(x+.3,yy,.56),.014,purple if tier==3 else silver)
 if tier==3:
  for i in range(6):
   x=-1.3+i*.3
   profile('Ice crest',[(x,.85),(x+.12,1.08+(i%2)*.12),(x+.25,.85)],.16,cyan if i%2 else purple)
def rifle(id,tier):
 body=silver if id in ['famas','m4a1s','xm1014'] else blue if id=='nova' else black
 if id=='famas':
  profile('Bullpup body',[(-2.6,.12),(-2.6,.9),(.8,.85),(1,.35),(-.5,.12)],.46,body); mag(-1.65); grip(-.1); trigger(.4)
  box('Carry handle',(-.55,0,1.18),(2,.22,.12),black)
  for x in [-1.4,.3]: box('Handle support',(x,0,1),(.12,.22,.3),steel)
  cyl('Barrel',1.65,.62,1.4,.08,steel)
 elif id=='mp9':
  box('Compact receiver',(-.25,0,.55),(2,.46,.65),black); stock(silver); grip(-.7); mag(-.6); trigger(-.05)
  box('Forward grip',(.65,0,-.05),(.25,.3,.75),black); cyl('Barrel',1.15,.65,.8,.1,steel)
  box('Red accent',(-.6,-.245,.65),(.6,.035,.16),red)
 else:
  stock(body); box('Receiver',(-.45,0,.55),(1.95,.46,.65),body); grip(); trigger()
  long=id in ['awp','ssg08','nova','xm1014']
  end=3.1 if long else 2.5
  cyl('Barrel',(1+end)/2,.68,end-1,.085,steel)
  cyl('Muzzle',end,.68,.23,.12,black)
  if id in ['nova','xm1014']:
   cyl('Magazine tube',1.5,.39,2.4,.105,steel)
   box('Pump / fore-end',(1.15,0,.43),(1.2,.42,.35),body)
   for i in range(7): box('Fore-end grooves',(.68+i*.15,-.225,.42),(.045,.025,.25),steel)
  elif id in ['awp','ssg08']:
   profile('Precision chassis',[(-1.4,.15),(.8,.15),(1.65,.4),(1.65,.6),(-1.4,.6)],.43,body); mag(.15); scope(-.35)
   for y in [-.22,.22]: line('Folded bipod',(1.6,y,.5),(2.6,y,.3),.045,steel)
  else:
   mag(.2,id=='ak47'); box('Handguard',(1.15,0,.65),(1.2,.36,.46),body)
   for i in range(6): box('Vent slots',(.7+i*.16,-.19,.69),(.075,.025,.16),black if body!=black else steel)
   box('Sight rail',(-.3,0,.94),(1.6,.2,.08),steel)
  if id=='m4a1s': cyl('Suppressor',3.05,.68,1.15,.17,black)
  if id=='negev':
   box('Belt box',(.05,0,-.35),(1.05,.8,1),blue)
   for i in range(7): box('Belt links',(.2+i*.12,-.35,.2+i*.05),(.09,.2,.17),silver)
   box('Carry handle',(.1,0,1.12),(.8,.16,.12),steel)
  if id=='awp':
   for i in range(8):
    x=-2.4+i*.19
    profile('Dragon scale',[(x,.35),(x+.11,.7),(x+.26,.43)],.39,cyan if i%2 else blue)
   profile('Dragon head',[(-1.1,.55),(-.82,.98),(-.5,.9),(-.3,.61),(-.65,.47)],.46,cyan)
 decorate(tier)
def pistol(id,tier):
 m=silver if id=='glock18' else black
 length=1.9 if id=='glock18' else 2.3 if id=='deagle' else 2.05
 box('Slide',(.1,0,.68),(length,.4,.42),m)
 profile('Lower frame',[(-.85,.5),(.9,.5),(.9,.22),(-.05,.18),(-.36,-.85),(-.92,-.72),(-.72,.15)],.34,black)
 trigger(.15)
 for i in range(6): box('Slide serrations',(-.68+i*.07,-.212,.67),(.027,.025,.26),steel)
 for x in [-.7,.85]: box('Iron sight',(x,0,.94),(.12,.13,.1),steel)
 cyl('Muzzle',length/2+.12,.68,.08,.1,steel)
 if id=='usp_s': cyl('Suppressor',1.75,.68,1.3,.17,steel)
 if id=='deagle': box('Barrel rib',(.65,0,.93),(1.2,.12,.1),purple)
 decorate(tier,True)

catalog=json.load(open(os.path.join(ROOT,'config','vip_weapons.concept.json')))['weapons']
manifest=[]
for idx,w in enumerate(catalog):
 current=[]; ident=w['id']; tier=w['required_vip']
 (pistol if w['slot']=='secondary' else rifle)(ident,tier)
 objects=list(current)
 # Every export is centered at origin, with original editable mesh parts and PBR materials.
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects: o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,ident+'.glb'),export_format='GLB',use_selection=True,export_apply=True)
 manifest.append({'id':ident,'name':w['name'],'file':ident+'.glb','status':'implemented','cs2_tested':False,'mesh_parts':len(objects)})
 col=(idx//4); row=idx%4; origin=Vector(((col-1)*8.0,0,(3-row)*3.65))
 for o in objects: o.location+=origin
 # Label sits in the same front-facing plane as the models.
 bpy.ops.object.text_add(location=(origin.x-3,-.5,origin.z-1.45),rotation=(math.pi/2,0,0))
 t=bpy.context.object; t.name=ident+' label'; t.data.body=w['name']; t.data.size=.25; t.data.extrude=0; t.data.materials.append(white)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
if os.path.exists(font):
 f=bpy.data.fonts.load(font)
 for o in bpy.data.objects:
  if o.type=='FONT': o.data.font=f
json.dump(manifest,open(os.path.join(OUT,'manifest.json'),'w'),ensure_ascii=False,indent=2)
# Studio render of the actual exported mesh designs.
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.cycles.use_denoising=False
scene.world.color=(.15,.15,.15)
for name,loc,energy,size in [('Key',(-4,-10,18),2300,12),('Fill',(12,-6,10),1800,10),('Rim',(0,5,17),2600,10)]:
 bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=energy; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(Vector((0,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(1,-34,16)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,5.6))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=25; scene.camera=cam
scene.render.resolution_x=2000; scene.render.resolution_y=1400; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,'arsenal.png')
scene.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'arsenal.blend'))
bpy.ops.render.render(write_still=True)
print('ARSENAL_COMPLETE',len(manifest))
