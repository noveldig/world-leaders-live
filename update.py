import feedparser
from datetime import datetime
import html
import re

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

def fetch_news():
    items = []
    for source_name, url in FEEDS.items():
        try:
            print(f"正在抓取: {source_name}...")
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

                # 对文本进行 HTML 实体转义，防止破坏前端 DOM 结构
                items.append({
                    "source": source_name,
                    "title": html.escape(title),
                    "summary": html.escape(summary),
                    "link": link,
                    "time": pub_time
                })
        except Exception as e:
            print(f"抓取 {source_name} 失败: {e}")

    items.sort(key=lambda x: x['time'], reverse=True)
    return items

def generate_html(items):
    cards_html = ""
    for index, item in enumerate(items):
        cards_html += f"""
        <div class="news-card" data-index="{index}">
            <div class="card-header">
                <span class="badge">{item['source']}</span>
                <span class="time">{item['time']}</span>
            </div>
            <h2><a href="{item['link']}" target="_blank" class="news-title" data-original="{item['title']}">{item['title']}</a></h2>
            <p class="summary" data-original="{item['summary']}">{item['summary']}...</p>
            <a href="{item['link']}" target="_blank" class="read-more">阅读原文 &rarr; <span class="translating-tag">🔄 翻译中...</span></a>
        </div>
        """

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
            transition: all 0.3s ease;
        }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .badge {{ background-color: #ebf8ff; color: #3182ce; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 20px; }}
        .time {{ font-size: 12px; color: var(--text-muted); }}
        h2 {{ font-size: 18px; margin: 0 0 8px 0; line-height: 1.4; }}
        h2 a {{ color: #2d3748; text-decoration: none; }}
        h2 a:hover {{ color: var(--accent); }}
        .summary {{ font-size: 14px; color: #4a5568; line-height: 1.6; margin-bottom: 12px; }}
        .read-more {{ font-size: 13px; color: var(--accent); text-decoration: none; font-weight: 500; }}
        .translating-tag {{ font-size: 11px; color: #e67e22; margin-left: 8px; font-weight: normal; }}
        footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: var(--text-muted); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 全球政要与主流媒体全景看板</h1>
            <p>汇聚全球元首推特动态与世界顶级媒体 <span id="trans-status" style="color: #3498db;">(正在异步翻译中...)</span></p>
        </header>
        <div class="news-list" id="news-container">
            {cards_html}
        </div>
        <footer><p>Powered by GitHub Actions & Async Frontend Translation</p></footer>
    </div>

    <script>
        async function translateText(text) {{
            if (!text) return "";
            try {{
                const url = `https://api.mymemory.translated.net/get?q=${{encodeURIComponent(text)}}&langpair=en|zh`;
                const response = await fetch(url);
                const data = await response.json();
                if (data && data.responseData && data.responseData.translatedText) {{
                    let translated = data.responseData.translatedText;
                    if (!translated.includes("MYMEMORY WARNING")) {{
                        return translated;
                    }}
                }}
            }} catch (e) {{
                console.log("Translation error:", e);
            }}
            return text;
        }}

        async function render() {{
            const cards = document.querySelectorAll('.news-card');
            
            for (let card of cards) {{
                const titleEl = card.querySelector('.news-title');
                const summaryEl = card.querySelector('.summary');
                const tagEl = card.querySelector('.translating-tag');

                const originalTitle = titleEl.getAttribute('data-original');
                const originalSummary = summaryEl.getAttribute('data-original');

                try {{
                    const [zhTitle, zhSummary] = await Promise.all([
                        translateText(originalTitle),
                        translateText(originalSummary)
                    ]);
                    
                    if (zhTitle && zhTitle !== originalTitle) {{
                        titleEl.innerText = zhTitle;
                    }}
                    if (zhSummary && zhSummary !== originalSummary) {{
                        summaryEl.innerText = zhSummary + '...';
                    }}
                    tagEl.innerText = "✅ 已译";
                    tagEl.style.color = "#27ae60";
                }} catch (err) {{
                    tagEl.innerText = "⚠️ 原文";
                }}
            }}
            document.getElementById('trans-status').innerText = "(加载完成)";
        }}

        document.addEventListener('DOMContentLoaded', render);
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
    print("看板生成成功，语法错误已彻底修复！")
