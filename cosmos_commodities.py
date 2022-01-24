#!/usr/bin/env python3
import requests
import json
import sys
PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"

class GetAssetPrices(object):
    def __init__(self, symbol):
        self.symbol = symbol

    def _handelDataSourceFailureForGoldSilver(self):
        # do something here
        return None
    
    def _handelDataSourceFailureForOil(self):
        # do something here
        return None

    def _makeRequest(self, requestType, url, headers={}, payload={}):
        if requestType not in ["GET", "POST"]:
            return {"result": "error", "message": "Invalid requestType"}
        try:
            response = requests.request(
                requestType, url, headers=headers, data=payload)
            response = response.json()
            data = {
                "result": "success",
                "responseData": response
            }
        except Exception as e:
            data = {"result": "error",
                    "message": "do something here", "responseData": None}
        return data

    def _getGoldSilverPrice(self):
        requestType = "GET"
        urlGoldSilver = "https://data-asg.goldprice.org/dbXRates/USD"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Cookie': 'lagrange_session=8a6ba1ba-dbda-4d01-b490-8e61cb308ea0'
        }
        payload = json.dumps({})
        data = self._makeRequest(
            requestType=requestType,
            url=urlGoldSilver,
            headers=headers,
            payload=payload
        )
        if data["result"] == "success" and data["responseData"] != None:
            data = data["responseData"]
            if (
                isinstance(data.get("items"), list) == True and
                "xauPrice" in data["items"][0] and
                "xagPrice" in data["items"][0]
            ):
                # GOLD
                if self.symbol == "XAU":
                    return data["items"][0]["xauPrice"]

                # SILVER
                if self.symbol == "XAG":
                    return data["items"][0]["xagPrice"]
            return self._handelDataSourceFailureForGoldSilver()
        return self._handelDataSourceFailureForGoldSilver()

    def _getOilPrice(self):
        requestType = "POST"
        urlOil = "https://asia-southeast2-price-caching.cloudfunctions.net/query-price"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Content-Type': 'application/json'
        }
        payload = json.dumps({
            "source": "oil",
            "symbols": [
                "oil"
            ]})
        data = self._makeRequest(
            requestType=requestType,
            url=urlOil,
            headers=headers,
            payload=payload
        )
        if data["result"] == "success" and data["responseData"] != None:
            data = data["responseData"]
            if isinstance(data, list) == True and len(data)==1:
                #  OIL
                return data[0]
            return self._handelDataSourceFailureForOil()
        return self._handelDataSourceFailureForOil()

    def getPrices(self):
        if self.symbol in ["XAU", "XAG"]:
            return self._getGoldSilverPrice()
        elif self.symbol in ["OIL"]:
            return self._getOilPrice()
        return None

def adjust_rounding(data):
    if data < 1:
        return round(data, 8)
    elif data < 10:
        return round(data, 6)
    else:
        return round(data, 4)


def main(symbols):
    COSMOS_TOKENS = {
        "ATOM": "cosmos",
        "OSMO": "osmosis",
        "SCRT": "secret",
        "AKT": "akash-network",
        "UST": "terrausd",
        "JUNO": "juno-network",
        "CRO": "crypto-com-chain",
        "ION": "ion",
        "XPRT": "persistence",
        "DVPN": "sentinel",
        "LUNA": "terra-luna",
        "REGEN": "regen",
        "KRT": "terra-krw",
        "IRIS": "iris-network",
        "IOV": "starname",
        "NGM": "e-money",
        "IXO": "ixo",
        "BCNA": "bitcanna",
        "BTSG": "bitsong",
        "XKI": "ki",
        "LIKE": "likecoin",
        "EEUR": "e-money-eur",
        "BAND": "band-protocol",
        "CMDX": "comdex",
        "TICK": "microtick",
        "MED" : "medibloc",
        "CHEQ": "cheqd-network",
        "STARS": "stargaze",
        "HUAHUA": "chihuahua-token",
        "LUM"  : "lum-network",
        "VDL"  : "vidulum",
        "DSM"  : "desmos",

    }
    COMMODITIES = {
        "XAU" : "gold",
        "XAG" : "silver",
        "OIL" : "oil",
    }
    slugs = []
    d = {}
    for symbol in symbols:
        if symbol not in COSMOS_TOKENS and symbol not in COMMODITIES:
            raise Exception(f"Unsupported {symbol} symbol")
        if symbol not in COMMODITIES:    
            slugs.append(COSMOS_TOKENS[symbol])
        else:
            result = GetAssetPrices(symbol).getPrices()
            d[symbol] = 0 if result==None else float(result)

    prices = requests.get(
        PRICE_URL,
        params={"ids": ",".join(slugs), "vs_currencies": "USD"},
    ).json()
    for token,name in COSMOS_TOKENS.items():
        for (key, px) in list(prices.items()):
            if name == key:
                d[token]=px['usd']
    result=[]
    index=0
    for symbol in symbols:
        if symbol in d:
            result.insert(index,d[symbol])
        else:
            result.insert(index,0)
        index+=1
    
    return ",".join([str(adjust_rounding(px)) for px in result])


if __name__ == "__main__":
    try:
        print(main([*sys.argv[1:]]))
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

