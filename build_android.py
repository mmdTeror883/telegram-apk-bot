from __future__ import annotations

import hashlib
import html
import os
from pathlib import Path


def main() -> None:
    name = os.environ.get("APP_NAME", "").strip()
    telegram_chat = os.environ.get("CHAT_ID", "").strip()
    if not name or not telegram_chat:
        raise SystemExit("APP_NAME and CHAT_ID are required")
    if len(name) > 32 or any(ord(ch) < 32 for ch in name):
        raise SystemExit("Invalid app name")

    app_hash = hashlib.sha256(f"{telegram_chat}:{name}".encode("utf-8")).hexdigest()[:10]
    app_id = f"com.generated.app.a{app_hash}"
    root = Path.cwd()
    files = {
        "settings.gradle": """pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = 'GeneratedApp'
include ':app'
""",
        "build.gradle": """plugins {
    id 'com.android.application' version '8.7.3' apply false
}
""",
        "gradle.properties": """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
""",
        "app/build.gradle": f"""plugins {{
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
}}
""",
        "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:allowBackup="false"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/AppTheme">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""",
        "app/src/main/res/values/strings.xml": f"""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name" formatted="false">{html.escape(name, quote=False)}</string>
    <string name="welcome" formatted="false">برنامهٔ «{html.escape(name, quote=False)}» با موفقیت ساخته شد.</string>
</resources>
""",
        "app/src/main/res/values/styles.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="@android:style/Theme.Material.Light.NoActionBar">
        <item name="android:fontFamily">sans</item>
        <item name="android:colorAccent">#2563EB</item>
    </style>
</resources>
""",
        "app/src/main/java/com/generated/app/MainActivity.java": """package com.generated.app;

import android.app.Activity;
import android.graphics.Color;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.TextView;

public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        TextView message = new TextView(this);
        message.setText(getString(R.string.welcome));
        message.setTextSize(24);
        message.setTextColor(Color.rgb(15, 23, 42));
        message.setGravity(Gravity.CENTER);
        int padding = (int) (24 * getResources().getDisplayMetrics().density);
        message.setPadding(padding, padding, padding, padding);
        message.setBackgroundColor(Color.rgb(248, 250, 252));
        setContentView(message);
    }
}
""",
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Generated app {app_id} for {name!r}")


if __name__ == "__main__":
    main()
