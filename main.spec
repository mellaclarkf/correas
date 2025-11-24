# -*- mode: python ; coding: utf-8 -*-
# pyinstaller main.spec

block_cipher = None

import os
import sys

# Obtener la ruta de Conda
conda_path = os.environ.get('CONDA_PREFIX', '')

# Recolectar TODAS las DLLs necesarias para OpenCV 4.8.1
binaries = []
datas = []

if conda_path:
    print(f"🔍 Conda path detected: {conda_path}")
    
    # 1. DLLs de Library/bin (OpenCV 4.8.1 y dependencias)
    library_bin = os.path.join(conda_path, 'Library', 'bin')
    if os.path.exists(library_bin):
        print(f"📁 Adding DLLs from: {library_bin}")
        for dll in os.listdir(library_bin):
            dll_lower = dll.lower()
            # Incluir TODAS las DLLs críticas
            if any(keyword in dll_lower for keyword in [
                'opencv', 'ffmpeg', 'msvc', 'vcruntime', 
                'tbb', 'ipp', 'libjpeg', 'libpng', 'libtiff',
                'zlib', 'webp', 'openjp'
            ]) or dll.endswith('.dll'):
                src_path = os.path.join(library_bin, dll)
                binaries.append((src_path, '.'))
    
    # 2. DLLs de la carpeta principal DLLs de Conda
    dlls_dir = os.path.join(conda_path, 'DLLs')
    if os.path.exists(dlls_dir):
        print(f"📁 Adding DLLs from: {dlls_dir}")
        for dll in os.listdir(dlls_dir):
            if dll.endswith('.dll'):
                src_path = os.path.join(dlls_dir, dll)
                binaries.append((src_path, '.'))
    
    # 3. Carpeta completa de cv2 (incluye .pyd files)
    cv2_path = os.path.join(conda_path, 'Lib', 'site-packages', 'cv2')
    if os.path.exists(cv2_path):
        print(f"📁 Adding cv2 package from: {cv2_path}")
        datas.append((cv2_path, 'cv2'))

# Hidden imports críticos
hiddenimports = [
    'cv2',
    'cv2.cv2',  # Para algunas versiones de OpenCV
    'ultralytics',
    'ultralytics.yolo',
    'ultralytics.nn',
    'sklearn.utils._weight_vector',
    'sklearn.neighbors._typedefs',
    'sklearn.neighbors._quad_tree',
    'sklearn.utils._cython_blas',
    'numpy.core._multiarray_umath',
    'numpy.core._multiarray_tests',
    'pandas._libs.tslibs',
    'pickle',
    'PIL._imaging',
    'torch',
    'torch._C'
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)