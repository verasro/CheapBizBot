import os, datetime as dt
from amadeus import Client, ResponseError

def daterange(start, end):
    d0, d1 = map(dt.date.fromisoformat, (start, end))
    for n in range((d1 - d0).days + 1):
        yield (d0 + dt.timedelta(n)).isoformat()

def run_once(origin="GIG", dest="MIA",
             start_date="2025-05-22", end_date="2025-06-30",
             max_price=2500, max_stops=1, max_layover=2.0):
    amadeus = Client()
    best = None
    for date in daterange(start_date, end_date):
        try:
            resp = amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=dest,
                departureDate=date,
                adults=1,
                travelClass="BUSINESS",
                currencyCode="USD",
                max=10
            ).data
        except ResponseError:
            continue

        for offer in resp:
            price = float(offer["price"]["grandTotal"])
            it = offer["itineraries"][0]
            stops = len(it["segments"]) - 1
            lay = 0
            if stops:
                lay = max(
                    (dt.datetime.fromisoformat(s2["departure"]["at"])
                     - dt.datetime.fromisoformat(s1["arrival"]["at"])
                    ).total_seconds()/3600
                    for s1, s2 in zip(it["segments"][:-1], it["segments"][1:])
                )
            if price <= max_price and stops <= max_stops and lay <= max_layover:
                if best is None or price < best["price"]:
                    best = {"price": price, "date": date,
                            "stops": stops, "layover": round(lay, 1)}
    return best
