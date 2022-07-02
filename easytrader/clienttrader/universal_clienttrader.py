# -*- coding: utf-8 -*-

import pywinauto
import pywinauto.clipboard

from easytrader.strategy import grid_strategies
from easytrader.clienttrader import clienttrader
import logging

logger = logging.getLogger(__name__)

class UniversalClientTrader(clienttrader.BaseLoginClientTrader):

    # piginzoo,默认使用拷贝的方法，来获得THS上的界面上的信息
    grid_strategy = grid_strategies.Copy # Xls

    @property
    def broker_type(self):
        return "universal"

    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        """
        :param user: 用户名
        :param password: 密码
        :param exe_path: 客户端路径, 类似
        :param comm_password:
        :param kwargs:
        :return:
        """
        self._editor_need_type_keys = False

        try:
            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=1
            )
            # logger.info("尝试连接到原有进程成功")
        # pylint: disable=broad-except
        except Exception:
            self._app = pywinauto.Application().start(exe_path)
            logger.info("尝试连接到原有进程失败，重新启动软件：%s", exe_path)

            # wait login window ready
            while True:
                try:
                    login_window = pywinauto.findwindows.find_window(class_name='#32770', found_index=1)
                    logger.info("登录对话框ready")
                    break
                except:
                    self.wait(1)

            self.wait(1)
            self._app.window(handle=login_window).Edit1.set_focus()
            self._app.window(handle=login_window).Edit1.type_keys('^a{BACKSPACE}')
            self._app.window(handle=login_window).Edit1.type_keys(user)
            logger.info("输入用户名：%s",self._app.window(handle=login_window).Edit1.texts())
            self._app.window(handle=login_window).Edit2.set_focus()
            self._app.window(handle=login_window).Edit2.type_keys('^a{BACKSPACE}')
            self._app.window(handle=login_window).Edit2.type_keys(password)
            logger.info("输入密码：%s", self._app.window(handle=login_window).Edit2.texts())

            # 点击登录按钮
            self._app.window(handle=login_window)['登录'].click()
            logger.info("点击登录按钮")

            # detect login is success or not
            # self._app.top_window().wait_not("exists", 100)
            self.wait(5)

            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=10
            )

        self._close_prompt_windows()
        self._main = self._app.window(title="网上股票交易系统5.0")

