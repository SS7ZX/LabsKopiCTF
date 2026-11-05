# HTTP parameter pollution simulasi

## Tujuan
Melihat ambiguitas saat satu parameter dikirim berulang kali dan parser memilih nilai berbeda.

## Konsep
Lapisan aplikasi/proxy dapat berbeda dalam memilih parameter pertama, terakhir, atau menggabungkannya. Ini bisa menyebabkan aturan validasi dan penggunaan nilai tidak konsisten. Lab hanya mengembalikan nilai yang terlihat; tidak memproses pembayaran atau mengubah akun.

## Hint 1
Kirim satu `amount=100` sebagai baseline.

## Hint 2
Tambahkan parameter kedua dengan nilai berbeda.

## Hint 3
Secure menolak request yang memiliki parameter duplikat.

## Solusi
`amount=1&amount=100` menghasilkan firstValue dan effectiveValue berbeda pada Vulnerable; Secure mengembalikan 400.

## Akar Masalah
Input parameter duplikat tidak memiliki kebijakan parsing/validasi tunggal.

## Perbaikan
Tolak parameter duplikat untuk field sensitif atau definisikan parsing konsisten pada seluruh lapisan.

## Contoh Rentan
Validasi memakai nilai pertama, sedangkan operasi memakai nilai terakhir.

## Contoh Aman
Pastikan jumlah nilai satu sebelum validasi dan pemrosesan.

## Analisis Mendalam
- Periksa raw query agar urutan nilai terlihat.
- Bandingkan `valuesReceived`, `firstValue`, dan `effectiveValue`.
- Gunakan nilai fixture numerik saja; tidak ada transaksi yang dibuat.
- Secure harus mengembalikan 400 untuk duplikasi.
- Jangan menyimpulkan behavior proxy eksternal dari simulator aplikasi tunggal.

## Langkah Latihan
1. Kirim GET `/extra/academy/parameter-pollution?amount=100`.
2. Kirim request ke Repeater dan catat JSON.
3. Ubah query menjadi `amount=1&amount=100` tanpa mengubah target.
4. Kirim sekali dan bandingkan nilai first/effective.
5. Ulangi pada Secure dan pastikan duplicate ditolak.

## Bukti yang Dicatat
Raw query yang tidak sensitif, daftar valuesReceived, first/effective value, status, mode.

## Kalau Masih Bingung
Pastikan query memuat dua pasangan `amount`, bukan satu nilai dengan tanda koma.
