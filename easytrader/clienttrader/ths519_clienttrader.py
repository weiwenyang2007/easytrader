# -*- coding: utf-8 -*-

from easytrader.clienttrader.universal_clienttrader import UniversalClientTrader


class THS519ClientTrader(UniversalClientTrader):
    """
    同花顺v5.19.15.133的实现(xiadan.exe)
    和5.18的界面相比，发生了变化，需要重新子类化
    """

    @property
    def broker_type(self):
        return "ths5.19"

    @property
    def balance(self):
        self._switch_left_menus(["查询[F4]", "资金股份"])

        return self._get_grid_data(self._config.COMMON_GRID_CONTROL_ID_NEW)
