# -*- mode: python ; coding: utf-8 -*-

import os
icon_path=os.path.join("assets","imgs","icon.png")

a = Analysis(
    ['desktop_version.py'],
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




excludes = ['.buildozer', '__pycache__', 'venv', 'public','.idea']
datas = []
for d in a.datas:
    skip=False
    for e in excludes:
        if e in d[0]:
            skip=True
            break
    if not skip: datas.append(d)
a.datas = TOC(datas)



pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Laner PC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
    icon=icon_path,
)