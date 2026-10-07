[app]

title = VENTE
package.name = app
package.domain = com.vente

source.dir = .
source.include_exts = py,png,jpg,jpeg,webp,kv,atlas,json,db
source.exclude_dirs = .git,.buildozer,bin,venv,__pycache__

version = 0.1

requirements = python3,kivy==2.3.0,kivymd==2.0.0,materialyoucolor==3.0.4,materialshapes==0.3,asynckivy==0.6.4,asyncgui==0.6.3,pillow

orientation = portrait
fullscreen = 0

android.accept_sdk_license = True
android.api = 34
android.minapi = 24
android.ndk_api = 24
android.ndk = 28c
android.archs = arm64-v8a

android.permissions = INTERNET,POST_NOTIFICATIONS
android.enable_androidx = True
android.gradle_dependencies = com.google.firebase:firebase-messaging:24.1.2
android.add_src = %(source.dir)s/android_src
android.extra_manifest_application_xml = %(source.dir)s/android_src/firebase_manifest.xml
android.add_resources = %(source.dir)s/android_src/res

android.allow_backup = True
android.debug_artifact = apk

p4a.url = https://github.com/kivy/python-for-android.git
p4a.branch = master
p4a.commit = v2026.05.09
p4a.source_dir = .buildozer/android/platform/python-for-android


[buildozer]

log_level = 2
warn_on_root = 1