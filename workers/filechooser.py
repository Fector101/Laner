""" Android File Chooser """

from datetime import datetime
import threading
# from concurrent.futures import ThreadPoolExecutor
from kivy.utils import platform
from kivy.clock import Clock

if platform == 'android':
    from jnius import autoclass,cast
    from android import activity,mActivity
    from android.activity import bind as android_bind
    DocumentsContract = autoclass('android.provider.DocumentsContract')
    BufferedInputStream = autoclass('java.io.BufferedInputStream')
    ByteArrayOutputStream = autoclass('java.io.ByteArrayOutputStream')
    Intent = autoclass('android.content.Intent')
    String = autoclass('java.lang.String')
    Uri = autoclass('android.net.Uri')
    
    # from android.os import Build
    # if Build.VERSION.SDK_INT >= 29:
    #     uri = MediaStoreFiles.getContentUri("external")
    # else:
    #     uri = autoclass('android.provider.MediaStore').Images.Media.EXTERNAL_CONTENT_URI
    
else:
    cast={}
    autoclass={}
    activity={}
    mActivity={}
    android_bind={}
    Intent={}
    String={}
    Uri={}
    DocumentsContract ={}
    BufferedInputStream ={}
    ByteArrayOutputStream ={}





class AndroidFileChooser:
    _instance = None
    waiting = False
    def __new__(cls,callback):
        """Will be called everytime new instance created"""
        if not cls._instance and platform == 'android':
            cls._instance = super().__new__(cls)
            android_bind(on_activity_result=cls.__parse_choice)
            cls._instance.initialized_at = datetime.now()
            
        return cls._instance

    def __init__(self,callback):
        """Will called every time initialized"""
        self.file_name = None
        self.callback = callback
        
        if platform == 'android' and not self._instance.waiting:
            self._instance.waiting = True
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("*/*")
            chooseFile = Intent.createChooser(intent, cast( 'java.lang.CharSequence', String("FileChooser") ))
            mActivity.startActivityForResult(chooseFile, 123456)
        
    @classmethod
    def __parse_choice(cls, request_code, result_code, intent):
        """parse users choice

        Args:
            received_code (int): _description_
            result_code (int): _description_
            intent (Intent): _description_

        Returns:
           list: [file_name, file_data]
        """
        instance = cls._instance
        cls._instance.waiting = False
        # print(instance,'||',request_code,'||',result_code,'||', intent)
        if result_code == -1:
            uri = intent.getData()
            # print('enrypted path',uri.getPath())
            print('enrypted stuff ',uri.toString())
            try:
                file_path = instance.__get_file_path(uri)
                print('file path ',file_path)
            except Exception as e:
                print('File path error 101',e)

            instance.file_name = instance.__get_file_name(uri)
            instance.__read_file_data( instance.__open_input_stream(uri))

    def __open_input_stream(self,uri): # pylint: disable=unused-private-member
        """
        Open an InputStream from the given content URI.
        Returns a Java InputStream.
        """
        content_resolver = mActivity.getContentResolver()
        return content_resolver.openInputStream(uri)

    def __read_file_data(self, input_stream):  # pylint: disable=unused-private-member
        """
        Read file data asynchronously while still returning the data.
        
        Args:
            input_stream: Java InputStream to read from
        
        Returns:
            bytes: File data
        """
        
        def read_data():
            try:
                buffered_input_stream = BufferedInputStream(input_stream)
                byte_array_output_stream = ByteArrayOutputStream()

                # Read the file data in chunks
                buffer = bytearray(1024)
                length = 0
                while (length := buffered_input_stream.read(buffer)) != -1:
                    byte_array_output_stream.write(buffer, 0, length)

                # Convert the ByteArrayOutputStream to a Python bytes object
                byte_array = byte_array_output_stream.toByteArray()
                file_data = bytes(byte_array)
                Clock.schedule_once(lambda dt: self.callback(self.file_name,file_data))
            except Exception as e:
                print(f"File reading error: {e}")
                return None
        threading.Thread(target=read_data).start()

    def __get_file_name(self,uri): # pylint: disable=unused-private-member
        """
        Query the ContentResolver to get the file name from the URI.
        """
        content_resolver = mActivity.getContentResolver()
        cursor = content_resolver.query(uri, None, None, None, None)
        if cursor:
            if cursor.moveToFirst():
                # Column index for the display name
                display_name_index = cursor.getColumnIndex("_display_name")
                if display_name_index != -1:
                    return cursor.getString(display_name_index)
            cursor.close()
        return None
    def __get_file_path(self, uri): # pylint: disable=unused-private-member
        """ Attempt to resolve the file path from the content URI. """
        if not uri:
            return None
        MediaStore = autoclass('android.provider.MediaStore')
        
        MediaStoreFiles = autoclass('android.provider.MediaStore$Files')
        ContentUris = autoclass('android.content.ContentUris')
        import os
        # Handle "raw" file URIs (e.g., file:///sdcard/...)
        if uri.getScheme() == "file":
            return uri.getPath()

        # Handle document URIs
        if DocumentsContract.isDocumentUri(mActivity, uri):
            doc_id = DocumentsContract.getDocumentId(uri)
            authority = uri.getAuthority()
            print('authority ',authority)
            if authority == "com.android.providers.media.documents":
                # Media files
                id_part = doc_id.split(":")[1]
                media_type = doc_id.split(":")[0]
                print("media_type --->",media_type)
                uri = {
                    "image": autoclass('android.provider.MediaStore$Images$Media').EXTERNAL_CONTENT_URI,
                    "video": autoclass('android.provider.MediaStore$Video$Media').EXTERNAL_CONTENT_URI,
                    "audio": autoclass('android.provider.MediaStore$Audio$Media').EXTERNAL_CONTENT_URI
                }.get(media_type,  MediaStoreFiles.getContentUri("external"))
                uri = ContentUris.withAppendedId(uri, int(id_part))

            elif authority == "com.android.providers.downloads.documents":
                # Downloads
                uri = ContentUris.withAppendedId(
                    Uri.parse("content://downloads/public_downloads"),
                    int(doc_id)
                )

            elif authority == "com.android.externalstorage.documents":
                # External storage (SD cards, USB drives)
                parts = doc_id.split(":")
                print('parts --->',parts)
                try:
                    print('getParent ',mActivity.getExternalFilesDir().getParent())
                    print('getParentNone ', mActivity.getExternalFilesDir(None).getParent())
                    print('getExternalFilesDir ',mActivity.getExternalFilesDir(None))
                except Exception as e:
                    print('ededede',e)
                if parts[0] == "primary":
                    return os.path.join(
                        mActivity.getExternalFilesDir(None).getParent(),  # /storage/emulated/0
                        parts[1]
                    )

            # Query the URI
            print("uri ---> ",uri)
            cursor = mActivity.getContentResolver().query(
                uri, 
                ['_data'],  # _data column
                # [MediaStore.MediaColumns.DATA],  # _data column
                None, None, None
            )
            if cursor:
                try:
                    if cursor.moveToFirst():
                        return cursor.getString(0)
                finally:
                    cursor.close()

        # Fallback: Use FileDescriptor (Android 10+ compatible)
        try:
            fd = mActivity.getContentResolver().openFileDescriptor(uri, "r")
            print('using last restort ',fd)
            return fd.getFileDescriptor().toString()  # Not a real path, but a reference
        except Exception as e:
            print(f"Fallback failed: {e}")

        return None

if __name__ == '__main__':
    print(999)
    def test(file_name,file_data):
        print("file_name ",file_name,"file_data ",file_data)
    AndroidFileChooser(test)