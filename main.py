import os
import requests
from datetime import datetime

BINANCE_URL = "https://fapi.binance.com/fapi/v1/ticker/24hr"

BLACKLIST = {
    "BTCUSDT", "ETHUSDT", "BNBUSDT",
    "SOLUSDT", "DOGEUSDT", "XRPUSDT", "ADAUSDT"
}


def send_feishu_message(text):
    webhook = os.getenv("FEISHU_WEBHOOK_URL")

    if not webhook:
        print("错误：没有配置 FEISHU_WEBHOOK_URL")
        return

    payload = {
        "msg_type": "text",
        "content": {
            "text": text
        }
    }

    try:
        res = requests.post(webhook, json=payload, timeout=15)
        print("飞书状态码:", res.status_code)
        print("飞书返回:", res.text[:300])
    except Exception as e:
        print("飞书推送失败:", e)


def fetch_market_data():
    try:
        res = requests.get(BINANCE_URL, timeout=15)
        print("Binance HTTP状态码:", res.status_code)
        print("Binance返回前300字:", res.text[:300])

        data = res.json()

        if not isinstance(data, list):
            return None, f"Binance 返回异常：{data}"

        return data, None

    except Exception as e:
        return None, f"请求 Binance 失败：{e}"


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


def filter_top_symbols(data):
    result = []

    for item in data:
        if not isinstance(item, dict):
            continue

        symbol = item.get("symbol", "")

        if not symbol.endswith("USDT"):
            continue

        if symbol in BLACKLIST:
            continue

        result.append(item)

    result.sort(
        key=lambda x: abs(safe_float(x.get("priceChangePercent"))),
        reverse=True
    )

    return result[:5]


def format_message(symbols):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = []
    lines.append("【山寨币异动监控】")
    lines.append(f"时间：{now}")
    lines.append("")

    if not symbols:
        lines.append("没有筛选出有效币种。")
        return "\n".join(lines)

    for i, item in enumerate(symbols, 1):
        symbol = item.get("symbol", "UNKNOWN")
        price = item.get("lastPrice", "未知")
        change = item.get("priceChangePercent", "未知")
        volume = item.get("quoteVolume", "未知")

        lines.append(f"{i}. {symbol}")
        lines.append(f"价格：{price}")
        lines.append(f"24h涨跌幅：{change}%")
        lines.append(f"24h成交额：{volume}")
        lines.append("")

    return "\n".join(lines)


def main():
    data, error = fetch_market_data()

    if error:
        msg = "【山寨币异动监控】\n运行失败：\n" + error
        print(msg)
        send_feishu_message(msg)
        return

    top_symbols = filter_top_symbols(data)
    msg = format_message(top_symbols)

    print(msg)
    send_feishu_message(msg)


if __name__ == "__main__":
    main()
