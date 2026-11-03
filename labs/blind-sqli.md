# SQLi boolean: pertanyaan benar atau salah

## Tujuan
Memahami inferensi boolean yang membocorkan informasi melalui perbedaan hasil.

## Konsep
Blind SQL injection tidak harus menampilkan hasil query. Perbedaan boolean pada respons dapat bertindak sebagai oracle. Endpoint latihan mengevaluasi kondisi terbatas pada SQLite lokal.

## Hint 1
Bandingkan respons kondisi yang benar dan salah.

## Hint 2
Keluaran endpoint sengaja hanya memuat boolean, bukan baris database.

## Hint 3
Flag ditandai pada header `X-Lab-Flag` jika kondisi lokal benar.

## Solusi
Tunjukkan bahwa ekspresi boolean SQLite lokal mengubah hasil endpoint. Jangan arahkan teknik ini ke sistem lain.

## Akar masalah
Ekspresi request disambungkan ke evaluasi SQL.

## Perbaikan
Jangan menerima ekspresi SQL dari request; gunakan parameter untuk nilai data dan hilangkan oracle yang mengungkap kondisi internal.

## Contoh rentan
`SELECT CASE WHEN (` + condition + `) THEN 1 ELSE 0 END`

## Contoh aman
Tentukan hasil dari data yang dipilih server melalui query berparameter; jangan izinkan fragmen SQL sebagai input.

## Langkah latihan
1. Buka `/extra/blind-sqli?condition=1%3D1` pada KopiLab lokal. Nilai `%3D` adalah tanda `=` di alamat web.
2. Lihat JSON: oracle hanya menjawab `true` atau `false`; flag latihan ada di header respons.
3. Coba kondisi salah `1%3D0` dan bandingkan jawabannya.
4. Aktifkan **Secure** dan ulangi. Mode itu tidak mengevaluasi teks sebagai SQL.

## Kalau masih bingung
Oracle seperti pertanyaan ya/tidak. Meski tidak menunjukkan isi database, jawaban yang berbeda tetap dapat membocorkan informasi. Periksa JSON dan header, bukan mencari tabel yang dicetak di halaman.
