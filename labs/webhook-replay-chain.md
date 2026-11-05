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
- Counter hanya milik sesi browser; tidak ada rekening, saldo, atau integrasi jaringan nyata.

## Persiapan Burp dan baseline

1. Gunakan KopiLab lokal dan buka endpoint melalui halaman materi.
2. Pastikan host request tetap `127.0.0.1:5000`; Intercept off.
3. Kirim request baseline sekali dari Repeater.
4. Catat status, `accepted`, `duplicate`, `creditCount`, dan event ID.
5. Simpan request yang persis sama. Hindari mengubah `amount` atau ID ketika menguji replay.

## Langkah analisis

### A. Satu event

1. Kirim body fixture dan header marker seperti contoh di bawah.
2. Pada Vulnerable, respons pertama biasanya `accepted=true`, `duplicate=false`, `creditCount=1`; belum ada flag.
3. Pada Secure, event pertama juga diterima satu kali. Ini kontrol positif bahwa jalur valid tidak diblokir seluruhnya.

### B. Replay terkontrol

1. Tanpa mengubah body, header, atau sesi, kirim request yang sama tepat satu kali lagi.
2. Bandingkan `creditCount` dan `duplicate`.
3. Vulnerable menunjukkan kenaikan counter dan flag pada replay.
4. Secure mengembalikan `409`, `accepted=false`, dan counter tetap 1.
5. Mulai sesi baru saat mengganti mode agar state pemrosesan tidak terbawa.

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

| Tahap | Vulnerable | Secure |
|---|---|---|
| Event pertama valid | diterima, count 1 | diterima, count 1 |
| Event ID sama dikirim ulang | diterima lagi, count bertambah, flag | `409`, count tetap 1 |
| Signature marker salah | `401` | `401` |
| Event fixture berubah | `400` | `400` |

Counter yang bertambah adalah indikator dampak dalam fixture. Jangan menggeneralisasi bahwa seluruh sistem webhook produksi memiliki perilaku yang sama.

## Analisis mendalam

- **Authenticity:** apakah pesan datang dari pengirim tepercaya? Fixture hanya memodelkan cabang valid/tidak valid.
- **Freshness:** apakah timestamp/nonce/event ID mencegah pesan lama dipakai ulang?
- **Idempotency:** apakah event yang telah diproses dicatat dengan unique key sebelum efek samping?
- **Atomicity:** pencatatan event dan pemberian efek harus satu transaksi agar race tidak menggandakan efek.
- **Ordering:** duplicate check saja yang terpisah dari increment masih dapat memiliki race di sistem konkuren.
- **Evidence:** bandingkan counter sebelum/sesudah satu replay; jangan kirim banyak request.
- **Scope:** simulator tidak menerima format provider nyata dan tidak membuat signature kriptografis.

## Root cause dan mitigasi

**Root cause yang dimodelkan:** event yang valid ditangani setiap kali diterima tanpa deduplikasi durable berdasarkan ID event.

**Mitigasi produksi:** validasi signature kriptografis atas raw body dan timestamp dengan toleransi waktu; rotasi/kelola secret secara aman; simpan event ID dengan unique constraint; proses deduplikasi dan efek samping secara atomik; log event tanpa membocorkan secret; tetapkan retensi replay yang sesuai.

## Troubleshooting

- `401`: pastikan header tepat `X-Training-Signature: fixture-valid`.
- `400`: body harus memakai event ID dan nominal fixture yang ditentukan.
- Counter sudah lebih dari 1 sebelum uji: mulai session browser baru, bukan mengulang sampai flag muncul.
- Secure mengembalikan `409` pada request pertama: sesi itu mungkin sudah memproses event; gunakan sesi bersih.
- Tidak ada flag pada request pertama Vulnerable: normal; lab menandai replay, bukan event valid pertama.

## Bukti dan laporan

Catat dua request identik, status, event ID, `duplicate`, nilai counter sebelum/sesudah, mode, dan hasil. Jangan memasukkan cookie.

Kesimpulan laporan harus menyebut bahwa autentikasi marker dan idempotensi adalah kontrol berbeda. Jelaskan batas simulasi dan perbaikan atomik yang diperlukan di layanan nyata.

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

1. Pastikan session baru dan Vulnerable mode.
2. Kirim event fixture sekali; catat counter 1.
3. Kirim request identik satu kali lagi.
4. Bandingkan `duplicate`, `creditCount`, dan flag.
5. Ulangi pada Secure dengan session bersih: request pertama diterima, replay mendapat `409`.
6. Uji satu kontrol negatif dengan signature marker yang salah; hasil harus `401`.

## Bukti yang Dicatat

Dua request identik, event ID, status, `accepted`, `duplicate`, counter sebelum/sesudah, mode, dan flag. Jangan salin cookie atau memperlakukan marker fixture sebagai secret nyata.

## Kalau Masih Bingung

Jika Secure memberi `409` pada request pertama, event ID sudah dipakai pada session itu. Buat sesi browser baru. Pastikan header ditulis tepat dan body memakai nilai fixture.
