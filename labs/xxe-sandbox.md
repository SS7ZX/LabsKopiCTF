# XXE pada parser XML mainan terisolasi

## Tujuan
Memahami bahwa deklarasi entity XML perlu dibatasi dan dapat memengaruhi pemrosesan dokumen.

## Konsep
XML External Entity (XXE) adalah kelas masalah parser XML yang mengizinkan entity eksternal. Untuk keselamatan, endpoint KopiLab tidak membaca file dan tidak membuat koneksi. String `training://marker` hanya dipetakan ke konstanta lokal.

## Hint 1
Kirim XML biasa terlebih dahulu untuk memastikan format form.

## Hint 2
Materi memakai DOCTYPE dengan entity `training://marker`, bukan file atau host sungguhan.

## Hint 3
Perhatikan `externalAccess=false`; nilai expanded adalah marker fixture.

## Solusi
POST dokumen XML training fixture. Vulnerable menampilkan konstanta marker; Secure menolak DOCTYPE.

## Akar Masalah
Parser rentan memproses deklarasi entity yang seharusnya tidak dipercaya.

## Perbaikan
Nonaktifkan DTD dan external entity pada parser XML; batasi ukuran dan jenis dokumen.

## Contoh Rentan
Mengaktifkan entity resolution tanpa kebutuhan dan batas.

## Contoh Aman
Parser yang menolak DOCTYPE dan tidak melakukan resolusi eksternal.

## Analisis Mendalam
- Request tetap form-urlencoded ke endpoint lokal; tidak ada XML parser yang membaca host filesystem.
- Bandingkan XML sederhana dengan fixture DOCTYPE.
- Catat status, `parsed`, `expanded`, `externalAccess`, dan error.
- Marker tidak mewakili isi file sistem atau response jaringan.
- Secure harus memblokir struktur berisiko tetapi tetap menerima XML sederhana.

## Langkah Latihan
1. Kirim POST `/extra/academy/xxe-sandbox` dengan body `xml=<note>KopiLab</note>`.
2. Catat response baseline.
3. Di Repeater gunakan body form field XML fixture:
   `xml=<!DOCTYPE note [<!ENTITY x SYSTEM "training://marker">]><note>&x;</note>`
4. Pastikan tujuan request tetap `127.0.0.1:5000`; kirim sekali dan baca response JSON.
5. Pada Secure, kirim ulang fixture dan pastikan 400, lalu coba lagi XML biasa.

## Bukti yang Dicatat
Status, jenis fixture, `expanded`, `externalAccess`, dan perbedaan Secure. Jangan mengganti URI fixture dengan file atau URL nyata.

## Kalau Masih Bingung
Encode karakter XML sebagai form body; jangan menaruh dokumen mentah pada baris request.
