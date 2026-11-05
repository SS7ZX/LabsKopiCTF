# OAuth redirect URI simulasi

## Tujuan
Menilai mengapa callback OAuth harus dibandingkan dengan URI yang telah didaftarkan secara tepat.

## Konsep
OAuth redirect URI menentukan tujuan kembalinya alur otorisasi. Validasi longgar dapat mengirim kode/hasil login ke tujuan yang keliru. Endpoint ini hanya memvalidasi preview string; tidak terhubung ke provider dan tidak pernah menerbitkan token.

## Hint 1
Baseline adalah callback relatif `/extra/academy/oauth-callback`.

## Hint 2
Bandingkan callback relatif dengan simulator loopback port 9000.

## Hint 3
Lihat `tokenIssued=false`; response redirect hanya preview data lokal.

## Solusi
Vulnerable menerima callback simulator lokal absolute; Secure hanya menerima callback relatif.

## Akar Masalah
Validasi redirect URI menerima lebih banyak tujuan daripada callback yang disetujui.

## Perbaikan
Cocokkan URI callback penuh dengan allowlist yang terdaftar dan ikat hasil authorization ke state.

## Contoh Rentan
Menerima URI callback arbitrary dari parameter.

## Contoh Aman
Perbandingan exact match terhadap URI callback yang dikonfigurasi.

## Analisis Mendalam
- Uji endpoint tetap `127.0.0.1:5000`; `redirect_uri` hanyalah data preview.
- Catat accepted, redirectPreview, tokenIssued, dan status.
- Simulator callback hanya boleh bernilai `http://127.0.0.1:9000/oauth-callback`.
- Jangan mengikuti preview atau menambahkan domain lain.
- Secure menolak absolute simulator dan masih menerima callback relatif yang ditetapkan.

## Langkah Latihan
1. Kirim GET endpoint dengan callback relatif sebagai baseline.
2. Kirim request ke Repeater.
3. Ubah parameter menjadi URL-encoded `http://127.0.0.1:9000/oauth-callback`.
4. Kirim sekali; analisis JSON saja, jangan ikuti URL.
5. Aktifkan Secure dan ulangi; hasil harus ditolak.

## Bukti yang Dicatat
Redirect URI sebagai nilai, accepted, status, tokenIssued=false, mode. Target HTTP selalu KopiLab.

## Kalau Masih Bingung
Pastikan URL simulator berada di dalam parameter, bukan pada baris Host atau tujuan request.
