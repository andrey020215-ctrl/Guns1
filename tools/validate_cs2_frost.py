"""Verify delivered Blender geometry/UVs against official source OBJs and inspect GLBs.
Run with Blender: blender -b --python tools/validate_cs2_frost.py -- /path/to/official/objs
"""
import bpy, hashlib, json, struct, sys
from pathlib import Path
import numpy as np
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path(sys.argv[sys.argv.index('--')+1])
ART=ROOT/'assets/frost_cs2'; LOCAL=ROOT/'assets/cs2_local'
manifest=json.loads((ART/'manifest.json').read_text())
assert len(manifest)==12

def same_points(actual, expected, tolerance=2e-6):
 # KDTree comparison avoids lexicographic reorderings at floating-point ties.
 for source, target in [(actual, expected), (expected, actual)]:
  tree=KDTree(len(target))
  for i,point in enumerate(target): tree.insert(tuple(point)+(0,)*(3-len(point)),i)
  tree.balance()
  for point in source:
   if tree.find(tuple(point)+(0,)*(3-len(point)))[2]>tolerance: return False
 return True

results=[]
for item in manifest:
 src=SOURCE/item['source_obj']; assert hashlib.sha256(src.read_bytes()).hexdigest()==item['source_sha256']
 verts=[]; uvs=[]; loops=[]; face_count=0
 for line in src.read_text().splitlines():
  f=line.split()
  if not f: continue
  if f[0]=='v': verts.append(list(map(float,f[1:4])))
  elif f[0]=='vt': uvs.append(list(map(float,f[1:3])))
  elif f[0]=='f':
   face_count+=1
   loops.extend(int(v.split('/')[1])-1 for v in f[1:])
 expected=np.array(verts)[:,[2,0,1]]*.0254
 expected-=(expected.min(axis=0)+expected.max(axis=0))*.5
 expected_uv=np.array(uvs)[loops]
 bpy.ops.wm.open_mainfile(filepath=str(LOCAL/(item['id']+'.blend')))
 models=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name!='Studio floor']
 actual=np.array([list(o.matrix_world@v.co) for o in models for v in o.data.vertices])
 assert actual.shape==expected.shape,(item['id'],'vertex count changed',actual.shape,expected.shape)
 assert same_points(actual,expected),(item['id'],'geometry changed')
 assert sum(len(o.data.polygons) for o in models)==face_count,(item['id'],'face count changed')
 actual_uv=np.array([list(x.uv) for o in models for x in o.data.uv_layers.active.data])
 assert actual_uv.shape==expected_uv.shape,(item['id'],'UV count changed')
 assert same_points(actual_uv,expected_uv),(item['id'],'UVs changed')
 data=(LOCAL/(item['id']+'.glb')).read_bytes(); magic,version,length=struct.unpack_from('<4sII',data)
 assert magic==b'glTF' and version==2 and length==len(data)
 size,chunk=struct.unpack_from('<II',data,12); assert chunk==0x4E4F534A
 gltf=json.loads(data[20:20+size]); assert gltf['meshes'] and gltf['images']
 assert all('bufferView' in image for image in gltf['images']),'GLB has external images'
 assert any('baseColorTexture' in m.get('pbrMetallicRoughness',{}) for m in gltf['materials'])
 assert (ART/item['render']).is_file(); assert item['cs2_tested'] is False
 texture=bpy.data.images.load(str(ART/item['basecolor']),check_existing=True)
 assert list(texture.size)==[2048,2048]
 pixels=np.empty(len(texture.pixels),dtype=np.float32); texture.pixels.foreach_get(pixels)
 sample=pixels.reshape(-1,4)[::64,:3]; assert sample.std()>.03,'Blank baked texture'
 results.append({'id':item['id'],'vertices':len(actual),'faces':face_count,'geometry_preserved':True,'original_uv_preserved':True,'glb_embedded_texture':True})
 print('VERIFIED',item['id'],flush=True)
(ART/'validation.json').write_text(json.dumps({'blender_version':bpy.app.version_string,'models':results,'cs2_tested':False},ensure_ascii=False,indent=2))
print('PASS: all 12 official meshes and UVs preserved, textured GLBs valid.',flush=True)
