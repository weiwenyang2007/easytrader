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

#：
user.get_stock_realtime_price('300059')
#user.get_stock_realtime_price('600547')


#user.exit()