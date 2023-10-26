import easytrader
import myLog as myLogger
log = myLogger.setup_custom_logger(__name__)

from pytesseract import pytesseract
pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

user = easytrader.use('universal_client') 

user.connect(r'C:\同花顺软件\同花顺\xiadan.exe')
user.enable_type_keys_for_editor()

#：
stock_id = '600547'
price = user.get_stock_realtime_price(stock_id)
log.debug('real time price for stock ' + stock_id + ' is ' + str(price))