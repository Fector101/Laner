async function getAllFiles(){
    const res= await fetch('/data.json')
    const data = await res.json()
    // console.log(data)
      
}
getAllFiles()