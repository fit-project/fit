# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

datas = [
    ('../../assets/config.ini', './assets/config.ini'),
    ('../../assets/templates/front.html', './assets/templates/front.html'),
    ('../../assets/templates/template_verification.html', './assets/templates/template_verification.html'),
    ('../../assets/templates/template_pec.html', './assets/templates/template_pec.html'),
    ('../../assets/templates/template_web.html', './assets/templates/template_web.html'),
    ('../../assets/templates/template_web_no_whois.html', './assets/templates/template_web_no_whois.html'),
    ('../../assets/templates/template_email.html', './assets/templates/template_email.html'),
    ('../../assets/branding/FIT-640.png', './assets/branding/FIT-640.png'),
    ('../../assets/svg/FIT.svg', './assets/svg/FIT.svg'),
    ('../../assets/images/no-preview.png', './assets/images/no-preview.png'),
    ('../../assets/images/loader.gif', './assets/images/loader.gif'),
    ('../../ui', './ui'),
    ('../../icon.ico', './icon.ico'),
    ("../windows/whois/data", "./whois/data"),
    ('../../ext_lib', './ext_lib')
]



a = Analysis(
    ["..\\..\\fit.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=["./pyinstaller/hooks"],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="fit",
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
    icon=["..\\icon.png"],
)
