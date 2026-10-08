"""Independently authored poses and procedural animation. Maya coordinates (cm).
Uses the original per-vertex skin weights, not pre-rendered demo images.
"""
import math
import numpy as np
from scipy.spatial.transform import Rotation

def R(a):return Rotation.from_euler('xyz',a,degrees=True).as_matrix()
def M(r=None,t=None):
    a=np.eye(4)
    if r is not None:a[:3,:3]=r
    if t is not None:a[:3,3]=t
    return a

def pivot(r,p):
    p=np.asarray(p,dtype=float);return M(r,p-r@p)
def align(a,b):
    a=a/np.linalg.norm(a);b=b/np.linalg.norm(b);v=np.cross(a,b);c=np.dot(a,b)
    if c>.999999:return np.eye(3)
    if c<-.999999:
        axis=np.cross(a,np.array([0.,1,0]));axis/=np.linalg.norm(axis);return Rotation.from_rotvec(axis*np.pi).as_matrix()
    k=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    return np.eye(3)+k+k@k/(1+c)

def default():
    return {'head':[0,0,0],'body':[0,0,0],'yaw':0.,'lift':0.,
            'L':{'wrist':[39,85,5],'hand':[.40,-.9,.05],'curl':8},
            'R':{'wrist':[-39,85,5],'hand':[-.40,-.9,.05],'curl':8}}

def pose(name):
    p=default()
    if name=='wave':
        p['L']={'wrist':[43,136,8],'hand':[.05,1,0],'curl':0};p['head']=[0,-5,-7];p['yaw']=-8
    elif name=='peace':
        p['L']={'wrist':[34,133,13],'hand':[-.2,1,0],'curl':75,'peace':True};p['head']=[-2,6,8];p['yaw']=8
    elif name=='cheeks':
        for side,s in [('L',1),('R',-1)]:p[side]={'wrist':[s*29,121,19],'hand':[-s*.2,1,-.05],'curl':12}
        p['head']=[-3,0,-5]
    elif name=='heart':
        for side,s in [('L',1),('R',-1)]:p[side]={'wrist':[s*17,106,22],'hand':[-s*.65,.78,0],'curl':65,'heart':True}
        p['head']=[0,0,5]
    elif name=='shy':
        for side,s in [('L',1),('R',-1)]:p[side]={'wrist':[s*11,91,23],'hand':[-s*.55,-.85,0],'curl':45}
        p['head']=[8,10,-9];p['yaw']=-12
    elif name=='bow':
        for side,s in [('L',1),('R',-1)]:p[side]={'wrist':[s*16,86,20],'hand':[-s*.3,-.8,.1],'curl':14}
        p['body']=[25,0,0];p['head']=[-12,0,0];p['yaw']=18
    elif name=='tiptoe':
        p['lift']=4;p['tiptoe']=True;p['head']=[-4,5,-6]
        p['L']={'wrist':[35,117,15],'hand':[.2,1,0],'curl':75}
        p['R']={'wrist':[-35,117,15],'hand':[-.2,1,0],'curl':75}
        p['yaw']=-15
    elif name=='cheer':
        p['L']={'wrist':[30,148,3],'hand':[.3,1,0],'curl':0}
        p['R']={'wrist':[-35,142,7],'hand':[-.4,1,0],'curl':0}
        p['head']=[-5,-7,8];p['yaw']=10;p['kick']='R'
    return p

def animated(t):
    p=default()
    # Six seconds: anticipation, hand raise, three waves, settle.
    def ease(a):a=np.clip(a,0,1);return a*a*(3-2*a)
    a=float(ease((t-.4)/1.0)*(1-ease((t-4.55)/1.0)))
    target=np.array([43,136,8]);rest=np.array(p['L']['wrist'])
    p['L']['wrist']=(rest*(1-a)+target*a).tolist()
    wave=math.sin((t-1.4)*math.pi*2*1.25)*.32*a
    h=np.array([.4,-.9,.05])*(1-a)+np.array([wave,1.,.04])*a
    # Avoid a zero hand direction during the transition via an outward arc.
    h[0]+=.8*math.sin(a*math.pi)
    p['L']['hand']=h.tolist();p['L']['curl']=8*(1-a)
    p['head']=[-2*math.sin(t*1.1),-4*a,-6*a+math.sin(t*2)*1.4]
    p['body']=[0,0,math.sin(t*1.4)*.8]
    p['yaw']=-5+math.sin(t*.7)*3
    p['lift']=.3+.3*math.sin(t*math.pi)
    return p

class Deformer:
    def __init__(self,meshes,binds):self.meshes=meshes;self.binds=binds
    def pos(self,n,fallback=None):
        if n in self.binds:return self.binds[n][:3,3]
        return np.asarray(fallback,dtype=float)
    def matrices(self,p):
        body=pivot(R(p['body']),[0,88,0]);head=body@pivot(R(p['head']),[0,124.575,-.897])
        transforms={};arms={}
        for side,s in [('L',1),('R',-1)]:
            sp=self.pos(side+'_upArm_bendy_01_drvjnt');ep=self.pos(side+'_loArm_bendy_01_drvjnt');wp=self.pos(side+'_hand_drvjnt')
            target=np.array(p[side]['wrist'],float);d=target-sp;l1=np.linalg.norm(ep-sp);l2=np.linalg.norm(wp-ep)
            dist=np.clip(np.linalg.norm(d),abs(l1-l2)+.5,l1+l2-.4);axis=d/np.linalg.norm(d);target=sp+axis*dist
            pole=np.array([s*55.,105.,-12.])-sp;pole-=axis*np.dot(pole,axis);pole/=np.linalg.norm(pole)
            along=(l1*l1-l2*l2+dist*dist)/(2*dist);height=math.sqrt(max(0,l1*l1-along*along));elbow=sp+axis*along+pole*height
            ru=align(ep-sp,elbow-sp);rl=align(wp-ep,target-elbow)
            upper=M(ru,sp-ru@sp);lower=M(rl,elbow-rl@ep)
            forward=np.array(p[side]['hand'],float);forward/=np.linalg.norm(forward)
            palm=np.array([0.,0,1.]);palm-=forward*np.dot(palm,forward);palm/=np.linalg.norm(palm)
            frame=np.column_stack((forward,palm,np.cross(forward,palm)))
            old=np.column_stack(([s,0,0],[0,-1,0],[0,0,-s]))
            rh=frame@old.T;hand=M(rh,target-rh@wp)
            arms[side]=(body@upper,body@lower,body@hand)
            transforms[side+'_hand_drvjnt']=body@hand
            for finger in ['index','middle','ring','pinky','thumb']:
                previous=hand.copy()
                for j in ([0,1,2] if finger=='thumb' else [0,1,2,3]):
                    name=side+('_thumb_' if finger=='thumb' else '_finger_'+finger+'_')+f'{j:02d}_drvjnt'
                    if name not in self.binds:continue
                    amount=p[side].get('curl',0)
                    if p[side].get('peace') and finger in ('index','middle'):amount=0
                    if p[side].get('heart') and finger=='index':amount=25 if j==1 else 50
                    if p[side].get('heart') and finger=='thumb':amount=10
                    angle=0 if j==0 else amount*(.75 if j==3 else 1)
                    yaw=0
                    if p[side].get('peace') and j==1 and finger in ('index','middle'):yaw=(-9 if finger=='index' else 7)*s
                    previous=previous@pivot(R([0,yaw,-s*angle]),self.pos(name))
                    transforms[name]=body@previous
        for name in self.binds:
            if name in transforms:continue
            side='L' if name.startswith('L_') else 'R' if name.startswith('R_') else None
            if side and 'upArm' in name:transforms[name]=arms[side][0]
            elif side and ('loArm' in name or 'sleeve' in name):transforms[name]=arms[side][1]
            elif 'neck' in name:transforms[name]=body@pivot(R(np.array(p['head'])*.45),[0,117,0])
            elif 'spine' in name or 'clav' in name:transforms[name]=body
            elif any(k in name for k in ['hair','head','bow','ponytail']):transforms[name]=head
            else:transforms[name]=np.eye(4)
        if p.get('tiptoe'):
            for side in ['L','R']:
                foot=pivot(R([27,0,0]),self.pos(side+'_ankle_drvjnt'))
                for name in transforms:
                    if name.startswith(side+'_') and ('foot' in name or 'ankle' in name):transforms[name]=foot
        if p.get('kick'):
            side=p['kick'];hip=self.pos(side+'_upLeg_bendy_01_drvjnt');knee=self.pos(side+'_loLeg_bendy_01_drvjnt')
            thigh=pivot(R([-12,0,12]),hip);lower=thigh@pivot(R([55,0,0]),knee)
            for name in transforms:
                if name.startswith(side+'_'):
                    if 'upLeg' in name:transforms[name]=thigh
                    elif any(k in name for k in ['loLeg','foot','ankle']):transforms[name]=lower
        root=M(R([0,p['yaw'],0]),[0,p['lift'],0])
        return transforms,root,head,body
    def vertices(self,p):
        transforms,root,head,body=self.matrices(p);result={}
        for label,d in self.meshes.items():
            v=d['vertices'];vh=np.column_stack((v,np.ones(len(v))))
            if label in ['head','eyes','highlight','face','hair','hair_sides','ponytail','bow']:
                posed=vh@head.T
            elif label in ['skirt','bloomers']:
                # Skirt remains planted; restrained upper-body bow does not
                # apply a cloth simulation or claim Maya's collision behavior.
                posed=vh.copy()
            elif d['weights'] is not None:
                posed=np.zeros_like(vh)
                for i,name in d['influences'].items():
                    mat=transforms.get(name,body if label=='top' else np.eye(4))
                    posed+=(vh@mat.T)*d['weights'][:,i,None]
            else:posed=vh.copy()
            result[label]=(posed@root.T)[:,:3]
        return result
