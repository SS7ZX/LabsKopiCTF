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

## Langkah latihan
1. Masuk ke KopiLab sebagai Budi.
2. Kirim beberapa request POST ke `/extra/coupon` dengan cepat dari dua tab browser lokal atau request paralel.
3. Perhatikan nilai `redemptions` dan header `X-Lab-Flag`; keduanya hanya mencatat kupon latihan.
4. Dalam mode **Secure**, redeem berulang harus tetap dihitung satu kali.

## Kalau masih bingung
Bayangkan dua kasir memeriksa kupon yang sama pada saat hampir bersamaan. Jika keduanya memeriksa sebelum ada yang mencatat, keduanya bisa menerima kupon. Database perlu mengunci proses cek dan catat sebagai satu transaksi.
