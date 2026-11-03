# Token reset password yang dapat ditebak

## Tujuan
Memahami properti keamanan token pemulihan akun.

## Konsep
Token reset harus acak secara kriptografis, kedaluwarsa, sekali pakai, dan dikaitkan dengan akun serta permintaan tertentu.

## Hint 1
Periksa bagaimana token dibuat dari nama akun.

## Hint 2
Token yang deterministik dapat dihitung ulang oleh pihak yang mengetahui inputnya.

## Hint 3
Gunakan database lab yang terisolasi dan akun seed admin hanya untuk mengamati flag latihan.

## Solusi
Identifikasi bahwa username saja menentukan token sehingga tidak ada rahasia acak yang membatasi penebakannya.

## Akar masalah
Token reset berasal dari hash cepat atas data publik dan tidak memiliki expiry atau konsumsi sekali pakai.

## Perbaikan
Gunakan `secrets.token_urlsafe`, simpan hash token dengan expiry, kaitkan ke akun, dan invalidasi setelah dipakai.

## Contoh rentan
`md5(username)`

## Contoh aman
Token acak kriptografis yang tersimpan sebagai hash dan hanya berlaku sekali dalam waktu singkat.

## Langkah latihan
1. Di mode **Vulnerable**, token latihan diturunkan langsung dari nama akun `admin`.
2. Untuk memahami kelemahannya, ingat bahwa MD5 dari teks yang sama selalu menghasilkan nilai yang sama; tidak ada rahasia acak yang dikirim ke email.
3. Kirim formulir reset dengan token latihan yang dapat dihitung dari username pada aplikasi lokal, lalu amati pesannya.
4. Di mode **Secure**, minta token baru dari formulir. Token demo acak ditampilkan khusus di lingkungan lokal, berlaku 10 menit, dan hanya bisa dipakai sekali.

## Kalau masih bingung
Password reset seperti kunci cadangan. Kalau kuncinya hanya dibuat dari nama akun, siapa pun yang tahu nama itu dapat menyalinnya. Kunci yang aman harus acak, sementara, dan dibuang setelah digunakan.
