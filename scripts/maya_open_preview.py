"""Run in Autodesk Maya's Python Script Editor. This is NOT a Blender script.
Opens a chosen greeting scene with source script nodes disabled, repairs exposed
texture paths, selects DG evaluation, and creates a Viewport 2.0 preview window.
Requires a Maya installation/license. Not runtime-tested in this environment.
"""
from pathlib import Path
import maya.cmds as cmds


def open_preview():
    selected = cmds.fileDialog2(fileMode=1, caption='Pilih Reimu_Greeting_DRAFT.ma',
                               fileFilter='Maya ASCII (*.ma)')
    if not selected:
        return
    path = Path(selected[0]).resolve()
    # Never silently discard the artist's unsaved current scene.
    if cmds.file(query=True, modified=True):
        choice = cmds.confirmDialog(title='Scene belum disimpan',
                                    message='Simpan pekerjaan sekarang sebelum membuka draft.',
                                    button=['Batal'], defaultButton='Batal')
        cmds.warning('Pembukaan dibatalkan. Simpan scene terlebih dahulu.')
        return
    root = path.parent
    cmds.workspace(str(root), openWorkspace=True)
    cmds.file(str(path), open=True, executeScriptNodes=False, prompt=False)
    cmds.currentUnit(time='ntsc')
    cmds.playbackOptions(minTime=1, maxTime=150, animationStartTime=1, animationEndTime=150,
                         playbackSpeed=1)
    cmds.evaluationManager(mode='off')  # DG: recommended in the original README.
    assets = {p.name.lower(): p for p in root.iterdir() if p.is_file()}
    repaired = []
    missing = []
    # File nodes and public ShaderFX string attributes, not only fileTextureName.
    for node in (cmds.ls(type='file') or []) + (cmds.ls(type='ShaderfxShader') or []):
        for attr in cmds.listAttr(node, scalar=True, read=True, write=True) or []:
            plug = node + '.' + attr
            try:
                if cmds.getAttr(plug, type=True) != 'string':
                    continue
                value = cmds.getAttr(plug)
                if not value or len(value) > 2000:
                    continue
                filename = value.replace('\\', '/').rsplit('/', 1)[-1]
                if not filename.lower().endswith(('.png','.tga','.tx','.jpg','.jpeg')):
                    continue
                if filename.lower() in assets and not cmds.getAttr(plug, lock=True):
                    cmds.setAttr(plug, assets[filename.lower()].as_posix(), type='string')
                    repaired.append(plug)
                else:
                    missing.append(plug + ': ' + value)
            except RuntimeError:
                continue
    cmds.currentTime(60, edit=True)
    if cmds.window('arenaReimuPreview', exists=True):
        cmds.deleteUI('arenaReimuPreview')
    window = cmds.window('arenaReimuPreview', title='Reimu — DRAFT / Megabubu rig', widthHeight=(800,800))
    layout = cmds.paneLayout(parent=window)
    panel = cmds.modelPanel(parent=layout, camera='arenaGreetingCamera', menuBarVisible=False)
    cmds.modelEditor(panel, edit=True, rendererName='vp2Renderer', displayAppearance='smoothShaded',
                     displayTextures=True, displayLights='default', grid=False,
                     nurbsCurves=False, joints=False, locators=False, cameras=False,
                     selectionHiliteDisplay=False)
    cmds.showWindow(window)
    cmds.setFocus(panel)
    cmds.select(clear=True)
    print('Texture attributes repaired:', len(repaired))
    for item in missing:
        cmds.warning('Periksa texture: ' + item)
    print('Draft 1–150 / 30 FPS. Tekan Play. Periksa pose, kedipan, tabrakan kain dan ShaderFX sebelum render.')
    return panel


if __name__ == '__main__':
    open_preview()
