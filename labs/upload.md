# Validasi upload lemah

## Tujuan
Membedakan validasi nama ekstensi dari validasi konten berkas.

## Konsep
Upload berbahaya dapat memengaruhi aplikasi jika nama atau konten tanpa validasi disajikan sebagai konten aktif. Lab menyimpan file kecil hanya di folder `uploads` milik proyek dan tidak mengeksekusinya.

## Hint 1
Perhatikan jenis nama file yang diterima server.

## Hint 2
Mode aman memakai allowlist ekstensi gambar, tetapi produksi juga perlu memeriksa magic bytes dan ukuran.

## Hint 3
Penanda flag hanya dikirim untuk file lokal dengan ekstensi non-gambar; tidak ada file yang dieksekusi.

## Solusi
Unggah file teks kecil pada endpoint lokal dan amati penerimaan nama non-gambar.

## Akar masalah
Mode vulnerable tidak membatasi tipe nama file yang diunggah.

## Perbaikan
Gunakan allowlist, validasi isi dan ukuran, nama acak, penyimpanan di luar web root, serta jangan mengeksekusi upload.

## Contoh rentan
Menerima semua ekstensi dari nama file pengguna.

## Contoh aman
Allowlist tipe gambar, validasi signature, simpan sebagai nama yang dibuat server di lokasi non-eksekusi.

## Analisis Mendalam
- **Kontrol yang berbeda:** ekstensi nama, MIME yang dikirim klien, signature isi file, ukuran, nama penyimpanan, dan lokasi eksekusi adalah hal terpisah. Satu pemeriksaan tidak menggantikan pemeriksaan lainnya.
- **Request Repeater:** tangkap upload teks kecil dari form; pertahankan boundary multipart dan ubah hanya nama/tipe yang diminta langkah lab. Jangan mengunggah executable atau file berisi data pribadi.
- **Bukti:** periksa status, nama tersimpan, header flag, dan lokasi proyek. Penerimaan file bukan berarti file dijalankan—simulator tidak mengeksekusi upload.
- **Secure:** file teks ditolak; tipe yang diizinkan tetap mengikuti allowlist. Uji menggunakan file gambar latihan yang aman bila perlu mengonfirmasi alur sah.
- **Mitigasi:** validasi allowlist di server, ukuran, signature/content, buat nama acak, simpan di luar web root dengan izin minimal, dan sajikan sebagai download non-eksekusi.

## Bukti yang Dicatat
- Nama field file, filename/ekstensi, Content-Type, status, dan nilai `saved`/flag.
- Jenis file aman yang digunakan dan perbedaan keputusan Vulnerable/Secure.
- Tegaskan bahwa upload disimpan dalam folder fixture dan tidak pernah dieksekusi; jangan lampirkan file sensitif.

## Langkah latihan
1. Siapkan file teks kecil berisi tulisan biasa—jangan pernah unggah program atau file berbahaya.
2. Kirim sebagai field `file` ke `POST /extra/upload` pada KopiLab lokal.
3. Mode **Vulnerable** menerima nama seperti `catatan.txt` dan memberi header flag. File hanya disimpan di folder `uploads`, tidak dijalankan.
4. Mode **Secure** menolak ekstensi `.txt` dan menerima hanya ekstensi gambar yang diizinkan.

## Kalau masih bingung
Nama file tidak membuktikan isi file. Mengganti akhiran nama saja bukan validasi yang cukup. Lab ini hanya mengajarkan aturan penerimaan; file tidak pernah dieksekusi.
