from pathlib import Path
from pythonforandroid.toolchain import ToolchainCL

def after_apk_build(toolchain: ToolchainCL):
    manifest_file = Path(toolchain._dist.dist_dir) / "src" / "main" / "AndroidManifest.xml"
    old_manifest = manifest_file.read_text(encoding="utf-8")

    # Your custom receiver XML
    receiver_xml = '''
    <receiver android:name="org.laner.lan_ft.Action1"
              android:enabled="true"
              android:exported="false">
        <intent-filter>
            <action android:name="android.intent.action.BOOT_COMPLETED" />
        </intent-filter>
    </receiver>
    '''

    # Insert before the closing </application>
    new_manifest = old_manifest.replace('</application>', f'{receiver_xml}\n</application>')

    manifest_file.write_text(new_manifest, encoding="utf-8")

    if old_manifest != new_manifest:
        print("✅ Receiver added successfully")
    else:
        print("⚠️ Failed to add receiver")