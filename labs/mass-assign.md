# Mass assignment pada profil

## Tujuan
Mencegah field sensitif berubah lewat endpoint pengubahan profil biasa.

## Konsep
Mass assignment terjadi ketika server memetakan seluruh field request ke kolom model tanpa allowlist. Role dan saldo adalah properti sensitif.

## Hint 1
Ikuti setiap nama field dari form sampai query UPDATE.

## Hint 2
Pisahkan atribut profil yang boleh diedit dari atribut internal akun.

## Hint 3
Konfirmasikan perubahan lewat halaman akun lokal, bukan hanya status respons.

## Solusi
Buktikan bahwa handler menerima field tambahan di luar form normal dan menerapkannya ke akun latihan.

## Akar masalah
Nama kolom SQL dibentuk langsung dari field request.

## Perbaikan
Gunakan allowlist field yang boleh diedit dan tetapkan perubahan role/saldo melalui alur admin terotorisasi.

## Contoh rentan
Loop atas seluruh `request.form.items()` sebagai kolom database.

## Contoh aman
`UPDATE users SET email=? WHERE id=?` dengan email tervalidasi.

## Analisis Mendalam
- **Batas kepercayaan:** seluruh body request dikendalikan klien; field yang tidak ditampilkan form tetap dapat dikirim. Karena itu UI bukan allowlist keamanan.
- **Identitas akun:** endpoint harus mengambil ID pengguna dari sesi tervalidasi. Jangan menerima `user_id` atau role sebagai sumber identitas dari body.
- **Eksperimen Repeater:** simpan request baseline perubahan email, kirim tanpa perubahan, lalu tambahkan hanya field `role` pada salinan body form lokal sebagaimana dijelaskan di panduan lab. Pertahankan cookie sesi, host, path, dan email.
- **Bukti persisten:** periksa response dan halaman `/me` setelah redirect untuk memastikan role aktual; jangan menyimpulkan hanya dari status atau pesan sukses.
- **Secure:** email yang diizinkan tetap dapat diperbarui, tetapi role harus tetap `user`. Terapkan allowlist di server dan jalur administrasi role yang terpisah dengan otorisasi/audit.

## Bukti yang Dicatat
- Baseline field email dan response sebelum perubahan.
- Field tambahan yang diuji, role aktual di `/me`, dan header flag pada Vulnerable/Secure.
- Jangan menaruh cookie sesi di catatan; simpulkan bahwa atribut sensitif harus dikeluarkan dari pembaruan profil.

## Langkah latihan
1. Masuk sebagai Budi, buka profil, lalu kirim perubahan email biasa.
2. Untuk menguji batas field di mode **Vulnerable**, tambahkan field `role=admin` pada POST profil lokal.
3. Buka `/me` dan lihat role serta flag latihan.
4. Ulangi pada mode **Secure**. Email boleh berubah, tetapi role harus tetap `user`.

## Kalau masih bingung
Form profil adalah formulir perubahan alamat, bukan formulir untuk mengubah jabatan. Server seharusnya hanya menerima daftar field yang memang boleh diubah pengguna.
