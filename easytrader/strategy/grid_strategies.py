# -*- coding: utf-8 -*-
import abc
import io
import os
import tempfile
from io import StringIO
from typing import TYPE_CHECKING, Dict, List, Optional

import pandas as pd
import pywinauto.keyboard
import pywinauto
import pywinauto.clipboard

from easytrader.log import logger
from easytrader.utils.captcha import captcha_recognize
from easytrader.utils.win_gui import SetForegroundWindow, ShowWindow, win32defines

if TYPE_CHECKING:
    # pylint: disable=unused-import
    from easytrader import clienttrader


class IGridStrategy(abc.ABC):
    @abc.abstractmethod
    def get(self, control_id: int) -> List[Dict]:
        """
        获取 gird 数据并格式化返回

        :param control_id: grid 的 control id
        :return: grid 数据
        """
        pass

    @abc.abstractmethod
    def set_trader(self, trader: "clienttrader.IClientTrader"):
        pass


class BaseStrategy(IGridStrategy):
    def __init__(self):
        self._trader = None

    def set_trader(self, trader: "clienttrader.IClientTrader"):
        self._trader = trader

    @abc.abstractmethod
    def get(self, control_id: int) -> List[Dict]:
        """
        :param control_id: grid 的 control id
        :return: grid 数据
        """
        pass

    def _get_grid(self, control_id: int):
        grid = self._trader.main.child_window(
            control_id=control_id, class_name="CVirtualGridCtrl"
        )
        return grid

    def _set_foreground(self, grid=None):
        try:
            if grid is None:
                grid = self._trader.main
            if grid.has_style(win32defines.WS_MINIMIZE):  # if minimized
                ShowWindow(grid.wrapper_object(), 9)  # restore window state
            else:
                SetForegroundWindow(grid.wrapper_object())  # bring to front
        except:
            pass


class Copy(BaseStrategy):
    """
    通过复制 grid 内容到剪切板再读取来获取 grid 内容
    """

    _need_captcha_reg = True

    def get(self, control_id: int) -> List[Dict]:
        grid = self._get_grid(control_id)
        self._set_foreground(grid)
        # Clt-A + Clt-C
        grid.type_keys("^A^C", set_foreground=False)

        # 从剪贴板获得相应信息
        content = self._get_clipboard_data()
        #print('clip data is ' + str(content))
        pywinauto.clipboard.EmptyClipboard()
        return self._format_grid_data(content)

    def _format_grid_data(self, data: str) -> List[Dict]:
        try:
            df = pd.read_csv(
                io.StringIO(data),
                delimiter="\t",
                dtype=self._trader.config.GRID_DTYPE,
                na_filter=False,
            )
            return df.to_dict("records")
        except:
            Copy._need_captcha_reg = True

    def _get_clipboard_data(self) -> str:
        if Copy._need_captcha_reg:
            try:
                #print('_need_captcha_reg')
                dlg = self._trader.app.top_window().window(class_name="Static", title_re="验证码")
                dlg.wait_not('visible', timeout=1)
            #if self._trader.app.top_window().window(class_name="Static", title_re="验证码").exists(timeout=1):
                # logger.debug("验证码对话框弹出，需要OCR识别")
                file_path = tempfile.mktemp()+".png"
                # print('tempfile is: '+ file_path)

                count = 5
                found = False
                while count > 0:
                    control = self._trader.app.top_window().window(
                        control_id=0x965, class_name="Static"
                    )

                    rect = control.element_info.rectangle
                    rect.right = round(
                        rect.right + (rect.right - rect.left) * 0.3
                    )  # 扩展验证码控件截图范围为5个字符
                
                    self._trader.app.top_window().window(
                        control_id=0x965, class_name="Static"
                    ).capture_as_image(rect).save(
                        file_path
                    )  # 保存验证码                   

                    captcha_num = captcha_recognize(file_path).strip()  # 识别验证码
                    captcha_num = "".join(captcha_num.split())
                    #logger.info("验证码识别结果：%s" , captcha_num)
                    #print('captcha_num='+str(captcha_num))
                    if len(captcha_num) == 5:
                        # self._trader.app.top_window().window(
                        #     control_id=0x964, class_name="Edit"
                        # ).set_text(
                        #     captcha_num
                        # )  # 模拟输入验证码
                        # https://github.com/shidenggui/easytrader/issues/452

                        editor = self._trader.app.top_window().child_window(control_id=0x964,class_name="Edit")# 0x964是验证码输入框
                        editor.select()
                        editor.type_keys(captcha_num)
                        self._trader.app.top_window().set_focus()
                        pywinauto.keyboard.SendKeys("{ENTER}")  # 模拟发送enter，点击确定
                        try:
                            self._trader.wait(1)
                            # 下面的"验证码错误！"label，如果不存在（会触发异常），说明识别通过了
                            logger.info(
                                self._trader.app.top_window()
                                    .window(control_id=0x966, class_name="Static")
                                    .window_text()
                            )
                        except Exception as ex:  # 窗体消失
                            found = True
                            # logger.info("识别完成")
                            #print('识别完成')
                            break
                    count -= 1
                    self._trader.wait(1)
                    self._trader.app.top_window().window(
                        control_id=0x965, class_name="Static"
                    ).click()
                if not found:
                    self._trader.app.top_window().Button2.click()  # 点击取消
            #else:
            #    print('Error No pop up windows is detect?')
            except Exception as e:
                logger.warn('No pop up windows is detect for password, ignore ORC and exception')

        count = 1  # 5
        while count > 0:
            try:
                return pywinauto.clipboard.GetData()
            # pylint: disable=broad-except
            except Exception as e:
                count -= 1
                logger.exception("%s, retry clipboard.GetData", e)


class WMCopy(Copy):
    """
    通过复制 grid 内容到剪切板再读取来获取 grid 内容
    """

    def get(self, control_id: int) -> List[Dict]:
        grid = self._get_grid(control_id)
        grid.post_message(win32defines.WM_COMMAND, 0xE122, 0)
        self._trader.wait(0.1)
        content = self._get_clipboard_data()
        return self._format_grid_data(content)


class Xls(BaseStrategy):
    """
    通过将 Grid 另存为 xls 文件再读取的方式获取 grid 内容
    """

    def __init__(self, tmp_folder: Optional[str] = None):
        """
        :param tmp_folder: 用于保持临时文件的文件夹
        """
        super().__init__()
        self.tmp_folder = tmp_folder

    def get(self, control_id: int) -> List[Dict]:
        grid = self._get_grid(control_id)

        # ctrl+s 保存 grid 内容为 xls 文件
        self._set_foreground(grid)  # setFocus buggy, instead of SetForegroundWindow
        grid.type_keys("^s", set_foreground=False)
        count = 10
        while count > 0:
            if self._trader.is_exist_pop_dialog():
                break
            self._trader.wait(0.2)
            count -= 1

        temp_path = tempfile.mktemp(suffix=".xls", dir=self.tmp_folder)
        self._set_foreground(self._trader.app.top_window())

        # alt+s保存，alt+y替换已存在的文件
        self._trader.app.top_window().Edit1.set_edit_text(temp_path)
        self._trader.wait(0.1)
        self._trader.app.top_window().type_keys("%{s}%{y}", set_foreground=False)
        # Wait until file save complete otherwise pandas can not find file
        self._trader.wait(0.2)
        if self._trader.is_exist_pop_dialog():
            self._trader.app.top_window().Button2.click()
            self._trader.wait(0.2)

        return self._format_grid_data(temp_path)

    def _format_grid_data(self, data: str) -> List[Dict]:
        with open(data, encoding="gbk", errors="replace") as f:
            content = f.read()

        df = pd.read_csv(
            StringIO(content),
            delimiter="\t",
            dtype=self._trader.config.GRID_DTYPE,
            na_filter=False,
        )
        return df.to_dict("records")
