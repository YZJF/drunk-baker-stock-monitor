# Drunk Baker 半价面包库存监控

想吃个醉师傅的新品也不容易啊！监控 Drunk Baker 小程序指定商品的库存变化，有货时弹窗提醒。headers可以抓包后用随便什么人工智能生成一下，这里我隐去了。

---

## 一、项目文件结构

```
drunk-baker-stock-monitor/
├── monitor_tiramisu_stock.py   # 核心：库存监控脚本（定时轮询、状态变化提醒）
├── extract_product_map.py      # 工具：从 http_raw.txt 提取 productId ↔ 商品名映射
├── product_map.csv             # 输出：提取后的商品对照表（productId / 中文名 / 英文名）
├── requirements.txt            # Python 依赖
├── README.md                   # 本文件
├── 屏幕截图 2026-02-27 110955.png  # 参考：小程序"已售罄"界面截图
└── .gitignore                  # 忽略抓包原文和本地笔记，避免提交敏感信息
```

抓包后的原始响应请自行放到仓库根目录的 `http_raw.txt`。该文件已加入 `.gitignore`，不会被提交。

---

## 二、技术栈与工具

### 编程语言
- **Python 3.x**：脚本主语言

### Python 库
- **requests**：发送 HTTP 请求，调用库存接口
- **json**：解析接口返回的 JSON 数据
- **csv**：导出商品映射表
- **ctypes**：调用 Windows 系统弹窗（MessageBoxW）
- **time / datetime**：定时轮询、日志时间戳
- **re**：正则表达式，拆分中英文商品名
- **pathlib**：文件路径处理

### 抓包工具（用于获取接口地址和请求参数）
- **Reqable**（小黄鸟，本项目实际使用，使用方法参见四参考资料）
- **Fiddler**：Windows 上常用的 HTTP/HTTPS 抓包工具
- **Charles**：Mac/Windows 通用抓包代理
- **mitmproxy**：命令行抓包工具（程序员向）
- **浏览器 DevTools（F12）**：网页场景下的抓包

### 涉及的接口
| 接口 | 用途 |
|------|------|
| `GET /menu/service?hqId=...&branchId=...&platform=...` | 获取菜单商品列表（productId、名称、价格、状态） |
| `GET /menu/branch-product-amount/{branchId}` | 获取门店商品实时库存（amount 字段，0=售罄，>0=有货） |

### 运行环境
- Windows 10/11
- Python 3.8+
- 微信 PC 版（用于打开小程序 + 抓包）

---

## 三、快速使用

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 抓包后把 /menu/service 的响应保存为仓库根目录的 http_raw.txt，
#    再把 /menu/branch-product-amount/{branchId} 的 sessionkey / sign / timestamp
#    更新到 monitor_tiramisu_stock.py 的 HEADERS 占位符中。

# 3. 运行监控
python monitor_tiramisu_stock.py

# 4. （可选）重新提取商品映射
python extract_product_map.py
# 或指定路径：
# python extract_product_map.py --input http_raw.txt --output product_map.csv
```

---

## 四、参考资料

- [抢不到 Drunk Baker 五折？怒写监控脚本 - 叶慈 | 小红书](https://www.xiaohongshu.com/discovery/item/692291ae000000001e024922)
  灵感来源：思路是定时请求接口，发现"有货"就提醒。
- [手把手教你爬取小程序 - 举哥爬虫自动化 | 小红书](https://www.xiaohongshu.com/discovery/item/693ea162000000001e02b594)
  视频详细讲了：怎么抓包、怎么找接口、怎么解析 JSON、怎么让 AI 合并代码导出 Excel。

---

## 免责声明

仅用于个人学习与合理使用，请遵守商家与平台规则，勿高频请求、勿滥用接口。
