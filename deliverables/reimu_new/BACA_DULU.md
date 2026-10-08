# Reimu — 10 gambar baru + animasi baru

**Ini hasil render baru, bukan demo bawaan, bukan hasil konversi GIF, dan bukan screenshot video pembuat.**

## Isi paket

- **2 gambar default**, seluruh badan dalam pose dasar: tampak depan dan belakang.
- **8 pose imut:** melambai, peace, pipi imut, hati kecil, malu-malu, membungkuk, berjinjit, dan ceria.
- Sepuluh PNG terpisah, masing-masing **1024 × 1024**.
- `Reimu_10_Gambar.jpg`: lembar pratinjau seluruh gambar, bukan pengganti file PNG individual.
- `Reimu_Animasi_Baru.mp4`: **6 detik, 720 × 720, 24 FPS, 144 frame render baru**, tanpa audio.
- `manifest.json`: rincian sumber, renderer, jumlah frame dan checksum hasil.

## Apa yang baru dibuat?

Pose, lintasan tangan, rotasi jari, gerakan kepala/tubuh, kamera, pencahayaan/shading yang disesuaikan, dan seluruh render gambar/video dibuat untuk permintaan ini. Animasi memiliki antisipasi, mengangkat tangan kiri, lambaian pergelangan, dan kembali ke pose santai. Gerakan tersebut bukan pengulangan klip lama.

Model/rig/tekstur aslinya **tetap karya Megabubu**, bukan karya baru asisten.

## Cara pembuatan dan batasan

Geometri, UV dan bobot kulit (*skin weights*) diambil dari file `.ma` asli yang diberikan pengguna. Sebanyak 13 bagian mesh dengan 31.222 vertex dasar dan 31.332 poligon dipakai. Parser membaca data Maya ASCII tanpa menjalankan script yang tertanam di file.

Karena Autodesk Maya tidak tersedia, pose baru dibuat dengan sistem deformasi sederhana, lalu dirender di Blender 4.2/Cycles. Tekstur diffuse asli tetap digunakan. Shader toon dua tingkat dibuat ulang sebagai pendekatan visual; warna rambut disesuaikan pada material, bukan mengubah file tekstur sumber.

**Hasil ini bukan evaluasi rig Maya lengkap, bukan render shader ShaderFX asli, dan tidak diklaim identik 100% dengan referensi.** Sistem kontrol wajah, simulasi kain, dan collision dari rig Maya tidak dipindahkan. Ini juga berbeda dari file draft Maya sebelumnya: gambar dan video di paket ini benar-benar sudah dirender dan diperiksa.

## Kredit dan izin

- **Model/rig dan tekstur asli: Megabubu** — https://gumroad.com/megabubu
- **Karakter Reimu Hakurei / Touhou Project: ZUN / Team Shanghai Alice.**
- README pembuat mengizinkan penggunaan **nonkomersial dengan menyertakan kredit pembuat**. Jangan mengklaim model asli sebagai buatan sendiri. Izin komersial tidak diasumsikan.
- Kredit ringkas juga dicantumkan pada gambar dan video.

## Reproduksi di repository

Kode baru: `scripts/render_original.py`, `scripts/reimu_motion.py`, `scripts/render_deliverables.py`, `scripts/package_new_renders.py`.

Dependensi Python: `bpy==4.2.0`, NumPy, SciPy, Pillow, `imageio-ffmpeg`.
Ekstrak `deliverables/Reimu_native_source.zip` ke `.cache/native/` dan library runtime ke `.cache/libs/`, lalu jalankan:

```bash
.venv/bin/python scripts/render_deliverables.py --stills --video
.venv/bin/python scripts/package_new_renders.py
```

Frame kerja, cache parsing, dan dependensi tidak dimasukkan ke Git. Video demo lama tidak dibaca oleh pipeline render baru ini.
