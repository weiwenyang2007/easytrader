# -*- coding: utf-8 -*-
import re
import time
import tempfile
import pywinauto
from easytrader.utils.captcha import recognize_verify_code

from easytrader.clienttrader import clienttrader
from easytrader.strategy import grid_strategies
import logging

logger = logging.getLogger(__name__)

class THS519ClientTrader(clienttrader.BaseLoginClientTrader):
    """
    同花顺v5.19.15.133的实现(xiadan.exe)
    和5.18的界面相比，发生了变化，需要重新子类化
    """
    grid_strategy = grid_strategies.Copy

    @property
    def broker_type(self):
        return "ths5.19"

    @property
    def balance(self):
        self._switch_left_menus(["查询[F4]", "资金股份"])

        return self._get_grid_data(self._config.COMMON_GRID_CONTROL_ID_NEW)

    def login(self, user, password, exe_path, comm_password=None, **kwargs):
        """
        登陆客户端

        :param user: 账号
        :param password: 明文密码
        :param exe_path: 客户端路径类似 'C:\\中国银河证券双子星3.2\\Binarystar.exe',
            默认 'C:\\中国银河证券双子星3.2\\Binarystar.exe'
        :param comm_password: 通讯密码, 华泰需要，可不设
        :return:
        """
        try:
            # 尝试连接一下，难道一定要等触发异常？？？
            logger.info("尝试连接到原有进程")
            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=1
            )
            logger.info("尝试连接到原有进程成功")

        # pylint: disable=broad-except
        except Exception:
            logger.info("尝试连接到原有进程失败，重新启动软件：%s",exe_path)
            self._app = pywinauto.Application().start(exe_path)

            # wait login window ready
            while True:
                try:
                    logger.info("启动软件完成，查找登录窗口")
                    login_window_handle = pywinauto.findwindows.find_window(class_name='#32770', found_index=1)
                    login_window = self._app.window(handle=login_window_handle).Edit1.wait("ready")
                    break
                except RuntimeError:
                    pass

            logger.info("自动输入：用户[%s]、密码[%s]",user,password[:2]+"*****")
            login_window.Edit1.set_focus()
            login_window.Edit1.type_keys(user)
            login_window.Edit2.set_focus()
            login_window.Edit2.type_keys(password)
            while True:
                try:
                    logger.info("准备开始解析验证码")
                    code = self._handle_verify_code(handle=login_window)
                    login_window.Edit3.type_keys(code)
                    logger.info("解析验证码解析成功，并输入：%s",code)
                    time.sleep(1)
                    self._app.window(handle=login_window)["确定(Y)"].click()
                    # detect login is success or not
                    try:
                        self._app.window(handle=login_window).wait_not("exists", 5)
                        break

                    # pylint: disable=broad-except
                    except Exception:
                        self._app.window(handle=login_window)["确定"].click()

                # pylint: disable=broad-except
                except Exception:
                    pass

            logger.debug("再一次尝试启动软件...")
            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=10
            )
        self._main = self._app.window(title="网上股票交易系统5.0")

    def _handle_verify_code(self,login_window):
        control = self._app.window(handle=login_window).window(control_id=0x5db)
        control.click()
        time.sleep(0.2)
        file_path = tempfile.mktemp() + ".jpg"
        control.capture_as_image().save(file_path)
        time.sleep(0.2)
        vcode = recognize_verify_code(file_path, "gj_client")
        return "".join(re.findall("[a-zA-Z0-9]+", vcode))