# Cara Build E-SISWA (SSD) Android v1.1.0

## Android Studio

1. Instal Android Studio stabil terbaru.
2. Buka folder project `ESISWA-Android-v1.1.0`.
3. Pastikan Android SDK Platform 36 tersedia.
4. Gunakan JDK 17.
5. Sync Gradle.
6. Pilih **Build > Build APK(s)**.

Hasil debug APK:

`app/build/outputs/apk/debug/app-debug.apk`

## GitHub Actions

Repository menyertakan `.github/workflows/build-debug-apk.yml`.

1. Push source ke GitHub.
2. Workflow **Build Android APK** berjalan saat push ke `main` atau dapat dijalankan manual.
3. Artifact bernama **E-SISWA-SSD-v1.1.0-debug-apk** berisi `app-debug.apk` yang installable.

## Signing produksi

Debug APK cocok untuk uji internal. Untuk distribusi jangka panjang/Play Store, gunakan satu keystore release milik sekolah. Jangan simpan file keystore atau password ke repository.

## Catatan Firebase

Build APK **tidak memerlukan `google-services.json`**. Firebase diinisialisasi saat runtime dari konfigurasi non-rahasia yang diberikan backend E-SISWA setelah login. Private key FCM tetap hanya di Script Properties Apps Script.
