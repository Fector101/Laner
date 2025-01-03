# How to Use Laner

Laner is a fast and secure file-sharing application that allows seamless file transfer between your PC and phone and vice-verse over a local network. Here's how to use both the desktop and phone versions effectively:

---

## Desktop Version (Host)

### Starting the Server

1. **Launch the App**: Open the Laner desktop application on your PC.  
2. **Connect to a Local Network**:  
   - Make sure your PC is connected to a local network or hotspot.  
   - Internet access is not required.  

3. **Start the Server**:  
   - Click the **Start Server** button.  
   - The app will display your local server address (IP code).  
   - This code will be used to connect your phone to the desktop.  

4. **Server Status**:  
   - The status label will show **"Server Running"** once the server starts.  
   - Avoid sharing the displayed code with unauthorized users.  

5. **Optional**:  
   - Use the **Hide Code** button to conceal the IP address for privacy.  
   - Click **End Server** to stop hosting files.  

---

### System Tray Features

- The app runs in the system tray when minimized.  
- Right-click the tray icon to access:  
  - **Show**: Reopen the app.  
  - **Quit**: Close the app entirely.  

---

## Phone Version (Client)

### Connecting to the Desktop

1. **Install and Open the App**: Launch the Laner app on your phone.  
2. **Enter the Server Code**:  
   - Navigate to the **Link** tab.  
   - Input the server code (IP address) displayed on the desktop app.  

3. **Verify Connection**:  
   - If successful, the app will display the file system from your PC.  
   - If not, ensure both devices are on the same network.  

---

### Browsing and Downloading Files

1. **Browse Files**:  
   - Use the grid layout to explore the folders and files hosted on your PC.  
2. **Download Files**:  
   - Tap the **Download** button on a file card.  
   - Files are saved in the `Downloads/Laner` folder on your phone.  

---

### Uploading Files to Desktop

1. **Select Files to Upload**:  
   - Tap the **Upload** button in the app.  
   - Choose files from your phone’s storage.  

2. **Transfer Files**:  
   - The selected files are uploaded to the current folder on your PC.  

---

### Managing Hidden Files

- To view hidden files on your PC, enable the **Show Hidden Files** option in the phone app's **Settings** tab.  

---

## Troubleshooting

- Ensure both devices are connected to the same Wi-Fi or hotspot.  
- Restart the desktop server if the connection fails.  
- Grant necessary permissions on the phone app (storage access, notifications).

# FAQs

### 1. **Do I need an active internet connection to use Laner?**  

No, Laner works entirely over a local network. Both devices must be connected to the same Wi-Fi or hotspot.  

### 2. **Where are downloaded files saved on my phone?**  

All downloaded files are stored in the `Downloads/Laner` folder on your phone.  

### 3. **How do I stop the server on my desktop?**  

Click the **End Server** button in the desktop app. This stops hosting files and ends the connection.  

### 4. **What if I can’t connect my phone to the server?**  

- Ensure both devices are connected to the same local network.  
- Verify the IP address (code) shown on the desktop app matches the one entered on your phone.  
- Restart the desktop server or your router if necessary.  

### 5. **Can I hide files from being shared?**  

Yes, hidden files can be excluded by default. Use the **Show Hidden Files** toggle in the phone app's settings to control this.  

### 6. **What happens when I minimize the desktop app?**  

The desktop app runs in the system tray. You can reopen it by right-clicking the tray icon and selecting **Show**.  

### 7. **Can I upload files from my phone to the PC?**  

Yes, use the **Upload** button in the phone app to select files for upload. Files will be saved to the desktop folder on your PC.  

### 8. **Does Laner support large file transfers?**  

Yes, but ensure both devices have sufficient storage space and a stable connection for large files.  

---

# Advanced Settings

### **For Desktop Users**

1. **Running in Background**  
   - The desktop app can continue serving files while minimized to the system tray. Use the tray menu for quick controls.  

3. **Using a Static IP Address**  
   - If your network assigns dynamic IPs, the server address might change. Configure a static IP on your router for consistency.  

---

### **For Phone Users**

1. **Customizing Themes**  
   - Laner supports dark and light themes. Switch between them via your phone's system theme settings.  

2. **Default Download Location**  
   - Downloads are saved in `Downloads/Laner`. If needed, you can modify this path in the app code by updating the `makeDownloadFolder()` function in `templates.py`.

3. **Offline Mode**  
   - While the app doesn't require the internet, you can use a phone hotspot with no data plan to create a local network.  

---

### **For Developers**

1. **Extending Functionality**  
   - Laner is open-source. You can add features like file previews, password-protected sharing, or multi-user support by extending its existing codebase.

2. **Changing the Default Port**
   - By default, Laner uses port `8000` for the server.  

- To scan a list of ports and use the first available one, update the `run_server()` method in the desktop app's main file:

   ```python
   ports = [8000, 8080, 9090]  # List of ports to scan

   for port in ports:
       try:
           # Attempt to start the server on the current port
           self.server = FileSharingServer(port, '/')
           self.server.start()  # Start the server
           print(f"Server running on port {port}")
           break  # Exit the loop if the server starts successfully
       except OSError:
           print(f"Port {port} is unavailable, trying the next one...")
   else:
       print("All specified ports are in use. Please free up a port and try again.")
   ```

- This ensures the server scans through a list of ports (`8000`, `8080`, `9090`, etc.) and uses the first available one. If no port is available, an error message will be displayed.

3. **Contributing to Laner**  
   - Fork the project repository, make your changes, and submit a pull request for review.  
