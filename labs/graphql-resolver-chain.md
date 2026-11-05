# Practitioner: otorisasi resolver bersarang dan alias API

## Tingkat dan batas lab

**Tingkat:** Super Sulit / Practitioner  
**Fokus:** otorisasi per objek pada relasi API, batas root/nested resolver, dan alias field.  
**Target:** `POST /extra/academy/graphql-resolver-chain` di KopiLab lokal.  
**Dampak simulasi:** mengembalikan satu invoice sintetis; tidak terhubung ke GraphQL server atau API lain.

Endpoint ini **bukan parser GraphQL sungguhan**. Ia adalah evaluator fixture dengan tiga field form (`viewer_id`, `invoice_id`, `alias`) untuk mengisolasi kesalahan otorisasi yang sering muncul pada API bertingkat. Tidak ada query parser, introspection, batching, atau layanan remote.

## Tujuan belajar

- Membedakan otorisasi objek root dari otorisasi setiap objek nested.
- Menyadari bahwa alias/nama field tidak boleh menjadi kontrol akses.
- Menguji ID dari relasi berbeda dengan principal sesi tetap.
- Menyusun request minimal untuk mengisolasi satu batas otorisasi.

## Model fixture

- Login sebagai Budi, principal seed `uid=2`; invoice milik Budi adalah `invoice_id=2`.
- `invoice_id=1` adalah record latihan milik admin.
- `viewer_id` mengidentifikasi root object yang diminta, bukan bukti hak akses atas invoice.
- `alias=ledger` atau `alias=invoice` memilih nama field pada respons saja.
- Vulnerable memeriksa root viewer tetapi melewatkan pemeriksaan kepemilikan invoice nested.
- Secure mengikat invoice yang diambil ke principal sesi, bukan ID yang dikirim klien.

## Persiapan Burp

1. Login sebagai Budi dan buka halaman lab pada KopiLab lokal.
2. Pastikan target hanya loopback dan Intercept off.
3. Tangkap POST ke endpoint evaluator dan kirim ke Repeater.
4. Pastikan `Content-Type` adalah `application/x-www-form-urlencoded`.
5. Pertahankan `viewer_id=2` sepanjang tes; hanya ubah `invoice_id` di langkah eksploit agar root authorization tetap menjadi kontrol.
6. Jangan menyimpulkan implementasi GraphQL umum dari fixture sederhana ini.

## Langkah demi langkah

### A. Baseline: relasi sah

1. Kirim `viewer_id=2&invoice_id=2&alias=ledger`.
2. Catat status, objek viewer, key alias, invoice ID, reference, dan total.
3. Respons harus berisi `BUDI-TRAINING-INVOICE`, tanpa flag.
4. Ganti hanya `alias=invoice`; pastikan alias mengubah bentuk nama field tetapi bukan hak akses.

### B. Uji objek nested

1. Kembali ke alias baseline `ledger`.
2. Pertahankan `viewer_id=2`, lalu ubah hanya `invoice_id=1`.
3. Pada Vulnerable, periksa apakah respons menyertakan `ADMIN-TRAINING-INVOICE`, total fixture, dan flag.
4. Bandingkan seluruh body dengan baseline. Root viewer yang tetap milik Budi menegaskan bahwa perubahan dampak datang dari objek nested.
5. Pada Secure, ulangi dari sesi bersih. Invoice asing harus ditolak (404), tanpa reference atau total.

### C. Uji asumsi dan kontrol negatif

1. Coba `viewer_id` yang bukan principal sesi sementara `invoice_id=2`; request harus ditolak.
2. Coba alias yang tidak terdaftar; harus mendapat `400`, tanpa mengubah otorisasi.
3. Jangan melakukan enumerasi ID otomatis; dua ID fixture sudah cukup untuk membuktikan hipotesis.
4. Catat apakah respons menyamarkan “tidak ada” dan “tidak berhak”; lab menetapkan keluaran lokal yang stabil agar dapat diuji.

## Request Repeater

Baseline milik Budi:

```http
POST /extra/academy/graphql-resolver-chain HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded

viewer_id=2&invoice_id=2&alias=ledger
```

Eksperimen objek nested dengan principal root tetap:

```http
POST /extra/academy/graphql-resolver-chain HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded

viewer_id=2&invoice_id=1&alias=ledger
```

Jika pengguna seed bukan Budi/ID 2 pada instalasi lokalmu, login melalui UI dan gunakan principal fixture yang ditetapkan materi aplikasi. Biarkan Burp mempertahankan cookie sesi lokal dan menghitung panjang body.

## Analisis response

- **Root check:** `viewer_id` cocok dengan pengguna sesi.
- **Nested check:** `invoice_id` harus diotorisasi secara terpisah, bukan diwarisi dari root.
- **Alias:** label respons bukan identitas atau izin. Mengganti `ledger` menjadi `invoice` tidak semestinya membuka akses.
- **Field-level:** reference dan total adalah data yang dilindungi; ukur dampak pada field yang benar-benar dikembalikan.
- **Status:** pada Secure, `404` tidak boleh disertai data sensitif. Baca body, bukan status saja.
- **Flag:** bukti lab hanya muncul jika invoice foreign dikembalikan dalam Vulnerable.
- **State/sesi:** pengguna harus login agar principal tidak `None`; respons `401` berarti prasyarat belum siap.

## Root cause dan perbaikan

**Root cause:** resolver anak mengambil objek berdasarkan ID input tanpa pemeriksaan owner/tenant yang terikat ke principal terautentikasi. Pemeriksaan root saja tidak transitif.

**Mitigasi:** otorisasi setiap resolver/field sensitif; query objek melalui relasi yang sudah difilter berdasarkan principal; hindari mempercayai `viewer_id` dari klien; uji kombinasi root sah/nested asing; terapkan kebijakan konsisten pada alias dan fragment.

## Jalur Secure dan troubleshooting

- `401`: login ulang ke KopiLab; pertahankan sesi browser yang sama di Repeater.
- `403` saat root ID diubah: kontrol viewer bekerja; untuk latihan nested, biarkan `viewer_id=2`.
- `404` untuk invoice 1 pada Secure: hasil yang diharapkan.
- Baseline invoice 2 tidak muncul: pastikan akun dan ID fixture benar.
- Alias tidak dikenal: gunakan `ledger` atau `invoice`.
- Flag tidak muncul pada perubahan alias saja: normal; alias bukan temuan tanpa akses data.

## Bukti dan latihan laporan

Catat pasangan request baseline/foreign dengan `viewer_id` sama, principal sesi (tanpa cookie), invoice ID, field alias, reference/total yang muncul, status, mode, dan flag.

Dalam laporan, jelaskan mengapa “root object sudah authorized” tidak membuktikan relasi turunannya juga aman. Sertakan rekomendasi per-resolver dan satu regression test yang memastikan principal Budi tidak pernah menerima invoice 1.

## Analisis Mendalam

- Pertahankan `viewer_id` yang cocok dengan sesi agar pengujian mengisolasi resolver invoice.
- Ubah satu `invoice_id` saja dan bandingkan reference serta total yang dikembalikan.
- Ganti alias sebagai kontrol negatif: alias bukan otorisasi dan tidak boleh mengubah izin.
- Respons Secure tidak boleh memuat field sensitif meskipun statusnya error.
- Simulasi memakai resolver fixture terbatas, bukan server GraphQL atau parser query sungguhan.

## Tujuan

Membuktikan bahwa setiap objek/relasi yang dimuat oleh API harus memiliki pemeriksaan izin sendiri, walaupun objek root sudah cocok dengan pengguna.

## Konsep

Dalam API bertingkat, satu resolver dapat mengotorisasi viewer sementara resolver anak mengambil invoice berdasarkan ID klien. Hak akses tidak otomatis diwariskan melewati relasi. Alias hanya mengubah nama field respons.

## Hint 1

Login sebagai Budi dan mulai dengan `viewer_id=2&invoice_id=2`.

## Hint 2

Pertahankan viewer dan alias; ubah hanya invoice ID ke 1.

## Hint 3

Bandingkan field `reference` dan `total`, bukan sekadar status. Secure harus menolak invoice foreign meskipun viewer root sah.

## Solusi

POST `viewer_id=2&invoice_id=1&alias=ledger` dalam Vulnerable mengembalikan invoice admin fixture dan flag. Secure mengembalikan 404 tanpa data.

## Akar Masalah

Resolver nested memakai ID dari klien tanpa mengikat record invoice ke principal sesi. Otorisasi root saja tidak mencukupi.

## Perbaikan

Otorisasi setiap resolver dan field sensitif; lakukan lookup invoice melalui query yang dibatasi owner/tenant principal; jangan mempercayai viewer ID dari klien.

## Contoh Rentan

```python
viewer = get_viewer(session_user)
return get_invoice(request.form["invoice_id"])
```

Root aman, tetapi invoice tidak dibatasi menurut pengguna.

## Contoh Aman

```python
viewer = get_viewer(session_user)
return invoice_owned_by(viewer, request.form["invoice_id"])
```

Relasi dipilih dari scope yang berhak diakses principal.

## Langkah Latihan

1. Login sebagai Budi dan kirim invoice ID 2 dengan alias `ledger`.
2. Catat reference, total, dan status baseline.
3. Ganti alias saja ke `invoice`, lalu pastikan perubahan nama tidak memberi data baru.
4. Kembalikan alias ke `ledger` dan ubah hanya invoice ID ke 1.
5. Periksa data dan flag pada Vulnerable.
6. Ulangi di Secure; invoice asing harus 404 tanpa reference/total.
7. Uji ID viewer yang salah sebagai kontrol negatif, lalu kembalikan viewer ke nilai sesi.

## Bukti yang Dicatat

Principal sesi tanpa cookie, viewer ID, invoice ID, alias, reference/total yang keluar, status, mode, serta flag.

## Kalau Masih Bingung

Jika menerima 401, login dulu sebagai Budi. Jangan ubah viewer dan invoice pada eksperimen yang sama; untuk menguji nested resolver, viewer harus tetap 2.
