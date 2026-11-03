# SQLi UNION di pencarian

## Tujuan
Memahami mengapa menggabungkan input pencarian langsung ke SQL dapat mengekspos data di luar katalog.

## Konsep
SQL injection terjadi saat aplikasi memperlakukan input pengguna sebagai bagian dari sintaks query. Pada lab ini query pencarian adalah target; database berisi tabel latihan terpisah dari katalog.

## Hint 1
Bandingkan teks pencarian biasa dengan query SQL yang dibentuk aplikasi.

## Hint 2
Perhatikan struktur dan jumlah kolom query asal sebelum memikirkan penggabungan hasil.

## Hint 3
Target hanya database SQLite sementara milik lab. Gunakan inspector atau kode sumber lokal untuk memeriksa tabel latihan.

## Solusi
Buktikan bahwa input dapat mengubah struktur pencarian sehingga hasil dari tabel latihan muncul. Flag ditanam sebagai data uji lokal; jangan gunakan teknik ini pada sistem lain.

## Akar masalah
Fungsi pencarian merangkai input ke string SQL dengan interpolasi.

## Perbaikan
Gunakan query berparameter (`WHERE name LIKE ?`) dan escape karakter wildcard sesuai kebutuhan produk.

## Contoh rentan
`SELECT ... WHERE name LIKE '%` + input + `%'`

## Contoh aman
`connection.execute("SELECT ... WHERE name LIKE ?", (f"%{query}%",))`

## Langkah latihan
1. Pastikan mode **Vulnerable**, lalu buka pencarian di KopiLab dan cari `Gayo`.
2. Buka Request Inspector. Lihat bahwa kata pencarian ikut masuk ke teks SQL.
3. Coba nilai uji UNION yang ada di tes lokal: `%' UNION SELECT 1,'flag',1,value FROM secrets-- `.
4. Hasilnya menunjukkan bahwa input mengubah query, bukan hanya mencari nama produk. Submit flag dari data latihan.
5. Ganti ke **Secure** dan ulangi. Hasil ekstra tidak boleh muncul.

## Kalau masih bingung
Bayangkan SQL seperti kalimat yang ditulis server. Aplikasi rentan menyisipkan kata-katamu ke dalam kalimat itu. Pertanyaannya: apakah input diperlakukan sebagai kata pencarian, atau malah sebagai bagian dari perintah SQL? Lihat query di Inspector sebelum mencoba lagi.
