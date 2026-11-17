# Bypass filter sederhana

## Tujuan
Memahami mengapa pemeriksaan blacklist case-sensitive mudah dilewati.

## Konsep
Normalisasi input sebelum validasi merupakan bagian penting dari kebijakan. Filter string sederhana tidak menggantikan parser atau validasi allowlist.

## Hint 1
Perhatikan apakah filter membandingkan teks dengan memperhatikan huruf besar-kecil.

## Hint 2
Bandingkan variasi kapitalisasi dari kata terlarang.

## Hint 3
Endpoint hanya memeriksa teks dan mengembalikan boolean; tidak menjalankan input sebagai perintah.

## Solusi
Gunakan variasi kapitalisasi kata admin pada endpoint lokal untuk menunjukkan perbedaan pemeriksaan.

## Akar masalah
Blacklist vulnerable memakai pencarian substring yang case-sensitive.

## Perbaikan
Normalisasi Unicode dan kapitalisasi, gunakan allowlist sesuai konteks, serta hindari blacklist string sebagai batas keamanan.

## Contoh rentan
`"admin" in query`

## Contoh aman
Normalisasi input, lalu gunakan allowlist nama yang diizinkan.

## Analisis Mendalam
- **Hipotesis:** apakah pemeriksaan blacklist membandingkan input secara case-sensitive, sehingga kapitalisasi mengubah keputusan?
- **Kontrol dan eksperimen:** kirim `admin` sebagai baseline, lalu ubah hanya kapitalisasi menjadi `ADMIN` pada parameter `q`. Endpoint ini hanya mengembalikan keputusan boolean dan tidak membuat akun atau menjalankan input.
- **Bukti:** bandingkan nilai `blocked`, status, dan header flag. Jangan menyimpulkan dampak lain yang tidak ditunjukkan simulator.
- **Secure:** normalisasi harus dilakukan sebelum kebijakan diterapkan, dan aturan harus tetap konsisten untuk variasi input yang ekuivalen.
- **Batas solusi:** blacklist string mudah melewatkan variasi encoding, Unicode, atau konteks lain. Untuk keputusan sensitif, tentukan input yang boleh melalui allowlist dan validasi sesuai tipe data.

## Bukti yang Dicatat
- Nilai baseline dan variasi kapitalisasi, status, JSON `blocked`, serta keberadaan flag.
- Apakah kedua variasi mendapat keputusan konsisten pada Secure.
- Penjelasan singkat urutan normalisasi dan pemeriksaan yang diperlukan.

## Langkah latihan
1. Buka `/extra/filter?q=admin` pada KopiLab lokal. Catat bahwa kata tersebut diblokir.
2. Ubah hurufnya menjadi kapital: `/extra/filter?q=ADMIN`.
3. Pada mode **Vulnerable**, hasil boolean berubah dan respons memberi header flag.
4. Mode **Secure** mengubah huruf ke format seragam sebelum membandingkan; kedua bentuk harus diblokir.

## Kalau masih bingung
Filter lama mencari satu ejaan yang persis sama. Huruf `A` dan `a` terlihat mirip bagi manusia tetapi berbeda bagi pemeriksaan yang peka huruf besar-kecil. Normalisasi dulu sebelum memeriksa.
