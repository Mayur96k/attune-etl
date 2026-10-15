import json

with open(
    "data/BULABR_20261012_175443.json",
    encoding="utf-8"
) as f:
    d = json.load(f)

s = d["Result"]["ResultData"]

print("Length:", len(s))

print("\n===== START =====\n")
print(s[:1500])

print("\n===== END =====\n")
print(s[-1500:])