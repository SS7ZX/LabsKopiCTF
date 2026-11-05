# Command injection konseptual tanpa shell

## Tujuan
Memahami pemisahan input dari operasi sistem tanpa menjalankan command atau program apa pun.

## Konsep
Command injection terjadi bila data menjadi bagian sintaks perintah. Endpoint ini bukan shell: ia hanya mengenali delimiter dan marker fixture yang sudah ditetapkan, lalu mengembalikan string statis. Tidak ada subprocess, command OS, atau akses file.

## Hint 1
Kirim nilai biasa untuk melihat echo baseline.

## Hint 2
Materi memakai suffix literal `;TRAINING_MARKER`.

## Hint 3
Periksa field execution yang menegaskan simulasi saja.

## Solusi
Nilai `coffee;TRAINING_MARKER` memicu marker statis pada mode Vulnerable. Secure memperlakukannya seluruhnya sebagai teks.

## Akar Masalah
Dalam model kerentanan, delimiter mengubah interpretasi input dari data menjadi pemisah operasi.

## Perbaikan
Hindari shell invocation; gunakan API/argumen terstruktur, allowlist nilai, dan hak proses minimum.

## Contoh Rentan
Meneruskan string gabungan ke shell.

## Contoh Aman
Gunakan fungsi library khusus dan nilai argumen tervalidasi tanpa shell.

## Analisis Mendalam
- Endpoint tidak menjalankan command apa pun; output adalah string konstanta.
- Request tetap GET lokal dan satu parameter `value`.
- Bandingkan input dengan `preview`, `execution`, dan flag.
- Jangan menambahkan perintah, path, atau payload lain.
- Secure tidak mem-parsing delimiter.

## Langkah Latihan
1. Buka GET `/extra/academy/command-simulation?value=coffee`.
2. Kirim ke Repeater dan catat output.
3. Ubah nilai menjadi `coffee;TRAINING_MARKER` (URL-encode `;` jika diperlukan).
4. Kirim sekali ke KopiLab lokal dan pastikan respons menyebut simulasi.
5. Aktifkan Secure, ulangi nilai yang sama; ia harus dipantulkan sebagai teks biasa.

## Bukti yang Dicatat
Input, preview, execution simulator, status, flag dan mode. Jangan menyertakan command sistem.

## Kalau Masih Bingung
`TRAINING_MARKER` adalah token fixture buatan aplikasi, bukan program. Tidak ada terminal OS yang dipanggil.
