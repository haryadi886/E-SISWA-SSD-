from pathlib import Path
import base64, re, sys

if len(sys.argv) != 3:
    raise SystemExit('usage: apply-v1.1.3.5.1-branding.py <project-dir> <logo-base64-file>')

root = Path(sys.argv[1]).resolve()
logo_b64 = Path(sys.argv[2]).resolve()


def replace(path, old, new, required=True):
    p = root / path
    s = p.read_text()
    if old not in s:
        if required:
            raise SystemExit(f'Expected text not found in {path}: {old!r}')
        return
    p.write_text(s.replace(old, new))

# Version: new installable branding baseline.
replace('app/build.gradle', 'versionCode 10', 'versionCode 11')
replace('app/build.gradle', "versionName '1.1.3.5'", "versionName '1.1.3.5.1'")

# App name and generic notification channel name.
replace('app/src/main/res/values/strings.xml', '<string name="app_name">E-SISWA (SSD)</string>', '<string name="app_name">(SSD) SMPN4D</string>')
replace('app/src/main/res/values/strings.xml', 'Notifikasi E-SISWA', 'Notifikasi (SSD) SMPN4D', required=False)

# Native notification fallback titles/bodies.
replace('app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java', 'safe(data.get("title"), "E-SISWA (SSD)")', 'safe(data.get("title"), "(SSD) SMPN4D")')
replace('app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java', 'safe(data.get("body"), "Ada notifikasi baru dari E-SISWA.")', 'safe(data.get("body"), "Ada notifikasi baru dari (SSD) SMPN4D.")')
replace('app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java', '.setContentTitle(safe(title, "E-SISWA (SSD)"))', '.setContentTitle(safe(title, "(SSD) SMPN4D"))')
replace('app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java', '.setContentText(safe(body, "Ada notifikasi baru dari E-SISWA."))', '.setContentText(safe(body, "Ada notifikasi baru dari (SSD) SMPN4D."))')
replace('app/src/main/java/id/sch/smpn4dumai/esiswa/PushMessagingService.java', '.setStyle(new Notification.BigTextStyle().bigText(safe(body, "Ada notifikasi baru dari E-SISWA.")))', '.setStyle(new Notification.BigTextStyle().bigText(safe(body, "Ada notifikasi baru dari (SSD) SMPN4D.")))')
replace('app/src/main/java/id/sch/smpn4dumai/esiswa/MainActivity.java', "title:'E-SISWA (SSD)'", "title:'(SSD) SMPN4D'", required=False)
replace('app/src/main/java/id/sch/smpn4dumai/esiswa/MainActivity.java', 'obj.optString("title", "E-SISWA (SSD)")', 'obj.optString("title", "(SSD) SMPN4D")', required=False)

# New user-supplied logo: launcher foreground + launch overlay.
logo_data = base64.b64decode(''.join(logo_b64.read_text().split()))
logo_path = root / 'app/src/main/res/drawable-nodpi/esiswa_logo.webp'
logo_path.write_bytes(logo_data)
if len(logo_data) < 10000:
    raise SystemExit('Decoded launcher logo is unexpectedly small.')
replace('app/src/main/res/layout/activity_main.xml', 'android:src="@drawable/launch_screen"', 'android:src="@drawable/esiswa_logo"')

# Keep regression suites valid for the new patch version.
p = root/'tools/test_v113_ui.py'; s=p.read_text(); s=s.replace("or (\"versionName '1.1.3.5'\" in build and 'versionCode 10' in build),", "or (\"versionName '1.1.3.5'\" in build and 'versionCode 10' in build) or (\"versionName '1.1.3.5.1'\" in build and 'versionCode 11' in build),"); p.write_text(s)
p = root/'tools/test_v1131_camera_print.py'; s=p.read_text(); s=s.replace("or (\"versionName '1.1.3.5'\" in build and 'versionCode 10' in build)),", "or (\"versionName '1.1.3.5'\" in build and 'versionCode 10' in build) or (\"versionName '1.1.3.5.1'\" in build and 'versionCode 11' in build)),"); p.write_text(s)
p = root/'tools/test_v1132_native_print_v2.py'; s=p.read_text(); s=s.replace("or (\"versionName '1.1.3.5'\" in build and 'versionCode 10' in build)),", "or (\"versionName '1.1.3.5'\" in build and 'versionCode 10' in build) or (\"versionName '1.1.3.5.1'\" in build and 'versionCode 11' in build)),"); p.write_text(s)
p = root/'tools/test_v112_permissions.py'; s=p.read_text(); s=s.replace("or (\"versionName '1.1.3.5'\" in b and 'versionCode 10' in b)),", "or (\"versionName '1.1.3.5'\" in b and 'versionCode 10' in b) or (\"versionName '1.1.3.5.1'\" in b and 'versionCode 11' in b)),"); p.write_text(s)
p = root/'tools/test_v1134_push_diagnostics.py'; s=p.read_text(); s=s.replace('"versionCode 9+":"versionCode 9" in gradle or "versionCode 10" in gradle,','"versionCode 9+":"versionCode 9" in gradle or "versionCode 10" in gradle or "versionCode 11" in gradle,'); s=s.replace('"versionName 1.1.3.4+":"versionName \'1.1.3.4\'" in gradle or "versionName \'1.1.3.5\'" in gradle,','"versionName 1.1.3.4+":"versionName \'1.1.3.4\'" in gradle or "versionName \'1.1.3.5\'" in gradle or "versionName \'1.1.3.5.1\'" in gradle,'); p.write_text(s)
p = root/'tools/test_v1135_print_state.py'; s=p.read_text(); s=s.replace("'version 1.1.3.5 code 10': \"versionName '1.1.3.5'\" in build and 'versionCode 10' in build,", "'version 1.1.3.5+ lineage': ((\"versionName '1.1.3.5'\" in build and 'versionCode 10' in build) or (\"versionName '1.1.3.5.1'\" in build and 'versionCode 11' in build)),"); p.write_text(s)
p = root/'tools/test_v1133_student_print_notifications.py'; s=p.read_text(); s=s.replace(r"versionName\s+'1\.1\.3(?:\.[0-9]+)?'", r"versionName\s+'1\.1\.3(?:\.[0-9]+){0,2}'"); p.write_text(s)

# Project verifier exact new version.
p = root/'tools/verify_project.py'; s=p.read_text(); s=s.replace("appgrad=need(Path('app/build.gradle'), \"versionName '1.1.3.5'\")", "appgrad=need(Path('app/build.gradle'), \"versionName '1.1.3.5.1'\")"); s=s.replace("VERIFY PASS: E-SISWA Android v1.1.3.5 project contract satisfied", "VERIFY PASS: (SSD) SMPN4D Android v1.1.3.5.1 project contract satisfied"); p.write_text(s)

# New branding-specific regression test.
(root/'tools/test_v11351_branding.py').write_text('''from pathlib import Path\nroot=Path(__file__).resolve().parents[1]\nstrings=(root/'app/src/main/res/values/strings.xml').read_text()\nbuild=(root/'app/build.gradle').read_text()\nlayout=(root/'app/src/main/res/layout/activity_main.xml').read_text()\nicon=root/'app/src/main/res/drawable-nodpi/esiswa_logo.webp'\nchecks={\n 'app name (SSD) SMPN4D':'<string name="app_name">(SSD) SMPN4D</string>' in strings,\n 'version 1.1.3.5.1 code 11':\"versionName '1.1.3.5.1'\" in build and 'versionCode 11' in build,\n 'new launcher logo nonempty':icon.exists() and icon.stat().st_size>10000,\n 'launch overlay uses new logo':'android:src="@drawable/esiswa_logo"' in layout,\n}\nbad=[k for k,v in checks.items() if not v]\nfor k,v in checks.items(): print(('PASS' if v else 'FAIL')+' - '+k)\nif bad: raise SystemExit('Branding regression failed: '+', '.join(bad))\nprint('PASS 4/4 branding checks')\n''')

# Light documentation refresh only.
for name in ['README.md','BUILDING.md']:
    p=root/name; s=p.read_text()
    s=s.replace('E-SISWA (SSD) Android v1.1.3.5','(SSD) SMPN4D Android v1.1.3.5.1')
    s=s.replace('`1.1.3.5` (versionCode 10)','`1.1.3.5.1` (versionCode 11)')
    p.write_text(s)

print('Branding patch applied: (SSD) SMPN4D v1.1.3.5.1 / versionCode 11')
