# Redirect ke simulator lokal

## Tujuan
Mengenali risiko redirect ketika tujuan berasal dari parameter pengguna.

## Konsep
Redirect terbuka dapat membuat tautan tepercaya membawa pengguna ke tujuan tak diinginkan. KopiLab hanya mengizinkan simulator lokal port 9000 pada mode vulnerable.

## Hint 1
Periksa nilai `next` dan header `Location`.

## Hint 2
Host yang diizinkan saat latihan dibatasi ke loopback.

## Hint 3
Target demo adalah server attacker simulator lokal proyek, bukan situs pihak lain.

## Solusi
Gunakan URL simulator loopback yang diizinkan dan amati bahwa browser diarahkan ke server itu.

## Akar masalah
Server memakai tujuan request tanpa allowlist ketat.

## Perbaikan
Gunakan identifier tujuan yang dipetakan server atau izinkan path relatif internal saja.

## Contoh rentan
Redirect ke URL yang dikendalikan pengguna.

## Contoh aman
Tolak URL absolute dan `//host`; izinkan path relatif internal.

## Analisis Mendalam
- **Perbedaan penting:** redirect mengubah tujuan navigasi browser; ia bukan bukti bahwa server mengambil atau mengakses URL tujuan.
- **Baseline:** gunakan path relatif `/labs` dan catat status serta header `Location`. Ini kontrol untuk memastikan navigasi internal tetap berfungsi.
- **Eksperimen:** ubah hanya `next` ke simulator loopback yang ditentukan materi. Pastikan target request tetap KopiLab di `127.0.0.1:5000`; simulator lokal adalah tujuan redirect latihan, bukan target pengujian baru.
- **Bukti:** periksa 302/400 dan nilai `Location` lengkap. Flag hanya menandai skenario simulator; jangan menganggap semua tujuan eksternal dapat dicapai.
- **Secure:** pertahankan redirect relatif yang sah dan tolak tujuan absolut maupun path yang dapat menafsirkan host lain. Validasi berbasis allowlist lebih aman daripada mencoba memblokir pola URL satu per satu.

## Bukti yang Dicatat
- Nilai `next`, status response, header `Location`, dan ada/tidaknya flag.
- Perbedaan path internal yang sah dengan URL simulator pada kedua mode.
- Jangan memasukkan domain publik/mesin lain atau mengikuti redirect keluar dari lingkungan lokal.

## Langkah latihan
1. Di aplikasi lokal, coba buka `/extra/redirect?next=/labs` dan lihat header `Location`.
2. Pada mode **Vulnerable**, coba tujuan simulator `http://127.0.0.1:9000/`.
3. Respons lokal menandai tujuan ini dengan header `X-Lab-Flag`. Tujuan internet lain memang ditolak lab.
4. Ganti ke **Secure**. Path `/labs` tetap boleh, tetapi URL lengkap simulator harus ditolak.

## Kalau masih bingung
Redirect seperti petugas yang menunjukkan arah. Jika petugas mengikuti alamat apa pun yang ditulis orang, tautan toko bisa membawa pengunjung ke tempat yang tidak diharapkan. Mode aman hanya menerima alamat halaman di dalam toko.
