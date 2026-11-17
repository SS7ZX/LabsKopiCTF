# SQLi auth bypass pada login

## Tujuan
Mengenali perbedaan antara data kredensial dan sintaks query SQL.

## Konsep
Login rentan bila nilai username dan password ditempelkan ke query. Database bisa menafsirkan bagian input sebagai kondisi, bukan nilai kredensial.

## Hint 1
Amati bagaimana query login dibuat saat username dan password diisi.

## Hint 2
Bandingkan bentuk query biasa dengan query yang dihasilkan input berisi tanda kutip.

## Hint 3
Uji hanya endpoint login KopiLab dan akun seed pada database tes lokal.

## Solusi
Tunjukkan pada endpoint lokal bahwa input mengubah evaluasi kondisi autentikasi dan sesi admin terbentuk.

## Akar masalah
Kredensial disambung langsung ke SQL sehingga batas antara kode dan data hilang.

## Perbaikan
Gunakan parameter SQL dan verifikasi password yang di-hash dengan algoritma khusus password seperti scrypt atau Argon2.

## Contoh rentan
`"... username='" + username + "' AND password='" + password + "'"`

## Contoh aman
`connection.execute("SELECT id FROM users WHERE username=?", (username,))`

## Analisis Mendalam
- **Batas kode/data:** query login yang rentan menempelkan nilai username dan password ke SQL. Input khusus dapat mengubah kondisi query, bukan sekadar dibandingkan sebagai kredensial.
- **Baseline:** kirim login biasa yang gagal dan amati status/redirect serta query Inspector. Gunakan akun latihan dan jangan mengirim kredensial ke host selain loopback.
- **Bukti autentikasi:** redirect `302` belum cukup. Ikuti halaman `/me` untuk memastikan principal yang terbentuk; perhatikan bahwa login sukses mengubah session.
- **Secure:** input uji yang sama harus diproses sebagai nilai data dan gagal autentikasi. Gunakan query berparameter, lalu verifikasi password yang di-hash dengan algoritma khusus password.
- **Batas bukti:** pesan database atau status respons saja tidak membuktikan bypass; identitas akun pada halaman sesudah login adalah bukti relevan.

## Bukti yang Dicatat
- Endpoint/method, mode, status atau redirect, dan principal yang ditampilkan sesudahnya.
- Perbedaan query Inspector bila tersedia, tanpa menyimpan cookie sesi atau password.
- Hasil Secure untuk input yang sama dan alasan parameterisasi menjaga batas antara sintaks dan data.

## Langkah latihan
1. Pastikan mode **Vulnerable**, buka Masuk, lalu kirim username biasa dan password salah.
2. Perhatikan pesan gagal dan query yang terlihat di Request Inspector.
3. Coba username lokal `' OR '1'='1' -- ` dengan password sembarang.
4. Amati apakah akun admin terbuka. Jangan gunakan teknik ini di situs lain.
5. Ganti ke **Secure** dan ulangi. Server seharusnya menolak login.

## Kalau masih bingung
Tanda kutip membatasi teks dalam SQL. Di lab ini, karakter khusus membuat database membaca sebagian username sebagai kondisi. Solusinya adalah parameter query: database menerima input sebagai data, bukan sebagai instruksi.
