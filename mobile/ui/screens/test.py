from jnius import autoclass, cast
import os
import time

from utils.helper import getAppFolder as makeDownloadFolder
print(makeDownloadFolder(),"***""")
def get_content_uri_for_file(file_path):
    """Convert file path to content URI using FileProvider to avoid FileUriExposedException"""
    try:
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        context = PythonActivity.mActivity
        
        # Try FileProvider first (Android 7.0+)
        try:
            FileProvider = autoclass('androidx.core.content.FileProvider')
            file_obj = autoclass('java.io.File')(file_path)
            authority = context.getPackageName() + ".fileprovider"
            content_uri = FileProvider.getUriForFile(context, authority, file_obj)
            return content_uri
        except:
            # Fallback to regular file URI for older Android versions
            sound_file = autoclass('java.io.File')(file_path)
            sound_uri = autoclass('android.net.Uri').fromFile(sound_file)
            return sound_uri
            
    except Exception as e:
        print(f"Content URI conversion failed: {e}")
        return None

def use_file_from_storage(file_path):
    """Use a sound file from device storage safely"""
    # Use the safe method that handles FileUriExposedException
    return get_content_uri_for_file(file_path)

def create_notification_channel(channel_id, channel_name, sound_uri=None):
    """Create a notification channel with optional custom sound"""
    Context = autoclass('android.content.Context')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    NotificationManager = autoclass('android.app.NotificationManager')
    NotificationChannel = autoclass('android.app.NotificationChannel')
    
    context = PythonActivity.mActivity
    notification_manager = context.getSystemService(Context.NOTIFICATION_SERVICE)
    
    # Check if channel already exists (Android O+)
    if hasattr(NotificationManager, 'getNotificationChannel'):
        try:
            existing_channel = notification_manager.getNotificationChannel(channel_id)
            if existing_channel:
                return channel_id
        except:
            pass
    
    # For Android O+ (API 26+) create notification channel
    if hasattr(NotificationManager, 'IMPORTANCE_DEFAULT'):
        importance = NotificationManager.IMPORTANCE_DEFAULT
        channel = NotificationChannel(channel_id, channel_name, importance)
        channel.setDescription("Notifications with custom sounds")
        
        # Set custom sound if provided
        if sound_uri:
            try:
                AudioAttributes = autoclass('android.media.AudioAttributes')
                AudioAttributesBuilder = autoclass('android.media.AudioAttributes$Builder')
                
                audio_attributes = AudioAttributesBuilder().setUsage(
                    AudioAttributes.USAGE_NOTIFICATION
                ).setContentType(
                    AudioAttributes.CONTENT_TYPE_SONIFICATION
                ).build()
                
                channel.setSound(sound_uri, audio_attributes)
            except Exception as e:
                print(f"Warning: Could not set custom sound: {e}")
        
        # Configure other channel settings (with proper error handling)
        try:
            channel.enableLights(True)
            channel.enableVibration(True)
            # Use a valid color integer (ARGB format)
            channel.setLightColor(0x000000FF)  # Blue light (fixed integer value)
        except Exception as e:
            print(f"Warning: Some channel features not available: {e}")
        
        try:
            notification_manager.createNotificationChannel(channel)
        except Exception as e:
            print(f"Warning: Could not create notification channel: {e}")
    
    return channel_id

def send_custom_sound_notification(channel_id, title, message, sound_uri):
    """Send a notification with custom sound"""
    Context = autoclass('android.content.Context')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    
    context = PythonActivity.mActivity
    current_activity = PythonActivity.mActivity
    
    # Create intent for when notification is clicked
    Intent = autoclass('android.content.Intent')
    PendingIntent = autoclass('android.app.PendingIntent')
    
    # Correct way to get the current activity class
    try:
        intent = Intent(context, current_activity.getClass())
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK)
        
        # Use FLAG_IMMUTABLE for newer Android versions, fallback for older
        try:
            pending_intent = PendingIntent.getActivity(
                context, 0, intent, 
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
            )
        except:
            pending_intent = PendingIntent.getActivity(
                context, 0, intent, 
                PendingIntent.FLAG_UPDATE_CURRENT
            )
    except Exception as e:
        print(f"Warning: Could not create pending intent: {e}")
        pending_intent = None
    
    # Use standard Android Notification.Builder (not androidx)
    builder = None
    try:
        # Try standard Android Notification.Builder first
        NotificationBuilder = autoclass('android.app.Notification$Builder')
        builder = NotificationBuilder(context, channel_id)
    except:
        try:
            # Fallback for older Android versions
            NotificationBuilder = autoclass('android.app.NotificationBuilder')
            builder = NotificationBuilder(context)
        except:
            print("Warning: Could not create Notification Builder")
    
    if builder:
        # Get app icon - handle different ways to get it
        try:
            app_info = context.getApplicationInfo()
            icon_id = app_info.icon
        except:
            try:
                # Fallback icon
                android = autoclass('android.R$drawable')
                icon_id = android.sym_def_app_icon
            except:
                icon_id = 0  # Default system icon
        
        # Set notification properties
        builder.setContentTitle(str(title))
        builder.setContentText(str(message))
        if icon_id:
            builder.setSmallIcon(icon_id)
        
        if pending_intent:
            builder.setContentIntent(pending_intent)
        
        builder.setAutoCancel(True)
        
        # Set custom sound
        if sound_uri:
            try:
                builder.setSound(sound_uri)
            except Exception as e:
                print(f"Warning: Could not set notification sound: {e}")
        
        # Build and show notification
        try:
            notification = builder.build()
        except:
            # Fallback for older Android versions
            notification = builder.getNotification()
    else:
        # Create basic notification as last resort
        try:
            Notification = autoclass('android.app.Notification')
            notification = Notification()
            notification.icon = context.getApplicationInfo().icon
            notification.tickerText = str(title)
            notification.when = time.time() * 1000  # Convert to milliseconds
            notification.flags = Notification.FLAG_AUTO_CANCEL
            
            if pending_intent and hasattr(notification, 'setLatestEventInfo'):
                notification.setLatestEventInfo(
                    context, str(title), str(message), pending_intent
                )
            
            if sound_uri:
                notification.sound = sound_uri
                
        except Exception as e:
            print(f"Error creating basic notification: {e}")
            return None
    
    # Show notification
    try:
        notification_manager = context.getSystemService(Context.NOTIFICATION_SERVICE)
        notification_id = int(time.time())  # Simple unique ID
        notification_manager.notify(notification_id, notification)
        return notification_id
    except Exception as e:
        print(f"Error showing notification: {e}")
        return None

def get_common_storage_locations():
    """Get common storage paths where audio files might be located"""
    Context = autoclass('android.content.Context')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Environment = autoclass('android.os.Environment')
    
    context = PythonActivity.mActivity
    
    locations = {}
    
    try:
        # Primary external storage
        if Environment.getExternalStorageState() == Environment.MEDIA_MOUNTED:
            locations['downloads'] = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_DOWNLOADS
            ).getAbsolutePath()
            locations['music'] = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_MUSIC
            ).getAbsolutePath()
            locations['notifications'] = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_NOTIFICATIONS
            ).getAbsolutePath()
    except:
        pass
    
    # App-specific directories
    try:
        locations['app_files'] = context.getExternalFilesDir(None).getAbsolutePath()
        locations['app_cache'] = context.getExternalCacheDir().getAbsolutePath()
    except:
        pass
    
    # Internal storage fallbacks
    try:
        locations['internal_files'] = context.getFilesDir().getAbsolutePath()
    except:
        pass
    
    return locations

def get_safe_sound_uri():
    """Get a sound URI that won't cause FileUriExposedException"""
    # Try to use the sneeze.wav file safely
    sound_path = os.path.join(makeDownloadFolder(), "assets", "audio", "sneeze.wav")
    
    if os.path.exists(sound_path):
        print(f"🔊 Found sound file: {sound_path}")
        # Use the safe method that handles FileProvider
        sound_uri = use_file_from_storage(sound_path)
        if sound_uri:
            return sound_uri
        else:
            print("⚠️ Could not create safe URI for sound file")
    else:
        print(f"⚠️ Sound file not found: {sound_path}")
    
    # Fallback to system default sound
    print("🔊 Using system default sound as fallback")
    return None

def example_usage():
    """Demonstrate different ways to use custom sound files"""
    
    print("🚀 Starting notification tests...")
    
    # Get storage locations
    storage_locs = get_common_storage_locations()
    print(f"📁 Available locations: {list(storage_locs.keys())}")
    
    # Test 1: Try using the sneeze.wav file safely
    try:
        sound_uri = get_safe_sound_uri()
        
        if sound_uri:
            channel_id = create_notification_channel(
                "test_channel_1", 
                "Test Notifications", 
                sound_uri
            )
            notification_id = send_custom_sound_notification(
                channel_id,
                "Custom Sound Test",
                "Using sneeze.wav sound",
                sound_uri
            )
            if notification_id:
                print(f"✅ Notification sent with ID: {notification_id}")
                return  # Success - stop after first successful test
            else:
                print("❌ Failed to send notification")
        else:
            print("❌ No sound URI available")
            
    except Exception as e:
        print(f"❌ Notification test 1 failed: {e}")
    
    # Test 2: Try without custom sound (system default)
    try:
        channel_id = create_notification_channel(
            "test_channel_2",
            "Default Sound Notifications", 
            None  # No custom sound
        )
        notification_id = send_custom_sound_notification(
            channel_id,
            "Default Sound Test",
            "This should use system default sound",
            None
        )
        if notification_id:
            print(f"✅ Default sound notification sent with ID: {notification_id}")
        else:
            print("❌ Failed to send default sound notification")
    except Exception as e:
        print(f"❌ Default sound test failed: {e}")
    
    # Test 3: Basic notification without channel (for older Android)
    try:
        Context = autoclass('android.content.Context')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Notification = autoclass('android.app.Notification')
        NotificationManager = autoclass('android.app.NotificationManager')
        
        context = PythonActivity.mActivity
        notification_manager = context.getSystemService(Context.NOTIFICATION_SERVICE)
        
        # Create very basic notification
        notification = Notification()
        notification.flags = Notification.FLAG_AUTO_CANCEL
        
        # Try to set basic properties
        try:
            # For older Android versions
            notification.icon = context.getApplicationInfo().icon
            notification.tickerText = "Basic Test"
            notification.when = time.time() * 1000
        except:
            pass
        
        notification_id = int(time.time())
        notification_manager.notify(notification_id, notification)
        print(f"✅ Basic notification sent with ID: {notification_id}")
        
    except Exception as e:
        print(f"❌ Basic notification test failed: {e}")

def list_available_sound_files():
    """Find and list available sound files in common locations"""
    storage_locs = get_common_storage_locations()
    sound_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.aac']
    found_files = {}
    
    for location_name, path in storage_locs.items():
        if os.path.exists(path):
            try:
                files = os.listdir(path)
                sound_files = [
                    f for f in files 
                    if any(f.lower().endswith(ext) for ext in sound_extensions)
                ]
                if sound_files:
                    found_files[location_name] = [
                        os.path.join(path, f) for f in sound_files[:5]  # Limit to 5 files per location
                    ]
            except (OSError, PermissionError) as e:
                print(f"⚠️ Cannot access {location_name}: {e}")
                continue
    
    return found_files

# Main execution
if __name__:
    print("🔊 Custom Sound Notification Demo")
    print("=" * 40)
    
    # List available sound files
    print("\n📁 Searching for sound files...")
    available_sounds = list_available_sound_files()
    
    if available_sounds:
        print("✅ Found sound files:")
        for location, files in available_sounds.items():
            print(f"  📂 {location}: {len(files)} files")
            for file_path in files:
                print(f"    🎵 {os.path.basename(file_path)}")
    else:
        print("❌ No sound files found in accessible locations")
    
    # Run examples
    print("\n🚀 Sending test notifications...")
    time.sleep(2)
    example_usage()
    
    print