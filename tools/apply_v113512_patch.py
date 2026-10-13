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

# Contract tests for Patch B and preservation of existing push behavior.
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
