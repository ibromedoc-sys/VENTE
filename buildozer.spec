[app]

title = VENTE
package.name = vente
package.domain = com.vente

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json

version = 0.1

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.accept_sdk_license = True
android.api = 34
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a

android.allow_backup = True
android.debug_artifact = apk

p4a.url = https://github.com/kivy/python-for-android.git
p4a.branch = master
p4a.commit = v2024.01.21


[buildozer]

log_level = 2
warn_on_root = 1