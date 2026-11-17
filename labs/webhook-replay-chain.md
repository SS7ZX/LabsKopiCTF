# Practitioner: replay event pada penerima webhook simulasi

## Tingkat dan batas lab

**Tingkat:** Super Sulit / Practitioner  
**Fokus:** pemrosesan event, autentikasi pesan, replay, dan idempotensi.  
**Target:** endpoint KopiLab lokal `POST /extra/academy/webhook-replay-chain`.  
**Dampak simulasi:** menaikkan counter kredit fixture; tidak ada pembayaran atau webhook keluar.

**Penting:** `X-Training-Signature: fixture-valid` adalah marker statis yang sengaja disediakan. Ini bukan HMAC, bukan contoh signature produksi, dan bukan instruksi untuk memalsukan webhook layanan nyata. Tidak ada provider eksternal.

## Tujuan belajar

- Memisahkan autentikasi event dari pencegahan replay.
- Menguji apakah event ID yang sama memberi efek samping lebih dari sekali.
- Menjaga eksperimen terukur dengan request baseline dan satu replay.
- Memahami kenapa signature valid saja tidak menjamin pemrosesan exactly-once.

## Kontrak fixture

- Body tetap: `event_id=evt-training-01&amount=50000`.
- Header marker tetap: `X-Training-Signature: fixture-valid`.
- Mode Vulnerable memodelkan penerimaan event duplikat.
- Secure menerima event pertama, menyimpan ID secara idempotent, lalu menolak replay dengan `409`.
- State disimpan di sesi browser dan dipisahkan antara mode Vulnerable dan Secure; ini bukan ledger durable.
- `duplicate` menyatakan apakah event ID sudah ada sebelum request saat ini diproses.
- `creditCount` adalah banyaknya entri pemrosesan fixture dalam sesi, bukan nilai uang, saldo, atau jumlah unik. Jalur Vulnerable menambahkan entri setiap kali, termasuk replay; jalur Secure tidak menambah entri untuk replay yang ditolak.
- `creditedAmount` hanya menampilkan nominal fixture pada response yang diterima; tidak ada rekening, saldo, pembayaran, atau integrasi jaringan nyata.

## Persiapan Burp dan baseline

1. Gunakan KopiLab lokal dan buka endpoint melalui halaman materi.
2. Pilih mode Vulnerable di UI, pastikan indikator mode terlihat, dan pastikan host request tetap `127.0.0.1:5000`; Intercept off.
3. Di HTTP history, pilih `POST /extra/academy/webhook-replay-chain` yang baru saja dikirim browser; klik kanan dan pilih **Send to Repeater**.
4. Periksa request line, `Host`, `Content-Type`, header marker, dan body. Pertahankan host `127.0.0.1:5000`, form-urlencoded, serta nilai fixture; jangan menyalin cookie ke catatan.
5. Kirim request tanpa perubahan sebagai baseline. Catat status, `accepted`, `duplicate`, `eventId`, `creditCount`, `creditedAmount`, dan ada/tidaknya header `X-Lab-Flag`.
6. Beri nama tab/request sebagai baseline agar mudah dibandingkan. Jangan membuat event ID baru: pengujian replay harus mengirim kembali event yang identik.

## Langkah analisis

### A. Satu event

1. Pastikan body request adalah `event_id=evt-training-01&amount=50000` dan header `X-Training-Signature` bernilai `fixture-valid`.
2. Kirim satu kali. Pada kedua mode, event pertama yang valid seharusnya menghasilkan HTTP `200`, `accepted=true`, `duplicate=false`, `eventId=evt-training-01`, dan `creditCount=1`. Response sukses juga memuat `creditedAmount=50000`; event pertama tidak memiliki flag.
3. Anggap hasil ini sebagai kontrol positif: request valid memang diterima. Jika hasilnya berbeda, jangan replay dulu; periksa status dan format request.

### B. Replay terkontrol

1. Duplikasikan tab baseline di Repeater atau gunakan kembali request itu. Jangan mengedit method, path, host, header, body, atau sesi.
2. Tekan **Send** tepat satu kali lagi. Ini replay terkontrol; jangan gunakan Intruder, macro, parallel requests, atau automasi.
3. Bandingkan response kedua dengan baseline: status, `accepted`, `duplicate`, `creditCount`, dan header `X-Lab-Flag`.
4. Pada Vulnerable, response kedua seharusnya HTTP `200`, `accepted=true`, `duplicate=true`, dan `creditCount=2`; flag muncul pada header. Artinya ID yang sama dikenali sebagai pernah terlihat, tetapi tetap diproses lagi.
5. Pada Secure, request kedua seharusnya HTTP `409`, `accepted=false`, `duplicate=true`, dan `creditCount=1`; flag tidak muncul. Event dikenali sebagai duplikat dan tidak menambah hitungan.
6. Untuk perbandingan Secure, ganti mode melalui UI dan pastikan indikator Secure aktif. Mode disimpan di sesi browser, sedangkan daftar event lab memakai key terpisah untuk setiap mode; karena itu event Vulnerable tidak menjadi baseline Secure. Jika state Secure sudah pernah dipakai, buka sesi baru, aktifkan Secure lagi, dan pastikan indikatornya sebelum mengirim.

## Request Repeater

```http
POST /extra/academy/webhook-replay-chain HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded
X-Training-Signature: fixture-valid

event_id=evt-training-01&amount=50000
```

Gunakan **Send** manual satu kali untuk baseline, kemudian satu kali untuk replay. Lab ini tidak membutuhkan Intruder, Macro, extension, parallel requests, atau automasi.

## Matriks hasil dan interpretasi

| Tahap | Vulnerable | Secure | Arti yang perlu dicatat |
|---|---|---|---|
| Event pertama valid | `200`; `accepted=true`; `duplicate=false`; `creditCount=1`; tanpa flag | Sama: `200`; `accepted=true`; `duplicate=false`; `creditCount=1`; tanpa flag | Kontrol positif: fixture valid diterima sekali. |
| Event ID sama dikirim ulang | `200`; `accepted=true`; `duplicate=true`; `creditCount=2`; flag ada | `409`; `accepted=false`; `duplicate=true`; `creditCount=1`; flag tidak ada | `duplicate` berubah ke true di kedua mode; hanya Vulnerable yang memproses ulang dan menaikkan count. |
| Header marker salah | `401`; tidak ada count baru | `401`; tidak ada count baru | Validasi marker gagal sebelum state event diubah. |
| Event ID atau nominal bukan fixture | `400`; tidak ada count baru | `400`; tidak ada count baru | Request tidak memenuhi kontrak input lab. |

`duplicate=true` tidak berarti request kedua pasti ditolak; lihat `accepted` dan status untuk keputusan itu. `creditCount` menghitung entri pemrosesan dalam sesi: karena Vulnerable menambahkan ID yang sama saat replay, count naik dari 1 menjadi 2. Ini bukan penjumlahan nominal `50000`, bukan saldo pengguna, dan bukan bukti transaksi uang sungguhan.

Counter yang bertambah adalah indikator dampak dalam fixture. Jangan menggeneralisasi bahwa seluruh sistem webhook produksi memiliki perilaku yang sama.

## Analisis mendalam

- **Authenticity:** apakah pesan datang dari pengirim tepercaya? Fixture hanya memodelkan cabang valid/tidak valid.
- **Freshness:** apakah timestamp/nonce/event ID mencegah pesan lama dipakai ulang?
- **Idempotency:** apakah event yang telah diproses dicatat dengan unique key sebelum efek samping?
- **Atomicity:** pencatatan event dan pemberian efek harus satu transaksi agar race tidak menggandakan efek.
- **Ordering:** duplicate check saja yang terpisah dari increment masih dapat memiliki race di sistem konkuren.
- **Arti response:** `duplicate` menjawab apakah ID pernah terlihat sebelumnya; `accepted` dan status menjawab apakah request saat ini diterima; `creditCount` mengukur jumlah pemrosesan fixture yang tercatat pada sesi.
- **Evidence:** baseline seharusnya count 1; satu replay Vulnerable menghasilkan count 2, sedangkan Secure tetap 1 dengan status `409`. Jangan kirim banyak request.
- **Kontrol negatif:** marker salah harus menghasilkan `401`, dan event/nominal yang tidak cocok harus menghasilkan `400`; keduanya tidak boleh mengubah state.
- **Scope:** simulator tidak menerima format provider nyata dan tidak membuat signature kriptografis.

## Root cause dan mitigasi

**Root cause yang dimodelkan:** event yang valid ditangani setiap kali diterima tanpa deduplikasi durable berdasarkan ID event.

**Mitigasi produksi:** validasi signature kriptografis atas raw body dan timestamp dengan toleransi waktu; rotasi/kelola secret secara aman; simpan event ID dengan unique constraint; proses deduplikasi dan efek samping secara atomik; log event tanpa membocorkan secret; tetapkan retensi replay yang sesuai.

## Troubleshooting

- `401`: pastikan header tepat `X-Training-Signature: fixture-valid`.
- `400`: body harus memakai event ID dan nominal fixture yang ditentukan.
- Request pertama sudah menunjukkan `duplicate=true` atau count lebih dari 1: sesi mode itu pernah memakai event; mulai sesi browser baru dan jangan mengirim request tambahan untuk mengejar flag. Pilih kembali mode yang ingin diuji setelah sesi baru dibuat.
- Secure mengembalikan `409` pada request pertama: sesi Secure itu mungkin sudah memproses event; mulai sesi bersih, aktifkan Secure lagi melalui UI, pastikan indikatornya, lalu ulangi baseline.
- Vulnerable memberi `200` pada replay tetapi `duplicate=false`: bandingkan event ID dengan baseline. Replay harus identik, bukan event baru.
- `duplicate=true` tetapi Secure tidak menaikkan count: ini hasil yang diharapkan; `accepted=false` dan status `409` menunjukkan duplikat ditolak.
- Tidak ada flag pada request pertama Vulnerable: normal; lab menandai replay, bukan event valid pertama.

## Bukti dan laporan

Catat kedua request identik (method/path dan nama field saja), status, event ID fixture, `accepted`, `duplicate`, `creditCount` sebelum/sesudah, `creditedAmount`, mode, serta ada/tidaknya flag. Label sesi secukupnya; jangan memasukkan cookie atau token.

Kesimpulan laporan harus menjawab secara terpisah: apakah marker diterima, apakah event ID dikenali sebagai duplikat, apakah request duplikat diterima, dan apakah counter berubah. Jelaskan bahwa marker fixture bukan signature kriptografis dan counter bukan saldo. Untuk mitigasi nyata, sebutkan verifikasi signature yang benar serta deduplikasi durable dan atomik.

## Tujuan

Menganalisis secara terpisah apakah event diterima dan apakah event yang sama dapat memberi efek berulang. Semua eksperimen hanya mengubah state fixture lokal.

## Konsep

Signature memeriksa asal/integritas pesan; idempotensi mencegah duplikat memicu efek samping berulang. Sistem perlu keduanya. Marker fixture di lab tidak melakukan kriptografi.

## Hint 1

Kirim event fixture tepat satu kali dan catat `creditCount`. Respons pertama belum harus memunculkan flag.

## Hint 2

Replay request identik, bukan event baru. Bandingkan event ID, `duplicate`, dan counter.

## Hint 3

Secure menerima event pertama dan menjawab `409` untuk ID yang sama berikutnya tanpa menaikkan counter.

## Solusi

Kirim dua POST identik dengan `event_id=evt-training-01`, `amount=50000`, dan header fixture. Vulnerable menambah counter saat replay; Secure memproses event ID satu kali.

## Akar Masalah

Penerima tidak melakukan deduplikasi durable/atomik berdasarkan ID event sebelum efek samping dijalankan.

## Perbaikan

Validasi signature atas raw payload dan timestamp, simpan unique event ID, dan lakukan deduplikasi serta efek samping dalam satu transaksi atomik.

## Contoh Rentan

```python
if signature_marker_is_valid(request):
    credit(amount)
```

Tidak ada pencatatan bahwa event yang sama telah diproses.

## Contoh Aman

```python
with transaction():
    if not insert_event_id_if_new(event_id):
        reject_duplicate()
    credit(amount)
```

Unique constraint dan transaksi menghindari pemrosesan ganda.

## Langkah Latihan

1. Jalankan KopiLab sendiri dan buka halaman lab pada `http://127.0.0.1:5000`. Pastikan request tidak diarahkan ke host lain.
2. Buka browser dari Burp (**Proxy → Open browser**), pastikan **Intercept is off**, lalu buka endpoint lab. Di **Proxy → HTTP history**, temukan `POST /extra/academy/webhook-replay-chain`.
3. Kirim request itu ke Repeater. Sebelum mengirim, cek `Host: 127.0.0.1:5000`, `Content-Type: application/x-www-form-urlencoded`, `X-Training-Signature: fixture-valid`, dan body `event_id=evt-training-01&amount=50000`.
4. Atur mode **Vulnerable** dan mulai dengan sesi browser bersih. Di Repeater, kirim request baseline sekali. Harapkan status `200`, `accepted=true`, `duplicate=false`, `eventId=evt-training-01`, `creditCount=1`, `creditedAmount=50000`, dan tidak ada `X-Lab-Flag`.
5. Simpan baseline tanpa mengedit field. Duplikasikan tab/request atau kirim ulang salinan yang sama—jangan mengubah satu karakter pun dan gunakan sesi yang sama.
6. Kirim replay tepat sekali. Harapkan status `200`, `accepted=true`, `duplicate=true`, `creditCount=2`, dan header `X-Lab-Flag`. Bandingkan langsung dengan baseline: `duplicate` berubah `false → true` dan count `1 → 2`.
7. Ganti mode ke **Secure** melalui UI dan pastikan indikator mode berubah. Gunakan sesi yang sama agar pemilihan mode tetap aktif; event list Secure terpisah dari event list Vulnerable. Jika Secure pernah diuji sebelumnya, buat sesi baru lalu aktifkan Secure lagi. Kirim fixture sekali sebagai kontrol: harapkan `200`, `accepted=true`, `duplicate=false`, dan `creditCount=1`.
8. Replay request Secure itu tepat sekali tanpa mengedit request. Harapkan status `409`, `accepted=false`, `duplicate=true`, `creditCount=1`, dan tidak ada flag. Penolakan duplikat yang tidak menaikkan count adalah perilaku aman yang diharapkan.
9. Sebagai kontrol negatif opsional, mulai sesi bersih, pilih mode yang ingin diuji, dan pastikan indikator mode. Kirim request dengan marker yang salah sekali (`401`), lalu request dengan event/nominal non-fixture sekali (`400`). Setelah itu kirim fixture benar: ia tetap harus menjadi event pertama (`duplicate=false`, count 1), membuktikan input ditolak tidak mengonsumsi event.
10. Catat output dan nama field saja. Jangan catat cookie; jangan mengulang POST setelah hasil yang diharapkan terlihat.

## Bukti yang Dicatat

Untuk setiap mode, catat pasangan baseline/replay yang identik: method/path, status, `eventId`, `accepted`, `duplicate`, `creditCount`, `creditedAmount` jika ada, dan header flag. Jelaskan bahwa replay Vulnerable menghasilkan `duplicate=true` sekaligus `accepted=true` dan count 2, sedangkan replay Secure menghasilkan `duplicate=true`, `accepted=false`, status 409, dan count tetap 1. Catat juga kontrol negatif 401/400 bila dilakukan. Jangan salin cookie atau memperlakukan marker fixture sebagai secret nyata.

## Kalau Masih Bingung

Untuk request pertama, gunakan satu request fixture persis seperti ini: `POST /extra/academy/webhook-replay-chain` ke `127.0.0.1:5000`, `Content-Type: application/x-www-form-urlencoded`, header `X-Training-Signature: fixture-valid`, body `event_id=evt-training-01&amount=50000`. Kirim sekali untuk baseline, lalu kirim salinan identik sekali untuk replay. Jika Secure memberi `409` pada request pertama, event ID sudah dipakai dalam sesi Secure itu—buat sesi browser baru. `duplicate` adalah indikator riwayat ID; `creditCount` adalah jumlah pemrosesan fixture, bukan nilai uang.
