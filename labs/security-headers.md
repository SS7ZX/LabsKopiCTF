# Security headers dan kebijakan browser

## Tujuan
Membaca beberapa header keamanan umum dan memahami batas perlindungannya.

## Konsep
Header seperti CSP, `X-Content-Type-Options`, `Referrer-Policy`, dan `Permissions-Policy` mengurangi risiko tertentu pada browser. Header tidak membuat input otomatis aman dan tidak menggantikan query parameter, escaping, autentikasi, atau otorisasi.

## Hint 1
Ambil response GET tanpa mengubah request; bandingkan response headers.

## Hint 2
Perhatikan perbedaan header yang mengatur sumber konten, MIME sniffing, referer, dan fitur browser.

## Hint 3
Header yang tidak relevan untuk suatu endpoint tidak perlu dipaksakan; kebijakan harus sesuai fungsi aplikasi.

## Solusi
Mode Vulnerable memberi response JSON sederhana tanpa set header demo. Secure menambahkan empat header defensif yang ditetapkan endpoint.

## Akar Masalah
Konfigurasi response tidak menetapkan beberapa batas browser sebagai defense-in-depth.

## Perbaikan
Tetapkan header terpusat, evaluasi CSP agar tidak mematahkan aplikasi, dan uji setiap kebijakan di browser yang didukung.

## Contoh Rentan
Tidak mengirim kebijakan MIME, referrer, permission, atau content source.

## Contoh Aman
Kirim policy minimum yang tepat, misalnya `X-Content-Type-Options: nosniff` dan CSP yang sesuai.

## Analisis Mendalam
- Catat keberadaan dan nilai setiap header, bukan hanya status 200.
- CSP mengendalikan sumber konten; `nosniff` mengurangi interpretasi MIME yang keliru.
- Referrer-Policy membatasi informasi navigasi; Permissions-Policy membatasi fitur browser.
- Header adalah lapisan tambahan, bukan kontrol otorisasi server.
- Bandingkan response Vulnerable dan Secure pada path yang sama.

## Langkah Latihan
1. Pastikan Intercept off dan buka GET `/extra/academy/security-headers`.
2. Kirim request ke Repeater tanpa modifikasi dan catat status/body/header.
3. Bandingkan daftar response headers dengan Secure mode.
4. Pastikan body fixture tidak berubah, sementara header kebijakan bertambah.
5. Jangan mengubah target atau mengaktifkan scanning otomatis.

## Bukti yang Dicatat
Method/path, status, Content-Type, CSP, nosniff, Referrer-Policy, Permissions-Policy dan mode.

## Kalau Masih Bingung
Klik panel Response Headers di Burp. Baris header berada sebelum body JSON.
