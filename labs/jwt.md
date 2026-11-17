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

## Analisis Mendalam
- **Struktur token:** header dan payload JWT dapat dibaca setelah Base64URL decoding; keduanya bukan bukti keaslian. Signature-lah yang mengikat klaim pada kunci penandatangan.
- **Eksperimen lokal:** ambil token fixture dari `GET /extra/jwt`, lalu gunakan helper lokal yang disebut materi untuk mengirim token demo ke endpoint yang sama. Jangan gunakan token atau secret dari layanan lain.
- **Bukti:** periksa status dan claims yang dikembalikan, khususnya role; cocokkan dengan header flag. Perubahan teks payload saja tidak cukup bila signature tidak valid.
- **Secure:** secret konfigurasi berbeda, sehingga token yang dibuat memakai secret demo tidak boleh diterima. Verifikasi juga harus mengunci algoritma yang diizinkan, bukan mempercayai algoritma dari token.
- **Batas klaim:** secret lemah pada fixture menjelaskan kegagalan tanda tangan; JWT tidak mengenkripsi isi sehingga token tetap tidak cocok untuk menyimpan rahasia.

## Bukti yang Dicatat
- Sumber token (fixture lokal), endpoint POST, status, role yang direspons, dan ada/tidaknya flag.
- Perbandingan token demo pada Vulnerable dan Secure tanpa menempelkan token penuh atau secret ke catatan.
- Mitigasi: secret kuat, algoritma tetap, validasi expiry/issuer/audience sesuai kebutuhan, dan rotasi kunci.

## Langkah latihan
1. Buka `GET /extra/jwt` di KopiLab lokal untuk menerima token demo pengguna biasa.
2. Baca token sebagai tiga bagian: header, klaim, dan tanda tangan. Token bukan data rahasia yang dienkripsi.
3. Untuk uji lab, gunakan kode helper `encode_token` lokal dengan secret demo `kopilab` dan klaim role `admin`, lalu kirim token ke `POST /extra/jwt`.
4. Mode **Vulnerable** menerima token yang ditandatangani secret lemah; mode **Secure** memakai secret server acak yang tidak diketahui siswa dan menolak token tersebut.

## Kalau masih bingung
Tanda tangan seperti segel pada surat: perubahan isi seharusnya membuat segel tidak cocok. Kalau kunci pembuat segelnya mudah ditebak, orang bisa membuat segel palsu. Isi JWT dapat dibaca siapa saja; jangan taruh rahasia di dalamnya.
