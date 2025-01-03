# Packing Docs for Devs (Link to Download Packaged File in Repo main Docs for Users)

## For Linux

### To Package

`dpkg-deb --build laner-pc`

### To install

`sudo dpkg -i laner-pc.deb`

### Finally to run Enter

`laner-pc`

### To uninstall properly

`sudo apt remove laner-pc && sudo rm -rf /etc/xdg/autostart/laner-pc.desktop`
