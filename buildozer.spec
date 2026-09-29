[app]
title = ATM Banking
package.name = atmbanking
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.exclude_dirs = venv, .buildozer, bin, build, dist, __pycache__, typings, .vscode, .git, .github
version = 1.0.0

requirements = python3,kivy==2.3.0,sqlite3

orientation = portrait
fullscreen = 0
android.presplash_color = #1A237E

android.api = 34
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.enable_androidx = True
android.archs = arm64-v8a
android.allow_backup = True
p4a.branch = develop

# icon.filename = %(source.dir)s/assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1