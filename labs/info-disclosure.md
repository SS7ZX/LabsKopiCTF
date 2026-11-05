# Information disclosure pada diagnostic endpoint

## Tujuan
Membedakan informasi status yang diperlukan pengguna dengan detail diagnostik internal yang tidak perlu diekspos.

## Konsep
Pesan debug dan metadata deployment dapat membantu penyerang memetakan sistem. Endpoint ini hanya menampilkan string dummy `local-demo` dan `fixture-only`, bukan konfigurasi atau rahasia nyata.

## Hint 1
Bandingkan `view=public` dan `view=diagnostic`.

## Hint 2
Cari field `diagnostic` dalam JSON, bukan hanya status.

## Hint 3
Secure tidak mengembalikan detail diagnostik meski parameter diminta.

## Solusi
Vulnerable mengembalikan metadata dummy pada view diagnostic; Secure hanya menyediakan schema publik.

## Akar Masalah
Mode diagnostik dapat dipilih dari input pengguna tanpa otorisasi atau sanitasi informasi.

## Perbaikan
Batasi diagnostic pada environment/admin yang sesuai, hilangkan rahasia dari output, dan gunakan logging server-side.

## Contoh Rentan
Mengembalikan debug/config object penuh ke response publik.

## Contoh Aman
Mengembalikan hanya field status yang di-allowlist dan menyimpan detail pada log internal.

## Analisis Mendalam
- Tidak ada rahasia nyata pada fixture.
- Catat status, service, diagnostic ada/tidak, dan flag.
- Perbedaan status 200 tidak cukup; bandingkan skema body.
- Secure harus menolak/meniadakan field diagnostic.
- Jangan mencoba menebak file atau konfigurasi lain; lab ini hanya satu marker.

## Langkah Latihan
1. Kirim GET `/extra/academy/info-disclosure?view=public`.
2. Kirim request ke Repeater, ubah hanya view menjadi diagnostic.
3. Catat field tambahan pada Vulnerable.
4. Aktifkan Secure, tangkap request baru, dan ulangi.
5. Pastikan detail diagnostik tidak muncul.

## Bukti yang Dicatat
View, schema body, status, diagnostic fixture, flag dan mode.

## Kalau Masih Bingung
Respons tetap JSON. Periksa body dengan format Pretty atau Raw di Repeater.
