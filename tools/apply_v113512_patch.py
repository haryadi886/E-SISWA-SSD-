#!/usr/bin/env python3
from pathlib import Path

root = Path("project")
build = root / "app/build.gradle"
s = build.read_text()
assert "versionCode 21" in s and "versionName '1.1.3.5.11'" in s, "Unexpected Android baseline"
s = s.replace("versionCode 21", "versionCode 24", 1)
s = s.replace("versionName '1.1.3.5.11'", "versionName '1.1.3.5.14'", 1)
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
    permission_check + "        if (shouldSuppressDuplicatePopup(context, messageId)) return;\n",
    1,
)

marker = "    private static String channelFor(String kind) {"
assert marker in s
methods = r'''    /** Suppress only repeat deliveries carrying the same stable FCM message ID. */
    static boolean shouldSuppressDuplicatePopup(Context context, String messageId) {
        if (context == null) return false;
        String stableId = messageId == null ? "" : messageId.trim();
        // Without a stable ID, do not guess that two messages are duplicates:
        // legitimate notifications can have the same title and body.
        if (stableId.isEmpty()) return false;

        long now = System.currentTimeMillis();
        SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        String key = KEY_POPUP_DEDUPE_PREFIX + popupFingerprint(stableId);
        long previous = prefs.getLong(key, 0L);
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

    private static String popupFingerprint(String messageId) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(messageId.getBytes(StandardCharsets.UTF_8));
            StringBuilder out = new StringBuilder(digest.length * 2);
            for (byte b : digest) out.append(String.format(Locale.ROOT, "%02x", b & 0xff));
            return out.toString();
        } catch (Exception ignored) {
            return Integer.toHexString(messageId.hashCode());
        }
    }

'''
s = s.replace(marker, methods + marker, 1)
p.write_text(s)

# Preserve FCM notification payloads when title/body are not duplicated in data.
service_source = p.read_text()
old_handler = '''    @Override
    public void onMessageReceived(RemoteMessage message) {
        super.onMessageReceived(message);
        Map<String, String> data = message.getData();
        String title = safe(data.get("title"), "(SSD) SMPN4D");
        String body = safe(data.get("body"), "Ada notifikasi baru dari (SSD) SMPN4D.");
        String kind = safe(data.get("kind"), "general");
        String view = safe(data.get("view"), "dashboard");
        showLocalNotification(this, title, body, kind, view, message.getMessageId());
    }
'''
new_handler = '''    @Override
    public void onMessageReceived(RemoteMessage message) {
        super.onMessageReceived(message);
        Map<String, String> data = message.getData();
        RemoteMessage.Notification notificationPayload = message.getNotification();
        String title = firstNonBlank(data.get("title"),
                notificationPayload == null ? null : notificationPayload.getTitle(), "(SSD) SMPN4D");
        String body = firstNonBlank(data.get("body"),
                notificationPayload == null ? null : notificationPayload.getBody(),
                "Ada notifikasi baru dari (SSD) SMPN4D.");
        String kind = safe(data.get("kind"), "general");
        String view = safe(data.get("view"), "dashboard");
        showLocalNotification(this, title, body, kind, view, message.getMessageId());
    }
'''
assert old_handler in service_source, "Original FCM handler not found"
service_source = service_source.replace(old_handler, new_handler, 1)
safe_marker = "    private static String safe(String value, String fallback) {"
assert safe_marker in service_source, "safe helper insertion point missing"
first_non_blank = '''    private static String firstNonBlank(String primary, String secondary, String fallback) {
        if (primary != null && !primary.trim().isEmpty()) return primary.trim();
        if (secondary != null && !secondary.trim().isEmpty()) return secondary.trim();
        return fallback;
    }

'''
service_source = service_source.replace(safe_marker, first_non_blank + safe_marker, 1)
# Use the raw PNG resource directly for Notification.Builder. Avoid indirection
# through an XML BitmapDrawable, which can fail as a status-bar SmallIcon on
# some Android builds/OEM frameworks.
assert "R.drawable.ic_stat_notification" in service_source, "Notification icon insertion point missing"
service_source = service_source.replace(
    "R.drawable.ic_stat_notification",
    "R.drawable.esiswa_notification_monochrome"
)
p.write_text(service_source)

# Point Android's auto-rendered FCM notification icon directly at the PNG too.
manifest_path = root / "app/src/main/AndroidManifest.xml"
manifest = manifest_path.read_text()
assert '<meta-data' in manifest and 'android:resource="@drawable/ic_stat_notification"' in manifest, "Default FCM icon metadata not found"
manifest = manifest.replace(
    'android:resource="@drawable/ic_stat_notification"',
    'android:resource="@drawable/esiswa_notification_monochrome"',
    1
)
manifest_path.write_text(manifest)

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

# Add a stable native notification for the web unread-count mirror.
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
# Every native notification tap opens the Notification Center first; the user
# chooses an individual item there to navigate to its destination module.
ss = ss.replace('.putExtra("push_view", view)', '.putExtra("push_view", "notification_center")', 1)
ss = ss.replace('.putExtra("push_view", safe(view, "pembinaan"))', '.putExtra("push_view", "notification_center")', 1)
service.write_text(ss)

# Synchronize the native mirror on unread-count increases, decreases, and zero.
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
            } else if (count <= previous && count > 0) {
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
ms = ms[:start] + replacement + ms[end:]
main.write_text(ms)

# Contract tests for Patch B, MONO98 installation and unread-count convergence.
''
s = p.read_text()
checks = {
    "10-minute window": "10L * 60L * 1000L" in s,
    "device-local persistence": 'getSharedPreferences(PREFS, Context.MODE_PRIVATE)' in s,
    "SHA-256 fingerprint": 'MessageDigest.getInstance("SHA-256")' in s,
    "dedupe keyed to stable message ID": "shouldSuppressDuplicatePopup(Context context, String messageId)" in s,
    "dedupe runs before notification creation": s.index("shouldSuppressDuplicatePopup(context, messageId)") < s.index("Notification notification ="),
    "FCM notification payload fallback": "notificationPayload.getTitle()" in s and "notificationPayload.getBody()" in s,
    "existing FCM handler": "onMessageReceived(RemoteMessage message)" in s,
    "existing notification channels": all(x in s for x in ("CHANNEL_ATTENDANCE", "CHANNEL_COACHING", "CHANNEL_GENERAL")),
    "existing launcher badge count": ".setNumber(1)" in s,
    "existing token persistence": "storeToken(this, token)" in s and 'putString(KEY_TOKEN, token.trim())' in s,
}
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + " - " + name)
main_source = (root / "app/src/main/java/id/sch/smpn4dumai/esiswa/MainActivity.java").read_text()
checks.update({
    "exact MONO98 asset installed": asset_target.is_file() and hashlib.sha256(asset_target.read_bytes()).hexdigest() == "a7b402ce4add2c3be053d33037dbd3aecc3d59f097162305229d04259d50d161",
    "Notification.Builder points directly to MONO98 PNG": "R.drawable.esiswa_notification_monochrome" in s and "R.drawable.ic_stat_notification" not in s,
    "FCM manifest icon points directly to MONO98 PNG": 'android:resource="@drawable/esiswa_notification_monochrome"' in manifest_path.read_text() and 'android:resource="@drawable/ic_stat_notification"' not in manifest_path.read_text(),
    "dynamic unread count on mirrored notification": ".setNumber(Math.max(1, unreadCount))" in s,
    "stable mirrored notification id": "nm.notify(WEB_BADGE_NOTIFICATION_ID, notification)" in s,
    "zero unread cancels mirrored notification": "nm.cancel(WEB_BADGE_NOTIFICATION_ID)" in s and "if (count == 0)" in main_source,
    "decreasing or unchanged unread count synchronizes mirror": "else if (count <= previous && count > 0)" in main_source,
    "native notification taps route to Notification Center": s.count('.putExtra("push_view", "notification_center")') >= 2,
})
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("Patch B checks failed: " + ", ".join(failed))
print("PASS - Android version bumped to 1.1.3.5.14 / versionCode 24")
