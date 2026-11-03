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

## Langkah latihan
1. Pastikan mode **Vulnerable**, buka Masuk, lalu kirim username biasa dan password salah.
2. Perhatikan pesan gagal dan query yang terlihat di Request Inspector.
3. Coba username lokal `' OR '1'='1' -- ` dengan password sembarang.
4. Amati apakah akun admin terbuka. Jangan gunakan teknik ini di situs lain.
5. Ganti ke **Secure** dan ulangi. Server seharusnya menolak login.

## Kalau masih bingung
Tanda kutip membatasi teks dalam SQL. Di lab ini, karakter khusus membuat database membaca sebagian username sebagai kondisi. Solusinya adalah parameter query: database menerima input sebagai data, bukan sebagai instruksi.
