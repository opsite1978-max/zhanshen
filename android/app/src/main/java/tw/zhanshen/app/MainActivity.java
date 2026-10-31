package tw.zhanshen.app;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

/** 戰神看盤 App：直接開啟網站版，指標更新不用重新安裝。 */
public class MainActivity extends Activity {
    private static final String HOME = "https://opsite1978-max.github.io/zhanshen/";
    private static final String HOST = "opsite1978-max.github.io";
    private WebView web;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        web = new WebView(this);
        web.setBackgroundColor(0xFF0D1016);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);          // FinMind 憑證、設定、常用指標都存在這裡
        s.setDatabaseEnabled(true);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setSupportZoom(false);               // 縮放交給圖表自己的兩指縮放
        s.setBuiltInZoomControls(false);
        s.setDisplayZoomControls(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        s.setUserAgentString(s.getUserAgentString() + " ZhanshenApp/1");
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest req) {
                Uri u = req.getUrl();
                if (HOST.equals(u.getHost())) return false;          // 同一個網站（戰神看盤、選股、計算機…）在 App 裡開
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) {}
                return true;                                         // 其他網站用手機瀏覽器開
            }
            @Override
            public void onReceivedError(WebView v, WebResourceRequest req, WebResourceError err) {
                if (req.isForMainFrame()) {
                    v.loadDataWithBaseURL(null,
                        "<html><body style='background:#0d1016;color:#d6dce6;font-family:sans-serif;padding:40px 24px;line-height:1.7'>"
                        + "<h2>連不上網路</h2><p>請確認手機有網路，然後點下面的按鈕重新整理。</p>"
                        + "<p><a href='" + HOME + "' style='display:inline-block;padding:10px 18px;background:#d9a85c;color:#1a1206;border-radius:8px;text-decoration:none'>重新整理</a></p></body></html>",
                        "text/html", "utf-8", null);
                }
            }
        });
        setContentView(web);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        if (savedInstanceState != null) web.restoreState(savedInstanceState);
        else web.loadUrl(HOME);
    }

    @Override
    protected void onSaveInstanceState(Bundle out) { super.onSaveInstanceState(out); web.saveState(out); }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack(); else super.onBackPressed();
    }

    @Override
    protected void onResume() { super.onResume(); web.onResume(); }

    @Override
    protected void onPause() { web.onPause(); super.onPause(); }
}
