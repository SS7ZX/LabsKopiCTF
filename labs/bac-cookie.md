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

## Langkah latihan
1. Di mode **Vulnerable**, buka `/admin` tanpa login dan lihat akses ditolak.
2. Pada browser lokal, ubah cookie `admin` menjadi `1`, lalu muat ulang halaman.
3. Amati apakah panel dan flag terbuka. Cookie ini hanya untuk aplikasi latihan lokal.
4. Aktifkan **Secure** dan ulangi. Cookie yang sama tidak boleh memberi akses.

## Kalau masih bingung
Cookie seperti kartu nama yang dibawa pengunjung. Pengunjung dapat menulis apa saja di kartunya. Satpam yang benar memeriksa daftar izin di server, bukan hanya tulisan di kartu.
