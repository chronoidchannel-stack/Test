import collections, json, pathlib, re, zipfile
import xml.etree.ElementTree as ET
archive = zipfile.ZipFile('source/REMU_rig_v8.zip')
out = pathlib.Path('reports')
notes = []
for name in archive.namelist():
    if name.lower().endswith('.docx'):
        import io
        with zipfile.ZipFile(io.BytesIO(archive.read(name))) as doc:
            tree = ET.fromstring(doc.read('word/document.xml'))
            paragraphs = [''.join(p.itertext()) for p in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')]
            notes.append(name + '\n' + '\n'.join(paragraphs))
(out/'source-readme.txt').write_text('\n\n'.join(notes))
data = archive.read('v008/Reimu_Rig_master_nonToon.ma').decode('utf-8', errors='replace')
nodes = re.findall(r'^createNode (\S+) -n "([^"]+)"([^;]*);', data, re.M)
(out/'maya-nodes.json').write_text(json.dumps([{'type':t,'name':n,'options':o} for t,n,o in nodes],indent=2))
(out/'maya-header.txt').write_text(data[:6000])
print(collections.Counter(t for t,n,o in nodes))
# Record the small controller transform settings, not bulk mesh arrays.
chunks = re.split(r'(?=^createNode )', data, flags=re.M)
transforms = []
for chunk in chunks:
    if chunk.startswith('createNode transform ') or chunk.startswith('createNode joint '):
        transforms.append(chunk[:6000])
(out/'maya-transforms.txt').write_text('\n'.join(transforms))
