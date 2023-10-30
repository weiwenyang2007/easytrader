from datetime import datetime
import json
import easytrader
import myLog as myLogger
import myGetBuySellPrice
log = myLogger.setup_custom_logger(__name__)

from pytesseract import pytesseract
pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

user = easytrader.use('universal_client') 
user.enable_type_keys_for_editor()
user.connect(r'C:\同花顺软件\同花顺\xiadan.exe')

def sanity_check():
    try:
        log.info('Sanity start')

        today = datetime.today().strftime('%Y-%m-%d')
        history_trade = open("Z:/easytrader/data/history_trade.json", "r")
        history_trade_balance_data = json.load(history_trade)
        history_trade.close()

        balance_data = {}
        #资金
        log.debug('get user.balance')
        balance = user.balance
        log.debug('当前资金:' + str(balance))

        money = {}
        money['balance_remain'] = balance['资金余额']
        money['balance_usable'] = balance['可用金额']
        money['balance_stockHold'] = balance['股票市值']
        money['balance_total'] = balance['总资产']

        balance_data['money'] = money

        #当前持仓
        log.debug('get user.position')
        position = user.position
        log.debug('当前持仓:' + str(position))

        stock_holds = []
        for item in position:
            stock = {}
            stock['stock_id'] = item['证券代码']
            stock['hold_number'] = item['股票余额']
            stock['usable_number'] = item['可用余额']
            stock['freeze_number'] = item['冻结数量']
            stock['trade_price'] = item['成本价']
            stock['balance'] = item['市值']
            log.debug(stock)
            stock_holds.append(stock)

        if len(stock_holds) == 0 and money['balance_stockHold'] > 0.0:
            log.error('股票市值 不为0, 但是没有查询到持仓股票')
            raise Exception("Sorry, no stock onHold is found") 
            
        balance_data['stock_holds'] = stock_holds

        #当日成交
        log.debug('get user.today_trades')
        today_trades = user.today_trades
        log.debug('当日成交:' + str(today_trades))

        stock_today_trades = []
        for item in today_trades:
            stock = {}
            stock['datetime'] = today + ' ' + item['成交时间']
            stock['stock_id'] = item['证券代码']
            stock['number'] = item['成交数量']
            stock['price'] = item['成交均价']
            stock['contract_id'] = item['合同编号']
            stock['operation'] = 'Buy' if item['操作']=="证券买入" else 'Sell' if item['操作']=="证券卖出" else 'Unknown'
            stock_today_trades.append(stock)
            
            exist = False
            for his_item in history_trade_balance_data:
                log.debug('his_item='+str(his_item))
                if his_item['contract_id'] == stock['contract_id'] and his_item['datetime'] == stock['datetime'] and his_item['stock_id'] == stock['stock_id']:
                    #already exist
                    exist = True
                    break
            
            if exist == False:
                history_trade_balance_data.append(stock)
                

        balance_data['stock_today_trades'] = stock_today_trades


        #当日委托
        log.debug('get user.today_entrusts')
        today_entrusts = user.today_entrusts
        log.debug('当日委托:' + str(today_entrusts))
        #操作：买入，卖出
        #备注：未报，已报，已撤，已成
        #委托类别：委托，撤单

        stock_today_entrusts = []
        money_occupy = 0.0
        for item in today_entrusts:
            # 过滤没有撤销和成交的委托订单
            if item['成交数量'] == 0 and (item['备注'] == '未报' or item['备注'] == '已报' or item['备注'] == '已报待撤'):
                stock = {}        
                stock['stock_id'] = item['证券代码']
                stock['number'] = item['委托数量']
                stock['price'] = item['委托价格']
                stock['contract_id'] = item['合同编号']
                stock['operation'] = 'Buy' if item['操作']=="买入" else 'Sell' if item['操作']=="卖出" else item['操作']
                
                if stock['operation'] == 'Buy':
                    money_occupy += (int(stock['number']) * float(stock['price']))
                log.debug('Entrust money_occupy: '+str(money_occupy))
                stock_today_entrusts.append(stock)

        balance_data['stock_today_entrusts'] = stock_today_entrusts

        log.debug('balance_data to save is:' +str(balance_data))
        # sanity check for the balance and stock
        # 总资产 = 可用金额 + 股票市值 + 委托占用资金
        # 总资产 - (可用金额 + 股票市值 + 委托占用资金) 的绝对差不能大于某个数。如果上面的查询有异常，资金肯定有很大的出入。
        if abs(float(money['balance_total']) - (float(money['balance_usable']) + float(money['balance_stockHold']) + money_occupy)) >= 100.0:
            log.error("资金验证发现异常,很可能是查询不到某些数据,比如委托订单,当前持仓等")
            raise Exception("Money and stock balance check failure")
        
        
        # Sanity Check is OK for this time, update the json file.
        #save to balance_data file
        with open("Z:/easytrader/data/balance.json", "w") as write_file:
            json.dump(balance_data, write_file, indent=2, sort_keys=True)
          
        #TODO:filter the history_trade_balance_data, only keep the latest buy and sell
        #append today trade to history file
        with open("Z:/easytrader/data/history_trade.json", "w") as write_file:
            json.dump(history_trade_balance_data, write_file, indent=2, sort_keys=True)    
            
        log.info('Sanity success and end')    
        return balance_data
    except Exception as ex:
        log.exception(ex)
        log.error('Sanity end with exception')
        return None


def check_buy_condition(balance_data, target_stock):
    try:
        #Check Buy condiction and make Buy
        log.debug('check_buy_condition start for ' + str(target_stock))
        
        buy_price = myGetBuySellPrice.get_suggested_buy_price(target_stock['stock_id'])
        if not buy_price:
            log.debug('There is no suggest buy_price for ' + target_stock['stock_id'])
            return None
            
        buy_items = {}
        buy_items['buy_price'] = buy_price

        curr_hold_entrust_number = 0
        
        # 检查当前持股数量
        if 'stock_holds' in balance_data:
            stock_holds = balance_data['stock_holds']
            for stock in stock_holds:
                if stock['stock_id'] == target_stock['stock_id']:
                    curr_hold_entrust_number += stock['hold_number']
                    
        # 检查今日委托买入数量            
        if 'stock_today_entrusts' in balance_data:
            stock_today_entrusts = balance_data['stock_today_entrusts']
            for stock in stock_today_entrusts:
                if stock['stock_id'] == target_stock['stock_id'] and stock['operation'] == 'Buy':
                    curr_hold_entrust_number += stock['number']
            
        log.debug('curr_hold_entrust_number is ' + str(curr_hold_entrust_number))    
        # 当前持股数量和委托数量都少于预定最大值,还可以加仓
        if curr_hold_entrust_number < target_stock['max_hold_number']:
            buy_items['stock_id'] = target_stock['stock_id']
            buy_items['buy_number'] = target_stock['base_buy_number']
            
            log.debug('check_buy_condition result: ' + str(buy_items))
            return buy_items
            
        #     
        log.debug('Can not buy more sotck ' + stock_id)
        return None    
    except Exception as ex:
        log.exception(ex)
        log.error('check_buy_condition end with exception') 
        return None
        
        
def check_sell_condition(balance_data, target_stock):
    try:
        #Check Buy condiction and make Buy
        #log.debug('check_sell_condition start for ' + str(target_stock))
        
        sell_price = myGetBuySellPrice.get_suggested_sell_price(target_stock['stock_id'])
        if not sell_price:
            log.debug('There is no suggest sell_price for ' + target_stock['stock_id'])
            return None
        log.debug('sell price for ' + target_stock['stock_id'] + ' is ' + str(sell_price))
            
        sell_items = {}
        sell_items['sell_price'] = sell_price

        curr_usable_number = 0
        curr_entrust_number = 0
        
        # 检查当前持股数量
        if 'stock_holds' in balance_data:
            stock_holds = balance_data['stock_holds']
            for stock in stock_holds:
                if stock['stock_id'] == target_stock['stock_id']:
                    curr_usable_number = stock['usable_number']
                    
        # 检查今日委托卖出数量            
        if 'stock_today_entrusts' in balance_data:
            stock_today_entrusts = balance_data['stock_today_entrusts']
            for stock in stock_today_entrusts:
                if stock['stock_id'] == target_stock['stock_id'] and stock['operation'] == 'Sell':
                    curr_entrust_number = stock['number']
            
        log.debug('curr_usable_number is ' + str(curr_usable_number) + ',curr_entrust_number is ' + str(curr_entrust_number)) 
        # 当前股票可用余额大于最少交易量(100), 而且没有委托卖单,说明还可以卖
        if curr_usable_number >= target_stock['base_sell_number'] and curr_entrust_number == 0:
            sell_items['stock_id'] = target_stock['stock_id']
            sell_items['sell_number'] = target_stock['base_sell_number']
            
            log.debug('check_sell_condition result: ' + str(sell_items))
            return sell_items
            
        #     
        log.debug('Can not sell sny stock ' + target_stock['stock_id'])
        return None    
    except Exception as ex:
        log.exception(ex)
        log.error('check_sell_condition end with exception') 
        return None
        
        
def deal_with_easy_trade(balance_data):
    try:
        #Check Buy condiction and make Buy
        log.debug('deal_with_easy_trade start')
        if not balance_data:
            log.error('balance_data from Sanity Check is None, skip deal_with_easy_trade')
            return None
            
        current_time = datetime.now().strftime("%H:%M:%S")
        if current_time >= '09:26:00' and current_time < '14:59:00':
            log.debug('within trade time, check buy and sell operation')
            target_stocks_f = open("Z:/easytrader/data/target_stocks.json", "r")
            target_stocks = json.load(target_stocks_f)
            for target_stock in target_stocks:
                buy_item = check_buy_condition(balance_data, target_stock)
                if buy_item:
                    log.debug('buy_item is ' + str(buy_item))
                    entrust_no = user.sell(buy_item['stock_id'], price=buy_item['buy_price'], amount=buy_item['buy_number'])        
                    log.debug('buy result: ' + str(entrust_no))
                else:
                    log.debug('no buy for ' + str(target_stock['stock_id']))
                    
                sell_item = check_sell_condition(balance_data, target_stock)
                if sell_item:
                    log.debug('sell_item is ' + str(sell_item))   
                    entrust_no = user.sell(sell_item['stock_id'], price=sell_item['sell_price'], amount=sell_item['sell_number'])        
                    log.debug('sell result: ' + str(entrust_no))
                else:
                    log.debug('no sell for ' + str(target_stock['stock_id']))    
        else:
            log.debug('Time is out of trade time, no buy or sell operation')        
        
        #Check Sell condiction and make Sell
    except Exception as ex:
        log.exception(ex)
        log.error('deal_with_easy_trade end with exception')  
        

if __name__ == "__main__":
    sanity_check()
    #deal_with_easy_trade(json.load(open("Z:/easytrader/data/balance.json", "r")))