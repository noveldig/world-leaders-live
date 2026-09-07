import feedparser
from datetime import datetime
import re

FEEDS = {
    "白宫 (The White House)": "https://www.whitehouse.gov/briefings-statements/feed/",
    "联合国 (UN News)": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "英国政府 (UK Gov)": "https://www.gov.uk/government/announcements.atom",
    "欧盟委员会 (European Commission)": "https://ec.europa.eu/commission/presscorner/api/rss?language=en",
    "克里姆林宫 (Kremlin)": "http://en.kremlin.ru/events/news/rss"
}

def fetch_news():
    items = []
    for source_name, url in FEEDS.items():
        try:
            print(f"正在抓取: {source_name}...")
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: # 每个源取最新的 5 条
                title = entry.get('title', 'No Title')
                link = entry.get('link', '#')
                
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    pub_time = datetime(*published[:6]).strftime('%Y-%m-%d %H:%M')
                else:
                    pub_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                summary = entry.get('summary', entry.get('description', ''))
                summary = re.sub('<[^<]+?>', '', summary)[:220] # 清洗 HTML 标签并截断摘要

                items.append({
                    "source": source_name,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "time": pub_time
                })
        except Exception as e:
            print(f"抓取 {source_name} 失败: {e}")

    # 按时间降序排序
    items.sort(key=lambda x: x['time'], reverse=True)
    return items

def generate_html(items):
    cards_html = ""
    for item in items:
        cards_html += f"""
        <div class="news-card">
            <div class="card-header">
                <span class="badge">{item['source']}</span>
                <span class="time">{item['time']}</span>
            </div>
            <h2><a href="{item['link']}" target="_blank">{item['title']}</a></h2>
            <p class="summary">{item['summary']}...</p>
            <a href="{item['link']}" target="_blank" class="read-more">Read Official Source &rarr;</a>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>World Leaders & Government Official Feeds</title>
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
        .container {{ max-width: 800px; margin: 0 auto; }}
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
        footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: var(--text-muted); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 World Leaders & Official Feeds</h1>
            <p>Real-time official announcements (Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')})</p>
        </header>
        <div class="news-list">{cards_html}</div>
        <footer><p>Powered by GitHub Actions | Auto-updated</p></footer>
    </div>
</body>
</html>
"""
    return html_content

if __name__ == "__main__":
    items = fetch_news()
    html = generate_html(items)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html 生成成功！")
