import feedparser
from datetime import datetime
import json
import re

FEEDS = {
    "The White House": "https://www.whitehouse.gov/briefings-statements/feed/",
    "UN News": "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "UK Gov": "https://www.gov.uk/government/announcements.atom",
    "European Commission": "https://ec.europa.eu/commission/presscorner/api/rss?language=en",
    "Kremlin": "http://en.kremlin.ru/events/news/rss"
}

def fetch_news():
    items = []
    for source_name, url in FEEDS.items():
        try:
            print(f"正在抓取: {source_name}...")
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                title = entry.get('title', 'No Title')
                link = entry.get('link', '#')
                
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    pub_time = datetime(*published[:6]).strftime('%Y-%m-%d %H:%M')
                else:
                    pub_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                
                summary = entry.get('summary', entry.get('description', ''))
                summary = re.sub('<[^<]+?>', '', summary)[:220]

                items.append({
                    "source": source_name,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "time": pub_time
                })
        except Exception as e:
            print(f"抓取 {source_name} 失败: {e}")

    items.sort(key=lambda x: x['time'], reverse=True)
    return items

def generate_html(items):
    # 将数据序列化注入到前端 JS 中，供浏览器异步渲染
    items_json = json.dumps(items, ensure_ascii=False)

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
            <h1>🌐 全球政要与官方动态实时看板</h1>
            <p>实时抓取官方资讯 <span id="trans-status" style="color: #3498db;">(正在异步翻译为中文...)</span></p>
        </header>
        <div class="news-list" id="news-container"></div>
        <footer><p>Powered by GitHub Actions & Frontend Async Translation</p></footer>
    </div>

    <script>
        const rawData = {items_json};

        async function translateText(text) {{
            if (!text) return "";
            try {{
                // 使用免费稳定的 MyMemory 翻译 API 进行异步请求
                const url = `https://api.mymemory.translated.net/get?q=${{encodeURIComponent(text)}}&langpair=en|zh`;
                const response = await fetch(url);
                const data = await response.json();
                if (data && data.responseData && data.responseData.translatedText) {{
                    let translated = data.responseData.translatedText;
                    // 过滤掉 API 配额超限时的提示污染
                    if (!translated.includes("MYMEMORY WARNING")) {{
                        return translated;
                    }}
                }}
            }} catch (e) {{
                console.log("Translation error:", e);
            }}
            return text; // 失败或超时则降级返回原文
        }}

        async function render() {{
            const container = document.getElementById('news-container');
            let htmlContent = '';

            // 先瞬间渲染英文骨架，保证秒开
            rawData.forEach((item, index) => {{
                htmlContent += `
                <div class="news-card" id="card-${{index}}">
                    <div class="card-header">
                        <span class="badge">${{item.source}}</span>
                        <span class="time">${{item.time}}</span>
                    </div>
                    <h2><a href="${{item.link}}" target="_blank" id="title-${{index}}">${{item.title}}</a></h2>
                    <p class="summary" id="summary-${{index}}">${{item.summary}}...</p>
                    <a href="${{item.link}}" target="_blank" class="read-more">阅读官方原文 &rarr; <span class="translating-tag" id="tag-${{index}}">🔄 翻译中...</span></a>
                </div>
                `;
            }});
            container.innerHTML = htmlContent;

            // 异步逐条翻译，成功即替换，失败自动保留英文
            let successCount = 0;
            for (let i = 0; i < rawData.length; i++) {{
                const item = rawData[i];
                try {{
                    const [zhTitle, zhSummary] = await Promise.all([
                        translateText(item.title),
                        translateText(item.summary)
                    ]);
                    
                    if (zhTitle && zhTitle !== item.title) {{
                        document.getElementById(`title-${{i}}`).innerText = zhTitle;
                        successCount++;
                    }}
                    if (zhSummary && zhSummary !== item.summary) {{
                        document.getElementById(`summary-${{i}}`).innerText = zhSummary + '...';
                    }}
                    document.getElementById(`tag-${{i}}`).innerText = "✅ 已译";
                    document.getElementById(`tag-${{i}}`).style.color = "#27ae60";
                }} catch (err) {{
                    document.getElementById(`tag-${{i}}`).innerText = "⚠️ 原文";
                }}
            }}
            document.getElementById('trans-status').innerText = "(中英双语实时加载完成)";
        }}

        document.addEventListener('DOMContentLoaded', render);
    </script>
</body>
</html>
"""
    return html_content

if __name__ == "__main__":
    items = fetch_news()
    html = generate_html(items)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html 异步翻译框架生成成功！")
