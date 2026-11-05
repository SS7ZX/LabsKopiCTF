# Cache deception pada resource privat simulasi

## Tujuan
Menganalisis ketidakcocokan antara path yang dianggap statis oleh cache dan konten privat yang dikembalikan aplikasi.

## Konsep
Cache deception dapat terjadi ketika layer cache dan aplikasi menafsirkan path secara berbeda. Endpoint ini hanya mengembalikan satu profil dummy dan header cache; tidak ada reverse proxy atau data akun nyata yang di-cache.

## Hint 1
Bandingkan `/profile` dengan `/profile.css`.

## Hint 2
Periksa body yang sama dengan nilai `Cache-Control`.

## Hint 3
Secure mode harus selalu mengirim `private, no-store` untuk fixture profil.

## Solusi
Pada Vulnerable, suffix ekstensi statis membuat response dummy diberi `Cache-Control: public`. Secure mengabaikan suffix dan menggunakan kebijakan privat.

## Akar Masalah
Keputusan cache dibuat dari pola URL tanpa mempertimbangkan bahwa response berasal dari resource privat.

## Perbaikan
Gunakan aturan cache berdasarkan tipe/resource dan autentikasi; data privat memakai `private, no-store`.

## Contoh Rentan
Menganggap semua URL berakhiran `.css` sebagai aset publik.

## Contoh Aman
Tentukan cache policy pada handler berdasarkan sensitivitas response.

## Analisis Mendalam
- Parameter `path` hanya mengubah simulasi klasifikasi; endpoint tetap lokal.
- Bandingkan body dummy, `cacheable`, dan Cache-Control.
- Status 200 bukan indikator apakah cache policy aman.
- Tidak ada shared cache, jadi jangan menyimpulkan kebocoran lintas pengguna nyata.
- Secure harus menjaga body fungsi tetap tetapi menghentikan caching publik.

## Langkah Latihan
1. Kirim GET dengan `path=/profile` untuk baseline.
2. Kirim request yang sama ke Repeater dan catat body serta Cache-Control.
3. Ubah hanya `path` menjadi `/profile.css`, kirim sekali, lalu bandingkan.
4. Aktifkan Secure dan ulangi kedua nilai.
5. Pastikan kedua respons Secure bersifat `private, no-store`.

## Bukti yang Dicatat
Nilai path, body profil fixture, header Cache-Control, `cacheable`, dan mode.

## Kalau Masih Bingung
Path uji dikirim sebagai parameter query. Jangan menambahkan cache proxy eksternal.
