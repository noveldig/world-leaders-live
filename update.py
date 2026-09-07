import feedparser
from deep_translator import GoogleTranslator
from datetime import datetime
import json
import os

# 官方 RSS / Atom 订阅源列表（涵盖主要政府与国际组织）
FEEDS = {
    "白宫 (The White House)": "https://www.whitehouse.gov/briefings-statements/feed/",
    "联合国 (UN News)": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "英国政府 (UK Gov)": "https://www.gov.uk/government/announcements.atom",
    "欧盟委员会 (European Commission)": "https://ec.europa.eu/commission/presscorner/api/rss?language=en",
    "克里姆林宫 (Kremlin)": "http://en.kremlin.ru/events/news/rss"
}

def fetch_and_translate():
    translator = GoogleTranslator(source='auto', target='zh-CN')
    items = []

    for source_name, url in FEEDS.items():
        try:
            print(f"正在抓取: {source_name}...")
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: # 每个源取最新的 5 条
                title_en = entry.get('title', '无标题')
                link = entry.get('link', '#')
                
                # 尝试获取发布时间
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    pub_time = datetime(*published[:6]).strftime('%Y-%m-%d %H:%M')
                else:
                    pub_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                # 获取摘要
                summary_en = entry.get('summary', entry.get('description', ''))
                # 简单清洗 HTML 标签
                import re
                summary_en = re.sub('<[^<]+?>', '', summary_en)[:200]
                
                # 翻译成中文
                try:
                    title_cn = translator.translate(title_en[:500])
                except Exception:
                    title_cn = title_en
                    
                try:
                    summary_cn = translator.translate(summary_en[:500]) if summary_en else ""
                except Exception:
                    summary_cn = summary_en

                items.append({
                    "source": source_name,
                    "title": title_cn,
                    "title_en": title_en,
                    "summary": summary_cn,
                    "link": link,
                    "time": pub_time
                })
        except Exception as e:
            print(f"抓取 {source_name} 失败: {e}")

    # 按时间排序
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
            <p class="original-title">原标题: {item['title_en']}</p>
            <p class="summary">{item['summary']}</p>
            <a href="{item['link']}" target="_blank" class="read-more">阅读官方原文 &rarr;</a>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>全球政要与官方动态实时看板</title>
    <style>
        :root {{
            --bg-color: #f4f6f9;
            --card-bg: #ffffff;
            --text-main: #2c3e50;
            --text-muted: #7f8c8d;
            --accent: #3498db;
            --border-color: #e2e8f0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        header h1 {{
            font-size: 24px;
            margin-bottom: 8px;
            color: #1a202c;
        }}
        header p {{
            color: var(--text-muted);
            font-size: 14px;
        }}
        .news-card {{
            background: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .news-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .badge {{
            background-color: #ebf8ff;
            color: #3182ce;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 20px;
        }}
        .time {{
            font-size: 12px;
            color: var(--text-muted);
        }}
        h2 {{
            font-size: 18px;
            margin: 0 0 8px 0;
            line-height: 1.4;
        }}
        h2 a {{
            color: #2d3748;
            text-decoration: none;
        }}
        h2 a:hover {{
            color: var(--accent);
        }}
        .original-title {{
            font-size: 12px;
            color: #a0aec0;
            margin-bottom: 8px;
            font-style: italic;
        }}
        .summary {{
            font-size: 14px;
            color: #4a5568;
            line-height: 1.6;
            margin-bottom: 12px;
        }}
        .read-more {{
            font-size: 13px;
            color: var(--accent);
            text-decoration: none;
            font-weight: 500;
        }}
        .read-more:hover {{
            text-decoration: underline;
        }}
        footer {{
            text-align: center;
            margin-top: 40px;
            font-size: 12px;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 全球政要与官方动态实时看板</h1>
            <p>自动聚合白宫、联合国、英国政府等官方最新通告并实时翻译 (最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})</p>
        </header>
        
        <div class="news-list">
            {cards_html}
        </div>
        
        <footer>
            <p>Powered by GitHub Actions & Python | 自动定时更新</p>
        </footer>
    </div>
</body>
</html>
"""
    return html_content

if __name__ == "__main__":
    items = fetch_and_translate()
    html = generate_html(items)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html 生成成功！")
