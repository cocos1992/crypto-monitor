import requests
import os
from datetime import datetime

BLACKLIST = ['BTCUSDT','ETHUSDT','BNBUSDT','SOLUSDT','DOGEUSDT','XRPUSDT','ADAUSDT']

def fetch_market_data():
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    try:
        res = requests.get(url, timeout=10)
        return res.json()
    except Exception as e:
        print("请求失败:", e)
        return []

def filter_top_symbols(data):
    filtered = []
    for item in data:
        if item['symbol'].endswith('USDT') and item['symbol'] not in BLACKLIST:
            filtered.append(item)

    sorted_list = sorted(
        filtered,
        key=lambda x: abs(float(x['priceChangePercent'])),
        reverse=True
    )
    return sorted_list[:5]

def format_message(symbols):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"【山寨币异动监控】\n时间：{now}\n\n"

    for i, s in enumerate(symbols, 1):
        msg += f"{i}. {s['symbol']}\n"
        msg += f"价格：{s['lastPrice']}\n"
        msg += f"涨跌幅：{s['priceChangePercent']}%\n"
        msg += f"成交量：{s['quoteVolume']}\n\n"

    return msg

def send_feishu_message(text):
    webhook = os.getenv("FEISHU_WEBHOOK_URL")
    if not webhook:
        print("❌ 未配置飞书 Webhook")
        return

    data = {
        "msg_type": "text",
        "content": {
            "text": text
        }
    }

    try:
        requests.post(webhook, json=data, timeout=10)
    except Exception as e:
        print("推送失败:", e)

def main():
    data = fetch_market_data()
    if not data:
        send_feishu_message("❌ 未获取到数据")
        return

    top_symbols = filter_top_symbols(data)
    if not top_symbols:
        send_feishu_message("❌ 没有筛选出币种")
        return

    msg = format_message(top_symbols)
    send_feishu_message(msg)

if __name__ == "__main__":
    main()
