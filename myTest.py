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

#资金
balance = user.balance
print('当前资金:' + str(balance))
#{'资金余额': 15004.8, '可用金额': 15004.8, '股票市值': 0.0, '总资产': 15004.8, '持仓盈亏': 0.0}  --now

#当前持仓
position = user.position
print('当前持仓:' + str(position))

#当日成交
today_trades = user.today_trades
print('当日成交:' + str(today_trades))

#当日委托
today_entrusts = user.today_entrusts
print('当日委托:' + str(today_entrusts))
#[{'委托时间': '12:19:02', '证券代码': '300059', '证券名称': '东方财富', '操作': '买入',     '备注': '未报', '委托数量': 100, '成交数量': 0, '委托价格': 12.52, '成交均价': 0.0, '撤消数量': 0,   '合同编号': '7113', '交易市场': '深圳Ａ股', 'Unnamed: 12': ''}]
#[{'委托时间': '12:19:02', '证券代码': '300059', '证券名称': '东方财富', '操作': '买入',     '备注': '已报', '委托数量': 100, '成交数量': 0, '委托价格': 12.52, '成交均价': 0.0, '撤消数量': 0,   '合同编号': '7113', '交易市场': '深圳Ａ股', 'Unnamed: 12': ''}]
#[{'委托时间': '12:19:02', '证券代码': '300059', '证券名称': '东方财富', '操作': '买入已撤', '备注': '已撤', '委托数量': 100, '成交数量': 0, '委托价格': 12.52, '成交均价': 0.0, '撤消数量': 100, '合同编号': '7113', '交易市场': '深圳Ａ股', 'Unnamed: 12': ''}]
#
#user.exit()