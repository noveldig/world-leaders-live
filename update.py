import feedparser
from datetime import datetime, timezone, timedelta
import json
import re

FEEDS = {
    # 🏛️ 核心官媒与国际组织
    "新华网头条 (Xinhua)": "https://rsshub.app/xinhua/latest",
    "人民网头条 (People's Daily)": "https://rsshub.app/people/latest",
    "白宫官方 (White House)": "https://www.whitehouse.gov/briefings-statements/feed/",
    "联合国新闻 (UN News)": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "克里姆林宫 (Kremlin)": "http://en.kremlin.ru/events/news/rss",
    
    # 🦅 美联储与全球财金、非农、股市指数
    "美联储官方发布 (Federal Reserve)": "https://www.federalreserve.gov/feeds/press_all.xml",
    "金十数据快讯 (Jin10)": "https://rsshub.app/jin10/important",
    "财联社电报 (CLS Telegraph)": "https://rsshub.app/cls/telegraph",
    "CNBC 市场与财经 (CNBC Markets)": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "华尔街日报市场 (WSJ Markets)": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    "金融时报全球头条 (Financial Times)": "https://www.ft.com/rss/home/international",
    "路透社财经与市场 (Reuters Business)": "https://rsshub.app/reuters/business",
    "彭博社财经 (Bloomberg)": "https://rsshub.app/bloomberg",
    
    # 🐦 全球核心领导人与政要推特 (X) 实时动态
    "Donald Trump (特朗普)": "https://rsshub.app/twitter/user/realDonaldTrump",
    "Elon Musk (马斯克)": "https://rsshub.app/twitter/user/elonmusk",
    "Volodymyr Zelenskyy (乌克兰总统)": "https://rsshub.app/twitter/user/ZelenskyyUa",
    "Emmanuel Macron (法国总统)": "https://rsshub.app/twitter/user/EmmanuelMacron",
    "Narendra Modi (印度总理)": "https://rsshub.app/twitter/user/narendramodi",
    "Olaf Scholz (德国总理)": "https://rsshub.app/twitter/user/Bundeskanzler",
    "Keir Starmer (英国首相)": "https://rsshub.app/twitter/user/Keir_Starmer",
    
    # 🌍 主流国际大报
    "路透社全球要闻 (Reuters World)": "https://rsshub.app/reuters/world",
    "美联社 (AP News)": "https://rsshub.app/apnews/topics/world-news",
    "BBC 世界新闻 (BBC World)": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "纽约时报世界 (NYT World)": "https://rsshub.app/nyt/world",
    "CNN 全球新闻 (CNN World)": "http://rss.cnn.com/rss/cnn_world.rss",
    "半岛电视台 (Al Jazeera)": "https://www.aljazeera.com/xml/rss/all.xml",
    "联合早报 (Lianhe Zaobao)": "https://www.zaobao.com.sg/rss/sea",
    "Asahi Shimbun (朝日新闻)": "https://www.asahi.com/rss/asahi/news.rdf"
}

def fetch_news():
    items = []
    current_year = 2026
    BEIJING_TZ = timezone(timedelta(hours=8))
    
    for source_name, url in FEEDS.items():
        try:
            print(f"正在抓取: {source_name}...")
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= 4:
                    break
                
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    dt_utc = datetime(*published[:6], tzinfo=timezone.utc)
                    dt_bj = dt_utc.astimezone(BEIJING_TZ)
                    
                    if dt_bj.year < current_year:
                        continue
                    pub_time_str = dt_bj.strftime('%Y-%m-%d %H:%M')
                else:
                    pub_time_str = datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M')
                
                title = entry.get('title', 'No Title')
                link = entry.get('link', '#')
                
                summary = entry.get('summary', entry.get('description', ''))
                summary = re.sub('<[^<]+?>', '', summary)[:150]

                items.append({
                    "source": source_name,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "time": pub_time_str
                })
                count += 1
        except Exception as e:
            print(f"抓取 {source_name} 失败: {e}")

    items.sort(key=lambda x: x['time'], reverse=True)
    return items

def generate_html(items):
    items_json = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")

    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全球官媒、政要推特与财金指数实时看板</title>
    <style>
        :root {
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --text-main: #2c3e50;
            --text-muted: #7f8c8d;
            --accent: #3498db;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
        }
        .container { max-width: 850px; margin: 0 auto; }
        header { text-align: center; margin-bottom: 30px; }
        header h1 { font-size: 24px; margin-bottom: 8px; color: #1a202c; }
        header p { color: var(--text-muted); font-size: 14px; }
        .news-card {
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .badge { background-color: #ebf8ff; color: #3182ce; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 20px; }
        .time { font-size: 12px; color: var(--text-muted); }
        h2 { font-size: 18px; margin: 0 0 8px 0; line-height: 1.4; }
        h2 a { color: #2d3748; text-decoration: none; }
        h2 a:hover { color: var(--accent); }
        .summary { font-size: 14px; color: #4a5568; line-height: 1.6; margin-bottom: 12px; }
        .read-more { font-size: 13px; color: var(--accent); text-decoration: none; font-weight: 500; }
        .translating-tag { font-size: 11px; color: #e67e22; margin-left: 8px; font-weight: normal; }
        .loading-status { text-align: center; padding: 20px; color: var(--text-muted); font-size: 14px; }
        footer { text-align: center; margin-top: 40px; font-size: 12px; color: var(--text-muted); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 全球官媒、政要推特与财金非农全景看板</h1>
            <p>北京时间实时更新 | 多源智能负载均衡与防429频控优化</p>
        </header>
        <div class="news-list" id="news-container"></div>
        <div id="loading" class="loading-status">正在加载更多资讯...</div>
        <footer><p>Powered by Multi-Engine Translation & Smart Caching</p></footer>
    </div>

    <script type="application/json" id="news-data">
    __ITEMS_JSON__
    </script>

    <script>
        let allData = [];
        try {
            allData = JSON.parse(document.getElementById('news-data').textContent);
        } catch (e) {
            console.error("Data parse error:", e);
        }

        let currentIndex = 0;
        const pageSize = 10;
        const container = document.getElementById('news-container');
        const loadingIndicator = document.getElementById('loading');

        // 专业财经与政治术语修正库
        const glossary = {
            "Federal Reserve": "美联储",
            "Nonfarm Payrolls": "非农就业数据",
            "Nonfarm": "非农",
            "Interest Rate": "利率",
            "Inflation": "通货膨胀",
            "Stock Market": "股市",
            "Wall Street": "华尔街",
            "White House": "白宫",
            "Supreme Court": "最高法院"
        };

        function applyGlossary(text) {
            if (!text) return text;
            let corrected = text;
            for (const [en, zh] of Object.entries(glossary)) {
                const regex = new RegExp(`\\b${en}\\b`, 'gi');
                corrected = corrected.replace(regex, zh);
            }
            return corrected;
        }

        // 多源轮询防429翻译核心（带本地缓存与故障自动转移）
        async function translateText(text) {
            if (!text || /^[\u4e00-\u9fa5]+$/.test(text)) return applyGlossary(text);
            
            // 检查本地缓存，避免重复请求
            const cacheKey = 'trans_' + text.substring(0, 50);
            const cached = localStorage.getItem(cacheKey);
            if (cached) return cached;

            let translated = text;

            // 线路 1: Argos Open Tech 节点
            try {
                const res = await fetch('https://translate.argosopentech.com/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ q: text, source: 'en', target: 'zh', format: 'text' })
                });
                if (res.ok) {
                    const data = await res.json();
                    if (data && data.translatedText) {
                        translated = data.translatedText;
                        localStorage.setItem(cacheKey, applyGlossary(translated));
                        return applyGlossary(translated);
                    }
                }
            } catch (e) {}

            // 线路 2: MyMemory 备用通道（带延迟控制防 429）
            try {
                await new Promise(r => setTimeout(r, 200)); // 控频防并发过高
                const res = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=en|zh-CN`);
                if (res.ok) {
                    const data = await res.json();
                    if (data && data.responseData && data.responseData.translatedText) {
                        let t = data.responseData.translatedText;
                        if (!t.includes("INVALID KEY") && !t.includes("QUOTA") && !t.includes("PERMISSION")) {
                            translated = t;
                            localStorage.setItem(cacheKey, applyGlossary(translated));
                            return applyGlossary(translated);
                        }
                    }
                }
            } catch (err) {}

            const finalResult = applyGlossary(translated);
            localStorage.setItem(cacheKey, finalResult);
            return finalResult;
        }

        // 控制每批次串行/限速并发，彻底解决 429 报错
        async function processBatchTranslation(cardEl, item) {
            const titleEl = cardEl.querySelector('.news-title');
            const summaryEl = cardEl.querySelector('.news-summary');
            const tagEl = cardEl.querySelector('.translating-tag');

            try {
                const transTitle = await translateText(item.title);
                await new Promise(r => setTimeout(r, 150)); // 缓冲间隔
                const transSummary = await translateText(item.summary);

                if (transTitle) titleEl.innerText = transTitle;
                if (transSummary) summaryEl.innerText = transSummary + "...";
            } catch (err) {
                console.error("Translation error:", err);
            } finally {
                if (tagEl) tagEl.remove();
            }
        }

        function loadMore() {
            if (currentIndex >= allData.length) {
                loadingIndicator.innerText = "已加载全部资讯";
                return;
            }

            const nextEnd = Math.min(currentIndex + pageSize, allData.length);
            const batch = allData.slice(currentIndex, nextEnd);
            
            let batchHtml = '';
            batch.forEach((item, index) => {
                const globalIdx = currentIndex + index;
                batchHtml += `
                <div class="news-card" id="card-${globalIdx}">
                    <div class="card-header">
                        <span class="badge">${item.source}</span>
                        <span class="time">${item.time} (北京时间)</span>
                    </div>
                    <h2><a href="${item.link}" target="_blank" class="news-title">${item.title}</a><span class="translating-tag">(极速翻译中...)</span></h2>
                    <p class="summary news-summary">${item.summary}</p>
                    <a href="${item.link}" target="_blank" class="read-more">阅读原文 &rarr;</a>
                </div>
                `;
            });

            container.insertAdjacentHTML('beforeend', batchHtml);

            // 错峰排队异步翻译，杜绝 429
            batch.forEach((item, index) => {
                const globalIdx = currentIndex + index;
                const cardEl = document.getElementById(`card-${globalIdx}`);
                if (cardEl) {
                    setTimeout(() => {
                        processBatchTranslation(cardEl, item);
                    }, index * 250); // 每条卡片错开 250ms 发送
                }
            });

            currentIndex = nextEnd;

            if (currentIndex >= allData.length) {
                loadingIndicator.innerText = "已加载全部资讯";
            }
        }

        window.addEventListener('scroll', () => {
            if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 300) {
                loadMore();
            }
        });

        loadMore();
    </script>
</body>
</html>
"""
    return html_template.replace("__ITEMS_JSON__", items_json)

if __name__ == "__main__":
    items = fetch_news()
    html_content = generate_html(items)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("看板生成成功，已成功升级多源轮询防429限速策略！")
