# Kontrol akses admin berbasis cookie

## Tujuan
Memahami bahwa cookie dari browser adalah input yang dapat dimanipulasi.

## Konsep
Broken access control terjadi saat server mempercayai klaim otorisasi yang dikendalikan klien, bukan identitas dan izin yang diverifikasi server.

## Hint 1
Periksa sumber keputusan akses route admin.

## Hint 2
Bandingkan data cookie dengan identitas sesi server.

## Hint 3
Gunakan hanya akun latihan dan panel lokal; cookie ini bukan mekanisme otorisasi sungguhan.

## Solusi
Tunjukkan bahwa nilai cookie klien saja cukup untuk membuka panel pada aplikasi latihan.

## Akar masalah
Server menggunakan boolean di cookie tanpa memverifikasi role dari sumber tepercaya.

## Perbaikan
Ambil role dari sesi terautentikasi dan periksa izin pada setiap request; gunakan cookie sesi yang ditandatangani serta konfigurasi aman.

## Contoh rentan
Memutuskan akses dari `request.cookies["admin"]`.

## Contoh aman
Periksa klaim role yang ditetapkan server pada sesi tervalidasi.

## Analisis Mendalam
- **Hipotesis:** apakah keputusan akses `/admin` dibuat dari role yang diperoleh server untuk pengguna login, atau dari cookie `admin` yang dapat dikirim klien?
- **Baseline:** login sebagai Budi, minta `/admin`, lalu catat status penolakan. Pertahankan akun dan sesi yang sama untuk eksperimen agar satu-satunya variabel adalah cookie latihan.
- **Bukti dampak:** bedakan cookie `admin` dari cookie sesi Flask. Perubahan cookie latihan yang diikuti tampilan panel/flag menunjukkan bahwa server mempercayai nilai klien; status saja tidak cukup.
- **Perbandingan Secure:** ulangi dengan sesi/mode Secure yang baru. Server harus tetap menolak karena role Budi pada database adalah `user`, terlepas dari nilai cookie latihan.
- **Batas kesimpulan:** hasil ini membuktikan cacat otorisasi pada fixture KopiLab, bukan bahwa cookie sesi Flask dapat dipalsukan atau bahwa akun nyata terdampak.

## Bukti yang Dicatat
- Mode, endpoint, status baseline dan uji, serta apakah panel admin benar-benar dirender.
- Nama cookie latihan yang diuji dan nilai role yang terlihat; jangan mencatat atau membagikan nilai cookie sesi.
- Hasil yang sama pada Secure dan kontrol bahwa Budi tetap memiliki role `user`.
- Perbaikan yang disarankan: ambil principal dari sesi tervalidasi dan otorisasi setiap request berdasarkan role server-side.

## Langkah latihan
1. Di mode **Vulnerable**, buka `/admin` tanpa login dan lihat akses ditolak.
2. Pada browser lokal, ubah cookie `admin` menjadi `1`, lalu muat ulang halaman.
3. Amati apakah panel dan flag terbuka. Cookie ini hanya untuk aplikasi latihan lokal.
4. Aktifkan **Secure** dan ulangi. Cookie yang sama tidak boleh memberi akses.

## Kalau masih bingung
Cookie seperti kartu nama yang dibawa pengunjung. Pengunjung dapat menulis apa saja di kartunya. Satpam yang benar memeriksa daftar izin di server, bukan hanya tulisan di kartu.
