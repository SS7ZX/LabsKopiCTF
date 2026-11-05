# Template injection pada renderer mainan

## Tujuan
Membedakan teks template yang tidak dipercaya dari template yang diproses oleh server.

## Konsep
Server-side template injection muncul bila input pengguna disisipkan ke template lalu dievaluasi. Endpoint ini sengaja hanya mengenali satu ekspresi tetap `{{7*7}}`; ia tidak menjalankan Jinja, Python, ekspresi arbitrer, atau akses object.

## Hint 1
Baseline memakai nama biasa seperti `Budi`.

## Hint 2
Bandingkan output untuk marker tetap `{{7*7}}`.

## Hint 3
Pada Secure, marker harus tampil literal sebagai teks.

## Solusi
GET `name={{7*7}}`. Vulnerable mengubah fixture menjadi `49`; Secure mengembalikan teks literal.

## Akar Masalah
Nilai input dalam simulasi rentan diperlakukan sebagai template, bukan data.

## Perbaikan
Gunakan template statis dengan variabel yang di-escape; jangan mengevaluasi template yang dirakit dari input pengguna.

## Contoh Rentan
Mengevaluasi teks pengguna sebagai ekspresi template.

## Contoh Aman
Render template tepercaya dan berikan input sebagai variabel teks.

## Analisis Mendalam
- Evaluator hanya perbandingan string tetap; tidak ada `eval` atau engine template yang dipanggil.
- Catat input `name`, field `rendered`, engine fixture, status, dan flag.
- Hasil `49` menandakan jalur demonstrasi rentan aktif.
- Secure tidak mengevaluasi input dan menjaga teks literal.
- Jangan mencoba ekspresi lain; scope lab hanya marker yang ditetapkan.

## Langkah Latihan
1. Kirim GET `/extra/academy/ssti-toy?name=Budi` sebagai baseline.
2. Kirim request ke Repeater.
3. Ubah hanya `name` menjadi `{{7*7}}` (URL-encode kurung kurawal jika Burp meminta).
4. Kirim ke host lokal dan catat hasil.
5. Ulangi dengan Secure; hasil harus literal, bukan `49`.

## Bukti yang Dicatat
Input fixture, output rendered, status, engine note, dan mode.

## Kalau Masih Bingung
Pakai nilai persis `{{7*7}}`; endpoint tidak menjalankan ekspresi lain.
