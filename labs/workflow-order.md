# Business workflow: validasi urutan langkah

## Tujuan
Memahami bahwa aturan proses bisnis harus ditegakkan server pada tiap transisi, bukan hanya di tampilan.

## Konsep
Workflow multi-langkah dapat dilewati jika endpoint klaim berdiri sendiri. Simulasi ini menyimpan satu state verified di session, bukan transaksi atau reward sungguhan.

## Hint 1
Periksa state awal sebelum melakukan aksi.

## Hint 2
Kirim `action=claim` sebelum `action=verify` pada Vulnerable.

## Hint 3
Secure mengharuskan verify pada session yang sama sebelum claim.

## Solusi
Klaim tanpa verifikasi diterima pada Vulnerable dan ditolak pada Secure.

## Akar Masalah
Endpoint claim tidak memvalidasi prasyarat proses.

## Perbaikan
Validasi transisi di server, ikat state ke pengguna, dan lakukan perubahan secara atomik sekali saja.

## Contoh Rentan
Memberi reward hanya berdasarkan pemanggilan endpoint claim.

## Contoh Aman
Memeriksa state `verified` yang disimpan server sebelum mengklaim dan menghapusnya setelah sukses.

## Analisis Mendalam
- `status` membaca state, `verify` menyiapkan state, `claim` menguji prasyarat.
- Semua state berada di cookie session bertanda tangan pada KopiLab.
- `accepted`, `currentStage`, status HTTP, dan flag menunjukkan hasil.
- Jangan mengirim request berulang; claim hanya simulasi lokal.
- Secure menolak claim langsung dan menerima verify → claim.

## Langkah Latihan
1. Kirim POST `action=status`; catat `start`.
2. Pada Vulnerable kirim `action=claim` sebelum verify.
3. Catat accepted dan flag.
4. Aktifkan Secure dan mulai sesi/state baru.
5. Kirim claim lebih dahulu (harus ditolak), lalu verify dan claim sekali.

## Bukti yang Dicatat
Urutan action, state awal/akhir, accepted, status, mode. Redaksi cookie.

## Kalau Masih Bingung
Di Repeater body berada setelah baris kosong. Kirim setiap action sebagai POST form-urlencoded.
