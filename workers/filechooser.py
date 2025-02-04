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
        
        if platform == 'android' and not self.waiting:
            self.waiting = True
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("*/*")
            chooseFile = Intent.createChooser(intent, cast( 'java.lang.CharSequence', String("FileChooser") ))
            mActivity.startActivityForResult(chooseFile, 123456)
        else:
            self.callback(None,None)
    @classmethod
    def __parse_choice(cls, request_code, result_code, intent):
        """parse users choice

        Args:
            received_code (int): _description_
            result_code (int): _description_
            intent (Intebt): _description_

        Returns:
           list: [file_name, file_data]
        """
        instance = cls._instance
        cls.waiting = False
        print(instance,'||',request_code,'||',result_code,'||', intent)
        if result_code == -1:
            uri = intent.getData()
            print('enrypted path',uri.getPath())
            print('enrypted stuff ',uri.toString())
            try:
                file_path = instance.__get_file_path(uri)
                print('file path ',file_path)
            except Exception as e:
                print('File path error 101',e)

            instance.file_name = instance.__get_file_name(uri)
            instance.__read_file_data( instance.__open_input_stream(uri))

    def __open_input_stream(self,uri):
        """
        Open an InputStream from the given content URI.
        Returns a Java InputStream.
        """
        content_resolver = mActivity.getContentResolver()
        return content_resolver.openInputStream(uri)

    def __read_file_data(self, input_stream):
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

    def __get_file_name(self,uri):
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
    def __get_file_path(self,uri):
        """ Attempt to resolve the file path from the content URI. """
        if not uri:
            return None
        # Check if the URI is a document URI
        selection = "_id=?"
        selection_args=[]
        if DocumentsContract.isDocumentUri(mActivity, uri):
            # Extract the document ID
            doc_id = DocumentsContract.getDocumentId(uri)

            print('doc_id --->',doc_id)
            # Handle different URI authorities
            if uri.getAuthority() == "com.android.providers.media.documents":
                # Media documents (e.g., images, videos)
                id__ = doc_id.split(":")[1]
                selection_args = [id__]

                if doc_id.startswith("image:"):
                    uri = Uri.parse("content://media/external/images/media")

                elif doc_id.startswith("video:"):
                    uri = Uri.parse("content://media/external/video/media")

                elif doc_id.startswith("audio:"):
                    uri = Uri.parse("content://media/external/audio/media")
                    
                elif doc_id.startswith("document:"):
                    uri = Uri.parse("content://media/external/documents/media")
                    
                # TODO follow pattern for "document" section
        if selection and selection_args:
            # Query the URI to get the file path
            content_resolver = mActivity.getContentResolver()
            cursor = content_resolver.query(uri, None, selection, selection_args, None)
            if cursor:
                try:
                    if cursor.moveToFirst():
                        # Column index for the data (file path)
                        data_index = cursor.getColumnIndex("_data")
                        if data_index != -1:
                            return cursor.getString(data_index)
                finally:
                    cursor.close()

        # Fallback: Return None if the file path cannot be resolved
        return None
