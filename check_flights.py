
import os, json, csv, datetime, requests

legs = [
    {"departure_id": "DUB", "arrival_id": "BKK", "date": "2027-10-23"},
    {"departure_id": "HKT", "arrival_id": "DUB", "date": "2027-11-07"},
]
r = requests.get("https://serpapi.com/search.json", timeout=120, params={
    "engine": "google_flights", "type": "3", "currency": "EUR", "hl": "en",
    "deep_search": "true",
    "multi_city_json": json.dumps(legs),
    "api_key": os.environ["SERPAPI_KEY"],
})
r.raise_for_status()
d = r.json()

offers = d.get("best_flights", []) + d.get("other_flights", [])
today = datetime.date.today().isoformat()

if offers:
    best = min(offers, key=lambda o: o["price"])
    seg = best["flights"]
    airlines = ", ".join(sorted({s["airline"] for s in seg}))
    msg = f"DUB→BKK 23 Oct / HKT→DUB 7 Nov 2027: €{best['price']} ({airlines}, {len(seg)-1} stop(s) outbound)"
    price = best["price"]
else:
    msg = "DUB→BKK / HKT→DUB 2027: no fares published yet"
    price = ""

print(msg)
with open("prices.csv", "a", newline="") as f:
    csv.writer(f).writerow([today, price])

requests.post(f"https://ntfy.sh/{os.environ['NTFY_TOPIC']}", data=msg.encode("utf-8"))