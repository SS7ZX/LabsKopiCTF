# Practitioner: manipulasi quote pada settlement bertahap

## Tingkat dan batas lab

**Tingkat:** Super Sulit / Practitioner  
**Fokus:** state bisnis, harga dari sisi server, ikatan quote ke sesi, dan konsumsi transaksi satu kali.  
**Target:** `POST /extra/academy/checkout-settlement-chain` pada KopiLab lokal saja.  
**Dampak simulasi:** mencatat hasil settlement fixture; tidak membuat order atau memindahkan saldo sungguhan.

## Tujuan belajar

- Menelusuri perbedaan nilai yang ditampilkan server dan nilai final yang dikirim klien.
- Menentukan state prasyarat dan urutan request yang diperlukan.
- Membedakan validasi parameter dari validasi invariant bisnis.
- Menguji mismatch, replay, dan perilaku mode Secure tanpa mengirim transaksi nyata.

## Kontrak aplikasi yang seharusnya

1. `action=quote` membuat quote dengan ID dan total server `125000` IDR.
2. `action=confirm` harus membawa ID quote yang aktif pada sesi yang sama.
3. Total yang dikonfirmasi harus sama dengan total server.
4. Quote hanya boleh dikonsumsi sekali.
5. Request tanpa quote, quote sesi lain, mismatch total, atau replay tidak boleh mengubah state sukses.

Lab tidak memakai database pembayaran. State hanya fixture di sesi KopiLab.

## Persiapan dan baseline Burp

1. Login ke KopiLab lokal jika UI meminta akun, lalu buka materi lab.
2. Proxy browser melalui Burp, pastikan target adalah `127.0.0.1:5000`, dan Intercept off.
3. Tangkap POST ke endpoint settlement dan kirim ke Repeater.
4. Gunakan tab/riwayat yang sama untuk urutan quote → confirm; setiap eksperimen mode baru sebaiknya dimulai dari sesi bersih.
5. Catat status, JSON, `quoteId`, `total`, dan `settled`; jangan menilai hanya dari respons HTTP.

## Praktikum bertahap

### A. Baseline yang valid

1. Kirim `action=quote`.
2. Pastikan respons menyebut `quoted=true`, `quoteId=quote-training-001`, `total=125000`, `currency=IDR`.
3. Kirim confirm dengan `quote_id=quote-training-001&total=125000`.
4. Catat `settled`, `submittedTotal`, `serverTotal`, `underpaid`, dan status.
5. Kirim ulang confirm yang sama. Quote seharusnya tidak dapat dipakai dua kali.

### B. Uji invariant harga

1. Mulai sesi/quote baru di mode Vulnerable.
2. Ambil quote dan simpan ID hasil respons.
3. Kirim confirm dengan ID yang sama tetapi `total=1`.
4. Bandingkan `submittedTotal` dengan `serverTotal`; periksa `underpaid` dan flag.
5. Jangan mengubah ID quote, jumlah, dan urutan sekaligus. Isolasi variabel membuat sebab hasil jelas.
6. Ulangi di Secure pada state bersih: mismatch harus mendapat `400` dan tidak boleh menghasilkan settlement.
7. Pada quote Secure yang sama, kirim total tepat `125000`; kemudian replay. Konfirmasi pertama valid, replay harus mendapat `409`.

## Request untuk Repeater

Kirim quote:

```http
POST /extra/academy/checkout-settlement-chain HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded

action=quote
```

Uji mismatch setelah respons quote:

```http
POST /extra/academy/checkout-settlement-chain HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded

action=confirm&quote_id=quote-training-001&total=1
```

Untuk baseline yang benar, ubah hanya `total=125000`. Biarkan Burp mengurus `Content-Length` dan pertahankan cookie sesi lokal.

## Matriks hasil

| Skenario | Vulnerable | Secure |
|---|---|---|
| Confirm sebelum quote | `409`, quote tidak ditemukan | `409`, quote tidak ditemukan |
| Quote lalu total `1` | settlement fixture diterima; flag | `400`, tidak settled |
| Quote lalu total `125000` | diterima | diterima |
| Replay quote yang sudah digunakan | `409` | `409` |

Jika hasil menyimpang, pastikan mode, sesi, dan urutan request tercatat. Respons flag pada mismatched total membuktikan hasil lab; bukan bukti transaksi sungguhan.

## Analisis mendalam

- **Source of truth:** harga harus dihitung/dibaca server, bukan dipercaya dari body confirm.
- **State binding:** quote harus terikat pada principal/cart dan sesi yang benar.
- **Invariant:** total konfirmasi sama dengan total quote yang belum digunakan.
- **Replay protection:** perubahan state harus atomik; dua confirm bersamaan tidak boleh sama-sama sukses di sistem nyata.
- **Error semantics:** `400` berarti isi tak valid; `409` menunjukkan conflict state. Jangan menganggap kode status saja sebagai bukti dampak.
- **Eksperimen kontrol:** baseline penuh penting untuk membedakan bug otorisasi, state kedaluwarsa, dan manipulasi nominal.
- **Scope:** simulator tidak menjalankan payment gateway, tidak menyentuh saldo, dan tidak membuat order.

## Root cause, mitigasi, dan troubleshooting

**Root cause:** finalisasi menerima nilai total yang dipilih klien tanpa menghitung ulang invariant quote di server.

**Mitigasi:** simpan quote server-side; ikat ke pengguna, cart, mata uang, dan masa berlaku; hitung ulang total saat commit; gunakan transaksi database atomik dan idempotency key unik; jangan pernah menyelesaikan pembayaran hanya karena klien mengirim `settled=true`.

- `409` pada confirm pertama: quote belum dibuat pada sesi itu atau ID salah.
- `409` pada confirm kedua: quote memang sudah dikonsumsi; buat quote baru.
- `400` di Secure saat total `1`: hasil yang diharapkan.
- Pastikan Repeater memakai cookie sesi yang sama dan body form-urlencoded.

## Bukti dan latihan laporan

Lampirkan urutan request quote/confirm/replay, nilai server dan klien, status, flag, serta mode. Redaksi cookie.

Dalam laporan, pisahkan **integritas harga**, **ikatan quote**, dan **idempotensi** menjadi tiga kontrol. Sebutkan hasil yang diuji untuk masing-masing; jangan menyatukan semuanya menjadi “checkout rentan”.

## Tujuan

Menemukan ketidaksesuaian antara quote server dan settlement yang diminta klien, sambil membuktikan urutan state dan perlindungan replay secara terpisah.

## Konsep

Total yang tampil/ditandatangani server adalah invariant bisnis. Handler finalisasi harus memvalidasi quote aktif, pemilik, nominal, mata uang, dan status konsumsi; validasi angka semata tidak cukup.

## Hint 1

Kirim `action=quote` terlebih dahulu. ID quote dan nominal server ada di JSON response.

## Hint 2

Kirim confirm yang benar sebagai kontrol. Setelah itu lihat apa yang terjadi jika quote sama dikirim ulang.

## Hint 3

Ambil quote baru, pertahankan `quote_id`, dan ubah hanya `total` menjadi `1`. Secure menolak mismatch sebelum settlement.

## Solusi

Vulnerable menerima confirm yang ID quote-nya benar meski total dikirim menjadi 1. Flag muncul untuk mismatch itu. Secure membandingkan dengan total tersimpan server-side; quote yang benar hanya sukses sekali.

## Akar Masalah

Handler finalisasi mempercayai field `total` pada request alih-alih menghitung ulang/menegakkan nilai quote server.

## Perbaikan

Simpan quote server-side dan ikat ke sesi/cart; hitung ulang total saat commit; gunakan transaksi atomik dan one-time/idempotency token; tolak mismatch dan replay.

## Contoh Rentan

```python
settle(total=int(request.form["total"]))
```

Nilai klien langsung menjadi sumber kebenaran.

## Contoh Aman

```python
quote = load_unspent_quote_for(current_user, quote_id)
if submitted_total != quote.total:
    reject()
settle_server_amount(quote.total)
consume_quote_atomically(quote)
```

Nominal berasal dari quote tepercaya dan status konsumsi diperbarui bersama settlement.

## Langkah Latihan

1. Minta quote dan catat ID serta total.
2. Confirm total yang benar, lalu coba replay sebagai kontrol.
3. Mulai state Vulnerable baru dan minta quote baru.
4. Confirm ID yang sama dengan `total=1`; catat `underpaid` dan flag.
5. Aktifkan Secure pada state bersih dan ulangi mismatch; respons harus `400`.
6. Confirm total yang benar sekali, lalu replay dan pastikan respons `409`.

## Bukti yang Dicatat

Urutan quote/confirm/replay, quote ID, nominal server dan klien, `underpaid`, `settled`, status, mode, dan flag. Jangan sertakan cookie.

## Kalau Masih Bingung

`409` pada confirm pertama biasanya berarti quote belum dibuat pada sesi itu atau ID salah. `400` untuk total 1 di Secure adalah hasil yang diharapkan. Minta quote baru setelah quote dipakai.
