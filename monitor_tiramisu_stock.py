import json
import time
from datetime import datetime
from typing import Dict, Optional

import requests


# ====== 基础配置 ======
CHECK_INTERVAL_SECONDS = 30
BRANCH_ID = 36839
API_URL = f"https://nice-api.51hchc.com/menu/branch-product-amount/{BRANCH_ID}"
NOTIFY_MODE = "both"  # 可选: "restock_only" / "both"

# 这些是指定要监控的商品
TARGET_PRODUCTS = {
    4318174: "提拉米苏焦糖恰巴塔",
    4318176: "布丁巧克力草莓卷",
    4301375: "红茶芝士草莓蜂蜜吐司三明治",
}

# 说明：
# 1) 下面 headers 用你抓包拿到的值，后续失效时可替换
# 2) 若接口返回 403/401，通常是 sessionkey/sign 过期，需要重新抓包更新
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254171e) XWEB/18787",
    "timestamp": "<YOUR_TIMESTAMP>",           # 抓包获取，每次请求时的毫秒时间戳
    "sign": "<YOUR_SIGN>",                      # 抓包获取，签名摘要
    "xweb_xhr": "1",
    "curpage": "mobile-delivery-ordering/menu/menu",
    "appversion": "2.3.90.103height",
    "vipnumber": "<YOUR_VIP_NUMBER>",           # 抓包获取，你的会员号
    "content-type": "application/json",
    "hqid": "<YOUR_HQID>",                     # 抓包获取，品牌/总部 ID
    "sessionkey": "<YOUR_SESSION_KEY>",         # 抓包获取，登录会话凭证
    "referer": "<YOUR_REFERER>",               # 抓包获取，小程序来源页面
    "accept-language": "zh-CN,zh;q=0.9",
}


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fetch_amount_map() -> Dict[int, int]:
    resp = requests.get(API_URL, headers=HEADERS, timeout=15, verify=False)
    resp.raise_for_status()
    payload = resp.json()
    if str(payload.get("code")) != "0":
        raise RuntimeError(f"接口返回异常 code={payload.get('code')} message={payload.get('message')}")

    amount_map: Dict[int, int] = {}
    for item in payload.get("data", []):
        product_id = item.get("productId")
        amount = item.get("amount")
        if isinstance(product_id, int) and isinstance(amount, int):
            amount_map[product_id] = amount
    return amount_map


def line_notify(msg: str) -> None:
    print(f"\n[{now_str()}] {msg}\n")
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, msg, "库存提醒", 0x40)
    except Exception:
        pass


def main() -> None:
    print(f"[{now_str()}] 启动监控，间隔 {CHECK_INTERVAL_SECONDS}s")
    print(f"[{now_str()}] 监控商品：{json.dumps(TARGET_PRODUCTS, ensure_ascii=False)}")
    print(f"[{now_str()}] 提醒模式：{NOTIFY_MODE}")

    # 记录上一次是否有货，避免重复提醒
    last_in_stock: Dict[int, Optional[bool]] = {pid: None for pid in TARGET_PRODUCTS}

    while True:
        try:
            amount_map = fetch_amount_map()

            for pid, name in TARGET_PRODUCTS.items():
                amount = amount_map.get(pid, -1)
                in_stock = amount > 0

                status_text = "有货" if in_stock else "无货"
                print(f"[{now_str()}] {name} (productId={pid}) 库存={amount} 状态={status_text}")

                # 仅在状态变化时提醒
                if last_in_stock[pid] is not None and last_in_stock[pid] != in_stock:
                    if in_stock:
                        line_notify(f"{name} 现在有货了！库存={amount}")
                    else:
                        if NOTIFY_MODE == "both":
                            line_notify(f"{name} 刚变为无货。")
                        else:
                            print(f"[{now_str()}] {name} 刚变为无货（未弹窗，当前模式: {NOTIFY_MODE}）")

                # 首次运行如果就是有货，也提醒一次，防止错过
                if last_in_stock[pid] is None and in_stock:
                    line_notify(f"{name} 当前有货！库存={amount}")

                last_in_stock[pid] = in_stock

        except requests.HTTPError as e:
            code = e.response.status_code if e.response is not None else "unknown"
            print(f"[{now_str()}] HTTP 错误: {code}，可能是 session/sign 失效，请重新抓包更新 HEADERS")
        except Exception as e:
            print(f"[{now_str()}] 监控异常: {e}")

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    # 某些环境证书链不完整，避免因 SSL 证书报错中断监控
    requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
    main()
