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

#撤单:
entrust_no = '10135'
canel_rtn = user.cancel_entrust(entrust_no)
print('撤单结果:' +str(canel_rtn))
#{'message': '委托单状态错误不能撤单, 该委托单可能已经成交或者已撤'}
#{'message': 'success'} -- 输入代码或者其他失败都回返回这个success

#user.exit()