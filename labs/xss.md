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

## Analisis Mendalam
- **Konteks pertama:** pencarian adalah reflected output; nilai `q` segera masuk ke response. Konteks kedua: review disimpan lewat POST lalu muncul lagi pada halaman produk, sehingga state dan output harus dianalisis terpisah.
- **Bukti browser vs response:** bandingkan input, raw HTML response, dan hasil render. Jika browser memperlakukan input sebagai elemen, output belum di-escape dengan benar; jangan hanya mengandalkan tampilan teks di satu panel.
- **Stored-state:** review dapat bertahan sampai database latihan direset. Gunakan nilai demonstrasi non-destruktif, jangan membuat payload yang membaca atau mengirim cookie, dan jangan uji origin lain.
- **Secure:** output harus ditampilkan sebagai teks dalam konteks yang sesuai. Template autoescape harus tetap aktif dan input pengguna tidak boleh ditandai `safe`.
- **Pertahanan berlapis:** output encoding sesuai konteks adalah inti; validasi input membantu aturan bisnis, sedangkan `HttpOnly` mengurangi akses JavaScript ke cookie tetapi tidak menghilangkan XSS.

## Bukti yang Dicatat
- Apakah kasus reflected atau stored, endpoint/metode, dan lokasi output.
- Perilaku raw response/browser pada kedua mode serta apakah konten disimpan/ditampilkan kembali.
- Jangan menyimpan cookie atau memakai payload yang mengambil/mengirim data; catat hanya perilaku render.

## Langkah latihan
1. Dalam mode **Vulnerable**, cari produk menggunakan teks `<script>alert(1)</script>`.
2. Lihat bagaimana teks itu muncul kembali pada halaman hasil pencarian. Coba juga mengirim teks yang sama sebagai ulasan.
3. Buka kembali halaman produk untuk melihat ulasan yang tersimpan.
4. Mode **Secure** seharusnya menampilkan teks sebagai tulisan biasa, bukan elemen HTML. Cookie flag juga mendapat `HttpOnly`.

## Kalau masih bingung
Reflected berarti teks kembali di halaman yang sama setelah dikirim. Stored berarti teks disimpan lalu muncul saat halaman dibuka lagi. Keduanya berbahaya karena browser bisa salah mengira tulisan pengunjung sebagai HTML.
