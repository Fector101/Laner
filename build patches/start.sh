python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# For Debugging
buildozer android debug && adb install bin/lan_ft-1.0-arm64-v8a_armeabi-v7a-debug.apk && adb shell monkey -p org.laner.lan_ft 1 && adb logcat | grep python