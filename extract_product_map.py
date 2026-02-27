import csv
import json
import re
from pathlib import Path


INPUT_FILE = Path(r"c:\Users\DELL\Desktop\code\新建文件夹\http_raw.txt")
OUTPUT_FILE = Path(r"c:\Users\DELL\Desktop\code\新建文件夹\product_map.csv")


def read_text_with_fallback(path: Path) -> str:
    data = path.read_bytes()
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def extract_json_blob(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("未找到有效 JSON 内容")
    return json.loads(text[start : end + 1])


def split_name_cn_en(name: str) -> tuple[str, str]:
    # Prefer splitting by two or more spaces first.
    by_spaces = re.split(r"\s{2,}", name.strip())
    if len(by_spaces) >= 2:
        cn = by_spaces[0].strip()
        en = " ".join(x.strip() for x in by_spaces[1:] if x.strip())
        return cn, en

    # Fallback: extract ASCII-like phrase as English name.
    en_candidates = re.findall(
        r"[A-Za-z][A-Za-z0-9&().,'+\-\/ ]*[A-Za-z0-9)]", name
    )
    en = max(en_candidates, key=len).strip() if en_candidates else ""

    if en:
        cn = name.replace(en, "").strip(" -_/|")
    else:
        cn = name.strip()

    return cn.strip(), en.strip()


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"找不到输入文件: {INPUT_FILE}")

    text = read_text_with_fallback(INPUT_FILE)
    payload = extract_json_blob(text)

    product_map: dict[int, str] = {}
    for category in payload.get("data", []):
        for product in category.get("products", []):
            product_id = product.get("id")
            name = product.get("name")
            if product_id is None or not isinstance(name, str):
                continue
            product_map[int(product_id)] = name.strip()

    rows = []
    for product_id, raw_name in sorted(product_map.items()):
        name_cn, name_en = split_name_cn_en(raw_name)
        rows.append(
            {
                "product_id": product_id,
                "name_raw": raw_name,
                "name_cn": name_cn,
                "name_en": name_en,
            }
        )

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f, fieldnames=["product_id", "name_raw", "name_cn", "name_en"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"已导出 {len(rows)} 条记录 -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
