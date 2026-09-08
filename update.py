import feedparser
from datetime import datetime
import json
import re
import urllib.request
import urllib.parse

# 汇聚官媒、领导人推特、美联储、股市指数与非农财金头条的超级源列表
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
    "朝日新闻 (Asahi Shimbun)": "https://www.asahi.com/rss/asahi/news.rdf"
}

def translate_to_zh(text):
    if not text or re.match(r'^[\u4e00-\u9fa5]+$', text):
        return text
    try:
        encoded_text = urllib.parse.quote(text[:400])
        url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|zh-CN"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and 'responseData' in data and data['responseData']['translatedText']:
                translated = data['responseData']['translatedText']
                if "INVALID KEY" not in translated and "QUOTA" not in translated:
                    return translated
    except Exception:
        pass
    return text

def fetch_news():
    items = []
    current_year = 2026
    
    for source_name, url in FEEDS.items():
        try:
            print(f"正在抓取: {source_name}...")
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= 4:  # 每个源取最新的4条
                    break
                
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    pub_time = datetime(*published[:6])
                    if pub_time.year < current_year:
                        continue
                    pub_time_str = pub_time.strftime('%Y-%m-%d %H:%M')
                else:
                    pub_time_str = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                title = entry.get('title', 'No Title')
                link = entry.get('link', '#')
                
                summary = entry.get('summary', entry.get('description', ''))
                summary = re.sub('<[^<]+?>', '', summary)[:150]

                zh_title = translate_to_zh(title)
                zh_summary = translate_to_zh(summary)

                items.append({
                    "source": source_name,
                    "title": zh_title,
                    "summary": zh_summary,
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

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全球实时看板</title>
    <style>
        :root {{
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --text-main: #2c3e50;
            --text-muted: #7f8c8d;
            --accent: #3498db;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
        }}
        .container {{ max-width: 850px; margin: 0 auto; }}
        header {{ text-align: center; margin-bottom: 30px; }}
        header h1 {{ font-size: 24px; margin-bottom: 8px; color: #1a202c; }}
        header p {{ color: var(--text-muted); font-size: 14px; }}
        .news-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .badge {{ background-color: #ebf8ff; color: #3182ce; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 20px; }}
        .time {{ font-size: 12px; color: var(--text-muted); }}
        h2 {{ font-size: 18px; margin: 0 0 8px 0; line-height: 1.4; }}
        h2 a {{ color: #2d3748; text-decoration: none; }}
        h2 a:hover {{ color: var(--accent); }}
        .summary {{ font-size: 14px; color: #4a5568; line-height: 1.6; margin-bottom: 12px; }}
        .read-more {{ font-size: 13px; color: var(--accent); text-decoration: none; font-weight: 500; }}
        .loading-status {{ text-align: center; padding: 20px; color: var(--text-muted); font-size: 14px; }}
        footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: var(--text-muted); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 全球全景看板</h1>
            <p>实时聚合官媒、领导人社交动态、美联储与全球股市指数</p>
        </header>
        <div class="news-list" id="news-container"></div>
        <div id="loading" class="loading-status">正在加载更多资讯...</div>
        <footer><p>Powered by GitHub Actions & Python Engine</p></footer>
    </div>

    <script type="application/json" id="news-data">
    {items_json}
    </script>

    <script>
        let allData = [];
        try {{
            allData = JSON.parse(document.getElementById('news-data').textContent);
        }} catch (e) {{
            console.error("Data parse error:", e);
        }}

        let currentIndex = 0;
        const pageSize = 10;
        const container = document.getElementById('news-container');
        const loadingIndicator = document.getElementById('loading');

        function loadMore() {{
            if (currentIndex >= allData.length) {{
                loadingIndicator.innerText = "已加载全部资讯";
                return;
            }}

            const nextEnd = Math.min(currentIndex + pageSize, allData.length);
            const batch = allData.slice(currentIndex, nextEnd);
            
            let batchHtml = '';
            batch.forEach((item) => {{
                batchHtml += `
                <div class="news-card">
                    <div class="card-header">
                        <span class="badge">${{item.source}}</span>
                        <span class="time">${{item.time}}</span>
                    </div>
                    <h2><a href="${{item.link}}" target="_blank">${{item.title}}</a></h2>
                    <p class="summary">${{item.summary}}...</p>
                    <a href="${{item.link}}" target="_blank" class="read-more">阅读原文 &rarr;</a>
                </div>
                `;
            }));

            container.insertAdjacentHTML('beforeend', batchHtml);
            currentIndex = nextEnd;

            if (currentIndex >= allData.length) {{
                loadingIndicator.innerText = "已加载全部资讯";
            }}
        }}

        window.addEventListener('scroll', () => {{
            if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 300) {{
                loadMore();
            }}
        }});

        loadMore();
    </script>
</body>
</html>
"""
    return html_content

if __name__ == "__main__":
    items = fetch_news()
    html_content = generate_html(items)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("看板生成成功，已成功加入官媒、推特及财金指数源！")
