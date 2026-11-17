# Race condition redeem kupon

## Tujuan
Melihat mengapa urutan check-then-act perlu dibuat atomik.

## Konsep
Dua request yang berjalan bersamaan dapat membaca kondisi kupon sebelum salah satunya menulis hasil, sehingga kupon yang sama terpakai lebih dari sekali.

## Hint 1
Cari jeda di antara pemeriksaan dan penyimpanan redemption.

## Hint 2
Pada aplikasi multi-thread, dua request paralel dapat melewati pemeriksaan awal yang sama.

## Hint 3
Ulangi hanya request ke endpoint `/extra/coupon` dengan akun database latihan lokal.

## Solusi
Tunjukkan dua redemption lokal untuk akun yang sama dan lihat penanda pada respons kedua.

## Akar masalah
Operasi pemeriksaan dan klaim tidak dilindungi transaksi atomik atau constraint unik.

## Perbaikan
Gunakan transaksi serializable/lock yang sesuai dan constraint unik `(user_id,coupon)`; perlakukan konflik sebagai kupon sudah digunakan.

## Contoh rentan
Baca jumlah klaim, lalu insert setelah operasi terpisah.

## Contoh aman
Transaksi write-lock dan constraint unik yang mengikat kupon kepada akun.

## Analisis Mendalam
- **Semantik endpoint:** fixture ini mensimulasikan check-then-act dengan counter yang terlihat; uji dasarnya adalah satu redeem baseline lalu satu replay manual, bukan stress test konkurensi.
- **Hipotesis:** apakah endpoint memeriksa kupon sudah dipakai dan mencatat redemption sebagai satu operasi atomik?
- **Bukti:** bandingkan counter sebelum/sesudah tiap request, status response kedua, dan flag. Karena state persisten, response kedua harus dibaca sebelum melakukan tindakan lain.
- **Secure:** transaksi/constraint harus memastikan satu kupon per akun hanya tercatat sekali. Penolakan duplikat tidak boleh menaikkan counter.
- **Batas uji:** jangan gunakan banyak request paralel, loop, Intruder, atau flood. Simulator ini cukup membuktikan cacat check-then-act tanpa mengukur performa.

## Bukti yang Dicatat
- Counter awal, hasil redeem pertama, hasil satu replay, counter akhir, dan mode.
- Pastikan sesi akun sama dan label status/response dicatat; jangan mengulang setelah flag muncul.
- Mitigasi atomik berupa transaksi dan constraint unik `(user_id, coupon)` dengan penanganan konflik.

## Langkah latihan
1. Masuk ke KopiLab sebagai Budi.
2. Kirim beberapa request POST ke `/extra/coupon` dengan cepat dari dua tab browser lokal atau request paralel.
3. Perhatikan nilai `redemptions` dan header `X-Lab-Flag`; keduanya hanya mencatat kupon latihan.
4. Dalam mode **Secure**, redeem berulang harus tetap dihitung satu kali.

## Kalau masih bingung
Bayangkan dua kasir memeriksa kupon yang sama pada saat hampir bersamaan. Jika keduanya memeriksa sebelum ada yang mencatat, keduanya bisa menerima kupon. Database perlu mengunci proses cek dan catat sebagai satu transaksi.
