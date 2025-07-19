import logging
from scanner import analyze_coin

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_analyze_coin(symbol):
    logging.info(f"بدء اختبار التحليل على {symbol}")
    result = analyze_coin(symbol)
    if result:
        logging.info(f"✅ إشارة شراء تم الكشف عنها لـ {symbol}")
    else:
        logging.info(f"❌ لا توجد إشارة شراء لـ {symbol}")

if __name__ == "__main__":
    # جرب أكثر من رمز هنا
    coins = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]
    for coin in coins:
        test_analyze_coin(coin)
