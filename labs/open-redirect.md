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

## Langkah latihan
1. Di aplikasi lokal, coba buka `/extra/redirect?next=/labs` dan lihat header `Location`.
2. Pada mode **Vulnerable**, coba tujuan simulator `http://127.0.0.1:9000/`.
3. Respons lokal menandai tujuan ini dengan header `X-Lab-Flag`. Tujuan internet lain memang ditolak lab.
4. Ganti ke **Secure**. Path `/labs` tetap boleh, tetapi URL lengkap simulator harus ditolak.

## Kalau masih bingung
Redirect seperti petugas yang menunjukkan arah. Jika petugas mengikuti alamat apa pun yang ditulis orang, tautan toko bisa membawa pengunjung ke tempat yang tidak diharapkan. Mode aman hanya menerima alamat halaman di dalam toko.
