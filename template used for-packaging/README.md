# Packing Docs for Devs (Link to Download Packaged File in Repo main Docs for Users)

## For Linux

### To Package

Run `pyinstaller main.spec` in Project Main Folder

Copy `../dist/laner-pc` to `./template used for-packaging/laner-pc/usr/local/bin`, replace `excutable.txt`

Then in `template used for-packaging` folder Run `dpkg-deb --build laner-pc`

### Speed Ticket

`rm -rf dist && rm -rf dist build && pyinstaller main.spec && cp dist/laner-pc  "template used for-packaging/laner-pc/usr/local/bin" && cd "template used for-packaging" && dpkg-deb --build laner-pc`

### To install

`sudo dpkg -i laner-pc.deb`

### Finally to run Enter

`laner-pc`

### To uninstall properly

`sudo apt remove laner-pc && sudo rm -rf /etc/xdg/autostart/laner-pc.desktop`
