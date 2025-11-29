python
from http.server import HTTPServer, BaseHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor
import json
import zipfile
from pyaxmlparser import APK
import base64
import os

# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=4)

# Track task status
task_status = {}

def extract_apk_icon(apk_path, task_id):
    """Extract icon from APK file"""
    try:
        task_status[task_id] = {'status': 'processing', 'progress': 0}
        
        apk = APK(apk_path)
        
        # Get icon path from manifest
        icon_path = apk.get_app_icon()
        
        if icon_path:
            # Extract icon from APK (APK is a zip file)
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                icon_data = zip_ref.read(icon_path)
                
                # Save or process icon
                output_path = f"icons/{task_id}.png"
                os.makedirs("icons", exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(icon_data)
                
                task_status[task_id] = {
                    'status': 'complete',
                    'icon_path': output_path,
                    'package': apk.package
                }
        else:
            task_status[task_id] = {'status': 'error', 'message': 'No icon found'}
            
    except Exception as e:
        task_status[task_id] = {'status': 'error', 'message': str(e)}

def process_multiple_apks(apk_paths, task_id):
    """Process multiple APKs"""
    try:
        results = []
        total = len(apk_paths)
        
        for i, apk_path in enumerate(apk_paths):
            apk = APK(apk_path)
            icon_path = apk.get_app_icon()
            
            if icon_path:
                with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                    icon_data = zip_ref.read(icon_path)
                    output_path = f"icons/{apk.package}.png"
                    os.makedirs("icons", exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(icon_data)
                    
                    results.append({
                        'package': apk.package,
                        'icon': output_path,
                        'app_name': apk.application
                    })
            
            # Update progress
            task_status[task_id] = {
                'status': 'processing',
                'progress': int((i + 1) / total * 100),
                'processed': i + 1,
                'total': total
            }
        
        task_status[task_id] = {
            'status': 'complete',
            'results': results
        }
        
    except Exception as e:
        task_status[task_id] = {'status': 'error', 'message': str(e)}

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/extract-icon':
            # Single APK
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            
            task_id = post_data.get('task_id', 'task_' + str(len(task_status)))
            apk_path = post_data.get('apk_path')
            
            # Submit to thread pool
            executor.submit(extract_apk_icon, apk_path, task_id)
            
            self.send_response(202)  # Accepted
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'task_id': task_id,
                'message': 'Task started'
            }).encode())
            
        elif self.path == '/extract-multiple':
            # Multiple APKs
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            
            task_id = post_data.get('task_id', 'batch_' + str(len(task_status)))
            apk_paths = post_data.get('apk_paths', [])
            
            executor.submit(process_multiple_apks, apk_paths, task_id)
            
            self.send_response(202)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'task_id': task_id,
                'message': f'Processing {len(apk_paths)} APKs'
            }).encode())
    
    def do_GET(self):
        if self.path.startswith('/status/'):
            # Check task status
            task_id = self.path.split('/')[-1]
            
            status = task_status.get(task_id, {'status': 'not_found'})
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'APK Icon Extractor API')

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), Handler)
    print("Server running on http://localhost:8000")
    server.serve_forever()
