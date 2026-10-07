"""Author a native Maya animation draft without executing the third-party scene.

This checks structure and asset integrity, NOT Maya evaluation or visual quality.
The draft must be opened in Maya for pose/collision/material review and rendering.
"""
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables'
SOURCE = OUT / 'Reimu_native_source.zip'

# Values are native rig control offsets, not changes to model vertices.
TRACKS = {
    'head_ctrl.rz': [(1,0),(25,-3),(45,-6),(95,-5),(125,2),(150,0)],
    'head_ctrl.ry': [(1,0),(40,4),(95,3),(130,-2),(150,0)],
    'cog_primary_ctrl.ty': [(1,0),(30,.35),(60,0),(90,.35),(120,0),(150,0)],
    'FK_L_arm_01_shoulder_ctrl.rx': [(1,10),(20,10),(42,85),(105,85),(138,10),(150,10)],
    'FK_L_arm_01_shoulder_ctrl.rz': [(1,-65),(20,-65),(42,-20),(105,-20),(138,-65),(150,-65)],
    'FK_L_arm_02_elbow_ctrl.ry': [(1,12),(20,12),(42,85),(105,85),(138,12),(150,12)],
    'FK_L_arm_03_wrist_ctrl.rz': [(1,0),(40,0),(50,-16),(62,16),(74,-16),(86,16),(98,-12),(110,0),(150,0)],
    'FK_R_arm_01_shoulder_ctrl.rz': [(1,-65),(150,-65)],
    'FK_R_arm_02_elbow_ctrl.ry': [(1,12),(150,12)],
}
for side in ('L', 'R'):
    TRACKS[f'{side}_eyeBlink_upper_ctrl.ty'] = [(1,0),(27,0),(30,-7),(32,-7),(36,0),(104,0),(107,-7),(109,-7),(113,0),(150,0)]
    TRACKS[f'{side}_eyeBlink_lower_ctrl.ty'] = [(1,0),(27,0),(30,1.6),(32,1.6),(36,0),(104,0),(107,1.6),(109,1.6),(113,0),(150,0)]


def main():
    with zipfile.ZipFile(SOURCE) as src:
        original = src.read('Reimu/Reimu_Rig_master.ma')
        data = original.decode('cp1252')
        nodes = {m.group(2): m.group(0) for m in re.finditer(
            r'^createNode (\S+) -n "([^"]+)".*?(?=^createNode |^select -ne |\Z)', data, re.M | re.S)}
        commands = ['// Reimu greeting BLOCKING DRAFT — not visually validated in Maya.',
                    '// Original rig: Megabubu. Non-commercial use with credit.',
                    'currentUnit -l centimeter -a degree -t ntsc;']
        for side in ('L', 'R'):
            # The right constraint retains left-side aliases from mirroring;
            # inspect actual connections, not those stale UI aliases.
            assert f'connectAttr "FK_{side}_upArm_drvjnt.t" "{side}_upArm_drvjnt_parentConstraint1.tg[1].tt"' in data
            assert f'connectAttr "{side}_arm_option_ctrl.IKFK" "{side}_upArm_drvjnt_parentConstraint1.w1"' in data
        # The source constraints explicitly bind FK to weight 1, driven by IKFK.
        for side in ('L', 'R'):
            commands.append(f'setAttr "{side}_arm_option_ctrl.IKFK" 1;')
        connections = []
        for plug, keys in TRACKS.items():
            node, attr = plug.split('.')
            assert node in nodes, f'Missing controller {node}'
            assert not re.search(r'setAttr -l on[^;]*"\.' + attr + r'"', nodes[node]), f'Locked channel {plug}'
            assert not re.search(r'connectAttr\s+"[^"]+"\s+"' + re.escape(plug) + r'"', data), f'Channel already driven: {plug}'
            assert all(keys[i][0] < keys[i+1][0] for i in range(len(keys)-1))
            assert keys[0][0] == 1 and keys[-1][0] == 150
            curve = 'arenaGreeting_' + node + '_' + attr
            assert curve not in nodes
            curve_type = 'animCurveTA' if attr.startswith('r') else 'animCurveTL'
            commands += [f'createNode {curve_type} -n "{curve}";',
                         'setAttr ".wgt" no;',
                         f'setAttr -s {len(keys)} ".ktv[0:{len(keys)-1}]" ' + ' '.join(f'{t} {v}' for t,v in keys) + ';']
            connections.append(f'connectAttr "time1.outTime" "{curve}.i";')
            connections.append(f'connectAttr "{curve}.o" "{plug}";')
        commands += connections
        commands += [
            'createNode transform -n "arenaGreetingCamera";',
            'setAttr ".t" -type "double3" 0 90 480;',
            'createNode camera -n "arenaGreetingCameraShape" -p "arenaGreetingCamera";',
            'setAttr ".o" yes;', 'setAttr ".ow" 220;', 'setAttr ".rnd" yes;',
            'setAttr "defaultResolution.width" 1080;',
            'setAttr "defaultResolution.height" 1080;',
            'setAttr "defaultResolution.pixelAspect" 1;',
            'setAttr "defaultResolution.deviceAspectRatio" 1;',
            'setAttr "defaultRenderGlobals.startFrame" 1;',
            'setAttr "defaultRenderGlobals.endFrame" 150;',
        ]
        patch = '\n'.join(commands) + '\n'
        # Preserve all model/rig/shader nodes. Change only known asset paths and
        # original playback range, then append new animation/camera nodes.
        textures = [Path(n).name for n in src.namelist() if Path(n).suffix.lower() in ('.png','.tga','.tx')]
        changes = 0
        for filename in textures:
            pattern = r'[A-Za-z]:/[^"\n\\]*?/' + re.escape(filename)
            data, count = re.subn(pattern, filename, data)
            changes += count
        data = data.replace('playbackOptions -min 0 -max 150 -ast 0 -aet 250',
                            'playbackOptions -min 1 -max 150 -ast 1 -aet 150')
        animated = (data + '\n' + patch).encode('cp1252')
        # All original mesh node blocks must remain byte-identical.
        pattern = rb'^createNode mesh .*?(?=^createNode |^select -ne |\Z)'
        meshes_before = re.findall(pattern, original, re.M | re.S)
        meshes_after = re.findall(pattern, animated, re.M | re.S)
        assert meshes_before and meshes_before == meshes_after
        readme = (ROOT / 'docs/ANIMASI_REIMU.md').read_text()
        package = OUT / 'Reimu_Greeting_DRAFT_Maya.zip'
        manifest = []
        with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for name in src.namelist():
                if name.endswith('.ma') or name.endswith('SHA256.json'):
                    continue
                content = src.read(name)
                if name.endswith('CREDITS.txt'):
                    content = content.replace(b'The included source is not a new animation or a GLB export.', b'This derivative includes a new structurally checked animation draft. It is not visually tested or a GLB export.')
                z.writestr(name, content)
                manifest.append({'file': name, 'sha256': hashlib.sha256(content).hexdigest()})
            z.writestr('Reimu/Reimu_Greeting_DRAFT.ma', animated)
            z.writestr('Reimu/READ_ME_FIRST.md', readme)
            z.writestr('Reimu/open_preview.py', (ROOT / 'scripts/maya_open_preview.py').read_bytes())
            z.writestr('Reimu/greeting_curves.mel', patch)
            z.writestr('Reimu/workspace.mel', '// Maya project with co-located original textures\nworkspace -fr "scene" ".";\nworkspace -fr "sourceImages" ".";\nworkspace -fr "images" "renders";\n')
            manifest.append({'file': 'Reimu/Reimu_Greeting_DRAFT.ma', 'sha256': hashlib.sha256(animated).hexdigest()})
            z.writestr('Reimu/ANIMATION_MANIFEST.json', json.dumps(manifest, indent=2))
        with zipfile.ZipFile(package) as z:
            assert z.testzip() is None
            assert z.read('Reimu/Reimu_Greeting_DRAFT.ma') == animated
        report = {
            'status': 'STRUCTURALLY_VALIDATED_DRAFT_NOT_MAYA_TESTED',
            'fps': 30, 'start_frame': 1, 'end_frame': 150,
            'tracks': TRACKS, 'original_mesh_nodes_preserved': len(meshes_before),
            'texture_path_references_made_relative': changes,
            'package_bytes': package.stat().st_size,
            'source_scene_sha256': hashlib.sha256(original).hexdigest(),
            'animated_scene_sha256': hashlib.sha256(animated).hexdigest(),
            'limitations': ['Maya not installed: scene evaluation, wave direction, blink closure, sleeve and hair collision, and shader output are NOT visually tested.',
                            'No MP4, new 2D render or GLB produced. ShaderFX requires Maya Viewport 2.0.']
        }
        (ROOT/'reports/animation-validation.json').write_text(json.dumps(report,indent=2))
        print(json.dumps({k:v for k,v in report.items() if k!='tracks'},indent=2))

if __name__ == '__main__':
    main()
