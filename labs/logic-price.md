# Manipulasi harga checkout

## Tujuan
Mengetahui mengapa nilai dari browser tidak boleh dianggap sebagai sumber harga.

## Konsep
Semua field form dapat diubah pengguna. Harga, diskon, dan total harus dihitung ulang di server dari katalog dan aturan bisnis tepercaya.

## Hint 1
Bandingkan harga pada form dengan harga produk di database.

## Hint 2
Cari variabel yang dipakai dalam perhitungan total dan catatan pesanan.

## Hint 3
Khusus lab, produk Secret Mug memiliki penanda untuk membuktikan alur checkout.

## Solusi
Perlihatkan pada instance lokal bahwa checkout memakai angka harga yang dikirim browser, bukan nilai katalog.

## Akar masalah
Server mempercayai field harga tersembunyi yang bisa diedit.

## Perbaikan
Ambil harga produk berdasarkan ID di server; hitung diskon serta total di server dan simpan snapshot harga tervalidasi.

## Contoh rentan
`price = int(request.form["price"])`

## Contoh aman
`price = product["price"]`

## Langkah latihan
1. Masuk dengan akun Budi dan buka halaman Secret Mug (`/product/99`).
2. Form checkout mengirim ID produk dan harga. Di mode **Vulnerable**, harga yang dikirim browser dipercaya.
3. Kirim checkout dengan `pid=99`, `price=0`, dan `qty=1` memakai form lokal lab.
4. Perhatikan order dan flag. Ulangi di mode **Secure**: harga katalog dipakai, sehingga saldo Budi tidak cukup.

## Kalau masih bingung
Harga di halaman web seperti label pada secarik kertas—pembeli bisa mengubahnya sebelum mengirim. Kasir harus melihat harga di katalog server, bukan mempercayai angka dari kertas itu.
