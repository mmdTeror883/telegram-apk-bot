#!/usr/bin/env python3
"""Generate a small customizable Android WebView app for GitHub Actions builds."""
from __future__ import annotations

import hashlib
import html
import os
from pathlib import Path

THEMES = {
    "blue": ("#60a5fa", "#2563eb", "#a5f3fc"),
    "violet": ("#c084fc", "#7c3aed", "#f0abfc"),
    "emerald": ("#34d399", "#059669", "#a7f3d0"),
    "rose": ("#fb7185", "#e11d48", "#fecdd3"),
}
TEMPLATE_IDS = {"glass", "tictactoe", "todo", "calculator", "chat_demo"}


def html_text(value: str) -> str:
    return html.escape(value, quote=True)


def shared_style(theme: str) -> str:
    light, main, soft = THEMES[theme]
    return f"""
    :root{{--light:{light};--accent:{main};--soft:{soft};--ink:#f8fafc;--muted:#cbd5e1;}}
    *{{box-sizing:border-box}}
    body{{margin:0;min-height:100vh;color:var(--ink);font-family:system-ui,'Noto Sans',sans-serif;
      direction:rtl;background:linear-gradient(145deg,#07111f,#111827 55%,#0a1020);
      background:radial-gradient(ellipse at 15% 15%,color-mix(in srgb,var(--accent) 55%,transparent),transparent 45%),
      radial-gradient(ellipse at 90% 85%,color-mix(in srgb,var(--light) 40%,transparent),transparent 42%),
      linear-gradient(145deg,#07111f,#111827 55%,#0a1020);padding:22px 16px 34px;}}
    .shell{{max-width:540px;margin:0 auto}}
    .topline{{display:flex;justify-content:space-between;align-items:center;margin-bottom:22px}}
    .brand{{display:flex;align-items:center;gap:10px;font-weight:800;letter-spacing:.2px}}
    .brand-icon{{width:42px;height:42px;border-radius:15px;display:grid;place-items:center;
      background:linear-gradient(135deg,var(--light),var(--accent));box-shadow:0 8px 28px color-mix(in srgb,var(--accent) 42%,transparent);font-size:21px}}
    .badge{{border:1px solid #ffffff2b;background:#ffffff12;padding:7px 11px;border-radius:999px;color:#e2e8f0;font-size:12px}}
    .glass{{background:linear-gradient(135deg,#ffffff18,#ffffff09);border:1px solid #ffffff28;
      box-shadow:0 18px 55px #0005,inset 0 1px #ffffff20;backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
      border-radius:26px;padding:22px}}
    h1{{font-size:clamp(27px,7vw,38px);line-height:1.2;margin:0 0 8px;font-weight:900;letter-spacing:-.7px}}
    .subtitle{{margin:0;color:var(--muted);line-height:1.8;font-size:15px}}
    .accent{{color:var(--light)}}
    button,input{{font:inherit}}
    .primary{{border:0;color:#06111d;background:linear-gradient(110deg,var(--light),var(--soft));font-weight:900;
      padding:13px 18px;border-radius:15px;min-height:48px;box-shadow:0 9px 26px color-mix(in srgb,var(--accent) 30%,transparent);cursor:pointer}}
    .secondary{{border:1px solid #ffffff2c;color:var(--ink);background:#ffffff12;padding:11px 16px;border-radius:14px;cursor:pointer}}
    .section-title{{font-size:18px;font-weight:850;margin:0 0 14px}}
    .muted{{color:var(--muted)}}
    .grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:16px}}
    .mini{{padding:15px;border-radius:18px;background:#ffffff0c;border:1px solid #ffffff19}}
    .mini b{{display:block;font-size:15px;margin:5px 0}} .mini span{{font-size:12px;color:var(--muted)}}
    .footer{{text-align:center;color:#94a3b8;font-size:11px;margin-top:20px}}
    .status{{min-height:25px;color:var(--light);font-weight:700;margin:12px 0}}
    @media(max-width:380px){{body{{padding:14px 10px}}.glass{{padding:18px}}}}
    """


def common_shell(name: str, tagline: str, theme: str, icon: str, content: str) -> str:
    title, line = html_text(name), html_text(tagline)
    subtitle = line if line else "یک تجربهٔ کوچک و زیبا، مخصوص شما."
    return f"""<!doctype html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="theme-color" content="#0b1220"><title>{title}</title><style>{shared_style(theme)}</style></head>
<body><main class="shell"><header class="topline"><div class="brand"><div class="brand-icon">{icon}</div><span>{title}</span></div><span class="badge">نسخهٔ آزمایشی</span></header>
{content}<footer class="footer">ساخته‌شده با سازندهٔ اپ تلگرام</footer></main></body></html>"""


def landing(name: str, tagline: str, theme: str) -> str:
    body = f"""
    <section class="glass"><p class="badge">خوش آمدی ✨</p><h1>{html_text(name)}<br><span class="accent">با طراحی اختصاصی</span></h1>
    <p class="subtitle">{html_text(tagline or 'رنگ و ظاهر برنامه با سلیقهٔ شما ساخته شده است.')}</p>
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:22px"><button class="primary" onclick="document.getElementById('hello').textContent='خوش آمدی به برنامهٔ شما ✨'">شروع کن</button>
    <button class="secondary" onclick="document.getElementById('hello').textContent='اپ اختصاصی شما آماده است.'">دربارهٔ برنامه</button></div>
    <div class="status" id="hello" aria-live="polite"></div></section>
    <section class="grid"><div class="mini"><span>✦ طراحی</span><b>شیشه‌ای و مدرن</b><span>سازگار با صفحهٔ گوشی</span></div>
    <div class="mini"><span>⚡ تجربه</span><b>سریع و سبک</b><span>بدون وابستگی به اینترنت</span></div></section>
    """
    return common_shell(name, tagline, theme, "✦", body)


def tic_tac_toe(name: str, tagline: str, theme: str) -> str:
    body = f"""
    <section class="glass"><h1>⭕ بازی دوز</h1><p class="subtitle">{html_text(tagline or 'دو بازیکن، یک گوشی؛ X در برابر O.')}</p>
    <div id="turn" class="status">نوبت X</div>
    <div id="board" style="display:grid;grid-template-columns:repeat(3,1fr);gap:9px;max-width:340px;margin:8px auto 18px"></div>
    <div style="display:flex;justify-content:space-between;align-items:center"><span class="badge" id="score">X: 0 · O: 0</span><button class="primary" id="reset">دور تازه</button></div></section>
    <script>
    const boardEl=document.getElementById('board'),turnEl=document.getElementById('turn'),scoreEl=document.getElementById('score');
    let cells=Array(9).fill(''),turn='X',over=false,scores={{X:0,O:0}};
    const wins=[[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
    function draw(){{boardEl.innerHTML='';cells.forEach((v,i)=>{{const b=document.createElement('button');b.className='secondary';b.textContent=v;b.setAttribute('aria-label','خانه '+(i+1));b.style.cssText='height:88px;font-size:34px;font-weight:900;border-radius:20px;color:var(--light)';b.onclick=()=>play(i);boardEl.appendChild(b)}});scoreEl.textContent='X: '+scores.X+' · O: '+scores.O}}
    function play(i){{if(over||cells[i])return;cells[i]=turn;const win=wins.find(line=>line.every(j=>cells[j]===turn));if(win){{over=true;scores[turn]++;turnEl.textContent='🏆 برنده: '+turn}}else if(cells.every(Boolean)){{over=true;turnEl.textContent='🤝 مساوی شد'}}else{{turn=turn==='X'?'O':'X';turnEl.textContent='نوبت '+turn}}draw()}}
    document.getElementById('reset').onclick=()=>{{cells=Array(9).fill('');turn='X';over=false;turnEl.textContent='نوبت X';draw()}};draw();
    </script>
    """
    return common_shell(name, tagline, theme, "⭕", body)


def todo(name: str, tagline: str, theme: str) -> str:
    body = f"""
    <section class="glass"><h1>✅ فهرست کارها</h1><p class="subtitle">{html_text(tagline or 'کارهای مهمت را یادداشت کن و انجام‌شده علامت بزن.')}</p>
    <div style="display:flex;gap:8px;margin-top:18px"><input id="task" placeholder="کار جدید…" style="flex:1;min-width:0;border:1px solid #ffffff30;background:#ffffff12;color:white;padding:12px;border-radius:14px;outline:none">
    <button id="add" class="primary">افزودن</button></div><ul id="list" style="list-style:none;padding:0;margin:16px 0 0"></ul></section>
    <script>
    const input=document.getElementById('task'),list=document.getElementById('list');let tasks=[];
    try{{tasks=JSON.parse(localStorage.getItem('tasks-{html_text(name)}')||'[]')}}catch(e){{tasks=[]}}
    function save(){{try{{localStorage.setItem('tasks-{html_text(name)}',JSON.stringify(tasks))}}catch(e){{}}}}
    function render(){{list.innerHTML='';tasks.forEach((t,i)=>{{const li=document.createElement('li');li.style.cssText='display:flex;align-items:center;gap:10px;padding:12px;margin:8px 0;border-radius:15px;background:#ffffff10;border:1px solid #ffffff18';const check=document.createElement('input');check.type='checkbox';check.checked=t.done;check.onchange=()=>{{tasks[i].done=check.checked;save();render()}};const span=document.createElement('span');span.textContent=t.text;span.style.cssText='flex:1;word-break:break-word;'+(t.done?'text-decoration:line-through;opacity:.6':'');const del=document.createElement('button');del.textContent='حذف';del.className='secondary';del.onclick=()=>{{tasks.splice(i,1);save();render()}};li.append(check,span,del);list.appendChild(li)}})}}
    function add(){{const v=input.value.trim();if(!v)return;tasks.push({{text:v,done:false}});input.value='';save();render()}}
    document.getElementById('add').onclick=add;input.addEventListener('keydown',e=>{{if(e.key==='Enter')add()}});render();
    </script>
    """
    return common_shell(name, tagline, theme, "✅", body)


def calculator(name: str, tagline: str, theme: str) -> str:
    body = f"""
    <section class="glass"><h1>🧮 ماشین‌حساب</h1><p class="subtitle">{html_text(tagline or 'یک ماشین‌حساب ساده و کاربردی.')}</p>
    <input id="display" value="0" readonly style="width:100%;margin:16px 0;padding:18px;border-radius:18px;border:1px solid #ffffff25;background:#07111f99;color:white;text-align:left;font-size:32px;font-weight:800">
    <div id="keys" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px"></div></section>
    <script>
    const display=document.getElementById('display'),keys=document.getElementById('keys');let current='0',prev=null,op=null,fresh=false;
    function show(){{display.value=current}}
    function calc(){{if(prev===null||!op)return;const a=Number(prev),b=Number(current);let r=op==='+'?a+b:op==='−'?a-b:op==='×'?a*b:op==='÷'?(b===0?NaN:a/b):b;current=Number.isFinite(r)?String(Number(r.toPrecision(10))):'خطا';prev=null;op=null;fresh=true;show()}}
    function press(k){{if(/^[0-9]$/.test(k)){{if(fresh||current==='0'||current==='خطا')current=k;else if(current.length<14)current+=k;fresh=false}}else if(k==='.'){{if(fresh){{current='0.';fresh=false}}else if(!current.includes('.'))current+='.'}}else if(k==='C'){{current='0';prev=null;op=null;fresh=false}}else if(k==='⌫'){{current=current.slice(0,-1)||'0'}}else if(k==='='){{calc();return}}else{{if(current==='خطا')current='0';if(prev!==null&&!fresh)calc();prev=current;op=k;fresh=true}}show()}}
    const buttons=['C','⌫','÷','×','7','8','9','−','4','5','6','+','1','2','3','=','0','.','='];buttons.forEach((k,i)=>{{const b=document.createElement('button');b.className=k==='='||['+','−','×','÷'].includes(k)?'primary':'secondary';b.textContent=k;b.style.cssText='min-height:54px;font-size:18px;font-weight:800'+(i===16?';grid-column:span 2':'');b.onclick=()=>press(k);keys.appendChild(b)}});show();
    </script>
    """
    return common_shell(name, tagline, theme, "🧮", body)


def chat_demo(name: str, tagline: str, theme: str) -> str:
    body = f"""
    <section class="glass"><h1>💬 چت‌روم</h1><p class="subtitle">{html_text(tagline or 'نمایش آزمایشی چت‌روم.')}</p>
    <p class="badge" style="margin:14px 0">نسخهٔ فعلی آفلاین است؛ پیام‌ها فقط روی همین گوشی دیده می‌شوند.</p>
    <div id="messages" style="height:42vh;min-height:230px;overflow:auto;padding:12px;border-radius:18px;background:#03071255;border:1px solid #ffffff18"></div>
    <div style="display:flex;gap:8px;margin-top:12px"><input id="msg" placeholder="پیامت را بنویس…" style="flex:1;min-width:0;border:1px solid #ffffff30;background:#ffffff12;color:white;padding:12px;border-radius:14px;outline:none"><button id="send" class="primary">ارسال</button></div></section>
    <script>
    const box=document.getElementById('messages'),inp=document.getElementById('msg');
    function addMessage(text,mine){{const row=document.createElement('div');row.style.cssText='display:flex;justify-content:'+(mine?'flex-start':'flex-end')+';margin:8px 0';const bubble=document.createElement('div');bubble.textContent=text;bubble.style.cssText='max-width:85%;padding:10px 13px;border-radius:16px;background:'+(mine?'var(--accent)':'#ffffff18')+';color:white;overflow-wrap:anywhere';row.appendChild(bubble);box.appendChild(row);box.scrollTop=box.scrollHeight}}
    function send(){{const t=inp.value.trim();if(!t)return;addMessage(t,true);inp.value=''}}
    addMessage('سلام! این نمونهٔ نمایشی چت است.',false);document.getElementById('send').onclick=send;inp.addEventListener('keydown',e=>{{if(e.key==='Enter')send()}});
    </script>
    """
    return common_shell(name, tagline, theme, "💬", body)


TEMPLATES = {
    "glass": landing,
    "tictactoe": tic_tac_toe,
    "todo": todo,
    "calculator": calculator,
    "chat_demo": chat_demo,
}


def main() -> None:
    name = os.environ.get("APP_NAME", "").strip()
    chat_id = os.environ.get("CHAT_ID", "").strip()
    template_id = os.environ.get("APP_TEMPLATE", "glass").strip()
    theme_id = os.environ.get("APP_THEME", "blue").strip()
    tagline = os.environ.get("APP_TAGLINE", "").strip()
    if not name or len(name) > 32 or any(ord(c) < 32 for c in name):
        raise SystemExit("APP_NAME is missing or invalid (max 32 characters).")
    if not chat_id:
        raise SystemExit("CHAT_ID is missing.")
    if template_id not in TEMPLATE_IDS:
        raise SystemExit(f"Unsupported template: {template_id}")
    if theme_id not in THEMES:
        raise SystemExit(f"Unsupported theme: {theme_id}")
    if len(tagline) > 80:
        raise SystemExit("APP_TAGLINE must be 80 characters or fewer.")

    app_hash = hashlib.sha256(f"{chat_id}:{name}:{template_id}".encode("utf-8")).hexdigest()[:10]
    app_id = f"com.generated.app.a{app_hash}"
    root = Path.cwd()
    assets = root / "app/src/main/assets"
    values = root / "app/src/main/res/values"
    java = root / "app/src/main/java/com/generated/app"
    assets.mkdir(parents=True, exist_ok=True)
    values.mkdir(parents=True, exist_ok=True)
    java.mkdir(parents=True, exist_ok=True)

    page = TEMPLATES[template_id](name, tagline, theme_id)
    (assets / "index.html").write_text(page, encoding="utf-8")

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
    <application android:allowBackup="false" android:label="@string/app_name"
        android:supportsRtl="true" android:theme="@style/AppTheme">
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
<resources><string name="app_name" formatted="false">{html_text(name)}</string></resources>
""",
        "app/src/main/res/values/styles.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="AppTheme" parent="@android:style/Theme.Material.Light.NoActionBar">
        <item name="android:fontFamily">sans</item>
        <item name="android:colorAccent">#60A5FA</item>
        <item name="android:windowLightStatusBar">false</item>
        <item name="android:statusBarColor">#07111F</item>
        <item name="android:navigationBarColor">#07111F</item>
    </style>
</resources>
""",
        "app/src/main/java/com/generated/app/MainActivity.java": """package com.generated.app;

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.View;

public class MainActivity extends Activity {
    private WebView webView;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        webView.setBackgroundColor(0xFF07111F);
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient());
        setContentView(webView);
        webView.loadUrl("file:///android_asset/index.html");
    }
    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }
}
""",
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(f"Generated {app_id}: template={template_id}, theme={theme_id}, name={name!r}")


if __name__ == "__main__":
    main()
