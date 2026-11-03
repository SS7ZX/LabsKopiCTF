# IDOR pada detail pesanan

## Tujuan
Memahami bahwa identifier objek bukan bukti kepemilikan atau otorisasi.

## Konsep
Insecure Direct Object Reference (IDOR) terjadi saat server mengambil objek berdasarkan ID dari pengguna tanpa memeriksa apakah pengguna berhak melihatnya.

## Hint 1
Amati ID pesanan pada URL dan identitas pengguna di sesi.

## Hint 2
Periksa apakah query pesanan juga membatasi `user_id`.

## Hint 3
Gunakan hanya pesanan seed Budi dan Siti pada database tes yang dibuat ulang.

## Solusi
Temukan pesanan seed yang bukan milik akun aktif dan amati bahwa endpoint mengembalikannya.

## Akar masalah
Pencarian pesanan hanya menggunakan ID global.

## Perbaikan
Tambahkan kondisi pemilik ke query dan kembalikan 404/403 secara konsisten bila objek bukan milik pengguna.

## Contoh rentan
`SELECT * FROM orders WHERE id=?`

## Contoh aman
`SELECT * FROM orders WHERE id=? AND user_id=?`

## Langkah latihan
1. Masuk sebagai Budi (`budi` / `budi123`).
2. Buka pesanan Budi dari menu riwayat, lalu perhatikan angka di alamat `/order/...`.
3. Di lab lokal, buka `/order/1`. Pesanan seed nomor 1 milik akun lain.
4. Mode **Vulnerable** menampilkan detailnya; mode **Secure** seharusnya menjawab “tidak ditemukan”.

## Kalau masih bingung
Nomor pesanan seperti nomor loker—mengetahui nomornya tidak berarti loker itu milikmu. Server harus mengecek dua hal: nomor pesanan cocok dan pemiliknya adalah pengguna yang sedang masuk.
