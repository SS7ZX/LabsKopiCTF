# JWT dengan secret lemah

## Tujuan
Memahami pentingnya verifikasi tanda tangan token dengan kunci yang rahasia dan kuat.

## Konsep
JWT ditandatangani, bukan dienkripsi. Klaim harus selalu diverifikasi server; secret yang lemah memungkinkan pemalsuan tanda tangan pada instance lab.

## Hint 1
Endpoint GET memberi token pengguna biasa untuk diperiksa strukturnya.

## Hint 2
Algoritma dan secret yang dipakai server menentukan apakah klaim dapat dipercaya.

## Hint 3
Gunakan secret lemah yang tercantum pada materi hanya terhadap endpoint lokal KopiLab.

## Solusi
Buat token latihan bertanda tangan secret demo lokal dengan klaim role admin lalu verifikasi pada endpoint.

## Akar masalah
Mode vulnerable memakai shared secret demo yang mudah ditebak.

## Perbaikan
Gunakan secret kuat dari konfigurasi server, validasi algoritma tetap, issuer/audience/expiry, dan rotasi kunci.

## Contoh rentan
Memverifikasi token dengan secret `kopilab`.

## Contoh aman
Verifikasi HS256 dengan kunci kriptografis acak hanya dari konfigurasi server.

## Langkah latihan
1. Buka `GET /extra/jwt` di KopiLab lokal untuk menerima token demo pengguna biasa.
2. Baca token sebagai tiga bagian: header, klaim, dan tanda tangan. Token bukan data rahasia yang dienkripsi.
3. Untuk uji lab, gunakan kode helper `encode_token` lokal dengan secret demo `kopilab` dan klaim role `admin`, lalu kirim token ke `POST /extra/jwt`.
4. Mode **Vulnerable** menerima token yang ditandatangani secret lemah; mode **Secure** memakai secret server acak yang tidak diketahui siswa dan menolak token tersebut.

## Kalau masih bingung
Tanda tangan seperti segel pada surat: perubahan isi seharusnya membuat segel tidak cocok. Kalau kunci pembuat segelnya mudah ditebak, orang bisa membuat segel palsu. Isi JWT dapat dibaca siapa saja; jangan taruh rahasia di dalamnya.
