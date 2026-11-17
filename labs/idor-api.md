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

## Analisis Mendalam
- **Autentikasi vs otorisasi:** login menetapkan principal Budi, tetapi tidak otomatis memberi hak baca terhadap setiap ID pengguna yang tersedia di API.
- **Eksperimen:** gunakan `/api/user/2` sebagai kontrol milik Budi, lalu ubah hanya ID path ke fixture admin yang ditentukan materi. Pertahankan sesi yang sama.
- **Bukti respons:** bandingkan `id`, `username`, `role`, `balance`, dan field lain yang benar-benar dikembalikan. Status `200` saja bukan bukti kebocoran; identitas record di body yang menentukan.
- **Secure:** objek sendiri tetap dapat dibaca sesuai kontrak endpoint, sementara objek lain harus ditolak atau tidak ditemukan tanpa mengungkap field privat.
- **Perbaikan:** lakukan pemeriksaan kepemilikan pada query atau service layer dan pilih field response secara eksplisit; jangan mengirim seluruh row pengguna secara otomatis.

## Bukti yang Dicatat
- ID yang diminta, akun sesi (label seperti “Budi”, bukan nilai cookie), status, dan nama field yang muncul.
- Hasil kontrol own-object serta hasil permintaan objek lain pada kedua mode.
- Data sensitif harus dirahasiakan; catat nama field, bukan nilai rahasia.

## Langkah latihan
1. Masuk sebagai Budi (`budi` / `budi123`) di aplikasi lokal.
2. Buka alamat `/api/user/2` dan lihat respons JSON milik Budi.
3. Ganti angka menjadi `/api/user/1`. Periksa apakah respons menyertakan informasi admin atau penanda latihan.
4. Ulangi dalam mode **Secure**. Pengguna lain tidak boleh terlihat.

## Kalau masih bingung
API adalah pintu data untuk aplikasi, bukan halaman khusus yang otomatis aman. Pintu ini juga harus memastikan bahwa ID di alamat memang milik orang yang sedang masuk.
