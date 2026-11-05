# Clickjacking dan frame policy

## Tujuan
Memeriksa apakah respons menyatakan kebijakan yang mencegah halaman sensitif ditampilkan dalam frame yang tidak diinginkan.

## Konsep
Clickjacking menipu pengguna melalui tampilan bertumpuk/frame. `Content-Security-Policy: frame-ancestors` dan `X-Frame-Options` membantu mengatur framing; keduanya bukan pengganti otorisasi atau perlindungan CSRF. Lab hanya mengembalikan metadata JSON dan tidak membuat frame atau halaman penipuan.

## Hint 1
Bandingkan header response pada mode Vulnerable dan Secure.

## Hint 2
Cari `frame-ancestors` pada CSP dan `X-Frame-Options`.

## Hint 3
Keberadaan header tidak membuktikan seluruh alur UI aman; periksa pula perubahan state dan CSRF secara terpisah.

## Solusi
Minta `/extra/academy/clickjacking-headers`. Vulnerable tidak menyertakan frame policy; Secure mengirim `frame-ancestors 'none'` dan `X-Frame-Options: DENY`.

## Akar Masalah
Respons halaman tidak memiliki arahan browser tentang siapa yang boleh membingkainya.

## Perbaikan
Tetapkan `frame-ancestors` sesuai kebutuhan produk dan konsisten pada seluruh halaman sensitif. Hindari mengandalkan kontrol UI untuk otorisasi.

## Contoh Rentan
Respons halaman sensitif tanpa kebijakan framing.

## Contoh Aman
`Content-Security-Policy: frame-ancestors 'none'` pada halaman yang tidak boleh di-embed.

## Analisis Mendalam
- Periksa status, Content-Type, CSP, dan X-Frame-Options pada respons.
- Tidak adanya header adalah temuan konfigurasi; endpoint tetap dapat mengembalikan body normal.
- CSP merupakan kontrol modern; X-Frame-Options membantu kompatibilitas browser lama.
- Repeater hanya menginspeksi respons. Ia tidak mensimulasikan klik pengguna atau membuktikan exploit UI.
- Secure harus mengubah header, bukan identitas atau data akun.

## Langkah Latihan
1. Buka Burp browser dan pastikan target KopiLab lokal.
2. Kirim GET `/extra/academy/clickjacking-headers`, tanpa parameter, sebagai baseline.
3. Catat status dan header CSP/X-Frame-Options pada Repeater.
4. Ganti ke Secure melalui UI, tangkap request baru, dan bandingkan.
5. Pastikan Secure memberi kebijakan framing restriktif; jangan membuat halaman eksternal untuk membingkai target.

## Bukti yang Dicatat
Method/path, status, Content-Type, CSP, X-Frame-Options, mode. Jangan sertakan cookie.

## Kalau Masih Bingung
Fokus pada panel Response Headers. Lab ini menguji konfigurasi response, bukan payload atau perubahan akun.
