"""测试股票搜索功能"""
import requests

url = "https://searchapi.eastmoney.com/api/suggest/get"
params = {
    "input": "海螺水泥",
    "type": 14,
    "token": "D43BF722C8E33BDC906FB84D85E326E8",
    "count": 10,
}

print("搜索: 海螺水泥")
print("=" * 80)

r = requests.get(url, params=params, timeout=10)
r.raise_for_status()
data = r.json()
items = data.get("QuotationCodeTable", {}).get("Data", [])

print(f"找到 {len(items)} 个结果:\n")

for idx, item in enumerate(items, 1):
    code = item.get("Code", "")
    name = item.get("Name", "")
    mkt = item.get("MktNum", "")
    mkt_name = {"0": "深A", "1": "沪A", "116": "港股"}.get(mkt, f"其他({mkt})")
    
    print(f"{idx}. {name} ({code}) - {mkt_name}")
    
print("\n" + "=" * 80)
print("搜索: 贵州茅台")
print("=" * 80)

params["input"] = "贵州茅台"
r = requests.get(url, params=params, timeout=10)
r.raise_for_status()
data = r.json()
items = data.get("QuotationCodeTable", {}).get("Data", [])

print(f"找到 {len(items)} 个结果:\n")

for idx, item in enumerate(items, 1):
    code = item.get("Code", "")
    name = item.get("Name", "")
    mkt = item.get("MktNum", "")
    mkt_name = {"0": "深A", "1": "沪A", "116": "港股"}.get(mkt, f"其他({mkt})")
    
    print(f"{idx}. {name} ({code}) - {mkt_name}")
