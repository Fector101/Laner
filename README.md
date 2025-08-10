# Laner

A Mobile/Desktop app mainly for Accessing PC files on Phone.

-----
## How to Run
- Laner PC doesn't need any dependencies to run you can `cd workers` then `python server.py`

-Or For **GUI** `pip install PyQT5` then `python main.py`

-or For **all features** `python install -r requirements.txt` then `python main.py`

-----

## Debugging
## General
- Errors.txt For all error logs

## On windows
- If running from script and not a built exe, You'll be able to discover your PC from Laner mobile but The Windows security app blocks requests from Laner mobile
to stop this 
    - open the windows security app -> Firewall & network protection section -> turn off private network firewall
    - Then in your connected wifi tap properites and change setting to `private network`  
    > Warning: turn off turn off `private` not `public`
