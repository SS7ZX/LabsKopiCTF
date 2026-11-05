# Hacker Class Final Boss: settlement dan receipt lintas-akun

## Tingkat dan batas latihan

**Tingkat:** Kelas Hacker / Final Boss — Expert track  
**Fokus:** analisis alur bisnis multi-request, integritas total, transaksi database, autentikasi versus otorisasi objek, serta pembuktian dampak berantai.  
**Target satu-satunya:** `http://127.0.0.1:5000/extra/academy/final-boss-ledger-chain`  
**Akun:** Budi (`budi` / `budi123`), database lokal KopiLab.  
**Dampak stateful:** settlement membuat baris order dan mengurangi saldo Budi. Gunakan percobaan rentan satu kali; reset database latihan bila ingin kembali ke seed awal.

Lab ini adalah skenario orisinal untuk aplikasi lokal KopiLab. Tidak ada pembayaran, gateway, merchant, ataupun sistem eksternal yang dihubungi. Gunakan hanya endpoint loopback di atas. Bagian “bug bounty” di sini adalah latihan metodologi pelaporan yang aman; ini bukan program bounty, bukan penilaian NASA, dan bukan izin untuk menguji sistem NASA atau target pihak ketiga.

## Tujuan pembelajaran

Setelah menyelesaikan lab, kamu diharapkan dapat:

1. Memetakan request multi-tahap sebagai satu alur bisnis, bukan memperlakukan setiap status HTTP sebagai temuan terpisah.
2. Menentukan asal nilai tepercaya: harga berasal dari `products.price`, bukan field `total` dari browser.
3. Mengikuti perubahan state melalui Flask session dan transaksi SQLite.
4. Membedakan autentikasi (“siapa Budi?”) dari otorisasi objek (“order mana yang boleh dibaca Budi?”).
5. Menguji pengamanan di setiap batas: sebelum settlement menulis DB dan saat receipt dibaca.
6. Mengumpulkan bukti yang menunjukkan urutan sebab-akibat tanpa mengulang transaksi yang mengubah saldo.
7. Menguji kontrol negatif—quote lama, quote lintas sesi, replay, dan penolakan tanpa side effect—agar kesimpulan tidak didasarkan pada satu respons.
8. Menulis laporan yang dapat direproduksi reviewer, menyatakan bukti dan batas inferensi secara jujur, serta tidak melebih-lebihkan dampak.

## Model aplikasi dan alur data

Endpoint menerima empat action POST:

| Action | Fungsi normal | Data yang harus diperiksa |
|---|---|---|
| `map` | Membaca principal, saldo, dan produk latihan | `principalId`, `balance`, `product.price` |
| `quote` | Membuat quote untuk satu unit produk 1 | `quoteId`, `serverTotal`, `item`, `qty` |
| `settle` | Mengonsumsi quote dan membuat order | `orderId`, `submittedTotal`, `serverTotal`, `underpaid` |
| `receipt` | Membaca receipt berdasarkan `order_id` | `ownerId`, `currentPrincipalId`, `total`, reference |

Alur yang diharapkan:

```text
login -> map -> quote -> settle -> receipt
                    |       |          |
              Flask session |      SELECT orders
                            +-> INSERT orders
                                UPDATE users.balance
```

### State sesi dan state database bukan hal yang sama

- Flask session menyimpan referensi `quoteId` aktif dan bukti settlement. Cookie sesi bertanda tangan; jangan mengedit atau membagikan nilainya.
- Tabel `final_boss_quotes` menyimpan principal pemilik, produk, item/qty, total server, dan status `used`. Quote disimpan di server agar pengikatan dan pemakaian ulang tidak bergantung pada cookie klien.
- SQLite `products` adalah sumber harga katalog. Produk 1 adalah Kopi Gayo 250g dengan harga seed Rp85.000.
- SQLite `orders` menerima satu baris baru saat settlement berhasil. `total` pada baris tersebut adalah bukti persisten atas nominal yang dibukukan.
- SQLite `users.balance` berkurang dengan nominal settlement yang sama. Catat saldo sebelum dan sesudah.
- `receipt` hanya membaca `orders`; pembacaan tidak membuat atau mengubah order.
- Seed `orders.id=1` adalah receipt milik akun admin untuk uji ownership lokal. Budi adalah `uid=2`; order miliknya seed awal adalah ID 2. Jangan menebak ID lain atau menjalankan enumerasi.

Di mode Vulnerable, handler settlement menggunakan total yang dikirim klien dan handler receipt mencari order hanya dengan `id`. Di Secure, handler membandingkan total terhadap quote server sebelum transaksi, mengonsumsi quote di transaksi yang sama dengan penulisan order/saldo, dan menambahkan `user_id` dari sesi pada query receipt.

## Metodologi ala engagement bug bounty—dalam scope lab

Gunakan urutan **scope → observasi → hipotesis → eksperimen terkendali → verifikasi dampak → laporan → regression check**. Tujuannya bukan mengirim banyak payload, melainkan menghasilkan bukti yang bisa diulang dan mengisolasi penyebabnya.

### Scope dan aturan engagement

| Aturan | Batas latihan |
|---|---|
| In-scope | Hanya endpoint loopback KopiLab yang tertulis pada materi |
| Akun | Budi dan fixture admin; jangan gunakan akun eksternal |
| Laju | Request manual di Burp Repeater; tanpa scanner, fuzzer, brute force, atau enumerasi ID |
| Data | Data seed sintetis; jangan kirim data pribadi atau rahasia nyata |
| Efek samping | Maksimal satu settlement rentan yang terencana; request lain read-only kecuali langkah Secure normal |
| Stop condition | Hentikan jika host berubah, akun bukan fixture, hasil tidak terduga mengubah state, atau ada indikasi keluar dari aplikasi lokal |

### Threat model dan aset

- **Aset integritas:** `orders.total`, `users.balance`, dan status konsumsi quote.
- **Aset kerahasiaan:** isi receipt/order yang hanya boleh dilihat pemilik.
- **Principal:** user ID dari sesi login; bukan `user_id`, `ownerId`, atau role dari request.
- **Trust boundary:** browser → route KopiLab → quote/database → receipt response.
- **Prasyarat dampak:** user sudah login. Bukti harga harus memperlihatkan transaksi tercatat; bukti akses harus memperlihatkan owner berbeda.
- **Di luar model:** gateway pembayaran, jaringan eksternal, eksploitasi server, dan akun/database sungguhan.

### Hipotesis yang bisa dibantah

Tuliskan prediksi sebelum mengirim request. Jika prediksi tidak terpenuhi, simpan hasil negatif; jangan mengubah hipotesis setelah melihat respons seolah-olah itu prediksi awal.

| ID | Hipotesis | Satu variabel yang diuji | Bukti yang mengonfirmasi | Bukti yang menyangkal |
|---|---|---|---|---|
| H1 | Server menerima nominal klien, bukan total quote | `total` pada `settle` | Order tersimpan di bawah harga quote dan saldo turun sebesar nominal itu | Ditolak sebelum commit; order count/saldo tetap |
| H2 | Otorisasi receipt hanya memeriksa keberadaan ID | `order_id` pada `receipt` | Receipt menunjukkan `ownerId` bukan principal | Receipt sendiri berhasil tetapi foreign receipt tidak memberi body |
| H3 | Quote terikat pada sesi dan pemilik | Sesi lain dengan quote ID yang sama | - | Quote ditolak tanpa order atau debit |
| H4 | Quote hanya bisa dikonsumsi sekali | Replay settlement yang sama satu kali | - | Replay ditolak dan tidak membuat order kedua |
| H5 | Kegagalan validasi atomik | Snapshot database sebelum/sesudah penolakan | - | Tidak ada order baru dan saldo tetap |

H3–H5 adalah pemeriksaan kontrol/negative case, bukan jalur untuk mengakali kontrol. Hanya H1 dan H2 yang menjadi temuan rentan yang ditargetkan lab.

### Bukti minimum untuk triase

Status `200` atau flag saja tidak cukup. Reviewer harus dapat menjawab:

1. **Siapa principal?** Catat user ID lokal, jangan lampirkan cookie.
2. **Apa baseline?** Catat harga katalog, saldo, dan receipt milik sendiri.
3. **Apa delta request?** Tunjukkan field yang berubah dan pertahankan request lainnya.
4. **Apakah dampak persisted?** Korelasikan `orderId`, `orders.total`, dan delta `users.balance`.
5. **Apakah objek asing benar-benar keluar?** Bandingkan `ownerId` dan `currentPrincipalId`.
6. **Apa hasil Secure?** Catat status penolakan dan bukti tidak ada side effect.
7. **Apa batas klaim?** Dampak hanya pada fixture KopiLab; jangan menggeneralisasi ke layanan produksi.

Gunakan redaksi minimal: ID seed, nama fixture, nominal, status, dan reference latihan. Jangan menyertakan session cookie, password, token aktif, atau dump database.

## Batas pengujian dan kehati-hatian state

1. Pastikan host selalu `127.0.0.1:5000`; jangan ganti ke alamat lain.
2. Lakukan eksperimen pada sesi Budi yang sama dari awal sampai receipt.
3. `settle` adalah operasi tulis. Jangan klik Send berkali-kali tanpa memeriksa status dan response; setiap settlement sukses membuat order baru dan mengurangi saldo.
4. Untuk percobaan Secure, minta quote baru. Jangan mencampur quote yang dibuat dalam satu mode dengan eksperimen mode lain.
5. Reset database mengembalikan order/saldo seed. Fitur reset database juga mereset progres lokal, jadi gunakan hanya bila memang ingin membersihkan seluruh fixture latihan.

## Persiapan Burp Suite yang spesifik untuk lab

1. Jalankan KopiLab lokal, login sebagai Budi di browser yang diproksikan melalui Burp.
2. Di **Proxy → Intercept**, biarkan **Intercept is off** agar navigasi normal tidak tertahan.
3. Buka halaman lab, lalu periksa **Proxy → HTTP history**. Filter host ke `127.0.0.1:5000`; cari hanya path `/extra/academy/final-boss-ledger-chain`.
4. Kirim request ke Repeater dan pastikan method `POST`, path tepat, host loopback, serta body `application/x-www-form-urlencoded`.
5. Pastikan Cookie berasal dari browser latihan. Jangan tempel cookie sesi ke laporan, chat, atau target lain.
6. Repeater tidak selalu memakai cookie browser terbaru secara otomatis. Setelah respons yang memuat `Set-Cookie`, gunakan cookie sesi terbaru untuk request tahap selanjutnya. Jangan menggabungkan cookie lama dan baru.
7. Catat setiap request sebagai tab bernama seperti `01-map`, `02-quote`, `03-settle-valid`, `04-receipt-own`. Buat tab baru untuk percobaan underpayment agar request baseline tetap utuh.

### Bentuk request dasar

Ganti Cookie dengan cookie sesi lokal yang dibuat browser/Repeater. Biarkan Burp menghitung `Content-Length`.

```http
POST /extra/academy/final-boss-ledger-chain HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded
Cookie: session=<cookie sesi lokal>

action=map
```

Request action lain memakai path dan header yang sama; ubah hanya body sesuai tahap. Cookie placeholder di atas bukan nilai yang dapat dipakai, dan jangan menyimpan cookie asli dalam catatan.

## Praktikum bertahap

### Tahap 1 — Peta baseline tanpa mengubah data

1. Pastikan mode **Vulnerable** aktif dan login sebagai Budi.
2. Kirim `action=map`.
3. Catat `principalId`, saldo, ID/nama produk, serta harga katalog.
4. Pastikan baseline menunjukkan principal 2 dan produk Gayo Rp85.000.
5. Request ini read-only. Jika angkanya berbeda, gunakan nilai yang benar-benar dikembalikan oleh fixture; jangan mengasumsikan transaksi sebelumnya belum mengubah saldo.

**Tujuan tahap ini:** membuat nilai pembanding sebelum eksperimen. Saldo adalah state database; jangan mengandalkan nilai yang diingat dari sesi lama.

### Tahap 2 — Quote dan receipt milik sendiri sebagai kontrol

1. Kirim body `action=quote`.
2. Simpan `quoteId` dan `serverTotal` dari JSON. Jangan mengarang quote ID.
3. Periksa response `Set-Cookie`. Jika Repeater tidak mengelola cookie jar, perbarui Cookie di request berikutnya dengan nilai sesi terbaru.
4. Kirim `action=settle&quote_id=<quoteId>&total=85000` (gunakan `serverTotal` aktual).
5. Settlement ini menulis DB. Kirim sekali; catat `orderId`, `submittedTotal`, `serverTotal`, `underpaid`, dan `databaseChanged`.
6. Gunakan cookie sesi terbaru dari respons settlement. Minta `action=receipt&order_id=<orderId>` untuk membaca order sendiri.
7. Pastikan `ownerId` sama dengan `currentPrincipalId`; receipt sendiri tidak menghasilkan flag.

**Mengapa kontrol ini penting:** quote dan settlement yang cocok membuktikan alur normal bekerja. Jika request uji gagal kemudian, kamu bisa membedakan masalah sesi/format dari kontrol keamanan yang benar-benar menolak manipulasi.

### Tahap 3 — Uji manipulasi total secara terisolasi

Jalankan hanya sekali pada mode Vulnerable dan sesi latihan lokal:

1. Minta quote baru, lalu catat `quoteId` dan `serverTotal`.
2. Dari request settle baseline, gunakan request yang sama dan ubah **hanya** nilai `total` menjadi `1`. Pertahankan `quote_id`, principal, host, path, dan method.
3. Kirim satu kali. Simpan respons; jangan mengirim ulang jika hasilnya belum jelas.
4. Periksa apakah respons menyebut `submittedTotal=1`, `serverTotal=85000`, dan `underpaid=true`.
5. Gunakan `orderId` dari respons untuk mengonfirmasi order yang tercipta. Pada aplikasi ini receipt sendiri dapat dipakai sebagai pembacaan konfirmasi.
6. Kirim `action=map` dan bandingkan saldo dengan nilai sebelum settlement.
7. Flag belum menjadi bukti rantai final pada tahap ini. Underpayment harus dibuktikan melalui nilai order dan perubahan saldo, bukan hanya response sukses.

**Hasil yang diharapkan di Vulnerable:** order baru menyimpan total 1 dan saldo Budi berkurang 1. Selisih dengan harga katalog menunjukkan invariant bisnis yang gagal.

### Tahap 4 — Sambungkan ke pemeriksaan ownership receipt

1. Jangan mengubah sesi atau principal; gunakan sesi yang sama setelah settlement underpaid berhasil.
2. Kirim `action=receipt&order_id=1` satu kali. ID 1 adalah fixture receipt admin yang diketahui dari materi, bukan ajakan enumerasi.
3. Periksa `receipt.ownerId` dan bandingkan dengan `currentPrincipalId`.
4. Temuan rantai lengkap terbukti hanya jika owner receipt berbeda dari principal **dan** sesi yang sama memiliki settlement underpaid. Respons Vulnerable pada kondisi ini memberikan `X-Lab-Flag`.
5. Simpan bukti yang diperlukan tanpa menyimpan cookie, kredensial, atau data pribadi.

**Tujuan tahap ini:** menunjukkan bahwa keberhasilan pada satu endpoint tidak otomatis membuktikan yang lain. Bug harga membuat order salah; bug receipt mengungkap objek akun lain. Kedua kelemahan berada pada boundary berbeda.

### Tahap 5 — Verifikasi Secure dengan sesi/quote bersih

1. Aktifkan **Secure** melalui UI KopiLab dan gunakan sesi browser yang sama setelah mode berubah, atau login ulang bila perlu.
2. Minta quote baru; catat total server.
3. Coba settle dengan `total=1`. Respons yang diharapkan `400` dengan pesan mismatch. Periksa bahwa tidak ada order baru, saldo tidak berubah, dan tidak ada flag.
4. Gunakan quote yang sama untuk settle dengan total server yang benar. Secure dapat menyelesaikan pembelian normal satu kali.
5. Baca receipt order sendiri: seharusnya berhasil dan owner sama dengan Budi.
6. Baca `order_id=1`: respons `404` tanpa objek receipt. Itu hasil kontrol ownership, bukan masalah cookie bila receipt sendiri berhasil.
7. Jangan gunakan lagi quote yang telah disettle; Secure mengonsumsi quote sekali.

### Tahap 6 — Expert track: validasi state, replay, dan batas pemilik

Lakukan setelah rantai utama. Percobaan di bawah harus berakhir tanpa flag dan tanpa order/debit tambahan; track ini menguji kualitas kontrol, bukan mencari bypass.

#### A. Quote lama setelah quote baru

1. Minta quote A; simpan `quoteId-A`.
2. Minta quote B dalam sesi yang sama; simpan `quoteId-B`.
3. Kirim settlement dengan quote A dan nominal normal satu kali.
4. Hasil yang benar adalah `409` karena quote A bukan referensi aktif sesi.
5. Pastikan order count dan saldo tidak berubah.
6. Untuk baseline transaksi normal, gunakan quote B dengan nominal server yang benar.

**Yang dipelajari:** row quote lama yang masih ada di DB bukan bukti bahwa klien berhak menggunakannya. Ada batas referensi quote aktif di sesi dan batas kepemilikan quote di server.

#### B. Quote lintas sesi/pemilik

1. Di sesi Budi, minta quote dan catat ID sebagai data fixture lokal.
2. Buka sesi browser/test client kedua dan login sebagai Siti.
3. Kirim settlement menggunakan ID quote Budi dari sesi Siti, tanpa mengubah host/path.
4. Hasil yang benar adalah `409`; tidak ada order baru dan saldo Siti tidak berubah.
5. Jangan memanipulasi atau menyalin session cookie.

**Yang dipelajari:** ID quote adalah referensi, bukan izin. Quote harus terikat pada principal dan context sesi.

#### C. Replay settlement

1. Dalam Secure, gunakan quote baru dan settle nominal server satu kali.
2. Simpan request yang sama lalu kirim ulang satu kali saja.
3. Hasil yang benar adalah `409` karena quote telah dikonsumsi.
4. Pastikan hanya ada satu order dan saldo hanya turun satu kali.

Lakukan hanya pada fixture lokal dan satu replay; jangan kirim request paralel atau berulang-ulang.

#### D. Uji penolakan tanpa side effect

Sebelum menyebut kontrol bekerja, bandingkan `action=map`, order count yang tersedia dari bukti aplikasi/test lokal, dan respons setelah request ditolak. Penolakan yang benar tidak boleh membuat order, mendebit saldo, atau mengonsumsi quote yang diperlukan untuk kontrol normal. Jika Secure menolak mismatch, quote yang sama harus tetap dapat dipakai untuk settlement nominal server yang benar.

#### E. Checklist sebelum menutup investigasi

- `quoteId` berasal dari respons server, bukan tebakan.
- Settlement dan receipt dilakukan dengan principal/sesi yang dimaksud.
- Harga katalog menjadi kontrol, bukan nilai yang diingat dari percobaan terdahulu.
- Bukti saldo dibaca ulang setelah settlement.
- Receipt foreign menunjukkan owner berbeda dari principal pada mode Vulnerable.
- Secure menolak mismatch dan foreign receipt tanpa perubahan database.
- Catatan tidak mengandung cookie, password, ataupun data di luar fixture.

## Request body yang disalin ke Repeater

Contoh berikut hanya body. Ganti `<quoteId>` dengan nilai respons `quote` yang benar; hapus tanda kurung sudut sebelum mengirim.

```text
action=quote
```

```text
action=settle&quote_id=<quoteId>&total=85000
```

```text
action=settle&quote_id=<quoteId>&total=1
```

```text
action=receipt&order_id=1
```

## Analisis Mendalam

### 1. Source of truth dan integrity

Quote memberi server total Rp85.000. Browser boleh mengirim field `total`, tetapi nilai dari klien tidak otomatis menjadi nilai yang benar. Periksa apakah backend mengambil nilai quote tersimpan atau sekadar memakai `request.form["total"]`. Uji hanya dengan total kecil positif agar tetap berada dalam ruang fixture latihan.

### 2. State machine dan urutan request

Alur valid memerlukan quote yang terikat ke `uid` sesi, quote belum digunakan, lalu settlement. Request tanpa quote atau dengan quote sesi lain harus gagal sebelum menulis DB. Sesudah sukses, quote ditandai used. Ulangi request settle hanya jika materi secara eksplisit meminta pengujian replay; untuk lab ini jangan replay transaksi yang sukses.

### 3. Transaksi dan bukti persisted

Settlement menjalankan `BEGIN IMMEDIATE`, membaca quote dan saldo di dalam transaksi, menandai quote used, memasukkan order, mengurangi saldo, lalu commit. Ini mencegah dua request yang memakai quote sama sama-sama membuat order. Karena itu gunakan dua bukti yang saling menguatkan:

- Baris `orders`: pemilik, item, qty, dan total.
- `users.balance`: perubahan sebesar total settlement.

JSON sukses tanpa perubahan DB bukan bukti transaksi. Sebaliknya, jangan menjalankan query modifikasi manual untuk “membuat” bukti.

### 4. Object-level authorization

Principal tetap Budi di semua request. Itu hanya menjawab autentikasi. Otorisasi receipt harus memeriksa `orders.user_id` pada setiap pembacaan. Query rentan hanya mencari `id`; query Secure mencari pasangan `id` dan `user_id` dari sesi. ID yang diketahui bukan izin.

### 5. Ambang temuan rantai

| Bukti | Makna |
|---|---|
| `quote` memberi total server | Nilai kontrol untuk eksperimen |
| Settlement menerima nilai berbeda | Potensi bug validasi, belum cukup membuktikan dampak persistent |
| Order total 1 dan saldo berkurang 1 | Dampak settlement berhasil disimpan |
| Receipt `ownerId` berbeda dari principal | Kebocoran objek lintas-akun |
| Dua kondisi di atas terjadi pada sesi/alur yang sama | Rantai Final Boss lengkap; flag diberikan |
| Secure mismatch tak mengubah DB, foreign receipt 404 | Kontrol server-side bekerja |

### 6. Differential analysis: satu delta per request

| Tahap | Delta request | Respons yang diamati | State yang harus diverifikasi |
|---|---|---|---|
| Quote baseline | `action=quote` | `quoteId`, `serverTotal` | Quote baru milik principal |
| Settlement kontrol | `total=serverTotal` | `settled`, `orderId` | Satu order; saldo turun tepat sebesar total |
| Settlement eksperimen | hanya `total=1` | `underpaid`, status | Apakah order persisted dan saldo berubah |
| Receipt sendiri | `order_id=orderId` | owner sama dengan principal | Tidak mengubah DB |
| Receipt foreign fixture | `order_id=1` | owner dibanding principal | Tidak mengubah DB; Secure tidak memberi body |
| Negative/replay | quote invalid, lama, atau used | respons 4xx | Order count, saldo, quote consumption |

Jika cookie, mode, principal, quote, dan total semuanya berubah sekaligus, hasilnya tidak terisolasi dan tidak dapat dipakai untuk mengatribusikan penyebab.

### 7. Analisis dampak tanpa overclaim

- Underpayment pada satu fixture membuktikan validasi nominal lemah dalam model ini; tidak membuktikan kerugian skala besar atau akses ke payment processor.
- Receipt foreign membuktikan object-level authorization gagal untuk fixture ID tertentu; tidak membuktikan semua order/tenant dapat diakses.
- Rantai dua kondisi menunjukkan komposisi dampak dalam satu principal/sesi. Jangan mengalikan nominal, menghitung jumlah korban, atau menyimpulkan privilege escalation tanpa bukti.
- Severity laporan latihan harus menyebut skenario, prasyarat, aset, dan bukti. Jangan menyebut temuan “Critical” hanya karena judul lab adalah Final Boss.

### 8. Hipotesis ala bug bounty yang dapat difalsifikasi

Tulis prediksi sebelum mengirim request. Ubah satu variabel per uji dan simpan hasil negatif.

- **H1 — integritas nominal:** ubah hanya `total`; konfirmasi perlu order yang tersimpan di bawah quote dan saldo yang berubah, bukan sekadar `200`.
- **H2 — otorisasi objek:** ubah hanya `order_id` ke fixture yang ditentukan materi; konfirmasi perlu `ownerId` berbeda dari `currentPrincipalId`.
- **H3 — quote stale:** minta quote A lalu B; quote A harus ditolak dan tidak membuat order.
- **H4 — binding principal:** gunakan quote Budi dari sesi Siti; request harus ditolak dan saldo kedua akun tetap.
- **H5 — replay/atomisitas:** dalam Secure, kirim ulang satu settlement yang sama; hanya satu order dan satu debit boleh terjadi.

H1 dan H2 adalah kelemahan Vulnerable yang sengaja dilatih. H3–H5 adalah kontrol negatif untuk menguji batas kesimpulan dan perilaku Secure. Semuanya tetap dilakukan pada fixture lokal, tanpa scanner, enumerasi, atau request paralel.

### 9. Alur triase reviewer

Reviewer seharusnya dapat mereproduksi klaim dari bukti yang disunting:

1. **Scope/prasyarat:** host loopback, path, mode, principal seed, dan state awal.
2. **Kontrol:** harga katalog, saldo awal, serta receipt milik sendiri.
3. **Delta:** satu field yang diubah; cookie/token tidak dicantumkan.
4. **Dampak persisted:** `orderId`, total tersimpan, dan saldo sebelum/sesudah.
5. **Akses objek:** `ownerId` dibanding principal, dengan response minimal.
6. **Secure regression:** status penolakan dan konfirmasi tidak ada order/debit.
7. **Batas inferensi:** dampak yang terlihat hanya berlaku pada fixture KopiLab.

Jangan menyebut kerugian produksi, jumlah korban, akses gateway, atau severity “Critical” tanpa bukti. Label Final Boss mengukur kesulitan lab, bukan severity temuan.

## Kalau mentok: diagnosis langkah demi langkah

### Request quote tidak mengembalikan `quoteId`

- Pastikan path tepat dan method POST.
- Pastikan body `action=quote`, bukan parameter query yang tidak ikut terkirim.
- Pastikan login Budi masih aktif; request tanpa login memberi `401`.
- Periksa respons JSON dan jangan lanjut dengan quote ID yang ditebak.

### Settlement menjawab quote tidak ditemukan / `409`

- Quote harus dibuat oleh principal sesi yang sama.
- Gunakan nilai `quoteId` persis dari respons quote.
- Jika Burp mengirim cookie sesi sebelum quote, salin nilai `session` terbaru dari `Set-Cookie` respons quote.
- Jangan menggabungkan atau memodifikasi cookie; gunakan cookie jar Burp atau cookie terbaru dari aplikasi lokal.

### Settlement memberi `400` untuk total 1

- Periksa indikator Secure mode. Pada Secure, penolakan mismatch adalah hasil yang benar.
- Untuk mempelajari vulnerable path, ganti mode melalui UI, minta quote baru, dan mulai eksperimen baru.
- Jangan mencoba mem-bypass Secure; perbandingan mode adalah tujuan latihan.

### Settlement sukses tetapi saldo tampak sama

- Periksa bahwa `action=map` dikirim lagi setelah settlement dan sesi login tetap sama.
- Bandingkan angka saldo sebelum dan sesudah; respons map adalah pembacaan DB, bukan nilai di cookie.
- Cocokkan `orderId` respons dengan ID order yang dikembalikan server.
- Jangan mengirim settlement kedua untuk membuat perubahan lebih terlihat.

### Receipt mengembalikan 404

- Pastikan action adalah `receipt` dan ID dikirim sebagai `order_id`.
- Untuk kontrol own receipt gunakan `orderId` dari settlement.
- Untuk uji foreign receipt gunakan fixture ID `1` hanya setelah settlement di sesi yang sama.
- Di Secure, 404 untuk receipt foreign memang hasil yang diharapkan. Jika receipt sendiri juga 404, periksa cookie sesi terbaru.

### Underpayment terbukti, tetapi flag tidak ada

- Pastikan request receipt memakai cookie yang sama setelah settlement; Flask session yang diperbarui berisi bukti settlement.
- Pastikan foreign receipt benar-benar mengembalikan `ownerId=1` sedangkan `currentPrincipalId=2`.
- Pastikan kedua request dijalankan pada mode Vulnerable dan sesi yang sama.
- Status 200 tanpa receipt asing bukan bukti rantai lengkap.
- Pastikan settlement menggunakan quote aktif terakhir dan receipt memakai sesi yang menyimpan bukti settlement.

### Quote lama atau lintas akun memberi `409`

- Ini hasil kontrol yang benar pada Expert track, bukan kesalahan format.
- Quote lama tidak lagi menjadi quote aktif setelah quote baru dibuat dalam sesi yang sama.
- Quote Budi harus ditolak di sesi Siti; jangan menyalin atau mengedit cookie sesi.
- Periksa order count dan saldo untuk mengonfirmasi tidak ada side effect.

### Repeater menampilkan error format

- Pertahankan `Content-Type: application/x-www-form-urlencoded`.
- Pastikan body hanya memiliki parameter yang diperlukan dan `quoteId` telah di-URL-encode bila perlu.
- Biarkan Burp menghitung `Content-Length`; jangan salin panjang lama setelah mengubah body.

## Akar masalah dan perbaikan

**Akar masalah yang dimodelkan:**

1. Handler settlement mempercayai nilai total yang dikirim klien, padahal quote server sudah menyimpan harga yang semestinya.
2. Handler receipt memeriksa keberadaan `order_id`, tetapi tidak membatasi record menurut principal aktif.

**Perbaikan yang disarankan:**

- Hitung nominal dari data katalog/quote server-side; jangan menerima total final dari browser sebagai nilai otoritatif.
- Ikat quote ke user, masa berlaku, item/qty, dan satu kali konsumsi yang disimpan server-side.
- Jalankan pemeriksaan saldo dan pencatatan order dalam transaksi atomik.
- Pada semua operasi order—detail, receipt, unduh, dan status—batasi query pada `user_id` principal.
- Gunakan respons generik untuk ID objek yang tidak dimiliki pengguna.
- Tambahkan regression test bahwa mismatch tidak menulis order atau mengubah saldo, serta receipt asing tidak mengembalikan body.

## Bukti untuk catatan praktikum

Catat secara lokal:

- Mode dan principal (ID saja, bukan cookie).
- Harga katalog dan total quote.
- Total yang dikirim, `orderId`, total order tersimpan, saldo sebelum/sesudah.
- `order_id` yang diminta, `ownerId` receipt, dan status Secure/Vulnerable.
- Apakah `X-Lab-Flag` muncul pada tahap akhir.

Jangan masukkan cookie sesi atau password pada laporan. Flag digunakan hanya untuk menyelesaikan lab ini.

## Template laporan latihan bergaya bug bounty

Isi template dengan fakta dari KopiLab lokal saja. Ini bukan laporan untuk NASA atau organisasi lain.

```text
Judul:
  [Validasi total / otorisasi receipt] — dampak teramati pada fixture KopiLab

Lingkungan dan scope:
  http://127.0.0.1:5000, lab final-boss-ledger-chain, mode Vulnerable

Ringkasan:
  Kontrol yang gagal, prasyarat, dan dampak yang benar-benar dibuktikan.

Principal/prasyarat:
  User ID seed saja; jangan masukkan password atau cookie.

Langkah reproduksi:
  1. Baseline read-only dan harga quote.
  2. Settlement dengan satu delta yang dijelaskan.
  3. Bukti order/saldo setelah request.
  4. Receipt dan perbandingan principal/owner.

Bukti:
  Request/response yang sudah disunting, orderId, nominal, delta saldo,
  ownerId/currentPrincipalId, status, dan flag bila relevan.

Dampak terverifikasi:
  Hanya data dan akun fixture yang benar-benar teramati.

Hasil Secure:
  Status penolakan serta konfirmasi tidak ada order/debit tambahan.

Batasan:
  Simulasi lokal; tidak menguji gateway pembayaran atau sistem produksi.

Rekomendasi:
  Hitung total di server, konsumsi quote atomik, dan filter setiap lookup order
  berdasarkan principal.
```

### Rubrik mutu laporan

Nilai setiap kriteria dari **0** (tidak ada), **1** (ada tetapi sulit diverifikasi), sampai **2** (jelas dan dapat direproduksi). Maksimum 12.

| Kriteria | Nilai 2 |
|---|---|
| Scope dan prasyarat | Host/path/mode/principal lokal disebut tanpa rahasia |
| Reproduksibilitas | Baseline, satu delta, dan hasil urut |
| Bukti integritas | Order dan perubahan saldo dikorelasikan |
| Bukti otorisasi | Owner receipt dibanding principal |
| Dampak | Klaim dibatasi pada bukti lokal |
| Rekomendasi | Menutup trust boundary dan efek samping |

Skor tinggi tidak menggantikan scope: pelanggaran batas target membuat latihan tidak valid.

## Tujuan

Menyelesaikan satu investigasi end-to-end dengan menghubungkan integritas transaksi, perubahan state SQLite, dan otorisasi objek pada pembacaan receipt.

## Konsep

Kegagalan berantai terjadi ketika validasi business logic dan pemeriksaan akses objek sama-sama mempercayai input klien. Kontrol harus diterapkan pada setiap transisi dan setiap lookup, bukan hanya saat login. Semua pengujian dan pelaporan di sini hanya untuk endpoint loopback KopiLab dan akun seed.

## Hint 1

Mulai dari action `map` dan `quote`. Simpan total server sebagai kontrol; sesi menyimpan referensi quote, sementara total tepercaya berada di tabel `final_boss_quotes`.

## Hint 2

Settlement rentan mengubah `orders` dan `users.balance`. Bandingkan nilai `total` yang dikirim dengan nilai katalog, dan cek perubahan database.

## Hint 3

Receipt adalah boundary terpisah. Setelah settlement berhasil, bandingkan owner receipt `order_id=1` dengan principal Budi. Flag baru muncul jika settlement underpaid dan receipt asing benar-benar dikembalikan.

## Solusi

Dalam Vulnerable, login sebagai Budi, minta quote, settle sekali dengan `total=1`, lalu gunakan sesi terbaru untuk meminta receipt `order_id=1`. Bukti lengkap adalah order tersimpan dengan total 1, saldo turun 1, dan receipt admin dikembalikan ke principal 2. Secure menolak total yang berbeda sebelum transaksi dan membatasi receipt pada order milik principal.

## Akar Masalah

Nilai finansial dari klien diperlakukan sebagai kebenaran saat menulis ledger, sementara pembacaan order hanya memeriksa ID objek. Autentikasi tidak menggantikan pemeriksaan izin per objek.

## Perbaikan

Gunakan harga/total hasil perhitungan server, konsumsi quote secara atomik, dan terapkan filter owner pada setiap operasi receipt/order. Pastikan penolakan terjadi sebelum efek samping database.

## Contoh Rentan

```python
total = int(request.form["total"])
create_order(user_id=session["uid"], total=total)
receipt = find_order(request.form["order_id"])
```

Contoh ini menggunakan nominal klien dan tidak memeriksa kepemilikan receipt.

## Contoh Aman

```python
quote = quote_for_user(quote_id, user_id=current_user.id)
settle_order(total=quote.server_total)
receipt = find_order(order_id, user_id=current_user.id)
```

Lookup quote dan order dibatasi pada principal, sedangkan total berasal dari state server.

## Langkah Latihan

1. Login sebagai Budi dan catat baseline dari `action=map`.
2. Quote dan settle dengan total normal sebagai kontrol; baca receipt sendiri.
3. Buat quote baru, ubah hanya `total` menjadi 1, kirim sekali, lalu catat `orders` dan saldo.
4. Pada sesi settlement yang sama, minta receipt `order_id=1` dan verifikasi owner.
5. Beralih ke Secure, minta quote baru, buktikan mismatch ditolak tanpa perubahan database.
6. Selesaikan quote Secure dengan benar; receipt sendiri tetap boleh, receipt foreign harus 404.
7. **Expert track:** minta dua quote di sesi Budi; coba quote pertama setelah quote kedua dibuat dan verifikasi `409` tanpa perubahan saldo/order.
8. Di sesi terpisah Siti, coba quote ID Budi sekali; verifikasi `409` dan saldo Siti tetap.
9. Dalam Secure, replay satu settlement berhasil sekali; verifikasi hanya satu order dan satu debit.
10. Tulis laporan memakai baseline, delta, bukti persisted, owner/principal, hasil Secure, dan batas dampak lokal.

## Bukti yang Dicatat

Mode, principal, `serverTotal`, `submittedTotal`, `orderId`, perubahan saldo, `ownerId`, status receipt, dan flag. Jangan menyimpan session cookie.

**Template laporan latihan bergaya bug bounty:** scope/prasyarat, ringkasan, langkah reproduksi, bukti request/response yang disunting, dampak terverifikasi, hasil Secure, batasan simulasi, rekomendasi.

**Rubrik mutu laporan:** nilai 0–2 untuk scope, reproduksibilitas, bukti integritas, bukti otorisasi, ketepatan dampak, dan kualitas rekomendasi; skor maksimum 12. Klaim yang melebihi fixture membuat laporan tidak valid.

## Kalau Masih Bingung

Jika quote tidak dikenal, periksa cookie terbaru setelah respons `Set-Cookie`. Jika Secure memberi 400 untuk total 1 atau 404 untuk order 1, kontrol bekerja. Jika receipt sendiri berhasil tetapi foreign receipt tidak, format dan sesi sudah benar; hasil 404 adalah pembatasan ownership yang diharapkan.
