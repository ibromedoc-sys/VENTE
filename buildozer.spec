[app]

title = VENTE
package.name = vente
package.domain = com.vente

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json

version = 0.1

requirements = python3==3.14.2,hostpython3==3.14.2,kivy==2.3.1
p4a.branch = develop

orientation = portrait
fullscreen = 0

android.accept_sdk_license = True
android.api = 35
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a

android.allow_backup = True
android.debug_artifact = apk


[buildozer]

log_level = 2
warn_on_root = 1