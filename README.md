# E-SISWA (SSD) Android v1.1.0

Android WebView wrapper untuk **E-SISWA (Sistem Siswa Digital) – SMP Negeri 4 Kota Dumai** dengan **Native Push Notification**.

## Identitas aplikasi

- Nama: **E-SISWA (SSD)**
- Application ID: `id.sch.smpn4dumai.esiswa`
- Version: `1.1.0` (versionCode 2)
- Min Android: API 26 / Android 8.0
- Target/Compile: API 36 / Android 16
- Web App: deployment E-SISWA Google Apps Script produksi milik sekolah.

## Fitur Android

- WebView JavaScript + DOM Storage dan cookie/session persisten.
- Kamera QR dan Face Recognition melalui `getUserMedia` dengan permission Android.
- Import/upload file, download HTTP/HTTPS dan `blob:`/`data:`.
- Popup WebView, tombol Back Android, loading dan halaman offline.
- Launcher icon + splash memakai logo E-SISWA (SSD).
- **Firebase Cloud Messaging (FCM) native push** untuk:
  - Pembinaan Siswa.
  - Absensi Masuk.
  - Absensi Pulang.
  - Izin Pulang Cepat.
- Android 13+ meminta izin `POST_NOTIFICATIONS`.
- Tap notifikasi Pembinaan membuka menu Pembinaan; tap Masuk/Pulang membuka Dashboard.

## HP Siswa + HP Orang Tua

Satu akun **Siswa/Orang Tua** dapat aktif di beberapa perangkat. Setiap perangkat mendapat token FCM sendiri dan server E-SISWA mengikat semua token aktif ke NISN yang sama. Dengan demikian **HP siswa dan HP orang tua menerima notifikasi Masuk/Pulang yang sama**.

Aktivasi perangkat cukup login sekali menggunakan akun Siswa/Orang Tua pada masing-masing HP. Session WebView dipertahankan. Logout dari satu perangkat hanya menonaktifkan token push perangkat tersebut.

## Firebase tanpa `google-services.json`

v1.1.0 menggunakan `FirebaseOptions` secara programatik. APK tidak menyimpan service-account/private key. Konfigurasi client Firebase non-rahasia diambil setelah login dari backend E-SISWA, lalu disimpan lokal agar FCM dapat diinisialisasi saat proses aplikasi dibuka kembali.

Lihat [FIREBASE-PUSH-SETUP.md](FIREBASE-PUSH-SETUP.md) untuk konfigurasi backend.

## Keamanan

- Service-account Firebase **tidak pernah** masuk APK/repository.
- Password E-SISWA, token session, API key Gemini, dan Spreadsheet ID tidak ditanam di source Android.
- Device ID di-hash server-side sebelum disimpan.
- FCM token hanya diregistrasikan setelah session E-SISWA valid.
- Notification payload hanya membawa **Nama + Kelas** dan metadata routing; **NISN tidak masuk isi notifikasi**.

## Build

Lihat [BUILDING.md](BUILDING.md).
