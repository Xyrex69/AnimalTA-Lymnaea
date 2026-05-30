# -*- mode: python ; coding: utf-8 -*-

import glob, os

# decord loads its native DLLs (decord.dll + bundled FFmpeg libs) at runtime via
# a ctypes path search, which PyInstaller cannot trace statically. Pull the exact
# working DLLs from the installed AnimalTA build and place them in a "decord"
# folder inside the bundle so decord._ffi.libinfo.find_lib_path() can locate them.
_decord_dir = r"C:\Users\trent\AppData\Local\Programs\AnimalTA\decord"
_decord_bins = [(f, 'decord') for f in glob.glob(os.path.join(_decord_dir, '*.dll'))]


a = Analysis(
    ['cli.py'],
    pathex=[],
    binaries=_decord_bins,
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
