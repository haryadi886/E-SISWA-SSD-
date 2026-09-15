# Security Notes

- `android:usesCleartextTraffic="false"`: hanya HTTPS.
- Camera Web Permission: whitelist origin Google Script, lalu tetap membutuhkan Android CAMERA permission.
- JavaScript bridge hanya menyediakan fungsi save-download; tidak mengekspos token/cookie/API key.
- Link top-level di luar origin E-SISWA dibuka dengan aplikasi/browser eksternal.
- Cookie WebView diperlukan untuk menjaga session E-SISWA; source tidak membaca nilai cookie selain meneruskannya ke DownloadManager untuk file yang diunduh dari session yang sama.
- `allowBackup=false` mencegah backup OS terhadap data aplikasi.
