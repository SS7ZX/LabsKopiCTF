# CORS policy trust boundary

## Tujuan
Menganalisis cara server mengirim kebijakan Cross-Origin Resource Sharing (CORS) dan membedakan header CORS dari autentikasi/otorisasi.

## Konsep
CORS adalah kebijakan browser tentang apakah halaman dari suatu origin boleh membaca response. CORS bukan kontrol akses pada route, dan Burp Repeater sendiri tidak menegakkan CORS. Endpoint ini hanya mencerminkan nilai Origin untuk demonstrasi header; tidak ada browser pihak ketiga atau koneksi eksternal yang digunakan.

## Hint 1
Bandingkan response tanpa header Origin dengan response yang memiliki `Origin: http://training.invalid`.

## Hint 2
Perhatikan `Access-Control-Allow-Origin` dan `Access-Control-Allow-Credentials` sebagai pasangan, bukan hanya status HTTP.

## Hint 3
Repeater dapat menunjukkan header kebijakan, tetapi bukan membuktikan browser akan mengizinkan JavaScript lintas origin membaca response.

## Solusi
Kirim GET ke `/extra/academy/cors-policy` dengan header Origin simulasi. Mode Vulnerable memantulkan origin dan mengizinkan credentials. Secure hanya mengizinkan origin KopiLab yang ditetapkan.

## Akar Masalah
Kebijakan rentan mempercayai nilai Origin yang dikendalikan request tanpa allowlist.

## Perbaikan
Gunakan allowlist origin yang eksplisit, jangan menggabungkan wildcard dengan credentials, dan tetap jalankan autentikasi serta otorisasi pada endpoint data.

## Contoh Rentan
Memantulkan Origin request tanpa validasi dan mengaktifkan credentials.

## Contoh Aman
Bandingkan Origin dengan daftar origin tepercaya dan kirim nilai yang cocok saja.

## Analisis Mendalam
- **Input:** Origin adalah header request yang dapat diatur klien; nama header bukan bukti identitas.
- **Decision point:** server menentukan `Access-Control-Allow-Origin`; browser kemudian menerapkan kebijakan tersebut.
- **Bukti:** status, `Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`, dan `Vary`.
- **Batas interpretasi:** Repeater bukan browser, jadi keberadaan header saja bukan bukti eksploitasi browser.
- **Secure control:** Origin lokal yang tepat dapat diizinkan, sedangkan origin lain tidak memperoleh izin.

## Langkah Latihan
1. Pastikan KopiLab berjalan lokal dan mode Vulnerable aktif.
2. Tangkap request GET `/extra/academy/cors-policy` melalui Burp Proxy; mulai tanpa Origin sebagai baseline.
3. Kirim ke Repeater dan catat response baseline.
4. Tambahkan hanya `Origin: http://training.invalid`; target request harus tetap `127.0.0.1:5000`.
5. Kirim sekali dan bandingkan header CORS. Jangan membuka alamat training.invalid atau mengirim request ke host tersebut.
6. Ganti ke Secure, tangkap request baru, lalu ulangi. Origin asing tidak boleh mendapat header izin.
7. Catat bahwa CORS mengatur pembacaan browser, bukan otorisasi server.

## Bukti yang Dicatat
Host/path lokal, nilai Origin simulasi, status, header CORS, mode, dan perbedaan hasil. Redaksi cookie.

## Kalau Masih Bingung
Request tetap menuju KopiLab. `Origin` hanya nilai header latihan; ia tidak mengarahkan koneksi ke `training.invalid`.
