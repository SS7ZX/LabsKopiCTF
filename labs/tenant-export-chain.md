# Practitioner: rantai otorisasi ekspor lintas-tenant

## Tingkat dan batas lab

**Tingkat:** Super Sulit / Practitioner  
**Fokus:** enumerasi resource, otorisasi tenant, kepemilikan job, dan pemeriksaan ulang saat unduh.  
**Target:** hanya `http://127.0.0.1:5000/extra/academy/tenant-export-chain`.  
**Dampak simulasi:** membaca tiga record sintetis; tidak ada file ekspor sungguhan yang dibuat.

Ini skenario orisinal untuk latihan lokal. Endpoint memodelkan API job ekspor; bukan layanan cloud, storage, atau API pihak ketiga.

## Tujuan belajar

- Membedakan autentikasi pengguna dari otorisasi tenant.
- Mengikuti resource ID melintasi beberapa endpoint/state, bukan menguji satu request terisolasi.
- Menguji pemeriksaan akses saat membuat job **dan** saat mengambil hasilnya.
- Menghubungkan observasi awal, hipotesis, eksperimen terkontrol, bukti dampak, dan perbaikan.

## Model aplikasi

- Login sebagai akun latihan **Budi** (di seed lokal, `uid=2`), yang hanya memiliki `tenant-campus`.
- Directory demo juga menampilkan `tenant-roastery`. Keberadaan ID di respons bukan bukti akses.
- `action=list` menampilkan fixture directory.
- `action=create&tenant_id=...` membuat ID ekspor deterministik, misalnya `export-tenant-roastery`.
- `action=download&export_id=...` mengambil record fiktif untuk job yang dibuat pada sesi browser saat ini.
- Flag hanya diberikan jika record tenant lain benar-benar dikembalikan dalam Vulnerable mode.
- Secure memeriksa tenant pada kedua tahap. Jangan menafsirkan status `201` saja sebagai bukti kebocoran.

## Persiapan Burp

1. Jalankan KopiLab di loopback dan login sebagai Budi.
2. Pastikan browser/proxy Burp hanya diarahkan ke host lokal. Jangan mengubah target ke domain lain.
3. Biarkan Intercept **off**, buka lab sekali, lalu cari request `/extra/academy/tenant-export-chain` di HTTP history.
4. Klik kanan request, pilih **Send to Repeater**. Pastikan cookie sesi masih milik browser latihan; jangan menyalin atau membagikan nilainya.
5. Untuk eksperimen stateful, kirim request berurutan pada tab Repeater yang sama agar sesi tetap konsisten.
6. Simpan baseline dengan nama yang jelas, misalnya `01-list`, `02-own-create`, `03-own-download`.

## Urutan praktikum terukur

### A. Pahami baseline dan state

1. Ulangi request directory dengan body `action=list`.
2. Catat principal, dua tenant yang tercantum, status HTTP, dan bahwa respons menyebut directory sebagai fixture.
3. Buat ekspor milik sendiri dengan `action=create&tenant_id=tenant-campus`.
4. Catat `exportId`. Jangan mengubah tenant dan ID sekaligus; satu variabel per eksperimen.
5. Unduh `exportId` tersebut memakai `action=download&export_id=export-tenant-campus`.
6. Konfirmasi baseline hanya berisi `TRAINING-RECORD-*`, tenant-campus, dan tidak ada flag.

### B. Susun hipotesis

1. Hipotesis yang diuji: server memeriksa bahwa pengguna sudah login, tetapi mungkin tidak mengikat tenant yang diminta kepada pengguna itu.
2. Prediksi yang dapat dibantah: job untuk `tenant-roastery` mungkin berhasil dibuat. Ini belum membuktikan kebocoran record.
3. Kriteria dampak: tahap download harus mengembalikan record tenant-roastery dan flag dalam mode Vulnerable.
4. Kontrol: gunakan sesi Budi yang sama dan ubah **hanya** `tenant_id` pada request create.

### C. Uji jalur lintas-tenant

1. Ganti body create menjadi `action=create&tenant_id=tenant-roastery`.
2. Bandingkan status, `tenantId`, `owner`, dan ID job terhadap baseline milik sendiri.
3. Jika job dibuat, catat ID yang benar-benar dikembalikan; jangan menebaknya atau melakukan enumerasi otomatis.
4. Pada request terpisah, kirim `action=download&export_id=export-tenant-roastery`.
5. Periksa `tenantId`, `recordCount`, isi record fixture, dan `X-Lab-Flag`.
6. Ulangi create/download pada Secure menggunakan sesi bersih. Pembuatan tenant asing harus ditolak; unduhan ID asing juga harus tidak mengembalikan data.

## Request Repeater yang bisa disalin

Ganti request yang ada di Repeater agar cookie sesi lokal tetap terjaga. Biarkan Burp menghitung `Content-Length`.

```http
POST /extra/academy/tenant-export-chain HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded

action=create&tenant_id=tenant-roastery
```

```http
POST /extra/academy/tenant-export-chain HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded

action=download&export_id=export-tenant-roastery
```

### Bentuk respons yang diharapkan

Create rentan dapat menghasilkan `201 Created` dan `exportId`. Download rentan menghasilkan record sintetis dan flag. Respons Secure untuk create tenant asing adalah `403`; respons download yang tidak berhak adalah `404` tanpa record atau flag.

Respons `200`/`201` bukan bukti final. Bukti utama adalah tenant pemilik objek yang dikembalikan pada tahap terakhir.

## Analisis mendalam

- **Authentication:** apakah sesi Budi dikenali?
- **Authorization:** apakah Budi boleh membuat ekspor untuk tenant-roastery?
- **Object ownership:** siapa pemilik job, dan tenant mana yang datanya terkandung di dalamnya?
- **Time-of-check/time-of-use:** apakah keputusan saat create diulang pada download?
- **Identifier:** ID yang dapat ditebak atau terlihat bukan kontrol akses.
- **State:** job terikat ke sesi lokal; request di sesi baru tidak harus mengenali job yang sama.
- **Bukti:** respons download dan flag lebih kuat daripada pesan sukses create.
- **Batas inferensi:** simulasi ini tidak membuktikan perilaku object storage/API cloud nyata.

## Akar masalah dan mitigasi

**Akar masalah yang dimodelkan:** endpoint job mempercayai tenant dari input klien dan/atau endpoint unduh hanya memeriksa bahwa ID job ada.

**Mitigasi:** derive daftar tenant dari principal terautentikasi; simpan owner/tenant pada record job di server; cek otorisasi pada create, status, dan download; gunakan respons generik untuk ID tak berhak; uji kasus lintas-tenant otomatis.

## Jalur Secure dan troubleshooting

- Mulai dari sesi baru setelah mengganti mode agar job Vulnerable yang tersimpan tidak mengacaukan hasil.
- Budi harus login; tanpa login, `401` menunjukkan prasyarat autentikasi belum terpenuhi.
- Jika create milik sendiri berhasil tetapi foreign `403`, Secure bekerja sesuai desain.
- Jika download memberi `404`, periksa ejaan `export_id` dan pastikan job dibuat pada sesi yang sama.
- Flag hanya muncul pada tahap download yang benar-benar mengembalikan data asing.
- Jangan mengirim request ke host selain `127.0.0.1`.

## Bukti dan latihan lanjutan

Catat mode, principal (tanpa cookie), tenant, action, ID job, status, `recordCount`, dan apakah flag muncul. Bandingkan empat request baseline/eksperimen.

## Tujuan

Mempraktikkan investigasi akses lintas-tenant dengan jejak request lengkap: observasi directory, baseline objek sendiri, uji create, lalu verifikasi dampak pada download.

## Konsep

ID resource/job adalah referensi, bukan otorisasi. Server harus menurunkan tenant yang diizinkan dari principal sesi dan mengulang pemeriksaan ownership pada setiap operasi terhadap job.

## Hint 1

Mulai dengan `action=list`, lalu simpan tenant ID yang terlihat. Gunakan Budi dan catat tenant yang benar-benar dimiliki.

## Hint 2

Keberhasilan `action=create` belum menunjukkan data bocor. Perhatikan `exportId`, lalu panggil tahap `download` sebagai request terpisah.

## Hint 3

Ubah hanya `tenant_id` menjadi `tenant-roastery`. Flag memerlukan record tenant tersebut pada respons download di Vulnerable.

## Solusi

Dalam Vulnerable, buat job tenant-roastery lalu unduh `export-tenant-roastery` pada sesi Budi yang sama. Secure menolak foreign tenant pada create dan memeriksa ownership lagi saat download.

## Akar Masalah

Tenant/job dipilih dari input klien tanpa kebijakan otorisasi yang mengikatnya kepada principal. Pemeriksaan login tidak sama dengan pemeriksaan izin objek.

## Perbaikan

Turunkan tenant dari principal di server, simpan pemilik job secara eksplisit, dan otorisasi setiap operasi job. Tambahkan regression test untuk create/status/download lintas tenant.

## Contoh Rentan

```python
job = create_export(request.form["tenant_id"])
return download(job_id=request.form["export_id"])
```

Kedua operasi menerima identifier klien tanpa memverifikasi keanggotaan tenant.

## Contoh Aman

```python
tenant = tenant_allowed_for(current_user, requested_tenant_id)
job = create_export(tenant)
job = export_owned_by(current_user, requested_export_id)
return download(job)
```

Setiap lookup membatasi objek menurut principal sesi.

## Langkah Latihan

1. Login sebagai Budi dan kirim `action=list`.
2. Buat dan unduh job tenant-campus untuk baseline.
3. Simpan baseline respons dan pastikan tidak ada flag.
4. Di Vulnerable, buat job tenant-roastery tanpa mengubah sesi.
5. Gunakan ID yang dikembalikan pada action download, lalu verifikasi tenant dan recordCount.
6. Ganti ke Secure dengan sesi bersih dan ulangi kedua tahap; pastikan create/download foreign tidak memberikan record.

## Bukti yang Dicatat

Mode, principal tanpa cookie, action berurutan, tenant ID, export ID, status, tenant pada respons download, recordCount, dan flag.

## Kalau Masih Bingung

Gunakan request POST form-urlencoded. Job hanya berlaku di sesi browser yang membuatnya. Budi harus login; status `401` berarti lakukan login dulu, sementara `403` saat membuat tenant-roastery adalah hasil Secure yang benar.

Tulis laporan singkat berisi hipotesis awal, hasil yang menyangkal/mendukungnya, dampak, dan kontrol yang gagal. Jelaskan mengapa validasi create saja tidak cukup jika endpoint download dapat dipanggil langsung.
