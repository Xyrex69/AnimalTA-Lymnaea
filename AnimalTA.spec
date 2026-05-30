# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['cli.py'],
    pathex=[],
    binaries=[],
    datas=[('AnimalTA\\Files', 'AnimalTA\\Files')],
    hiddenimports=['AnimalTA', 'AnimalTA.A_General_tools', 'AnimalTA.B_Project_organisation', 'AnimalTA.C_Pretracking', 'AnimalTA.D_Tracking_process', 'AnimalTA.E_Post_tracking', 'AnimalTA.F_Behaviors_Neuro', 'AnimalTA.G_Specials', 'scipy.signal', 'sklearn.cluster', 'pkg_resources.py2_warn'],
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
    name='AnimalTA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\trent\\AppData\\Local\\Programs\\AnimalTA\\AnimalTA\\Files\\Logo.ico'],
)
