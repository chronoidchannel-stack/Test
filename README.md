# Reimu — native Maya animation draft

Transfer sumber melalui GitHub berhasil; pengguna tidak perlu mengunggah ulang ZIP Drive.

## Unduh

- **[MP4 demo asli — 5,76 detik](deliverables/Reimu_ORIGINAL_DEMO.mp4)** — contoh animasi berlari bawaan Megabubu, dikonversi dari GIF dan diulang 8 kali. **Bukan render draft sapaan baru.** [Kredit dan asal video](deliverables/Reimu_ORIGINAL_DEMO_CREDITS.txt).

- **[Draft animasi Maya — ZIP](deliverables/Reimu_Greeting_DRAFT_Maya.zip)** — scene asli, tekstur, keyframe sapaan 150 frame / 30 FPS, kamera dan helper preview.
- [Scene toon asli + tekstur — ZIP](deliverables/Reimu_native_source.zip) — tanpa backup, contoh GIF, atau scene alternatif non-toon; aset yang disertakan tetap utuh.
- **[Petunjuk penggunaan dan batasan](docs/ANIMASI_REIMU.md).**

**Ini draft Maya yang diperiksa secara struktural, belum diuji secara visual atau dirender. Belum ada MP4 hasil render draft ini, render 2D baru, atau ekspor GLB. MP4 demo asli yang ditautkan di atas merupakan konversi contoh GIF, bukan evaluasi scene draft.** Maya/ShaderFX diperlukan untuk mengevaluasi rig dan mempertahankan shader asli.

## Sumber dan kredit

Rig asli: **Megabubu**, https://gumroad.com/megabubu. Karakter Reimu Hakurei / Touhou Project: ZUN / Team Shanghai Alice. README pembuat mengizinkan penggunaan nonkomersial dengan kredit; lihat [README asli yang diekstrak](reports/source-readme.txt).

Sumber diberikan pengguna melalui Google Drive. Workflow pada branch sesi mengunduh ZIP sumber 176.755.016 byte. Paket scene utama diperkecil secara lossless dengan menghilangkan backup/contoh yang tidak diperlukan, bukan menurunkan resolusi tekstur atau mengubah mesh.

## Pemeriksaan

```bash
python scripts/build_animation.py
python -m unittest discover -s tests -v
```

Pemeriksaan meliputi integritas ZIP, sambungan controller/time pada kurva animasi, pelestarian 239 blok mesh, dan kesamaan byte tekstur. Pemeriksaan tersebut tidak menggantikan review gerakan, tabrakan kain, kompatibilitas plug-in, atau render di Autodesk Maya. Detail: `reports/animation-validation.json`.
