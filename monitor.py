import requests
from datetime import datetime

# Bark Key
BARK_KEY = "yLVUqadwXKiBYHXVs8FkHo"

# 监控的股票
STOCKS = [
    "sh600519",  # 贵州茅台
    "sh000001",  # 上证指数
    "sz000001",  # 平安银行
    "sz300750",  # 宁德时代
]

# 阈值
SPEED_THRESHOLD = 0.6

def fetch_data():
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    code_str = ",".join(STOCKS)
    
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f2,f3,f10,f12,f14,f22",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "secids": code_str,
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if data.get("data") and data["data"].get("diff"):
            alerts = []
            for item in data["data"]["diff"]:
                name = item.get("f14", "")
                price = round(item.get("f2", 0) / 100, 2) if item.get("f2") else 0
                speed = round(item.get("f22", 0) / 100, 2) if item.get("f22") else 0
                
                # 涨速超过 0.6% 就提醒
                if abs(speed) >= SPEED_THRESHOLD:
                    direction = "📈" if speed > 0 else "📉"
                    alerts.append(f"{direction} {name} 涨速 {speed:+.2f}% (现价{price})")
            
            if alerts:
                content = "\n".join(alerts)
                content += f"\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                send_bark("⚠️ 股票异动", content)
            else:
                print("无异常")
        else:
            print("API返回数据为空")
                
    except Exception as e:
        print(f"错误: {e}")

def send_bark(title, body):
    try:
        import urllib.parse
        safe_title = urllib.parse.quote(title)
        safe_body = urllib.parse.quote(body)
        
        url = f"https://api.day.app/{BARK_KEY}/{safe_title}/{safe_body}"
        response = requests.get(url, timeout=10)
        print(f"推送状态: {response.status_code}")
    except Exception as e:
        print(f"❌ 推送失败: {e}")

if __name__ == "__main__":
    print(f"开始运行 - {datetime.now()}")
    
    # 测试推送
    send_bark("🧪 股票监控测试", "涨速阈值 0.6%，集合竞价监控已启动！")
    
    fetch_data()
    print("运行结束")
