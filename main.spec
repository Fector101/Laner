# -*- mode: python ; coding: utf-8 -*-

debugging=True


import os
_icon_path=["assets","imgs","img.ico" if os.name == 'nt' else "icon.png"]
icon_path = os.path.join(*_icon_path)
print("Wine test: ",icon_path)


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[("assets",'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Laner PC',
    debug=debugging,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=debugging,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
    icon=icon_path,

)
