# -*- mode: python ; coding: utf-8 -*-

import glob, os

# decord loads its native DLLs (decord.dll + bundled FFmpeg libs) at runtime via
# a ctypes path search, which PyInstaller cannot trace statically. Pull the exact
# working DLLs from the installed AnimalTA build and place them in a "decord"
# folder inside the bundle so decord._ffi.libinfo.find_lib_path() can locate them.
_decord_dir = r"C:\Users\trent\AppData\Local\Programs\AnimalTA\decord"
_decord_bins = [(f, 'decord') for f in glob.glob(os.path.join(_decord_dir, '*.dll'))]

# pymediainfo (used by the video converter, Class_converter.py) loads MediaInfo.dll
# from its package directory. Bundle that DLL so video conversion works.
import pymediainfo as _pmi
_pmi_dir = os.path.dirname(_pmi.__file__)
_pmi_dll = os.path.join(_pmi_dir, 'MediaInfo.dll')
_pmi_datas = [(_pmi_dll, 'pymediainfo')] if os.path.exists(_pmi_dll) else []

# Note: ffmpeg.exe lives in AnimalTA/Files/ffmpeg/ and is bundled via the
# Files datas entry below; the converter calls it for .mp4 / incompatible .avi.


a = Analysis(
    ['cli.py'],
    pathex=[],
    binaries=_decord_bins,
    datas=[('AnimalTA\\Files', 'AnimalTA\\Files')] + _pmi_datas,
    hiddenimports=['AnimalTA', 'AnimalTA.A_General_tools', 'AnimalTA.B_Project_organisation', 'AnimalTA.C_Pretracking', 'AnimalTA.D_Tracking_process', 'AnimalTA.E_Post_tracking', 'AnimalTA.F_Behaviors_Neuro', 'AnimalTA.G_Specials', 'scipy.signal', 'sklearn.cluster', 'pkg_resources.py2_warn', 'pymediainfo'],
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
