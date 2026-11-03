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

## Langkah latihan
1. Buka `/extra/filter?q=admin` pada KopiLab lokal. Catat bahwa kata tersebut diblokir.
2. Ubah hurufnya menjadi kapital: `/extra/filter?q=ADMIN`.
3. Pada mode **Vulnerable**, hasil boolean berubah dan respons memberi header flag.
4. Mode **Secure** mengubah huruf ke format seragam sebelum membandingkan; kedua bentuk harus diblokir.

## Kalau masih bingung
Filter lama mencari satu ejaan yang persis sama. Huruf `A` dan `a` terlihat mirip bagi manusia tetapi berbeda bagi pemeriksaan yang peka huruf besar-kecil. Normalisasi dulu sebelum memeriksa.
