#!/usr/bin/env python3
"""從 twstock-chart 的 zhanshen.html／holders.html／insider.html 產生獨立的戰神看盤網站。
資料（權證、集保、內部人、台指期籌碼）直接讀同一帳號底下 /twstock-chart/data/；設定、畫線、FinMind 憑證另外存。"""
import re, sys, os, shutil
SRC = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/twstock-chart'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = '/twstock-chart/data/'
def rd(p): return open(os.path.join(SRC, p), encoding='utf-8').read()
def must(s, a, b, cnt=1):
    if a not in s: sys.exit('MISSING: ' + a[:80])
    return s.replace(a, b, cnt)

s = rd('zhanshen.html')
s = must(s, "const NO_INTRA = false;", "const NO_INTRA = true;")
s = must(s, "const PAGE = new URLSearchParams(location.search).get('p') === 'gt' ? { key:'gt', name:'狗頭看盤' } : { key:'zs', name:'戰神看盤' };",
         """const PAGE = { key:'zx', name:'戰神看盤' };
// 一次性設定連結：網址後面帶 #t=憑證，存進這台裝置後立刻從網址拿掉
{ const m = location.hash.match(/^#t=([\\w.\\-]+)$/); if (m){ try { localStorage.setItem('zsite.token', m[1]); } catch (e){} history.replaceState(null, '', location.pathname + location.search); } }""")
s = must(s, """function siteToken(){ try { return (JSON.parse(localStorage.getItem('twchart.settings') || '{}').token || '').trim(); } catch(e){ return ''; } }""",
         """function siteToken(){ try { return (localStorage.getItem('zsite.token') || '').trim(); } catch(e){ return ''; } }""")
s = re.sub(r'\s*<nav class="chips">.*?</nav>', '', s, count=1)
s = s.replace("'data/", "'" + DATA)
s = must(s, """'<div class="row"><label for="a-token">本頁專用 token</label><input type="password" id="a-token" value="' + esc(UI.token || '') + '" placeholder="留空＝沿用看盤頁憑證" autocomplete="off" spellcheck="false"></div>' +""",
         """'<div class="row"><label for="a-token">FinMind 憑證</label><input type="password" id="a-token" value="' + esc(siteToken()) + '" placeholder="貼上 api token" autocomplete="off" spellcheck="false"></div>' +""")
s = must(s, """(siteToken() ? '目前沿用看盤頁「⚙ 設定」裡的 FinMind 憑證，這裡不用另外填。' : '看盤頁還沒有設定 FinMind 憑證；可以在這裡填，或到看盤頁「⚙ 設定」填一次全站共用。')""",
         """(siteToken() ? '這台裝置已經存好 FinMind 憑證。' : '這台裝置還沒有 FinMind 憑證：用設定連結點一次，或直接貼在上面。')""")
s = must(s, "document.getElementById('a-token').onchange = e => { UI.token = e.target.value.trim(); saveUI(); };",
         "document.getElementById('a-token').onchange = e => { try { localStorage.setItem('zsite.token', e.target.value.trim()); } catch (er){} UI.token = ''; saveUI(); };")
s = must(s, "UI.token = document.getElementById('a-token').value.trim(); saveUI(); closeDrawer();",
         "try { localStorage.setItem('zsite.token', document.getElementById('a-token').value.trim()); } catch (er){} UI.token = ''; saveUI(); closeDrawer();")
s = s.replace("到看盤頁「⚙ 設定」確認 FinMind 憑證", "到「指標設定 → 資料與顯示」確認 FinMind 憑證")
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(s)

TOKEN_FIX = "\ntry { const t = localStorage.getItem('zsite.token'); SET.token = t || ''; } catch(e){}"
for fn in ('holders.html', 'insider.html'):
    t = rd(fn)
    t = must(t, "try { SET = JSON.parse(localStorage.getItem('twchart.settings') || '{}') || {}; } catch(e){}",
             "try { SET = JSON.parse(localStorage.getItem('twchart.settings') || '{}') || {}; } catch(e){}" + TOKEN_FIX)
    t = t.replace("'data/", "'" + DATA).replace('manifest-m.webmanifest', 'manifest.webmanifest')
    t = t.replace("看盤頁「⚙ 設定」貼上新的 FinMind 憑證", "戰神看盤「指標設定 → 資料與顯示」貼上新的 FinMind 憑證")
    open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(t)
for fn in ('autoreload.js', 'icon-192.png', 'icon-512.png'):
    shutil.copy(os.path.join(SRC, fn), os.path.join(OUT, fn))
open(os.path.join(OUT, 'manifest.webmanifest'), 'w', encoding='utf-8').write('''{
  "id": "./index.html", "name": "戰神看盤", "short_name": "戰神看盤",
  "start_url": "./index.html", "scope": "./", "display": "standalone",
  "background_color": "#0d1016", "theme_color": "#0d1016", "lang": "zh-Hant-TW",
  "icons": [
    { "src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" }
  ]
}
''')
ver = sys.argv[3] if len(sys.argv) > 3 else '1'
open(os.path.join(OUT, 'sw.js'), 'w', encoding='utf-8').write('''// 讓戰神看盤可以「安裝成 App」：外殼檔案離線可開，資料一律即時抓
const CACHE = 'zhanshen-v%s';
const SHELL = ['./', './index.html', './holders.html', './insider.html', './autoreload.js', './manifest.webmanifest', './icon-192.png', './icon-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('zhanshen-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method !== 'GET' || u.hostname.includes('finmindtrade') || u.pathname.includes('/data/')) return;
  const mine = u.origin === location.origin && u.pathname.startsWith(new URL('./', location.href).pathname);
  e.respondWith(fetch(e.request, mine ? { cache:'no-cache' } : {}).then(r => {
    if (r.ok && (mine || /jsdelivr|unpkg|gstatic|googleapis/.test(u.hostname))){ const cp = r.clone(); caches.open(CACHE).then(c => c.put(e.request, cp)); }
    return r; }).catch(() => caches.match(e.request)));
});
''' % ver)
open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8').write('''# 戰神看盤

台股看盤網站：VWB 成交量加權通道、VW Z、VWD、布林大底、布林谷底線、龜苓膏、主力意圖、DegenX，日／週／月 K 線、畫圖、權證挑選、籌碼。

- 網址：https://opsite1978-max.github.io/%s/
- 行情：FinMind（憑證只存在各自裝置的瀏覽器，不在程式裡）
- 權證、集保、內部人、台指期籌碼：讀同帳號 twstock-chart 網站每天整理的資料
- `tools/build.py`：從 twstock-chart 的戰神看盤重新產生本站（維護用）
''' % os.path.basename(OUT.rstrip('/')))
print('built into', OUT)
