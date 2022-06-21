# import pywinauto
#
# _app = pywinauto.Application().connect("c:\\software\\ths\\xiadan.exe")
# _main = _app.top_window()
# grid = _main.child_window(control_id=???, class_name="CVirtualGridCtrl")


# coding: utf-8
import os
import sys
import time
import unittest

sys.path.append(".")


class TestTHS519ClientTrader(unittest.TestCase):
    def setUp(self):
        import easytrader
        # input your test account and password
        self._ACCOUNT = os.environ.get("ACCOUNT")
        self._PASSWORD = os.environ.get("PASSWORD")
        self._user = easytrader.use("ths5.19")
        print("准备登录:", self._ACCOUNT, self._PASSWORD)
        self._user.prepare(user=self._ACCOUNT, password=self._PASSWORD)
        self._user.enable_type_keys_for_editor()

    def tearDown(self) -> None:
        self._user.exit()

    def test_balance(self):
        time.sleep(2)
        result = self._user.balance
        print("查看当前资金：")
        print(result)

    def test_position(self):
        time.sleep(2)
        result = self._user.position
        print("查看当前仓位：")
        print(result)

    def test_buy(self):
        time.sleep(2)
        result = self._user.buy('162411', price=0.05, amount=100)
        print("尝试买入：")
        print(result)

    # def test_today_entrusts(self):
    #     result = self._user.today_entrusts
    #
    # def test_today_trades(self):
    #     result = self._user.today_trades
    #
    # def test_cancel_entrusts(self):
    #     result = self._user.cancel_entrusts
    #
    # def test_cancel_entrust(self):
    #     result = self._user.cancel_entrust("123456789")
    #
    # def test_invalid_buy(self):
    #     import easytrader
    #
    #     with self.assertRaises(easytrader.exceptions.TradeError):
    #         result = self._user.buy("511990", 1, 1e10)
    #
    # def test_invalid_sell(self):
    #     import easytrader
    #
    #     with self.assertRaises(easytrader.exceptions.TradeError):
    #         result = self._user.sell("162411", 200, 1e10)
    #
    # def test_auto_ipo(self):
    #     self._user.auto_ipo()


"""
ACCOUNT= \
PASSWORD= \
python -m unittest tests.test_new_ths.TestTHS519ClientTrader.test_balance
"""
if __name__ == "__main__":
    unittest.main(verbosity=2)
