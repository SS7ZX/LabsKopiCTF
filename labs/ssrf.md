# SSRF menuju service simulasi

## Tujuan
Mengenali server-side request forgery tanpa mengirim trafik ke host pihak lain.

## Konsep
SSRF terjadi ketika server mengambil URL yang dipilih pengguna. Target KopiLab sengaja hanya mengizinkan service internal simulasi di loopback dan port lab.

## Hint 1
Lihat bagaimana URL preview diteruskan ke pengambil konten server.

## Hint 2
Perhatikan batas host dan port yang dikonfigurasi untuk service internal.

## Hint 3
Service latihan berjalan di 127.0.0.1:5001; tujuan selain service lokal ditolak.

## Solusi
Gunakan halaman preview untuk memeriksa respons service internal simulasi KopiLab.

## Akar masalah
Handler melakukan request server-side berdasarkan parameter URL.

## Perbaikan
Gunakan allowlist host dan skema, blok alamat non-loopback, cegah redirect keluar batas, dan batasi egress di deployment nyata.

## Contoh rentan
`urlopen(url)` tanpa kebijakan tujuan.

## Contoh aman
Validasi tujuan terhadap satu service lab loopback tetap sebelum request.

## Analisis Mendalam
- **Dua koneksi berbeda:** browser mengirim request ke `127.0.0.1:5000/preview`; kemudian server KopiLab yang melakukan fetch ke service latihan `127.0.0.1:5001`. Repeater hanya mengubah request pertama.
- **Baseline:** gunakan URL persis yang disediakan materi. Catat response preview, status, dan apakah konten berasal dari service simulasi; tidak perlu mengubah tujuan.
- **Bukti:** parameter URL yang diterima serta isi hasil menunjukkan bahwa server melakukan fetch. Jangan menguji host, skema, redirect, atau port lain di luar fixture.
- **Secure:** URL service latihan yang tepat tetap berfungsi, sedangkan tujuan yang tidak diizinkan ditolak sebelum koneksi dilakukan.
- **Mitigasi:** validasi skema, hostname, port, alamat hasil resolusi, dan redirect; tambahkan pembatasan egress di deployment. Allowlist harus diterapkan pada tujuan final, bukan sekadar memeriksa teks URL.

## Bukti yang Dicatat
- URL lokal yang diminta, status/response preview, dan fakta bahwa port 5001 adalah service simulasi.
- Perbandingan keberhasilan fixture yang tepat dengan penolakan Secure; jangan mencatat atau mencoba tujuan eksternal.
- Rekomendasi allowlist dan validasi tujuan setelah resolusi/redirect.

## Langkah latihan
1. Pastikan KopiLab berjalan; saat dijalankan lewat `run.py`, service latihan ada di `127.0.0.1:5001`.
2. Buka `/preview?url=http://127.0.0.1:5001/` pada aplikasi lokal.
3. Amati respons service internal simulasi dan flag latihan.
4. Mode **Secure** membatasi URL ke alamat service yang tepat. Jangan mengganti tujuan menjadi alamat internet atau mesin lain.

## Kalau masih bingung
SSRF berarti server yang membuka tautan, bukan browser kamu. Lab ini sengaja hanya memiliki satu tujuan lokal palsu; jangan gunakan preview untuk mencoba alamat lain.
