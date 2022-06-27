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


class TestUniversalClientTrader(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        import easytrader
        # input your test account and password
        cls._ACCOUNT = os.environ.get("ACCOUNT")
        cls._PASSWORD = os.environ.get("PASSWORD")
        cls._user = easytrader.use("universal_client")
        print("准备登录:", cls._ACCOUNT, cls._PASSWORD)
        cls._user.enable_type_keys_for_editor()
        cls._user.prepare(user=cls._ACCOUNT, password=cls._PASSWORD)

    @classmethod
    def tearDownClass(cls) -> None:
        # cls._user.exit()
        pass

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
        result = self._user.market_buy('600106',amount=100)
        print("尝试买入：")
        print(result)

    def test_cancel(self):
        entrust_no = '2889423298'
        self._user.cancel_entrust(entrust_no)


"""
ACCOUNT= \
PASSWORD= \
python -m unittest tests.test_universal_client.TestUniversalClientTrader.test_cancel
"""
if __name__ == "__main__":
    unittest.main(verbosity=2)
