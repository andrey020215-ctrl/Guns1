"""Download official Valve authoring geometry into an ignored local directory."""
import argparse, hashlib, json, urllib.request, zipfile
from pathlib import Path
URL='https://media.steampowered.com/apps/csgo/images/workshop/workshop/cs2_weapon_model_geometry.zip'
EXPECTED='f06ed57135a3875658eaee4175c46b203d4c91f83a7f287ef6663dee11b79bbe'
p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'assets/cs2_local/source'); opts=p.parse_args()
opts.output.mkdir(parents=True,exist_ok=True)
archive=opts.output/'cs2_weapon_model_geometry.zip'
if not archive.exists():
 with urllib.request.urlopen(URL,timeout=60) as response: archive.write_bytes(response.read())
actual=hashlib.sha256(archive.read_bytes()).hexdigest()
if actual != EXPECTED: raise SystemExit(f'Archive changed: expected {EXPECTED}, got {actual}. Review the new official archive before updating the hash.')
with zipfile.ZipFile(archive) as z:
 for info in z.infolist():
  path=Path(info.filename)
  if path.name==info.filename and path.suffix.lower()=='.obj':
   (opts.output/path.name).write_bytes(z.read(info))
print(json.dumps({'source_url':URL,'sha256':actual,'directory':str(opts.output)},indent=2))
