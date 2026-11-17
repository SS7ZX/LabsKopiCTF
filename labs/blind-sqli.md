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

## Analisis Mendalam
- **Model oracle:** endpoint hanya mengembalikan boolean. Ia tidak menampilkan baris database, sehingga bukti yang diamati adalah perbedaan hasil antara kondisi benar dan salah, bukan isi tabel.
- **Eksperimen terkontrol:** gunakan hanya dua kondisi fixture yang disebut di langkah latihan. Pertahankan endpoint dan parameter tetap, lalu bandingkan JSON `result`, status, error, dan header flag.
- **Makna perbedaan:** bila satu kondisi menghasilkan `true` dan kondisi pembanding `false`, input memengaruhi evaluasi server. Itu cukup untuk mengenali oracle; jangan menyusun rangkaian tebakan atau mengekstrak data.
- **Secure:** input kondisi mentah tidak boleh diteruskan ke interpreter SQL. Respons Secure dapat menolak format tersebut, tetapi tetap harus memberikan respons valid untuk fungsi aplikasi yang sah.
- **Akar mitigasi:** parameter SQL hanya untuk nilai data; struktur query harus tetap ditentukan kode server. Menghapus kata tertentu dari input tidak memperbaiki injeksi.

## Bukti yang Dicatat
- Kondisi fixture yang dipakai (benar/salah), mode, status, dan nilai JSON `result`.
- Ada/tidaknya header `X-Lab-Flag`; jangan menambahkan percobaan di luar pasangan kondisi dalam materi.
- Hasil Secure untuk input yang sama dan ringkasan mengapa parameterisasi menutup jalur evaluasi.

## Langkah latihan
1. Buka `/extra/blind-sqli?condition=1%3D1` pada KopiLab lokal. Nilai `%3D` adalah tanda `=` di alamat web.
2. Lihat JSON: oracle hanya menjawab `true` atau `false`; flag latihan ada di header respons.
3. Coba kondisi salah `1%3D0` dan bandingkan jawabannya.
4. Aktifkan **Secure** dan ulangi. Mode itu tidak mengevaluasi teks sebagai SQL.

## Kalau masih bingung
Oracle seperti pertanyaan ya/tidak. Meski tidak menunjukkan isi database, jawaban yang berbeda tetap dapat membocorkan informasi. Periksa JSON dan header, bukan mencari tabel yang dicetak di halaman.
