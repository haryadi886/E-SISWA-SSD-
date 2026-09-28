from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
build=(root/'app/build.gradle').read_text()
layout=(root/'app/src/main/res/layout/activity_main.xml').read_text()
fg=(root/'app/src/main/res/drawable/ic_launcher_foreground.xml').read_text()
icon=root/'app/src/main/res/drawable-nodpi/esiswa_logo.webp'
splash=root/'app/src/main/res/drawable-nodpi/launch_screen.jpg'
checks={
 'version 1.1.3.5.4':"versionName '1.1.3.5.4'" in build and 'versionCode 14' in build,
 'launcher asset exists':icon.exists() and icon.stat().st_size>20000,
 'splash asset exists':splash.exists() and splash.stat().st_size>10000,
 'launcher foreground uses esiswa_logo':'@drawable/esiswa_logo' in fg,
 'launcher safe inset':'android:insetLeft="18dp"' in fg and 'android:insetTop="18dp"' in fg,
 'launch overlay uses launch_screen':'android:src="@drawable/launch_screen"' in layout,
 'launcher and splash separated':'android:src="@drawable/esiswa_logo"' not in layout,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(('PASS' if v else 'FAIL')+' - '+k)
if bad: sys.exit('Branding R7 v1.1.3.5.4 failed: '+', '.join(bad))
print('PASS',len(checks),'/',len(checks),'R7 branding checks')
