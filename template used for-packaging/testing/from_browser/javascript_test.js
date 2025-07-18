async function test(){
    const server_ip = ''
    const port = 8000
    const path='C:\Users\hp\Desktop\Linux\Laner-main'
    const url = `http://${server_ip}:${port}/api/getpathinfo`;
    const data = await fetch(url,{method: 'GET'});
    const res = await data.json()
    console.log(res);  
}