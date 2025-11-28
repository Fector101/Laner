from kivy.app import App
from jnius import autoclass
from android_notify import Notification
import os

def n(t):
    Notification(message=t).send()

APK_PATH = "/storage/emulated/0/Download/Laner/app.apk"
OUTPUT_PATH = "/storage/emulated/0/Download/Laner/icons/icon.png"

def extract_icon():
    try:
        n("Loading classes...")

        PackageManager = autoclass('android.content.pm.PackageManager')
        Bitmap = autoclass('android.graphics.Bitmap')
        BitmapConfig = autoclass('android.graphics.Bitmap$Config')
        BitmapCompressFormat = autoclass('android.graphics.Bitmap$CompressFormat')
        Canvas = autoclass('android.graphics.Canvas')
        FileOutputStream = autoclass('java.io.FileOutputStream')

        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        pm = context.getPackageManager()

        n("Reading APK...")

        package_info = pm.getPackageArchiveInfo(APK_PATH, PackageManager.GET_META_DATA)
        if not package_info:
            n("Cannot read APK!")
            return

        app_info = package_info.applicationInfo
        app_info.sourceDir = APK_PATH
        app_info.publicSourceDir = APK_PATH

        n("Loading icon...")

        icon_drawable = app_info.loadIcon(pm)

        width = icon_drawable.getIntrinsicWidth()
        height = icon_drawable.getIntrinsicHeight()

        bitmap = Bitmap.createBitmap(width, height, BitmapConfig.ARGB_8888)
        canvas = Canvas(bitmap)
        icon_drawable.setBounds(0, 0, width, height)
        icon_drawable.draw(canvas)

        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

        fos = FileOutputStream(OUTPUT_PATH)
        bitmap.compress(BitmapCompressFormat.PNG, 100, fos)
        fos.close()

        n(f"Icon saved:\n{OUTPUT_PATH}")

    except Exception as e:
        n(f"Error:\n{e}")

if __name__ == "__main__":
    extract_icon()