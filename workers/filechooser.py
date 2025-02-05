""" Android File Chooser """

from datetime import datetime
import os
import traceback
import threading
from kivy.utils import platform
from kivy.clock import Clock

# pylint: disable=broad-exception-caught,bare-except

if platform == 'android':
    # pylint: disable=no-name-in-module
    from jnius import autoclass,cast,JavaException
    from android import activity,mActivity #pylint: disable=unused-import
    from android.activity import bind as android_bind
    DocumentsContract = autoclass('android.provider.DocumentsContract')
    BufferedInputStream = autoclass('java.io.BufferedInputStream')
    ByteArrayOutputStream = autoclass('java.io.ByteArrayOutputStream')
    Intent = autoclass('android.content.Intent')
    Long = autoclass('java.lang.Long')
    String = autoclass('java.lang.String')
    Uri = autoclass('android.net.Uri')
    ContentUris = autoclass('android.content.ContentUris')

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
    JavaException = None #pylint: disable=invalid-name


class AndroidFileChooser:
    """File Chooser that returns file data and name"""
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
        self.file_path = None
        self.file_name = None
        self.callback = callback
        
        if platform == 'android' and not self._instance.waiting:
            self._instance.waiting = True
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("*/*")
            chooseFile = Intent.createChooser(intent, cast( 'java.lang.CharSequence', String("FileChooser") ))
            mActivity.startActivityForResult(chooseFile, 123456)
        
    @classmethod
    def __parse_choice(cls, _, result_code, intent):
        """parse users choice

        Args:
            received_code (int): _description_
            result_code (int): _description_
            intent (Intent): _description_

        Returns:
           list: [file_name, file_data]
        """
        # pylint: disable=protected-access, bare-except
        instance = cls._instance
        cls._instance.waiting = False
        if result_code == -1:
            uri = intent.getData()
            
            # print('enrypted stuff ',uri.toString())
            try:
                instance.file_path = instance.__get_file_path(uri)
            except:
                traceback.format_exc()
                print('File path error 101')

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
                Clock.schedule_once(lambda dt: self.callback(self.file_name,file_data,self.file_path))
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
    @staticmethod
    def _handle_downloads_documents(uri):
        '''
        Selection from the system filechooser when using ``Downloads``
        option from menu. Might not work all the time due to:

        1) invalid URI:

        jnius.jnius.JavaException:
            JVM exception occurred: Unknown URI:
            content://downloads/public_downloads/1034

        2) missing URI / android permissions

        jnius.jnius.JavaException:
            JVM exception occurred:
            Permission Denial: reading
            com.android.providers.downloads.DownloadProvider uri
            content://downloads/all_downloads/1034 from pid=2532, uid=10455
            requires android.permission.ACCESS_ALL_DOWNLOADS,
            or grantUriPermission()

        Workaround:
            Selecting path from ``Phone`` -> ``Download`` -> ``<file>``
            (or ``Internal storage``) manually.

        .. versionadded:: 1.4.0
        '''
        # pylint: disable=protected-access
        from plyer.platforms.android.filechooser import AndroidFileChooser as plyerChooser
        # known locations, differ between machines
        downloads = [
            'content://downloads/public_downloads',
            'content://downloads/my_downloads',

            # all_downloads requires separate permission
            # android.permission.ACCESS_ALL_DOWNLOADS
            'content://downloads/all_downloads'
        ]
        try:    
            file_id = DocumentsContract.getDocumentId(uri)
            try_uris = [ ]
            for down in downloads:
                print('file_id ',file_id)
                # try:
                #     int_stuff=Long.valueOf(file_id.split(':')[-1])
                #     print('first int_stuff',int_stuff)
                # except Exception as e:
                #     print('file id stuff',e)
                int_stuff=int(file_id.split(':')[-1])
                uri_stuff = Uri.parse(down)
                print('int_stuff ',int_stuff,'uri_stuff ',uri_stuff)
                try_uris.append(ContentUris.withAppendedId(uri_stuff, int_stuff ))
        except:
            traceback.print_exc()
            return
        # try all known Download folder uris
        # and handle JavaExceptions due to different locations
        # for content:// downloads or missing permission
        path = None
        for down in try_uris:
            try:
                
                # path = plyerChooser._parse_content(
                #     uri=down, projection=['_data'],
                #     selection=None,
                #     selection_args=None,
                #     sort_order=None
                # )
                cursor = mActivity.getContentResolver().query(
                    uri, 
                    ['_data'],  # _data column
                    # [MediaStore.MediaColumns.DATA],  # _data column
                    None, None, None
                )
                if cursor and cursor.moveToFirst():
                    path = cursor.getString(0)

            except JavaException:
                traceback.print_exc()
            finally:
                if cursor:
                    cursor.close()
            print('This is path ',path)
            # we got a path, ignore the rest
            if path:
                break

        # alternative approach to Downloads by joining
        # all data items from Activity result
        if not path:
            for down in try_uris:
                try:
                    path = plyerChooser._parse_content(
                        uri=down, projection=None,
                        selection=None,
                        selection_args=None,
                        sort_order=None,
                        index_all=True
                    )

                except JavaException:
                    traceback.print_exc()

                # we got a path, ignore the rest
                if path:
                    break
        return path
    def __get_file_path(self, uri): # pylint: disable=unused-private-member
        """ Attempt to resolve the file path from the content URI. """
        if not uri:
            return None
        # MediaStore = autoclass('android.provider.MediaStore')
        Environment = autoclass('android.os.Environment')
        
        MediaStoreFiles = autoclass('android.provider.MediaStore$Files')
        
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
                print('working doc_id ---> ',doc_id,'working id_part --> ',  int(id_part))
                uri = ContentUris.withAppendedId(uri, int(id_part))

            elif authority == "com.android.providers.downloads.documents":
                # Downloads
                return self._handle_downloads_documents(uri)
                # uri = ContentUris.withAppendedId(
                #     Uri.parse("content://downloads/public_downloads"),
                #     int(doc_id)
                # )

            elif authority == "com.android.externalstorage.documents":
                # External storage (SD cards, USB drives)
                parts = doc_id.split(":")
                if parts[0] == "primary":
                    return os.path.join(
                        Environment.getExternalStorageDirectory().getAbsolutePath(),
                        parts[1]
                    )

            # Query the URI
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
