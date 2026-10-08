"""Package NEW still renders and NEW authored motion. Does not read any demo media."""
from pathlib import Path
import hashlib, json, pickle, subprocess, zipfile
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/reimu_new'
FRAMES=ROOT/'.cache/new_motion'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
LABELS=['Default · Depan','Default · Belakang','Melambai','Peace!','Pipi imut','Hati kecil','Malu-malu','Membungkuk','Berjinjit','Ceria']

def font(size,bold=False):return ImageFont.truetype(BOLD if bold else FONT,size)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def credit(image):
    im=image.convert('RGB');d=ImageDraw.Draw(im);size=max(9,round(im.width*.012))
    text='Model: Megabubu  |  Pose & render baru'
    f=font(size);box=d.textbbox((0,0),text,font=f);width=box[2]-box[0]
    d.text(((im.width-width)/2,im.height-size-12),text,font=f,fill=(117,97,98))
    return im

images=sorted((OUT/'images').glob('*.png'))
frames=sorted(FRAMES.glob('*.png'))
assert len(images)==10, len(images)
assert len(frames)==144, len(frames)
for i,path in enumerate(frames):assert path.name==f'{i:04d}.png'
# Reopening an already stamped image simply paints the same text in the same place.
for path in images:
    with Image.open(path) as im:
        assert im.size==(1024,1024)
        credit(im).save(path,optimize=True)
video=OUT/'Reimu_Animasi_Baru.mp4'
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
cmd=[ffmpeg,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','720x720','-r','24','-i','-',
     '-an','-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',
     '-metadata','title=Reimu - new greeting animation',
     '-metadata','artist=New motion and render; original model/rig by Megabubu',
     '-metadata','comment=144 newly rendered frames. Original Maya geometry/UVs/skin weights; simplified new posing and adapted toon shader. No demo GIF or video used.',str(video)]
process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for path in frames:
    with Image.open(path) as im:
        assert im.size==(720,720)
        process.stdin.write(credit(im).tobytes())
process.stdin.close()
assert process.wait()==0
subprocess.run([ffmpeg,'-v','error','-i',str(video),'-f','null','-'],check=True)
count,secs=imageio_ffmpeg.count_frames_and_secs(str(video));assert count==144 and abs(secs-6)<.01
# Readable overview; the ten full-resolution PNGs remain separate deliverables.
W=2360;pad=40;gap=20;cardw=440;top=145;cardh=496
sheet=Image.new('RGB',(W,1225),'#f7f2ee');d=ImageDraw.Draw(sheet)
d.text((pad,35),'REIMU HAKUREI',font=font(43,True),fill='#38272c')
d.text((pad,94),'2 DEFAULT  /  8 POSE IMUT  /  RENDER BARU',font=font(19),fill='#806a70')
d.rounded_rectangle((2020,46,2320,94),radius=24,fill='#a80d29')
d.text((2053,57),'10 GAMBAR · PNG',font=font(19,True),fill='white')
for i,(path,label) in enumerate(zip(images,LABELS)):
    x=pad+(i%5)*(cardw+gap);y=top+(i//5)*(cardh+24)
    d.rounded_rectangle((x,y,x+cardw,y+cardh),radius=16,fill='white',outline='#e7dcda',width=2)
    with Image.open(path) as im:
        thumb=im.convert('RGB').resize((cardw-12,cardw-12),Image.Resampling.LANCZOS)
        sheet.paste(thumb,(x+6,y+6))
    d.rounded_rectangle((x+18,y+453,x+52,y+480),radius=8,fill='#f5e3e7')
    d.text((x+24,y+456),f'{i+1:02d}',font=font(15,True),fill='#9f1833')
    d.text((x+64,y+455),label,font=font(19,True),fill='#463038')
d.text((pad,1193),'Model / rig asli: Megabubu · Karakter: ZUN / Team Shanghai Alice · Penggunaan nonkomersial dengan kredit',font=font(16),fill='#806a70')
sheet.save(OUT/'Reimu_10_Gambar.jpg',quality=94,subsampling=0)
# Animation verification frames for visual inspection, not shipped as requested poses.
qa=Image.new('RGB',(1440,520),'white');qd=ImageDraw.Draw(qa)
for i,index in enumerate([0,24,48,72,108,143]):
    with Image.open(frames[index]) as im:qa.paste(im.convert('RGB').resize((240,240)),(i%3*480,i//3*260))
    qd.text((i%3*480+245,i//3*260+100),f'Frame {index}\n{index/24:.2f}s',font=font(20),fill='black')
qa.save(ROOT/'.cache/new_animation_qa.jpg',quality=92)
meshes,binds=pickle.loads((ROOT/'.cache/reimu_parsed.pkl').read_bytes())
manifest={
 'status':'NEW_RENDERS_AND_NEW_ANIMATION_COMPLETE',
 'uses_demo_media':False,
 'original_asset':'Reimu_native_source.zip / Reimu_Rig_master.ma',
 'source_scene_sha256':sha(ROOT/'.cache/native/Reimu/Reimu_Rig_master.ma'),
 'renderer':'Blender 4.2 / Cycles CPU',
 'geometry':'Original mesh positions, face topology and UVs; source skin weights; new simplified deformations.',
 'materials':'Original diffuse texture; adapted two-tone shader, not a ShaderFX-equivalent renderer.',
 'original_mesh_parts':len(meshes),'base_vertices':sum(len(v['vertices']) for v in meshes.values()),
 'base_polygons':sum(len(v['faces']) for v in meshes.values()),
 'images':[{'file':'images/'+p.name,'label':label,'width':1024,'height':1024,'sha256':sha(p)} for p,label in zip(images,LABELS)],
 'animation':{'file':video.name,'width':720,'height':720,'fps':24,'frames':count,'seconds':secs,'audio':False,'sha256':sha(video),'full_decode_passed':True},
 'motion':'New six-second greeting: anticipation, raise left hand, three wrist waves, head/torso movement, settle. Not the previous untested Maya draft and not a reused clip.',
 'limitations':['Maya constraint graph, facial rig, cloth collision and ShaderFX are not evaluated.','Visual equivalence to the supplied reference is not claimed to be 100%.'],
 'attribution':'Original model/rig: Megabubu; character: ZUN / Team Shanghai Alice. Non-commercial with credit per creator README.',
}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
(OUT/'BACA_DULU.md').write_text((ROOT/'docs/HASIL_BARU.md').read_text())
package=ROOT/'deliverables/Reimu_Baru_10_Gambar_dan_Animasi.zip'
with zipfile.ZipFile(package,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in sorted(OUT.rglob('*')):
        if path.is_file():z.write(path,'Reimu_Baru/'+path.relative_to(OUT).as_posix())
with zipfile.ZipFile(package) as z:assert z.testzip() is None
print(json.dumps({'new_images':len(images),'new_animation_frames':count,'seconds':secs,'video_bytes':video.stat().st_size,'bundle_bytes':package.stat().st_size},indent=2))
