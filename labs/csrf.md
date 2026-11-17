# Cross-site request forgery pada transfer

## Tujuan
Mengetahui bagaimana browser dapat mengirim request terautentikasi tanpa tindakan yang dimaksud pemilik akun.

## Konsep
CSRF menyalahgunakan kredensial yang otomatis dikirim browser. Aplikasi perlu membuktikan bahwa request perubahan state berasal dari alur aplikasi yang sah.

## Hint 1
Perhatikan bahwa transfer mengubah saldo dan hanya memerlukan sesi browser.

## Hint 2
Cari token tak terduga yang terikat pada sesi dan diverifikasi server.

## Hint 3
Attacker simulator di proyek terisolasi; flag uji hanya muncul ketika referer lokal simulasi berbeda.

## Solusi
Buktikan bahwa endpoint transfer menerima request lintas origin simulasi tanpa token anti-CSRF.

## Akar masalah
Handler menerima aksi perubahan state tanpa validasi token anti-CSRF.

## Perbaikan
Gunakan token CSRF yang unik per sesi dan diverifikasi server; cookie `SameSite` adalah pertahanan tambahan, bukan pengganti universal.

## Contoh rentan
POST transfer hanya memerlukan cookie sesi.

## Contoh aman
Tolak POST bila token form tidak cocok dengan token sesi.

## Analisis Mendalam
- **Batas kepercayaan:** browser secara otomatis menyertakan cookie sesi yang berlaku; keberadaan cookie membuktikan sesi, bukan niat pengguna untuk melakukan transfer tertentu.
- **Alur yang diamati:** simulator lokal memicu `POST /transfer`. Bandingkan method, penerima, jumlah, origin/referer, dan keberadaan token CSRF; nilai token itu sendiri tidak perlu disalin ke catatan.
- **Dampak stateful:** transfer mengubah saldo pengirim dan penerima. Catat kedua saldo sebelum dan sesudah satu demo saja agar hasil dapat dibedakan dari state lama.
- **Interpretasi Secure:** penolakan request demo tanpa token adalah hasil yang diharapkan. Pastikan form asli KopiLab masih dapat melakukan transfer sah dengan token sesi yang benar.
- **Pertahanan berlapis:** token yang terikat sesi dan diverifikasi server adalah kontrol utama dalam latihan ini; `SameSite` dan pemeriksaan origin membantu, tetapi kebijakan harus sesuai arsitektur aplikasi.

## Bukti yang Dicatat
- Endpoint dan origin simulator lokal, method, field `to`/`amount`, status, dan ada/tidaknya token.
- Saldo awal/akhir akun latihan yang terlibat; jangan mengulang POST hanya untuk memperoleh screenshot tambahan.
- Perbedaan penerimaan Vulnerable dan penolakan Secure, tanpa menyalin cookie atau token.

## Langkah latihan
1. Jalankan `python run_attacker.py` di terminal kedua, lalu buka `http://127.0.0.1:9000`.
2. Masuk ke KopiLab sebagai Budi di port 5000 dan buka halaman simulator.
3. Tekan tombol demo untuk mengirim transfer latihan ke KopiLab lokal.
4. Mode **Vulnerable** menerima request tanpa token. Mode **Secure** menolak request demo karena token formulir tidak ada.

## Kalau masih bingung
Browser membawa cookie login secara otomatis. Situs lain dapat mencoba membuat browser mengirim formulir tanpa kamu membuka KopiLab. Token rahasia di formulir membantu server membedakan formulir asli dari kiriman tak terduga.
