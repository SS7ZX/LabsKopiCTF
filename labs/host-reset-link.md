# Host header pada tautan reset simulasi

## Tujuan
Menelusuri risiko ketika aplikasi membangun URL absolut dari nilai host yang dikendalikan request.

## Konsep
Host header biasanya menentukan host tujuan request. Jika aplikasi menggunakan nilai itu untuk membuat tautan sensitif, URL yang ditampilkan bisa salah. Endpoint ini hanya membuat preview teks fiktif; tidak mengirim email, menerbitkan token, atau mengakses host yang ditulis.

## Hint 1
Bandingkan parameter `host` dengan host lokal KopiLab.

## Hint 2
Perhatikan apakah `resetLinkPreview` dibangun dari konfigurasi tetap atau nilai input.

## Hint 3
Status sukses tidak berarti email dikirim; field `emailSent` selalu false pada simulator.

## Solusi
Kirim GET `/extra/academy/host-reset-link?host=training.invalid`. Vulnerable mengembalikan preview dengan host tersebut; Secure memakai origin lokal yang tetap.

## Akar Masalah
Aplikasi mempercayai nilai host dari request saat menyusun URL absolut.

## Perbaikan
Gunakan origin tepercaya dari konfigurasi deployment, bukan header atau parameter request; validasi URL reset dan masa hidup token.

## Contoh Rentan
Menyusun `https://{request_host}/reset?...` tanpa validasi host.

## Contoh Aman
Menyusun URL dari origin tetap yang dikelola konfigurasi server.

## Analisis Mendalam
- Request tetap dikirim ke `127.0.0.1:5000`; `host` adalah data uji, bukan tujuan jaringan.
- Baca `resetLinkPreview` dan `emailSent`, serta bandingkan mode.
- Demo tidak membuat token yang dapat digunakan dan tidak mengirim email.
- Host yang direfleksikan berisiko memengaruhi kepercayaan pengguna pada tautan; jangan mengklik atau membagikan preview.
- Secure harus mengabaikan input host dan memilih origin konfigurasi.

## Langkah Latihan
1. Buka endpoint tanpa parameter untuk merekam baseline.
2. Kirim request ke Repeater dan catat preview default.
3. Ubah hanya query `host` menjadi `training.invalid`; target Host header tetap localhost.
4. Kirim sekali dan periksa JSON. Jangan buka link hasil preview.
5. Aktifkan Secure dan ulangi. URL preview harus tetap ber-origin lokal.

## Bukti yang Dicatat
Target loopback, nilai host uji, resetLinkPreview yang sudah disamarkan, emailSent=false, dan perbandingan Secure.

## Kalau Masih Bingung
Jangan ubah baris `Host: 127.0.0.1:5000` pada request. Ubah parameter `host` di query saja.
