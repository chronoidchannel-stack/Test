"""Convert the creator-supplied GIF to MP4, NOT render our Maya draft.
The output filename, credits and metadata explicitly identify its provenance.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from PIL import Image, ImageSequence
import imageio_ffmpeg

SOURCE_MEMBER = 'Info/ANIM_Megabubu.gif'
root = Path(__file__).resolve().parents[1]
source = root/'source'
out = root/'deliverables'
report = root/'reports'
out.mkdir(exist_ok=True)
report.mkdir(exist_ok=True)
with zipfile.ZipFile(source/'REMU_rig_v8.zip') as archive:
    data = archive.read(SOURCE_MEMBER)
gif = source/'ANIM_Megabubu.gif'
gif.write_bytes(data)
with Image.open(gif) as image:
    width, height = image.size
    durations = [frame.info.get('duration', 100) for frame in ImageSequence.Iterator(image)]
    frames = len(durations)
    duration = sum(durations) / 1000
    image.seek(frames//2)
    image.convert('RGB').save(report/'demo-preview.png')
video = out/'Reimu_ORIGINAL_DEMO.mp4'
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
# Explicitly do NOT loop the source forever; preserve one original animation cycle.
command = [ffmpeg, '-hide_banner', '-y', '-ignore_loop', '1', '-i', str(gif),
           '-an', '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
           '-fps_mode', 'vfr', '-movflags', '+faststart',
           '-metadata', 'title=Reimu - Original Megabubu Demo (GIF to MP4)',
           '-metadata', 'artist=Megabubu',
           '-metadata', 'comment=Converted from Info/ANIM_Megabubu.gif in creator-supplied REMU_rig_v8.zip. Not a render of the new greeting draft. Non-commercial use with credit.',
           str(video)]
subprocess.run(command, check=True)
# Decode the complete result to catch corrupt packets or an invalid container.
check = subprocess.run([ffmpeg, '-v', 'error', '-i', str(video), '-f', 'null', '-'],
                       check=True, capture_output=True, text=True)
# Ask the same decoder for duration/frame count and codec information.
metadata = imageio_ffmpeg.read_frames(str(video), pix_fmt='rgb24')
info = next(metadata)
metadata.close()
frame_count, decoded_duration = imageio_ffmpeg.count_frames_and_secs(str(video))
assert video.stat().st_size > 1000
assert abs(decoded_duration-duration) < .15, (decoded_duration, duration)
assert frame_count > 1
credits = '''REIMU — ORIGINAL DEMO / KONVERSI MP4

Video ini berasal dari animasi contoh yang sudah ada di paket pembuat:
REMU_rig_v8.zip → Info/ANIM_Megabubu.gif.

Animasi demo dan rig asli: Megabubu
https://gumroad.com/megabubu
Karakter Reimu Hakurei / Touhou Project: ZUN / Team Shanghai Alice.

Pekerjaan pada file ini: konversi GIF menjadi MP4 H.264 yang kompatibel dengan
pemutar video umum. Satu siklus animasi asli, tanpa audio dan tanpa upscaling.
Padding maksimal satu piksel ditambahkan bila dimensi GIF ganjil.

PENTING: Ini bukan animasi baru buatan asisten, bukan render draft greeting
5 detik, dan bukan bukti bahwa rig Maya berhasil dievaluasi di lingkungan ini.
Draft .ma tetap perlu Autodesk Maya untuk review dan rendering.

README asli mengizinkan penggunaan nonkomersial dengan kredit kepada pembuat.
Sertakan kredit ini saat membagikan video. Jangan klaim animasi/model asli
sebagai karya sendiri. Lihat reports/source-readme.txt untuk petunjuk asli.
'''
(out/'Reimu_ORIGINAL_DEMO_CREDITS.txt').write_text(credits)
(report/'demo-conversion.json').write_text(json.dumps({
    'provenance': SOURCE_MEMBER,
    'is_new_animation': False,
    'is_greeting_draft_render': False,
    'source_sha256': hashlib.sha256(data).hexdigest(),
    'source_dimensions': [width,height], 'source_frames': frames,
    'source_duration_seconds': duration,
    'output_dimensions': list(info['size']), 'output_codec': info['codec'],
    'output_frames': frame_count, 'output_duration_seconds': decoded_duration,
    'output_bytes': video.stat().st_size,
    'output_sha256': hashlib.sha256(video.read_bytes()).hexdigest(),
    'complete_decode_passed': True,
    'audio': False,
    'credit': 'Megabubu — https://gumroad.com/megabubu',
    'usage': 'Non-commercial use with attribution, per original README',
}, indent=2))
print((report/'demo-conversion.json').read_text())
