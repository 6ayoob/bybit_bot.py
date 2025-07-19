from ta.volatility import average_true_range
import pandas as pd
import logging

class RiskManager:
    def __init__(self, capital: float, risk_percent: float = 0.02):
        """
        :param capital: رأس المال الكلي (مثلاً 1000 دولار)
        :param risk_percent: نسبة المخاطرة لكل صفقة (مثلاً 0.02 = 2%)
        """
        self.capital = capital
        self.risk_percent = risk_percent

    def calculate_position_size(self, df: pd.DataFrame, current_price: float, atr_multiplier: float = 1.5):
        """
        حساب حجم الصفقة ووقف الخسارة الديناميكي بناءً على ATR

        :param df: بيانات الشموع (DataFrame)
        :param current_price: السعر الحالي للعملة
        :param atr_multiplier: مضاعف ATR لتحديد وقف الخسارة (افتراضي 1.5)
        :return: (quantity, stop_loss_price)
        """
        try:
            atr = average_true_range(df['high'], df['low'], df['close'], window=14)
            latest_atr = atr.iloc[-1]

            stop_loss_price = current_price - (atr_multiplier * latest_atr)
            risk_amount = self.capital * self.risk_percent

            # التأكد أن الفرق بين السعر ووقف الخسارة موجب
            risk_per_unit = current_price - stop_loss_price
            if risk_per_unit <= 0:
                logging.warning("فرق السعر ووقف الخسارة غير صالح لحساب الحجم")
                return 0, 0

            quantity = risk_amount / risk_per_unit

            # تقريب الكمية لعدد مناسب (4 خانات عشرية)
            return round(quantity, 4), round(stop_loss_price, 4)

        except Exception as e:
            logging.error(f"[RiskManager] خطأ في حساب المخاطر: {e}")
            return 0, 0
