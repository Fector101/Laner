from pathlib import Path
from pythonforandroid.toolchain import ToolchainCL

def after_apk_build(toolchain: ToolchainCL):
    manifest_file = Path(toolchain._dist.dist_dir) / "src" / "main" / "AndroidManifest.xml"
    text = manifest_file.read_text(encoding="utf-8")

    package = toolchain.args.package
    target = f'android:name="{package}.ServiceMydownloader"'

    # -----------------------------
    # Inject foregroundServiceType
    # -----------------------------
    pos = text.find(target)
    if pos != -1:
        end = text.find("/>", pos)
        if end != -1:
            # Avoid double-adding
            if "foregroundServiceType=" not in text[pos:end]:
                text = (
                    text[:end] +
                    ' android:foregroundServiceType="dataSync"' +
                    text[end:]
                )
                print("✅ Added foregroundServiceType to ServiceMydownloader")
        else:
            print("⚠️ Service block found but no '/>' closing tag")
    else:
        print("⚠️ ServiceMydownloader not found in manifest")

    # ---------------------------------------
    # Always add your receiver (no early exit)
    # ---------------------------------------
    receiver_xml = '''
    <receiver android:name="org.laner.lan_ft.Action1"
              android:enabled="true"
              android:exported="false">
        <intent-filter>
            <action android:name="android.intent.action.BOOT_COMPLETED" />
        </intent-filter>
    </receiver>
    '''

    # Safe insertion: only if </application> exists
    if "</application>" in text:
        text = text.replace("</application>", f"{receiver_xml}\n</application>")
        print("✅ Receiver added")
    else:
        print("⚠️ Could not find </application> to insert receiver")

    # -----------------------------
    # Write back the final manifest
    # -----------------------------
    manifest_file.write_text(text, encoding="utf-8")
    print("🏁 Manifest update completed")