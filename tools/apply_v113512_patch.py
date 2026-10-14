#!/usr/bin/env python3
from pathlib import Path

root = Path("project")
build = root / "app/build.gradle"
s = build.read_text()
assert "versionCode 21" in s and "versionName '1.1.3.5.11'" in s, "Unexpected Android baseline"
s = s.replace("versionCode 21", "versionCode 22", 1)
s = s.replace("versionName '1.1.3.5.11'", "versionName '1.1.3.5.12'", 1)
build.write_text(s)

p = root / "app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java"
s = p.read_text()
assert 'private static final String KEY_TOKEN = "fcm_token";' in s
assert "shouldSuppressDuplicatePopup(context, title, body)" not in s

s = s.replace(
    "import java.util.Map;",
    "import java.util.Map;\nimport java.util.Locale;\nimport java.security.MessageDigest;\nimport java.nio.charset.StandardCharsets;",
    1,
)
s = s.replace(
    '    private static final String KEY_TOKEN = "fcm_token";',
    '    private static final String KEY_TOKEN = "fcm_token";\n'
    '    private static final String KEY_POPUP_DEDUPE_PREFIX = "popup_seen_";\n'
    '    private static final long DUPLICATE_WINDOW_MS = 10L * 60L * 1000L;',
    1,
)
permission_check = """        if (Build.VERSION.SDK_INT >= 33
                && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            return;
        }
"""
assert permission_check in s, "Notification permission guard not found"
s = s.replace(
    permission_check,
    permission_check + "        if (shouldSuppressDuplicatePopup(context, title, body)) return;\n",
    1,
)

marker = "    private static String channelFor(String kind) {"
assert marker in s
methods = r'''    /** Suppress identical title/body popups for 10 minutes on this device. */
    static boolean shouldSuppressDuplicatePopup(Context context, String title, String body) {
        if (context == null) return false;
        long now = System.currentTimeMillis();
        SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        String key = KEY_POPUP_DEDUPE_PREFIX + popupFingerprint(title, body);
        long previous = prefs.getLong(key, 0L);

        // A backwards clock change should fail safe: do not show a duplicate early.
        if (previous > 0L && (now < previous || now - previous < DUPLICATE_WINDOW_MS)) {
            return true;
        }

        SharedPreferences.Editor edit = prefs.edit();
        for (Map.Entry<String, ?> entry : prefs.getAll().entrySet()) {
            if (!entry.getKey().startsWith(KEY_POPUP_DEDUPE_PREFIX)) continue;
            Object value = entry.getValue();
            if (!(value instanceof Long)) {
                edit.remove(entry.getKey());
                continue;
            }
            long timestamp = (Long) value;
            if (now >= timestamp && now - timestamp >= DUPLICATE_WINDOW_MS) {
                edit.remove(entry.getKey());
            }
        }
        edit.putLong(key, now).apply();
        return false;
    }

    private static String popupFingerprint(String title, String body) {
        String normalized = normalizeForDedupe(title) + "\n" + normalizeForDedupe(body);
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(normalized.getBytes(StandardCharsets.UTF_8));
            StringBuilder out = new StringBuilder(digest.length * 2);
            for (byte b : digest) out.append(String.format(Locale.ROOT, "%02x", b & 0xff));
            return out.toString();
        } catch (Exception ignored) {
            // Stable fallback still avoids storing the raw title/body in preferences.
            return Integer.toHexString(normalized.hashCode());
        }
    }

    private static String normalizeForDedupe(String value) {
        String text = value == null ? "" : value.trim().replaceAll("\\s+", " ");
        return text.toLowerCase(Locale.ROOT);
    }

'''
s = s.replace(marker, methods + marker, 1)
p.write_text(s)

# Install the exact, user-approved MONO98 asset in the built project.
import base64
import hashlib
asset_b64 = Path("revision-assets/v113512/esiswa_notification_monochrome_98.png.b64").read_text().strip()
asset_bytes = base64.b64decode(asset_b64, validate=True)
asset_sha256 = hashlib.sha256(asset_bytes).hexdigest()
assert asset_sha256 == "a7b402ce4add2c3be053d33037dbd3aecc3d59f097162305229d04259d50d161", "MONO98 asset hash mismatch"
asset_target = root / "app/src/main/res/drawable-nodpi/esiswa_notification_monochrome.png"
asset_target.parent.mkdir(parents=True, exist_ok=True)
asset_target.write_bytes(asset_bytes)

# Use one stable native notification for the in-app unread badge mirror.
# The notification number tracks unread count; zero cancels the mirror so the
# launcher badge can clear after the web Notification Center reports zero.
service = root / "app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java"
ss = service.read_text()
ss = ss.replace(
    '    private static final String KEY_TOKEN = "fcm_token";',
    '    private static final String KEY_TOKEN = "fcm_token";\n'
    '    private static final int WEB_BADGE_NOTIFICATION_ID = 0x45534953;',
    1,
)
method_marker = "    public static void storeToken(Context context, String token) {"
assert method_marker in ss, "PushMessagingService insertion point missing"
badge_method = r'''    public static void updateWebBadgeNotification(Context context, String title, String body,
                                                  String kind, String view, int unreadCount,
                                                  boolean alert) {
        if (context == null) return;
        NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;
        if (unreadCount <= 0) {
            nm.cancel(WEB_BADGE_NOTIFICATION_ID);
            return;
        }
        ensureChannels(context);
        if (Build.VERSION.SDK_INT >= 33
                && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            return;
        }
        String safeTitle = safe(title, "(SSD) SMPN4D");
        String safeBody = safe(body, "Ada notifikasi baru yang belum dibaca.");
        Intent open = new Intent(context, MainActivity.class)
                .addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP)
                .putExtra("push_kind", safe(kind, "pembinaan_new"))
                .putExtra("push_view", safe(view, "pembinaan"));
        PendingIntent contentIntent = PendingIntent.getActivity(
                context, WEB_BADGE_NOTIFICATION_ID, open,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
        Notification notification = new Notification.Builder(context, channelFor(kind))
                .setSmallIcon(R.drawable.ic_stat_notification)
                .setContentTitle(safeTitle)
                .setContentText(safeBody)
                .setStyle(new Notification.BigTextStyle().bigText(safeBody))
                .setAutoCancel(true)
                .setShowWhen(true)
                .setNumber(Math.max(1, unreadCount))
                .setOnlyAlertOnce(!alert)
                .setContentIntent(contentIntent)
                .build();
        nm.notify(WEB_BADGE_NOTIFICATION_ID, notification);
    }

'''
ss = ss.replace(method_marker, badge_method + method_marker, 1)
service.write_text(ss)

# Synchronize the native mirrored notification for both increases and decreases.
main = root / "app/src/main/java/id/sch/smpn4dumai/esiswa/MainActivity.java"
ms = main.read_text()
start = ms.index("    private void handleMirroredWebNotification(String raw) {")
end = ms.index("    private static final class PrintRequestData", start)
replacement = r'''    private void handleMirroredWebNotification(String raw) {
        try {
            JSONObject obj = new JSONObject(raw == null ? "{}" : raw);
            int count = Math.max(0, obj.optInt("notifyCount", 0));
            SharedPreferences prefs = getSharedPreferences(WEB_NOTIFICATION_PREFS, Context.MODE_PRIVATE);
            int previous = Math.max(0, prefs.getInt(KEY_LAST_WEB_BADGE_COUNT, 0));
            if (count == 0) {
                PushMessagingService.updateWebBadgeNotification(
                        this, "(SSD) SMPN4D", "", "pembinaan_new", "pembinaan", 0, false);
            } else if (count > previous) {
                showMirroredWebNotification(
                        obj.optString("title", "(SSD) SMPN4D"),
                        obj.optString("body", "Ada " + count + " notifikasi baru yang belum dibaca."),
                        obj.optString("kind", "pembinaan_new"),
                        obj.optString("view", "pembinaan"),
                        count,
                        true
                );
            } else if (count < previous) {
                showMirroredWebNotification(
                        obj.optString("title", "(SSD) SMPN4D"),
                        obj.optString("body", "Ada " + count + " notifikasi baru yang belum dibaca."),
                        obj.optString("kind", "pembinaan_new"),
                        obj.optString("view", "pembinaan"),
                        count,
                        false
                );
            }
            prefs.edit().putInt(KEY_LAST_WEB_BADGE_COUNT, count).apply();
        } catch (Exception ignored) {}
    }

    private void showMirroredWebNotification(String title, String body, String kind, String view,
                                             int count, boolean alert) {
        PushMessagingService.updateWebBadgeNotification(this, title, body, kind, view, count, alert);
    }

'''
ms = ms.slice(0,start) + replacement + ms.slice(end);
main.write_text(ms);

# Contract tests for Patch B, MONO98 installation and unread-count convergence.
''
s = p.read_text()
checks = {
    "10-minute window": "10L * 60L * 1000L" in s,
    "device-local persistence": 'getSharedPreferences(PREFS, Context.MODE_PRIVATE)' in s,
    "SHA-256 fingerprint": 'MessageDigest.getInstance("SHA-256")' in s,
    "whitespace normalization": 'replaceAll("\\\\s+", " ")' in s,
    "dedupe runs before notification creation": s.index("shouldSuppressDuplicatePopup(context, title, body)") < s.index("Notification notification ="),
    "existing FCM handler": "onMessageReceived(RemoteMessage message)" in s,
    "existing notification channels": all(x in s for x in ("CHANNEL_ATTENDANCE", "CHANNEL_COACHING", "CHANNEL_GENERAL")),
    "existing launcher badge count": ".setNumber(1)" in s,
    "existing token persistence": "storeToken(this, token)" in s and 'putString(KEY_TOKEN, token.trim())' in s,
}
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + " - " + name)
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("Patch B checks failed: " + ", ".join(failed))
print("PASS - Android version bumped to 1.1.3.5.12 / versionCode 22")
