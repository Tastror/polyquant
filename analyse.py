import re
import sys
import json

data_file = sys.argv[1]

stock_re = re.compile(r"(Bought|Sold) ([\d,\.]*) (Yes|No) at ([\d,\.]*)¢ \(\$([\d,\.]*)\)")

profile_list = []
tmp_dict = {}

f = open(data_file, 'r')


yes = {
    "buy-money": 0.0,
    "buy-stock": 0,
    "sell-money": 0.0,
    "sell-stock": 0,
    "remain-money": 0.0,
    "remain-stock": 0,
    "profit-weight-buy-money": 0.0,  # sum of each (buy-money * profit)
    "profit-weight-buy-stock": 0.0,  # sum of each (buy-stock * profit)
    "profit-weight-sell-money": 0.0,  # sum of each (sell-money * profit)
    "profit-weight-sell-stock": 0.0,  # sum of each (sell-stock * profit)
    "profit-weight-remain-money": 0.0,  # sum of each (remain-money * profit)
    "profit-weight-remain-stock": 0.0,  # sum of each (remain-stock * profit)
}

no = yes.copy()

result = {
    "yes": yes,
    "no": no
}

most_profitable_person = { "profit": float("-inf") }
most_nonprofitable_person = { "profit": float("inf") }
prefix = 0
start = False
last_time = ""
print()
for lineno, line in enumerate(f):
    if not start:
        if line.strip() == "--- start ---":
            prefix = lineno + 1
            start = True
            continue
        else:
            print(f"metadata: {line.strip()}")
            continue
    profile_num = (lineno - prefix) // 5
    profile_pos = (lineno - prefix) % 5
    if profile_pos == 0:
        tmp_dict["url"] = line.strip()
    elif profile_pos == 1:
        tmp_dict["name"] = line.strip()
    elif profile_pos == 2:
        tmp_dict["reltime"] = line.strip()
        last_time = tmp_dict["reltime"]
    elif profile_pos == 3:
        stock_match = stock_re.match(line.strip())
        if stock_match:
            tmp_dict["buy"] = stock_match.group(1) == "Bought"
            tmp_dict["stock"] = int(stock_match.group(2).replace(",", ""))
            tmp_dict["yes"] = stock_match.group(3) == "Yes"
            tmp_dict["price"] = float(stock_match.group(4).replace(",", "")) / 100
            tmp_dict["total-price(show)"] = float(stock_match.group(5).replace(",", ""))
            tmp_dict["total-price"] = tmp_dict["stock"] * tmp_dict["price"]
        else:
            raise ValueError(f"Invalid stock line: {line.strip()}")
    elif profile_pos == 4:
        tmp_dict["profit"] = float(line.strip().replace("$", "").replace(",", ""))
        profile_list.append(tmp_dict)

        # print(f"{profile_num}: {tmp_dict}")

        if tmp_dict["profit"] > most_profitable_person["profit"]:
            most_profitable_person = tmp_dict
        if tmp_dict["profit"] < most_nonprofitable_person["profit"]:
            most_nonprofitable_person = tmp_dict

        yes_or_no = "yes" if tmp_dict["yes"] else "no" 
        buy_or_sell = "buy" if tmp_dict["buy"] else "sell"
        result[yes_or_no][f"{buy_or_sell}-money"] += tmp_dict["total-price"]
        result[yes_or_no][f"{buy_or_sell}-stock"] += tmp_dict["stock"]
        result[yes_or_no][f"profit-weight-{buy_or_sell}-money"] += tmp_dict["total-price"] * tmp_dict["profit"]
        result[yes_or_no][f"profit-weight-{buy_or_sell}-stock"] += tmp_dict["stock"] * tmp_dict["profit"]

        tmp_dict = {}


for yes_or_no in ["yes", "no"]:
    result[yes_or_no]["remain-money"] = result[yes_or_no]["buy-money"] - result[yes_or_no]["sell-money"]
    result[yes_or_no]["remain-stock"] = result[yes_or_no]["buy-stock"] - result[yes_or_no]["sell-stock"]
    result[yes_or_no]["profit-weight-remain-money"] = result[yes_or_no]["profit-weight-buy-money"] - result[yes_or_no]["profit-weight-sell-money"]
    result[yes_or_no]["profit-weight-remain-stock"] = result[yes_or_no]["profit-weight-buy-stock"] - result[yes_or_no]["profit-weight-sell-stock"]

f.close()

print(f"last time: {last_time}")
print()

print(f"most profitable person: {most_profitable_person}")
print()
print(f"most nonprofitable person: {most_nonprofitable_person}")
print()

print(f"result: {json.dumps(result, indent=4)}")
print(f"yes - no (money): {result['yes']['remain-money'] - result['no']['remain-money']}")
print(f"yes - no (stock): {result['yes']['remain-stock'] - result['no']['remain-stock']}")
print(f"yes - no (profit-weight-money): {result['yes']['profit-weight-remain-money'] - result['no']['profit-weight-remain-money']}")
print(f"yes - no (profit-weight-stock): {result['yes']['profit-weight-remain-stock'] - result['no']['profit-weight-remain-stock']}")
