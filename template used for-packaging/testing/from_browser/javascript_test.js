async function test(ip,folder='assets') {
    const server_ip = ip;
    const port = 8000;
//    const path = `C:\\Users\\hp\\Downloads`;
    const path = `C:\\Users\\hp\\Desktop\\Linux\\my_code\\Laner\\${folder}`;
    const encodedPath = encodeURIComponent(path); // encode backslashes and special characters
    const url = `http://${server_ip}:${port}/api/getpathinfo?path=${encodedPath}`;

    const data = await fetch(url, { method: 'GET' });
    console.log('got_request')
    const res = await data.json();
    console.log(res);
}


// def _get_path_from_url(self):
//     query = urlparse(self.path).query
//     params = parse_qs(query)
//     path_list = params.get("path")
//     return path_list[0] if path_list else None

// def do_GET(self):
//     """Handle GET requests for various API endpoints."""
//     try:

//     # if self.path.startswith("/api/getpathinfo"):
