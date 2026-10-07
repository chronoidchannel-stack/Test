"""Transfer a losslessly compact native Maya package; no source scripts are executed."""
import hashlib
import json
from pathlib import Path
import zipfile

source = zipfile.ZipFile('source/REMU_rig_v8.zip')
out = Path('deliverables')
out.mkdir(exist_ok=True)
selected = []
for name in source.namelist():
    p = Path(name)
    if len(p.parts) == 2 and p.parts[0] == 'v008':
        if p.suffix.lower() in ('.tga', '.png', '.tx') or p.name == 'Reimu_Rig_master.ma':
            selected.append(name)
package = out / 'Reimu_native_source.zip'
manifest = []
with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for name in selected:
        data = source.read(name)
        target = Path(name).name
        z.writestr('Reimu/' + target, data)
        manifest.append({'file': target, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
    z.writestr('Reimu/ORIGINAL_README.txt', Path('reports/source-readme.txt').read_text())
    z.writestr('Reimu/CREDITS.txt', 'Original Reimu rig: Megabubu — https://gumroad.com/megabubu\nReimu Hakurei / Touhou Project: ZUN / Team Shanghai Alice.\nUse subject to the original creator\'s README: non-commercial use with credit.\nThis package preserves original scene and texture bytes. Backups, sample GIFs and the alternative non-toon scene are omitted.\nThe included source is not a new animation or a GLB export.\n')
    z.writestr('Reimu/SHA256.json', json.dumps(manifest, indent=2))
with zipfile.ZipFile(package) as z:
    assert z.testzip() is None
assert package.stat().st_size < 90_000_000, 'Package too large for ordinary git storage'
Path('reports/compact-package.json').write_text(json.dumps({'bytes': package.stat().st_size, 'sha256': hashlib.sha256(package.read_bytes()).hexdigest(), 'files': manifest}, indent=2))
# Small controller-connection report needed for authoring animation without guessing modes.
import re
data = source.read('v008/Reimu_Rig_master.ma').decode('cp1252')
lines = []
for line in data.splitlines():
    if line.startswith('connectAttr ') and any(word in line for word in ['arm_option_ctrl.IKFK','eyeBlink_upper_ctrl.ty','eyeBlink_lower_ctrl.ty']):
        lines.append(line)
Path('reports/animation-bindings.txt').write_text('\n'.join(lines))
print('Compact native package:', package.stat().st_size, 'bytes')
