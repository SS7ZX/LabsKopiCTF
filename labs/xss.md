# Reflected dan stored XSS

## Tujuan
Membedakan input yang dipantulkan segera dari konten yang disimpan lalu ditampilkan kembali.

## Konsep
Cross-site scripting muncul ketika data tak tepercaya ditafsirkan browser sebagai markup atau skrip. KopiLab menyediakan dua konteks lokal: hasil pencarian dan ulasan produk.

## Hint 1
Cari tempat nilai pencarian dan teks ulasan ditampilkan kembali ke halaman.

## Hint 2
Pertimbangkan encoding sesuai konteks HTML, atribut, atau JavaScript.

## Hint 3
Flag cookie demonstrasi tersedia pada origin KopiLab saja; tidak ada cookie pengguna eksternal yang digunakan.

## Solusi
Buktikan pada halaman lokal bahwa konten yang dikendalikan pengguna tidak di-encode sebelum dirender.

## Akar masalah
Nilai tak tepercaya ditandai sebagai HTML tepercaya sehingga autoescape template dilewati.

## Perbaikan
Biarkan autoescape Jinja aktif, jangan gunakan `safe` untuk input pengguna, validasi konten, dan beri cookie sensitif atribut `HttpOnly`.

## Contoh rentan
`{{ review.body|safe }}`

## Contoh aman
`{{ review.body }}`

## Langkah latihan
1. Dalam mode **Vulnerable**, cari produk menggunakan teks `<script>alert(1)</script>`.
2. Lihat bagaimana teks itu muncul kembali pada halaman hasil pencarian. Coba juga mengirim teks yang sama sebagai ulasan.
3. Buka kembali halaman produk untuk melihat ulasan yang tersimpan.
4. Mode **Secure** seharusnya menampilkan teks sebagai tulisan biasa, bukan elemen HTML. Cookie flag juga mendapat `HttpOnly`.

## Kalau masih bingung
Reflected berarti teks kembali di halaman yang sama setelah dikirim. Stored berarti teks disimpan lalu muncul saat halaman dibuka lagi. Keduanya berbahaya karena browser bisa salah mengira tulisan pengunjung sebagai HTML.
