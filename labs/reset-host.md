# Password reset: URL origin tepercaya

## Tujuan
Membedakan origin reset yang berasal dari konfigurasi tepercaya dengan host yang dikirim request.

## Konsep
Tautan reset sensitif terhadap tujuan dan token. Jika host request langsung dipakai untuk membuat link, nilai yang tidak dipercaya dapat mengubah preview. Lab ini hanya membuat teks fixture: tidak mengirim email, tidak menerbitkan token yang sah, dan tidak mengubah password.

## Hint 1
Mulai dengan host lokal default.

## Hint 2
Ubah parameter `host`, bukan Host header tujuan Burp.

## Hint 3
Secure selalu menggunakan `127.0.0.1:5000`.

## Solusi
Parameter host asing mengubah link preview di Vulnerable. Secure mengabaikannya dan memakai origin lokal tetap.

## Akar Masalah
Origin reset disusun dari input request, bukan konfigurasi deployment tepercaya.

## Perbaikan
Simpan canonical public origin di konfigurasi, gunakan token reset acak, sekali pakai, dan singkat masa berlakunya.

## Contoh Rentan
Membuat link reset dari Host request.

## Contoh Aman
Membuat link dari origin server tetap dan mengikat token ke akun.

## Analisis Mendalam
- Parameter `host` adalah input body/query; target tetap localhost.
- `tokenIssued` dan `messageSent` harus tetap false.
- Perhatikan `linkPreview`, status, dan flag.
- Jangan klik atau bagikan link preview.
- Secure harus menolak pengaruh parameter host.

## Langkah Latihan
1. Kirim GET `/extra/academy/reset-host` tanpa parameter.
2. Catat preview awal.
3. Di Repeater tambahkan `?host=training.invalid`; jangan ubah Host header.
4. Kirim sekali dan bandingkan.
5. Aktifkan Secure dan ulangi. Origin preview harus tetap lokal.

## Bukti yang Dicatat
Target loopback, parameter host, preview yang disensor, tokenIssued=false, messageSent=false.

## Kalau Masih Bingung
Ini variasi kedua untuk pembentukan URL reset; tidak melakukan reset password sungguhan.
