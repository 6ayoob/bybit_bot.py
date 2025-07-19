mport requests

def get_top_spot_symbols(limit=30):
    """
    جلب أفضل العملات Spot حسب السيولة والحركة الذكية.
    """
    url = "https://api.bybit.com/spot/v3/public/quote/ticker/24hr"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"❌ Network/API error: {e}")
        return []

    if data.get('retCode') != 0:
        print(f"❌ API returned error: {data.get('retMsg', 'Unknown error')}")
        return []

    tickers = data.get('result', [])
    filtered = []

    for ticker in tickers:
        symbol = ticker.get('symbol', '')

        try:
            volume = float(ticker.get('quoteVolume', 0))
            price = float(ticker.get('lastPrice', 0))
            change_percent = abs(float(ticker.get('priceChangePercent', 0)))
        except (ValueError, TypeError):
            continue

        # ✅ شروط الفلتر الذكي
        if (
            symbol.endswith("USDT") and            # فقط رموز USDT
            volume > 500_000 and                   # سيولة جيدة
            price > 0.05 and                       # عملة غير "خردة"
            change_percent > 1                     # تغير سعري ملحوظ اليوم
        ):
            filtered.append({'symbol': symbol, 'volume': volume})

    # ✅ ترتيب حسب السيولة ونأخذ الأعلى
    filtered.sort(key=lambda x: x['volume'], reverse=True)
    top_symbols = [item['symbol'] for item in filtered[:limit]]

    return top_symbols


# اختباريًا
if name == "__main__":
    top = get_top_spot_symbols()
    print("🧠 Top filtered Spot Symbols:")
    for s in top:
        print("•", s)
