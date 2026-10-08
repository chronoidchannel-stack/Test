# Reimu — 10 gambar baru dan animasi baru

## Hasil baru

- **[MP4 animasi baru](deliverables/reimu_new/Reimu_Animasi_Baru.mp4)** — 6 detik, 720 × 720, 24 FPS, 144 frame render baru.
- **[Unduh 10 PNG + MP4 dalam ZIP](deliverables/Reimu_Baru_10_Gambar_dan_Animasi.zip).**
- **[Pratinjau 10 gambar](deliverables/reimu_new/Reimu_10_Gambar.jpg).**
- [Folder sepuluh PNG individual](deliverables/reimu_new/images), masing-masing 1024 × 1024.
- [Cara pembuatan, kredit dan batasan](docs/HASIL_BARU.md).

**2 default:** tampak depan dan belakang. **8 pose imut:** melambai, peace, pipi imut, hati kecil, malu-malu, membungkuk, berjinjit, dan ceria.

Pose dan gerakan pada hasil baru dibuat untuk permintaan ini. Pipeline baru **tidak membaca atau mengulang demo GIF/MP4 lama**. Geometri, UV, tekstur diffuse dan skin weights berasal dari model asli Megabubu; posing dan shading toon disesuaikan untuk Blender/Cycles. Kesamaan shader Maya 100% tidak diklaim.

## Kode baru dan pemeriksaan

- `scripts/render_original.py`: membaca geometri Maya ASCII tanpa menjalankan script file sumber; membuat scene render.
- `scripts/reimu_motion.py`: pose baru, IK sederhana, artikulasi jari, dan lintasan gerakan 6 detik.
- `scripts/render_deliverables.py`: render dalam worker kecil agar penggunaan memori terbatas.
- `scripts/package_new_renders.py`: kredit, encoding MP4 H.264, pemeriksaan decode, lembar pratinjau, manifest, dan paket ZIP.
- `tests/test_new_motion.py`: pemeriksaan kelengkapan topology/UV, skin weights, pose unik, deformasi finite, dan kontinuitas gerak.

```bash
.venv/bin/python scripts/render_deliverables.py --stills --video
.venv/bin/python scripts/package_new_renders.py
.venv/bin/python -m unittest discover -s tests -p 'test_new_motion.py' -v
```

Lihat `docs/HASIL_BARU.md` untuk dependensi dan persiapan aset. Cache, frame antara dan dependensi tidak dimasukkan ke Git.

## Kredit

**Model/rig/tekstur asli: Megabubu** — https://gumroad.com/megabubu. **Karakter Reimu Hakurei / Touhou Project: ZUN / Team Shanghai Alice.** README pembuat mengizinkan penggunaan nonkomersial dengan kredit. [README asli](reports/source-readme.txt).

## Arsip pekerjaan sebelumnya — bukan hasil baru

- [Scene toon asli + tekstur](deliverables/Reimu_native_source.zip).
- [Draft keyframe Maya](deliverables/Reimu_Greeting_DRAFT_Maya.zip), belum dievaluasi/dirender di Maya.
- `deliverables/Reimu_ORIGINAL_DEMO.mp4` adalah konversi demo pembuat dari tahap sebelumnya, **bukan animasi baru**. Tidak digunakan dalam hasil baru di atas.
