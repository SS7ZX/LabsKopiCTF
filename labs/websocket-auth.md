# Otorisasi handshake WebSocket simulasi

## Tujuan
Mengetahui bahwa status autentikasi yang dikirim klien tidak seharusnya menjadi bukti otorisasi untuk koneksi atau event.

## Konsep
WebSocket biasanya dimulai dengan handshake HTTP lalu mempertahankan koneksi. Lab ini tidak membuka WebSocket; endpoint JSON hanya mensimulasikan keputusan handshake agar aman dan mudah dianalisis melalui Repeater.

## Hint 1
Mulai dengan `authenticated=false`.

## Hint 2
Bandingkan query claim dengan status login KopiLab.

## Hint 3
Secure mode menggunakan sesi lokal, bukan query string, dan endpoint tidak mengirim event nyata.

## Solusi
Dalam Vulnerable, `authenticated=true` dari query mengaktifkan event fixture. Secure mensyaratkan sesi login.

## Akar Masalah
Server mempercayai klaim autentikasi yang dikendalikan peminta.

## Perbaikan
Validasi sesi/token pada handshake dan otorisasi setiap operasi/event setelah koneksi terbentuk.

## Contoh Rentan
Menganggap parameter `authenticated=true` membuktikan identitas.

## Contoh Aman
Mengambil identitas dari sesi tervalidasi dan memeriksa hak akses per event.

## Analisis Mendalam
- Perhatikan field `transport` yang menyatakan simulasi; tidak ada protokol upgrade.
- Uji baseline `authenticated=false`, lalu `true` pada endpoint lokal.
- Periksa status 401/200, `authorized`, dan event fixture.
- Jangan mengirim credential atau token nyata; query tidak mewakili autentikasi produksi.
- Secure memakai session user yang sudah terverifikasi.

## Langkah Latihan
1. Kirim GET `/extra/academy/websocket-auth?authenticated=false`.
2. Catat status dan JSON.
3. Ubah hanya parameter menjadi `true` lewat Repeater dan lihat respons Vulnerable.
4. Aktifkan Secure. Tanpa login, query tidak boleh memberi akses.
5. Login pada browser KopiLab lokal dan tangkap ulang request; Secure boleh mengenali sesi lokal, namun query tetap bukan sumber izin.

## Bukti yang Dicatat
Request target, query claim, status, authorized/event, transport simulator, dan mode.

## Kalau Masih Bingung
Ini endpoint HTTP JSON biasa. Tidak ada tab WebSocket atau frame yang perlu dikirim.
