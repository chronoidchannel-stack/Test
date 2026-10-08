"""Run native geometry renders in bounded-size workers to release renderer memory."""
import argparse, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JOBS=[('01_default_front','front'),('02_default_back','back'),('03_wave','wave'),('04_peace','peace'),('05_cheeks','cheeks'),('06_heart','heart'),('07_shy','shy'),('08_bow','bow'),('09_tiptoe','tiptoe'),('10_cheer','cheer')]
ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');ap.add_argument('--video',action='store_true');args=ap.parse_args()
env=dict(os.environ);env['LD_LIBRARY_PATH']=str(ROOT/'.cache/libs')+':'+env.get('LD_LIBRARY_PATH','')
logdir=ROOT/'.cache/render_logs';logdir.mkdir(exist_ok=True,parents=True)
def run(label,options):
    print('RENDER_START',label,flush=True)
    with (logdir/(label+'.log')).open('w') as log:
        subprocess.run([sys.executable,str(ROOT/'scripts/render_original.py')]+options,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    print('RENDER_DONE',label,flush=True)
if args.stills:
    for filename,pose in JOBS:
        run(filename,['--pose',pose,'--out',f'deliverables/reimu_new/images/{filename}.png','--res','1024','--samples','16'])
if args.video:
    for start in range(0,144,6):
        run(f'frames_{start:04d}',['--animation','--out','.cache/new_motion','--res','720','--samples','4','--frames','144','--fps','24','--start-frame',str(start),'--end-frame',str(start+6)])
print('RENDERS_COMPLETE',flush=True)
