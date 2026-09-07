import feedparser
from deep_translator import GoogleTranslator
from datetime import datetime
import time
import re

FEEDS = {
    "白宫 (The White House)": "https://www.whitehouse.gov/briefings-statements/feed/",
    "联合国 (UN News)": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "英国政府 (UK Gov)": "https://www.gov.uk/government/announcements.atom",
    "欧盟委员会 (European Commission)": "https://ec.europa.eu/commission/presscorner/api/rss?language=en",
    "克里姆林宫 (Kremlin)": "http://en.kremlin.ru/events/news/rss"
}

def safe_translate(translator, text):
    if not text or not text.strip():
        return ""
    # 清洗掉可能导致翻译崩溃的特殊空白或格式
    clean_text = text.strip()[:400]
    for attempt in-range(3): # 最多重试 3 次
        try:
            time.sleep(0.5) # 每次请求间隔 0.5 秒，防止触发 500 频控
            res = translator.translate(clean_text)
            if res:
                return res
        except Exception as e:
            print(f"翻译重试 {attempt+1} 失败: {e}")
            time.sleep(2)
    return text # 如果实在失败，返回原文，避免程序报错中断

def fetch_and_translate():
    translator = GoogleTranslator(source='auto', target='zh-CN')
    items = []

    for source_name, url in FEEDS.items():
        try:
            print(f"正在抓取: {source_name}...")
            feed = feedparser.parse(url)
            for entry in feed.entries[:4]: # 每个源控制在 4 条以内，降低并发
                title_en = entry.get('title', '无标题')
                link = entry.get('link', '#')
                
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    pub_time = datetime(*published[:6]).strftime('%Y-%m-%d %H:%M')
                else:
                    pub_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                summary_en = entry.get('summary', entry.get('description', ''))
                summary_en = re.sub('<[^<]+?>', '', summary_en)[:180]
                
                # 安全翻译
                title_cn = safe_translate(translator, title_en)
                summary_cn = safe_translate(translator, summary_en)

                items.append({
                    "source": source_name,
                    "title": title_cn,
                    "title_en": title_en,
                    "summary": summary_cn,
                    "link": link,
                    "time": pub_time
                })
        except Exception as e:
            print(f"抓取 {source_name} 发生异常: {e}")

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
        .original-title {{ font-size: 12px; color: #a0aec0; margin-bottom: 8px; font-style: italic; }}
        .summary {{ font-size: 14px; color: #4a5568; line-height: 1.6; margin-bottom: 12px; }}
        .read-more {{ font-size: 13px; color: var(--accent); text-decoration: none; font-weight: 500; }}
        footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: var(--text-muted); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 全球政要与官方动态实时看板</h1>
            <p>自动聚合白宫、联合国、欧盟等官方最新通告并实时翻译 (最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})</p>
        </header>
        <div class="news-list">{cards_html}</div>
        <footer><p>Powered by GitHub Actions & Python | 自动定时更新</p></footer>
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
    print("index.html 生成成功且自带容错！")
