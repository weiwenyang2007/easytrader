import easytrader
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

from pytesseract import pytesseract
pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

user = easytrader.use('universal_client') 

user.connect(r'C:\同花顺软件\同花顺\xiadan.exe')
user.enable_type_keys_for_editor()

#买入：
entrust_no = user.buy('300059', price=12.52, amount=100)
print('买入结果: ' + str(entrust_no))
#{'entrust_no': '7113'} --真正成功返回一个合同编号的数字
#{'message': 'success'} -- 输入代码或者其他失败都回返回这个success

#user.exit()