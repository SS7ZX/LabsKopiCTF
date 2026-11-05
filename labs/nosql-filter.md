# NoSQL filter injection simulasi

## Tujuan
Mengenali perbedaan antara nilai filter literal dan operator query yang tidak semestinya diterima dari klien.

## Konsep
NoSQL injection terjadi saat input pengguna dapat mengubah struktur filter dokumen. KopiLab memakai evaluator string fixture yang hanya mengenali beberapa nilai tetap; tidak ada MongoDB atau query dinamis.

## Hint 1
Mulai dengan `filter=role=user`.

## Hint 2
Gunakan operator demonstrasi `$ne:user` dari halaman materi.

## Hint 3
Secure menerima allowlist sederhana dan menolak token operator.

## Solusi
GET dengan `filter=$ne:user` memberi `matched=true` dan flag hanya pada mode Vulnerable. Secure menolak input tersebut.

## Akar Masalah
Dalam skenario rentan, input operator diperlakukan sebagai struktur filter alih-alih data biasa.

## Perbaikan
Validasi bentuk dan tipe input, buat query menggunakan operator yang ditetapkan server, dan jangan menerima object operator dari klien tanpa kebijakan.

## Contoh Rentan
Menggabungkan filter dokumen langsung dari object request.

## Contoh Aman
Terima field/value yang di-allowlist, lalu susun filter server-side.

## Analisis Mendalam
- Endpoint mengembalikan boolean; ia tidak membaca atau mengekspos koleksi.
- Bandingkan baseline literal dan operator fixture.
- Status, `matched`, `filter`, dan flag merupakan bukti latihan.
- Jangan menambah operator atau mencoba query syntax di database eksternal.
- Secure mengembalikan 400 untuk operator yang tak dikenal.

## Langkah Latihan
1. Kirim GET `/extra/academy/nosql-filter?filter=role%3Duser`.
2. Catat JSON dan status.
3. Di Repeater ubah nilai filter ke `$ne:user` (encode `$` bila diperlukan).
4. Pastikan host tetap localhost dan kirim satu kali.
5. Ulangi pada Secure; input operator harus ditolak.

## Bukti yang Dicatat
Filter, matched, status, header flag, mode, dan fakta bahwa evaluator adalah fixture lokal.

## Kalau Masih Bingung
Jika `$` muncul URL-encoded, itu normal. Lihat nilai decoded melalui Inspector tanpa mengubah host.
