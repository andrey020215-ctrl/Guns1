"""Compose the actual Blender renders into a labelled arsenal contact sheet."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/'assets/frost_cs2'
manifest=json.loads((ART/'manifest.json').read_text())
W,H=2880,2710
board=Image.new('RGB',(W,H),'#07121d'); d=ImageDraw.Draw(board)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
regular=ImageFont.truetype(font,27); title=ImageFont.truetype(font,58); small=ImageFont.truetype(font,23)
d.text((55,32),'PEGASUS / FROST ARSENAL',font=title,fill='#e3f3ff')
d.text((58,111),'Оригинальная геометрия CS2 Workshop · Новые материалы по видео',font=regular,fill='#8eb5ca')
for col,tier in enumerate(['VIP I · Иней','VIP II · Метель','VIP III · Аврора']):
 d.text((col*960+35,183),tier,font=regular,fill='#5ed5e2')
for idx,item in enumerate(manifest):
 col=idx//4; row=idx%4; x=col*960; y=240+row*595
 render=Image.open(ART/item['render']).convert('RGB').resize((940,529),Image.Resampling.LANCZOS)
 board.paste(render,(x+10,y))
 d.text((x+28,y+540),item['reference_name'],font=regular,fill='#e4f1f7')
 d.line((x+28,y+581,x+920,y+581),fill='#193144',width=1)
d.text((40,H-53),'Рендеры Blender · Материалы ещё не проверены в CS2',font=small,fill='#7a9aaf')
board.save(ART/'arsenal-cs2.jpg',quality=94)
print(ART/'arsenal-cs2.jpg')
