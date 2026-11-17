# Path traversal pada unduhan

## Tujuan
Memahami risiko menggabungkan nama file dari request menjadi path filesystem.

## Konsep
Path traversal terjadi ketika segmen relatif membuat pencarian keluar dari direktori yang dimaksud. Lab membatasi target pada file proyek KopiLab.

## Hint 1
Lihat bagaimana parameter `file` menjadi bagian dari path.

## Hint 2
Normalisasi path dan pastikan hasil akhirnya tetap berada di direktori data yang diizinkan.

## Hint 3
Marker latihan berada dalam file proyek lokal; tidak ada akses ke file host di luar proyek.

## Solusi
Tunjukkan bahwa normalisasi input pada implementasi lama dapat memilih file latihan di luar folder unduhan tetapi tetap di dalam proyek.

## Akar masalah
Aplikasi menyatukan parameter pengguna dan lokasi file tanpa pemeriksaan batas direktori.

## Perbaikan
Gunakan ID file yang dipetakan ke nama tepercaya, atau pastikan path resolved berada di bawah direktori data khusus.

## Contoh rentan
Menggabungkan `FILES_DIR` dengan seluruh nilai request.

## Contoh aman
Resolve path lalu validasi bahwa direktori induknya adalah direktori penyimpanan yang diizinkan.

## Analisis Mendalam
- **Batas direktori:** menempelkan string nama file ke direktori dasar tidak cukup; path harus dinormalisasi/resolved lalu dibandingkan dengan direktori yang diizinkan.
- **Baseline:** `welcome.txt` adalah kontrol positif di dalam folder `files`. Catat status dan isi fixture agar perilaku normal tetap terverifikasi.
- **Eksperimen:** uji hanya marker `secret.txt` di dalam proyek yang disebut materi. Jangan mencoba file sistem operasi atau path di luar direktori proyek.
- **Bukti:** bandingkan parameter `file` dengan file yang benar-benar dikembalikan. Mode Vulnerable mengizinkan traversal terbatas di dalam proyek; Secure harus menolak hasil resolved yang keluar dari folder `files`.
- **Mitigasi:** pemetaan ID ke nama tepercaya mengurangi kontrol path dari pengguna. Jika path harus diterima, lakukan canonicalization dan periksa bahwa hasil tetap berada di bawah root yang diizinkan.

## Bukti yang Dicatat
- File kontrol, nilai parameter fixture, status, dan apakah konten yang diharapkan dikembalikan.
- Hasil `welcome.txt` serta penolakan marker di Secure.
- Jangan mencatat atau mencoba file di luar project fixture; jelaskan pemeriksaan containment yang harus dilakukan.

## Langkah latihan
1. Buka `/download?file=welcome.txt` untuk mengunduh file panduan biasa.
2. Di mode **Vulnerable**, ganti nama menjadi `../secret.txt`. File ini adalah file latihan di dalam folder proyek KopiLab.
3. Periksa isi respons dan temukan penanda latihan.
4. Ulangi di mode **Secure**. File di luar folder `files` harus ditolak.

## Kalau masih bingung
`..` berarti “naik satu folder”. Server perlu memastikan hasil akhir tetap berada di folder unduhan yang diizinkan—bukan sekadar menempelkan nama yang diminta.
