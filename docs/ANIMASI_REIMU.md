# Reimu — draft animasi sapaan

**Status: draft keyframe Maya, belum diuji atau dirender di Autodesk Maya. Ini bukan MP4, bukan GLB, dan belum merupakan animasi final.**

## Yang tersedia

- `Reimu_Greeting_DRAFT.ma`: scene Maya asli dengan kurva animasi baru untuk draft sapaan.
- 150 frame pada 30 FPS (5 detik playback).
- Gerakan yang dirancang: tangan kiri diangkat untuk melambai, kepala sedikit miring, kedipan dua kali, dan gerakan tubuh kecil.
- Model, UV, rig, material ShaderFX dan tekstur berasal dari paket asli. Blok mesh asli diperiksa identik; tekstur tidak diperkecil atau dikompresi ulang.
- Kamera ortografis `arenaGreetingCamera`, pengaturan output 1080 × 1080.
- `open_preview.py`: pembantu pembukaan di Maya untuk menghubungkan tekstur, memilih DG evaluation, dan menampilkan Viewport 2.0.
- `greeting_curves.mel`: kurva animasi yang ditambahkan, untuk inspeksi. Jangan dijalankan lagi pada scene draft karena kurvanya sudah ada.
- `ORIGINAL_README.txt`: petunjuk asli pembuat.

## Cara membuka

1. Ekstrak ZIP ke folder lokal. Pertahankan scene dan seluruh tekstur dalam folder `Reimu` yang sama.
2. Gunakan Autodesk Maya yang kompatibel dengan scene Maya 2020 serta node ShaderFX/MayaMuscle. Blender tidak dapat langsung membuka rig `.ma` ini.
3. Simpan pekerjaan yang sedang terbuka di Maya.
4. Buka Script Editor → tab Python. Muat `open_preview.py`, lalu jalankan seluruh script. Pilih `Reimu_Greeting_DRAFT.ma` saat dialog muncul. Script tidak menyimpan ulang scene atau menimpa file sumber.
5. Tekan Play. Timeline menggunakan frame 1–150. Frame 60 berada di bagian tengah lambaian.

Alternatif: buka scene secara manual, atur project ke folder `Reimu`, pilih DG evaluation dan Viewport 2.0, perbaiki path tekstur jika perlu, lalu gunakan kamera `arenaGreetingCamera`.

## Yang sudah diperiksa

- ZIP sumber 176.755.016 byte berhasil diunduh melalui GitHub Actions, bukan melalui upload ulang pengguna.
- Integritas ZIP dan checksum aset.
- Nama controller diambil dari file asli; kanal yang dikunci atau sudah memiliki koneksi input tidak ditimpa.
- FK dipilih berdasarkan koneksi constraint asli (`IKFK = 1` adalah FK).
- Data geometri/mesh asli dipertahankan persis pada tingkat blok Maya ASCII.
- File animasi benar-benar berisi kurva keyframe yang tersambung ke controller, bukan hanya rencana gerakan.

## Batasan penting

Maya tidak terpasang di lingkungan pembuatan ini. Pemeriksaan yang dilakukan adalah pemeriksaan struktur file, **bukan evaluasi rig atau penilaian visual**. Arah lambaian, penutupan kelopak mata, tabrakan tangan/lengan baju/rambut, dan framing kamera masih harus ditinjau di Maya. Tidak ada klaim bahwa hasil geraknya sudah final atau sama dengan video referensi.

ShaderFX Maya tidak otomatis setara dengan material Blender/glTF. Karena itu belum dibuat konversi GLB atau gambar 2D baru yang diklaim identik dengan referensi. Render final harus diperiksa di Maya Viewport 2.0 atau Maya Hardware 2.0 sesuai petunjuk pembuat.

## Kredit dan penggunaan

- **Rig/model asli: Megabubu** — https://gumroad.com/megabubu
- **Karakter Reimu Hakurei / Touhou Project: ZUN / Team Shanghai Alice.**
- README asli mengizinkan penggunaan **nonkomersial dengan kredit kepada pembuat**. Ketersediaan publik bukan izin penggunaan komersial; ikuti README asli untuk syaratnya.
- Kurva animasi draft dan alat transfer ditambahkan untuk permintaan ini. Jangan mengklaim model/rig asli sebagai buatan Anda.

`Reimu_native_source.zip` disediakan terpisah sebagai paket scene toon asli dan tekstur. Ukurannya lebih kecil karena backup, contoh GIF, dan alternatif non-toon tidak disertakan—bukan karena kualitas model diturunkan.
