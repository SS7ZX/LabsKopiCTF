# IDOR pada API profil pengguna

## Tujuan
Menerapkan pemeriksaan otorisasi objek yang sama pada endpoint JSON.

## Konsep
Endpoint API tetap membutuhkan kontrol akses; menyembunyikan tombol di UI tidak membatasi permintaan langsung ke resource.

## Hint 1
Bandingkan ID di URL dengan user ID pada sesi.

## Hint 2
Perhatikan kolom apa saja yang dikirim kembali untuk setiap akun.

## Hint 3
Pada lab lokal, data admin berisi penanda flag khusus untuk mendeteksi akses lintas akun.

## Solusi
Tunjukkan bahwa endpoint mengembalikan data pengguna lain tanpa keputusan otorisasi atas objek tersebut.

## Akar masalah
Handler API mempercayai identifier dari URL dan langsung mengambil pengguna.

## Perbaikan
Batasi query pada pemilik yang terautentikasi; berikan akses lintas akun hanya melalui kebijakan role yang eksplisit.

## Contoh rentan
`SELECT * FROM users WHERE id=?`

## Contoh aman
`SELECT id, username, email FROM users WHERE id=?` dengan ID yang juga cocok dengan pengguna di sesi.

## Langkah latihan
1. Masuk sebagai Budi (`budi` / `budi123`) di aplikasi lokal.
2. Buka alamat `/api/user/2` dan lihat respons JSON milik Budi.
3. Ganti angka menjadi `/api/user/1`. Periksa apakah respons menyertakan informasi admin atau penanda latihan.
4. Ulangi dalam mode **Secure**. Pengguna lain tidak boleh terlihat.

## Kalau masih bingung
API adalah pintu data untuk aplikasi, bukan halaman khusus yang otomatis aman. Pintu ini juga harus memastikan bahwa ID di alamat memang milik orang yang sedang masuk.
