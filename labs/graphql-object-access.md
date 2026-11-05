# Otorisasi objek API bergaya GraphQL

## Tujuan
Menguji apakah API menerapkan otorisasi objek berdasarkan sesi, bukan hanya menerima identifier yang diminta.

## Konsep
API yang memberi bentuk response fleksibel tetap harus membatasi setiap objek yang dapat dibaca. Endpoint ini merupakan resolver mini JSON, bukan server GraphQL lengkap, dan hanya menyajikan label akun dummy.

## Hint 1
Login sebagai Budi; objek ID 2 adalah baseline seed standar.

## Hint 2
Kirim POST dengan field `id` dan pertahankan session Budi.

## Hint 3
Bandingkan resolver Vulnerable dan Secure saat ID menunjuk objek latihan lain.

## Solusi
POST `id=1` ke endpoint saat login sebagai Budi. Vulnerable mengembalikan label profil admin fixture; Secure mengembalikan 404.

## Akar Masalah
Resolver memilih objek dari ID tanpa memeriksa pemilik terhadap identitas sesi.

## Perbaikan
Terapkan otorisasi di resolver pada setiap objek/field sensitif dan batasi query sesuai principal tervalidasi.

## Contoh Rentan
Resolver mengembalikan objek berdasarkan `id` tanpa ownership check.

## Contoh Aman
Query hanya mencari objek yang ID-nya cocok dan owner-nya sama dengan sesi.

## Analisis Mendalam
- Endpoint meminta login; anonymous akan mendapat 401.
- Baseline `id=2` sebagai Budi membuktikan sesi dan format request bekerja.
- Ubah hanya ID menjadi 1; response JSON menunjukkan apakah object-level authorization terjadi.
- Field data adalah label fixture, tidak ada credential/API key yang dikembalikan.
- Secure harus menolak ID lintas pemilik tanpa mengubah sesi.

## Langkah Latihan
1. Login sebagai Budi di browser Burp.
2. Kirim `POST /extra/academy/graphql-object-access` dengan `Content-Type: application/x-www-form-urlencoded` dan body `id=2`.
3. Periksa response baseline, lalu Send to Repeater.
4. Ubah body menjadi `id=1`, pastikan cookie sesi login tetap dari browser sendiri, dan kirim sekali.
5. Catat response Vulnerable.
6. Aktifkan Secure, tangkap request baru, dan ulangi `id=1`; pastikan objek ditolak.

## Bukti yang Dicatat
Status login, ID yang diminta, profile ID/label yang dikembalikan, status response, dan mode. Redaksi cookie.

## Kalau Masih Bingung
Gunakan body form-urlencoded di Repeater; jangan menaruh `id` sebagai JSON.
