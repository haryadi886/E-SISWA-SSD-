# Setup Firebase Push E-SISWA v1.1.0

APK dapat dibuild tanpa Firebase config di source. Agar push aktif, siapkan satu project Firebase/Google Cloud dengan Android app package:

`id.sch.smpn4dumai.esiswa`

## Script Properties E-SISWA

Tambahkan properti berikut di Apps Script **Project Settings > Script Properties**:

- `FCM_PROJECT_ID` = Project ID Firebase.
- `FCM_ANDROID_APP_ID` = Firebase Android App ID (`1:...:android:...`).
- `FCM_ANDROID_API_KEY` = Web/API key client Android dari Firebase config.
- `FCM_SENDER_ID` = Project Number / Messaging Sender ID.
- `FCM_SERVICE_ACCOUNT_JSON` = seluruh JSON service account yang mempunyai izin mengirim Firebase Cloud Messaging.

`FCM_SERVICE_ACCOUNT_JSON` adalah rahasia. Simpan hanya di Script Properties; jangan taruh di APK atau GitHub.

## Aktivasi Siswa dan Orang Tua

1. Instal APK pada HP siswa dan HP orang tua.
2. Login dengan akun Siswa/Orang Tua yang sama pada kedua HP.
3. Izinkan notifikasi Android.
4. Setelah dashboard terbuka, tiap HP mendaftarkan token FCM berbeda ke NISN yang sama.
5. Scan Masuk/Pulang berikutnya dikirim ke semua perangkat aktif siswa tersebut.

## Jenis push

- Absensi Masuk / Terlambat.
- Absensi Pulang.
- Pulang Cepat.
- Pembinaan baru.

Kegagalan FCM tidak membatalkan transaksi absensi atau Pembinaan; push bersifat best-effort setelah data utama tersimpan.
