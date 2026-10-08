"""New poses/renders using geometry, UVs and skin weights from the original Maya asset.
This is a simplified, independently authored deformation/render pipeline, not an
emulation of Maya's constraints or ShaderFX. No demo GIF/video is used.
"""
import os, sys, re, json, math, argparse, pickle
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'.cache/native/Reimu'
CACHE=ROOT/'.cache/reimu_parsed.pkl'
PARTS={
 'head':'head_geoShapeOrig2', 'eyes':'eyes_geoShapeOrig',
 'highlight':'highlight_geoShapeOrig','body':'body_geoShapeOrig1',
 'face':'facial_misc_geoShapeOrig', 'hair_sides':'hairWisk_geoShapeOrig1',
 'hair':'hair_geo_newShapeOrig2','ponytail':'ponytail_geo_newShapeOrig2',
 'bloomers':'bloomer_geoShapeOrig','skirt':'skirt_geoShapeOrig1',
 'top':'top_geoShapeOrig1','bow':'bow_geoShapeOrig1','sleeves':'sleeve_geoShapeOrig1',
}
SHAPES={'hair':'hair_geo_newShape','ponytail':'ponytail_geo_newShape','hair_sides':'hairWisk_geoShape','face':'facial_misc_geoShape','bloomers':'bloomer_geoShape','sleeves':'sleeve_geoShape','bloomers':'bloomer_geoShape'}

def indexed(block, attr, width, dtype=float):
    arr={}
    pattern=r'setAttr(?:\s+-s\s+\d+)?\s+"'+re.escape(attr)+r'\[(\d+)(?::(\d+))?\]"\s*(?:-type\s+"[^"]+"\s*)?([^;]+);'
    for m in re.finditer(pattern,block):
        start=int(m[1]); end=int(m[2] or m[1]); vals=np.fromstring(m[3],sep=' ',dtype=dtype)
        if vals.size!=(end-start+1)*width:raise ValueError((attr,start,end,vals.size))
        for i,v in enumerate(vals.reshape(-1,width)):arr[start+i]=v
    if not arr:return np.zeros((0,width),dtype=dtype)
    return np.array([arr[i] for i in range(max(arr)+1)],dtype=dtype)

def parse():
    if CACHE.exists():return pickle.loads(CACHE.read_bytes())
    text=(ASSETS/'Reimu_Rig_master.ma').read_text(encoding='cp1252')
    nodes={m[2]:(m[1],m[0]) for m in re.finditer(r'^createNode (\S+) -n "([^"]+)".*?(?=^createNode |^select -ne |\Z)',text,re.M|re.S)}
    links=re.findall(r'connectAttr\s+"([^"]+)"\s+"([^"]+)"',text)
    meshes={}; binds={}
    for label,name in PARTS.items():
        block=nodes[name][1]
        verts=indexed(block,'.vt',3)
        edges=indexed(block,'.ed',3,int)
        uv=indexed(block,'.uvst[0].uvsp',2)
        faces=[]; fuv=[]
        for m in re.finditer(r'setAttr[^;]*?"\.fc\[\d+(?::\d+)?\]"(?:\s+-type "polyFaces")?\s+([^;]+);',block):
            current=None
            for line in m[1].splitlines():
                a=line.strip().split()
                if not a:continue
                if a[0]=='f':
                    edgeids=[int(v) for v in a[2:]]
                    face=[int(edges[i,0] if i>=0 else edges[-i-1,1]) for i in edgeids]
                    assert len(face)==int(a[1])
                    faces.append(face); fuv.append(None);current=len(faces)-1
                elif a[0]=='mu' and a[1]=='0': fuv[current]=[int(v) for v in a[3:]]
        assert len(faces)>0 and all(u is not None for u in fuv), name
        visible=SHAPES.get(label,label+'_geoShape')
        skin=next((a.split('.')[0] for a,b in links if b==visible+'.i' and a.split('.')[0] in nodes and nodes[a.split('.')[0]][0]=='skinCluster'),None)
        influences={};weights=None
        if skin:
            sb=nodes[skin][1]
            for a,b in links:
                ma=re.fullmatch(re.escape(skin)+r'\.ma\[(\d+)\]',b)
                if ma:influences[int(ma[1])]=a.split('.')[0]
            weights=np.zeros((len(verts),max(influences)+1))
            for m in re.finditer(r'setAttr\s+"\.wl\[(\d+)(?::(\d+))?\]\.w"\s+([^;]+);',sb):
                i=int(m[1]);end=int(m[2] or m[1]); tokens=m[3].split();pos=0
                for v in range(i,end+1):
                    count=int(tokens[pos]);pos+=1
                    for _ in range(count):
                        joint=int(tokens[pos]);w=float(tokens[pos+1]);pos+=2
                        weights[v,joint]=w
                assert pos==len(tokens)
            # Some older arrays use indexed individual weights; handle those too.
            for m in re.finditer(r'setAttr[^;]*?"\.wl\[(\d+)\]\.w\[(\d+)(?::(\d+))?\]"\s+([^;]+);',sb):
                v=int(m[1]);lo=int(m[2]);hi=int(m[3] or m[2]);weights[v,lo:hi+1]=np.fromstring(m[4],sep=' ')
            for m in re.finditer(r'setAttr "\.pm\[(\d+)\]" -type "matrix"\s+([^;]+);',sb):
                i=int(m[1]);inv=np.fromstring(m[2],sep=' ').reshape(4,4).T
                if i in influences:binds.setdefault(influences[i],np.linalg.inv(inv))
            sums=weights.sum(axis=1)
            if not np.allclose(sums,1,atol=.001):print('WEIGHT WARNING',label,sums.min(),sums.max())
            weights/=np.maximum(sums[:,None],1e-10)
        meshes[label]={'vertices':verts,'faces':faces,'uv':uv,'fuv':fuv,'influences':influences,'weights':weights,'skin':skin,'source_node':name}
        print('PARSED',label,len(verts),len(faces),skin,flush=True)
    result=(meshes,binds)
    CACHE.write_bytes(pickle.dumps(result))
    return result

def rot(angles):return Rotation.from_euler('xyz',angles,degrees=True).as_matrix()
def matrix(r=None,p=None):
    m=np.eye(4)
    if r is not None:m[:3,:3]=r
    if p is not None:m[:3,3]=p
    return m

def pivot(r,p):return matrix(r,p-r@p)
def xyz(v):return np.column_stack((v[:,0],-v[:,2],v[:,1]))/100

def material(name,tex=None,color=(1,1,1,1),hair=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
    out=n.new('ShaderNodeOutputMaterial');emit=n.new('ShaderNodeEmission')
    if tex:
        t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(tex),check_existing=True);t.interpolation='Linear'
        geom=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(-.28,-.62,.735)
        l.new(geom.outputs['Normal'],dot.inputs[0])
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
        ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=(.50,.46,.50,1)
        ramp.color_ramp.elements[1].position=.22;ramp.color_ramp.elements[1].color=(1,1,1,1)
        l.new(dot.outputs['Value'],ramp.inputs[0])
        mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1
        color_output=t.outputs['Color']
        if hair:
            sep=n.new('ShaderNodeSeparateColor');sep.mode='HSV';l.new(t.outputs['Color'],sep.inputs[0])
            dark=n.new('ShaderNodeMath');dark.operation='LESS_THAN';dark.inputs[1].default_value=.3;l.new(sep.outputs[2],dark.inputs[0])
            gray=n.new('ShaderNodeMath');gray.operation='LESS_THAN';gray.inputs[1].default_value=.45;l.new(sep.outputs[1],gray.inputs[0])
            mask=n.new('ShaderNodeMath');mask.operation='MULTIPLY';l.new(dark.outputs[0],mask.inputs[0]);l.new(gray.outputs[0],mask.inputs[1])
            tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[2].default_value=(.48,.38,.34,1)
            l.new(mask.outputs[0],tint.inputs[0]);l.new(t.outputs['Color'],tint.inputs[1]);color_output=tint.outputs[0]
        l.new(color_output,mul.inputs[1]);l.new(ramp.outputs['Color'],mul.inputs[2]);l.new(mul.outputs[0],emit.inputs[0])
    else:emit.inputs[0].default_value=color
    l.new(emit.outputs[0],out.inputs['Surface']);return m

def look(obj,target):obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def setup(meshes,res=800):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8
    scene.cycles.use_denoising=False;scene.cycles.max_bounces=1;scene.render.threads_mode='FIXED';scene.render.threads=4
    scene.render.resolution_x=res;scene.render.resolution_y=res;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast'
    scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    world=bpy.data.worlds.new('Studio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.8,.85,1,1);world.node_tree.nodes['Background'].inputs[1].default_value=.55;scene.world=world
    tex=material('Original Reimu diffuse map',ASSETS/'reimu_diffuse_tex.tga')
    white=material('Original eye glints',color=(1,1,1,1))
    hairmat=material('Adapted toon hair',ASSETS/'reimu_diffuse_tex.tga',hair=True)
    objects={}
    for label,d in meshes.items():
        mesh=bpy.data.meshes.new(label);mesh.from_pydata(xyz(d['vertices']).tolist(),[],d['faces']);mesh.update()
        ob=bpy.data.objects.new(label,mesh);scene.collection.objects.link(ob);mesh.materials.append(white if label=='highlight' else hairmat if label in ['hair','hair_sides','ponytail'] else tex)
        uv=mesh.uv_layers.new(name='map1')
        for poly,indices in zip(mesh.polygons,d['fuv']):
            for li,ui in zip(poly.loop_indices,indices):uv.data[li].uv=d['uv'][ui]
            poly.use_smooth=True
        mod=ob.modifiers.new('Surface smoothing','SUBSURF');mod.levels=1;mod.render_levels=1
        objects[label]=ob
    bpy.ops.object.camera_add(location=(0,-5,1.05));camera=bpy.context.object;camera.name='Portrait camera';camera.data.type='ORTHO';camera.data.ortho_scale=2.06;look(camera,(0,0,.91));scene.camera=camera
    for name,pos,power,size in [('Key',(-3,-4,5),450,4),('Fill',(3,-2,3),160,3),('Rim',(0,3,4),350,3)]:
        bpy.ops.object.light_add(type='AREA',location=pos);lamp=bpy.context.object;lamp.name=name;lamp.data.energy=power;lamp.data.shape='DISK';lamp.data.size=size;look(lamp,(0,0,1))
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.006));floor=bpy.context.object;floor.name='Studio floor';floor.data.materials.append(material('Warm paper',color=(.91,.87,.84,1)))
    return scene,objects,camera

def apply_rest(meshes,objects):
    for n,d in meshes.items():objects[n].data.vertices.foreach_set('co',xyz(d['vertices']).ravel());objects[n].data.update()

def apply_pose(deformer,p,objects):
    for name,vertices in deformer.vertices(p).items():
        objects[name].data.vertices.foreach_set('co',xyz(vertices).astype(np.float32).ravel());objects[name].data.update()
    bpy.context.view_layer.update()

POSES=[('01_default_front','front','Default · Depan'),('02_default_back','back','Default · Belakang'),
       ('03_wave','wave','Melambai'),('04_peace','peace','Peace!'),('05_cheeks','cheeks','Tangan di pipi'),
       ('06_heart','heart','Hati kecil'),('07_shy','shy','Malu-malu'),('08_bow','bow','Membungkuk'),
       ('09_tiptoe','tiptoe','Berjinjit'),('10_cheer','cheer','Ceria')]

def create_heart():
    v=[(0,-.30,1.125)]
    for i in range(96):
        t=i*2*math.pi/96;x=16*math.sin(t)**3;y=13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)
        v.append((x*.0047,-.30,1.13+y*.0047))
    faces=[(0,i+1,(i+1)%96+1) for i in range(96)]
    mesh=bpy.data.meshes.new('New heart accent');mesh.from_pydata(v,[],faces);mesh.materials.append(material('Rose heart',color=(.88,.075,.20,1)))
    ob=bpy.data.objects.new('New heart accent',mesh);bpy.context.scene.collection.objects.link(ob);ob.hide_render=True;return ob

def main():
    from reimu_motion import Deformer, pose, animated
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='.cache/rest.png');ap.add_argument('--res',type=int,default=640);ap.add_argument('--pose',default='front');ap.add_argument('--batch',action='store_true');ap.add_argument('--animation',action='store_true');ap.add_argument('--frames',type=int,default=144);ap.add_argument('--fps',type=int,default=24);ap.add_argument('--samples',type=int,default=8);ap.add_argument('--start-frame',type=int,default=0);ap.add_argument('--end-frame',type=int,default=None);args=ap.parse_args()
    meshes,binds=parse();scene,objects,cam=setup(meshes,args.res);scene.cycles.samples=args.samples
    deformer=Deformer(meshes,binds);heart=create_heart()
    if args.animation:
        folder=ROOT/args.out;folder.mkdir(parents=True,exist_ok=True)
        for f in range(args.start_frame,min(args.frames,args.end_frame if args.end_frame is not None else args.frames)):
            target=folder/f'{f:04d}.png'
            if target.exists():continue
            p=animated(f/args.fps);apply_pose(deformer,p,objects)
            scene.render.filepath=str(target);bpy.ops.render.render(write_still=True)
            print(f'NEW_ANIMATION_FRAME {f+1}/{args.frames}',flush=True)
    else:
        jobs=POSES if args.batch else [(Path(args.out).stem,args.pose,args.pose)]
        for filename,name,title in jobs:
            apply_pose(deformer,pose(name),objects);heart.hide_render=name!='heart'
            cam.location=(0,5 if name=='back' else -5,1.05);look(cam,(0,0,.91))
            target=ROOT/args.out/(filename+'.png') if args.batch else ROOT/args.out
            target.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(target);bpy.ops.render.render(write_still=True)
            print('NEW_POSE_RENDERED',name,flush=True)
if __name__=='__main__':main()
