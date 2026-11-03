# Validasi jumlah dan kupon

## Tujuan
Menguji invariant bisnis yang harus tetap benar untuk setiap transaksi.

## Konsep
Validasi input bukan hanya soal tipe data. Kuantitas harus positif, diskon dibatasi aturan kupon, dan total tidak boleh negatif.

## Hint 1
Periksa bagaimana kuantitas dan daftar kupon diubah menjadi total.

## Hint 2
Tanyakan apakah mengirim kupon berulang atau nilai jumlah di luar rentang mengubah saldo.

## Hint 3
Gunakan akun Budi yang di-seed khusus pada database tes terisolasi.

## Solusi
Tunjukkan pelanggaran aturan jumlah atau diskon pada checkout lokal hingga indikator saldo lab terpenuhi.

## Akar masalah
Perhitungan total dilakukan tanpa validasi batas jumlah dan penerapan kupon.

## Perbaikan
Validasi kuantitas positif dalam batas stok, terapkan kupon sekali sesuai kebijakan, dan pastikan total tidak negatif.

## Contoh rentan
`total = price * quantity - sum(discounts)`

## Contoh aman
Validasi `1 <= quantity <= stock`, deduplikasi kupon, lalu hitung total dari harga katalog dan aturan diskon server.

## Langkah latihan
1. Masuk sebagai Budi. Catat saldo awal pada halaman akun.
2. Dalam mode **Vulnerable**, kirim checkout lokal dengan jumlah `-200` untuk produk berharga Rp85.000.
3. Buka kembali akun. Perhatikan bahwa saldo berubah ke arah yang tidak masuk akal.
4. Ulangi di mode **Secure**. Jumlah negatif ditolak sebelum saldo atau order berubah.

## Kalau masih bingung
Jumlah barang seharusnya 1, 2, 3, dan seterusnya. Jumlah negatif membalik perkalian: server tanpa sadar dapat menambahkan saldo saat mengurangi total belanja. Kupon berulang adalah masalah terpisah yang perlu dibatasi juga.
