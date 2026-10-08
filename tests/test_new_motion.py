"""Numerical checks for the new geometry-driven animation (no Maya required)."""
import pickle
import sys
import unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from reimu_motion import Deformer, pose, animated

class NewMotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cache=ROOT/'.cache/reimu_parsed.pkl'
        if not cache.exists():raise unittest.SkipTest('Run the native geometry parser first')
        cls.meshes,cls.binds=pickle.loads(cache.read_bytes())
        cls.deformer=Deformer(cls.meshes,cls.binds)

    def test_all_faces_and_uvs_complete(self):
        self.assertEqual(13,len(self.meshes))
        self.assertEqual(31222,sum(len(m['vertices']) for m in self.meshes.values()))
        self.assertEqual(31332,sum(len(m['faces']) for m in self.meshes.values()))
        for mesh in self.meshes.values():
            self.assertEqual(len(mesh['faces']),len(mesh['fuv']))
            for face,uv in zip(mesh['faces'],mesh['fuv']):
                self.assertEqual(len(face),len(uv))
                self.assertGreaterEqual(min(face),0)
                self.assertLess(max(face),len(mesh['vertices']))
                self.assertGreaterEqual(min(uv),0)
                self.assertLess(max(uv),len(mesh['uv']))

    def test_original_skin_weights_normalized(self):
        for mesh in self.meshes.values():
            if mesh['weights'] is not None:
                self.assertTrue(np.allclose(mesh['weights'].sum(axis=1),1))
                # Source Maya weights contain machine-epsilon negatives.
                self.assertGreaterEqual(mesh['weights'].min(),-1e-12)

    def test_new_poses_distinct_and_finite(self):
        signatures=[]
        for name in ['front','wave','peace','cheeks','heart','shy','bow','tiptoe','cheer']:
            vertices=self.deformer.vertices(pose(name))
            for label,v in vertices.items():
                self.assertTrue(np.isfinite(v).all())
                self.assertEqual(v.shape,self.meshes[label]['vertices'].shape)
            signatures.append(vertices['body'].tobytes())
        self.assertEqual(9,len(set(signatures)))

    def test_motion_is_new_continuous_deformation_not_static_frames(self):
        previous=None;max_step=0.;seen=set()
        for frame in range(144):
            vertices=self.deformer.vertices(animated(frame/24))
            for v in vertices.values():self.assertTrue(np.isfinite(v).all())
            body=vertices['body'];seen.add(body.tobytes())
            if previous is not None:max_step=max(max_step,float(np.linalg.norm(body-previous,axis=1).max()))
            previous=body
        self.assertEqual(144,len(seen))
        self.assertLess(max_step,12.,'Unexpected per-frame teleport in cm')

if __name__=='__main__':unittest.main()
