# -*- coding: utf-8 -*-
import re
import time
import tempfile
import pywinauto
from pywinauto.findwindows import WindowNotFoundError

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
            logger.info("启动软件完毕，等待登录窗口出现")
            while True:
                try:
                    login_window_handle = pywinauto.findwindows.find_window(class_name='#32770', found_index=1)
                    login_window = self._app.window(handle=login_window_handle)
                    login_window.Edit1.wait("ready")
                    break
                except WindowNotFoundError:
                    logger.debug(".")
                    time.sleep(1)

            logger.info("登录窗口出现，准备输入用户名和密码")
            logger.info("自动输入：用户[%s]、密码[%s]",user,password[:2]+"****")
            login_window.Edit1.set_focus()
            login_window.Edit1.type_keys(user)
            login_window.Edit2.set_focus()
            login_window.Edit2.type_keys(password)

            logger.info("准备开始解析验证码")
            retry = 0
            while retry<5:
                try:
                    code = self._handle_verify_code(handle=login_window_handle)
                    login_window.Edit3.type_keys('^a{BACKSPACE}')
                    login_window.Edit3.type_keys(code)
                    logger.info("解析验证码解析成功，并输入到Edit框：%s",code)
                    time.sleep(1)
                    # 点击右侧的确定按钮来登录
                    self._app.window(handle=login_window_handle)["确定(Y)"].click()
                    # 等待登录窗口消失
                    self._app.window(handle=login_window_handle).wait_not("exists", 5)
                    # 跳出去
                    break
                # pylint: disable=broad-except
                except Exception:
                    time.sleep(1)
                    logger.debug("登录失败，再一次尝试")
                    retry+= 1

            logger.debug("再一次尝试启动软件...")
            self._app = pywinauto.Application().connect(
                path=self._run_exe_path(exe_path), timeout=10
            )
        self._main = self._app.window(title="网上股票交易系统5.0")

    def _handle_verify_code(self,handle):
        control = self._app.window(handle=handle).window(control_id=0x5db)
        control.click()
        time.sleep(0.2)
        file_path = tempfile.mktemp() + ".jpg"
        # 新版同花顺的登录验证码居然是分成了2部分，3个数字+1个数字，很恶心，需要hack一下宽度，扩大一些来存图片
        rect = control.rectangle()
        height = rect.bottom - rect.top
        rect.right += height
        control.capture_as_image(rect).save(file_path)
        time.sleep(0.2)
        vcode = recognize_verify_code(file_path)
        logger.debug("验证码识别结果：%s",vcode)
        return "".join(re.findall("[a-zA-Z0-9]+", vcode))