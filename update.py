import feedparser
from datetime import datetime
import json
import re
import urllib.request
import urllib.parse

FEEDS = {
    "White House (白宫官方)": "https://www.whitehouse.gov/briefings-statements/feed/",
    "UN News (联合国)": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "UK Government (英国政府)": "https://www.gov.uk/government/announcements.atom",
    "European Commission (欧盟委员会)": "https://ec.europa.eu/commission/presscorner/api/rss?language=en",
    "Kremlin (克里姆林宫)": "http://en.kremlin.ru/events/news/rss",
    "Donald Trump": "https://rsshub.app/twitter/user/realDonaldTrump",
    "Elon Musk": "https://rsshub.app/twitter/user/elonmusk",
    "Emmanuel Macron (法国总统)": "https://rsshub.app/twitter/user/EmmanuelMacron",
    "Narendra Modi (印度总理)": "https://rsshub.app/twitter/user/narendramodi",
    "Volodymyr Zelenskyy (乌克兰总统)": "https://rsshub.app/twitter/user/ZelenskyyUa",
    "Justin Trudeau (加拿大总理)": "https://rsshub.app/twitter/user/JustinTrudeau",
    "Olaf Scholz (德国总理)": "https://rsshub.app/twitter/user/Bundeskanzler",
    "Keir Starmer (英国首相)": "https://rsshub.app/twitter/user/Keir_Starmer",
    "Reuters (路透社)": "https://rsshub.app/reuters/world",
    "Associated Press (美联社)": "https://rsshub.app/apnews/topics/world-news",
    "BBC World (BBC新闻)": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "Wall Street Journal (华尔街日报)": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "New York Times (纽约时报)": "https://rsshub.app/nyt/world",
    "CNN World (CNN)": "http://rss.cnn.com/rss/cnn_world.rss",
    "Bloomberg (彭博社)": "https://rsshub.app/bloomberg",
    "Al Jazeera (半岛电视台)": "https://www.aljazeera.com/xml/rss/all.xml",
    "Lianhe Zaobao (联合早报)": "https://www.zaobao.com.sg/rss/sea",
    "Asahi Shimbun (朝日新闻)": "https://www.asahi.com/rss/asahi/news.rdf"
}

def translate_to_zh(text):
    if not text or re.match(r'^[\u4e00-\u9fa5]+$', text):
        return text
    try:
        encoded_text = urllib.parse.quote(text[:500]) # 限制单次长度防止溢出
        url = f"https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|zh-CN"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data and 'responseData' in data and data['responseData']['translatedText']:
                translated = data['responseData']['translatedText']
                if "INVALID KEY" not in translated and "QUOTA" not in translated:
                    return translated
    except Exception as e:
        print(f"翻译出错: {e}")
    return text  # 失败则降级返回原文

def fetch_news():
    items = []
    for source_name, url in FEEDS.items():
        try:
            print(f"正在抓取并翻译: {source_name}...")
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                title = entry.get('title', 'No Title')
                link = entry.get('link', '#')
                
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    pub_time = datetime(*published[:6]).strftime('%Y-%m-%d %H:%M')
                else:
                    pub_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                summary = entry.get('summary', entry.get('description', ''))
                summary = re.sub('<[^<]+?>', '', summary)[:180]

                # 后端直接转换为简体中文
                zh_title = translate_to_zh(title)
                zh_summary = translate_to_zh(summary)

                items.append({
                    "source": source_name,
                    "title": zh_title,
                    "summary": zh_summary,
                    "link": link,
                    "time": pub_time
                })
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
    <title>全球政要与主流媒体全景实时看板</title>
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
            <h1>🌐 全球政要与主流媒体全景看板</h1>
            <p>已自动转换为简体中文并启用滚动加载</p>
        </header>
        <div class="news-list" id="news-container"></div>
        <div id="loading" class="loading-status">正在加载更多资讯...</div>
        <footer><p>Powered by GitHub Actions & Python Translation Engine</p></footer>
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
            }});

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
    print("看板生成成功，已全部翻译为简体中文并写入 index.html！")
