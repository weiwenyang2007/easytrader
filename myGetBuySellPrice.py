from datetime import datetime, timedelta
import http.client
import json
import myLog as myLogger
log = myLogger.setup_custom_logger(__name__)


def get_suggested_buy_price(stock_id):

    # first get last Sell trade price from history trades
    # 高抛低吸做T:建议买入价格比上次卖出价格低0.022
    price = get_last_price_from_history_trads(stock_id, 'Sell')
    #TODO: additional check price is within price+-10% or 20%
    if price and price > 0.0:
        return price * 0.978
    
    #Has risk to based on realtime
    #price = get_realtime_price_from_sina(stock_id)
    #if price:
    #    return price * 0.978 
        
    # else get suggest buy price from shenXian Indicator (hc6 value)
    price = get_indocator_from_easystogu(stock_id, 'Buy')
    #TODO: additional check price is within price+-10% or 20%
    if price and price > 0.0:
        return price
               
    log.debug('Can not get_suggested_buy_price for ' + stock_id)
    
    return None     

def get_suggested_sell_price(stock_id):
    
    # first get last Buy trade price from history trades
    # 高抛低吸做T:建议卖出价格比上次买入价格高0.022
    # 优先选择上次买入价格，做T
    price = get_last_price_from_history_trads(stock_id, 'Buy')
    #TODO: additional check price is within price+-10% or 20%
    if price and price > 0.0:
        return price * 1.022
    
    #Has risk to based on realtime
    #price = get_realtime_price_from_sina(stock_id)
    #if price:
    #    return price * 1.022
    
    # else get suggest buy price from shenXian Indicator (hc6 value)
    # 其次选择shenxian卖指标，这个值比上面那个要高或者低都有可能
    price = get_indocator_from_easystogu(stock_id, 'Sell')
    #TODO: additional check price is within price+-10% or 20%
    if price and price > 0.0:
        return price
               
    log.debug('Can not get_suggested_sell_price for ' + stock_id)
    
    return None     

def get_realtime_price_from_sina(stock_id):
    try:
        log.debug('get_realtime_price_from_sina start')
        
        symbol_value = ''
        if stock_id.startswith('6'):
            symbol_value = 'sh' + stock_id
        elif stock_id.startswith('3') or stock_id.startswith('0'):
            symbol_value = 'sz' + stock_id
            
        conn = http.client.HTTPConnection('vip.stock.finance.sina.com.cn')
        headers = {'Content-type': 'application/json'}
        conn.request('GET', '/quotes_service/view/vML_DataList.php?asc=j&symbol=' + symbol_value + '&num=1', None, headers)

        response = conn.getresponse()
        resp = response.read().decode()
        log.debug('realtime price for ' + stock_id + ' is ' + resp)
        #var minute_data_list = [['15:00:00', '24.89', '215872']];
        
        return None
        
    except Exception as ex:
        log.exception(ex)
        log.error('get_realtime_price_from_sina End with exception')
        return None      


def get_last_price_from_history_trads(stock_id, buyOrSell):
    try:
        log.debug('get_last ' + buyOrSell + ' price_from_history_trads Start')        
        
        his_trade_file = open("D:/github/easytrader/data/history_trade.json", "r")
        his_trade_data = json.load(his_trade_file)
        log.debug('his_trade_data for ' + stock_id + ' is ' + str(his_trade_data))
        
        for item in his_trade_data:
            if item['stock_id'] == stock_id:
                if item['operation'] == 'Buy' and buyOrSell == 'Buy':
                    return float(item['price'])
                elif item['operation'] == 'Sell' and buyOrSell == 'Sell':
                    return float(item['price'])                           
        
        log.debug('Can not get_last_' + buyOrSell + '_price_from_history_trads')
        
        return None
        
    except Exception as ex:
        log.exception(ex)
        log.error('get_last ' + buyOrSell + ' price_from_history_trads End with exception')
        return None    

def get_indocator_from_easystogu(stock_id, buyOrSell):
    try:
        log.debug('get ' + buyOrSell + ' indocator_from_easystogu Start')       
        
        conn = http.client.HTTPConnection('192.168.10.200:8080')

        headers = {'Content-type': 'application/json'}

        # use 120 days data for prediction
        days_before_120 = (datetime.today() - timedelta(days=120)).strftime('%Y-%m-%d')  
        today = datetime.today().strftime('%Y-%m-%d')
        dayParm = days_before_120 + '_' + today

        if buyOrSell == 'Buy':
            # Buy
            conn.request('POST', '/portal/indv3/predictTodayBuy/' + stock_id + '/' + dayParm, None, headers)

            response = conn.getresponse()
            respJson = json.loads(response.read().decode())
            log.debug('predictTodayBuy for ' + stock_id + 'is ' + str(respJson))

            if 'B' in respJson['sellFlagsTitle']:
                log.debug(stock_id + ' Buy@'+str(respJson['hc6']))
                #TODO: to check if respJson['updatedTime'] is outof dated
                return float(respJson['hc6'])
        else:
            # Sell
            conn.request('POST', '/portal/indv3/predictTodaySell/' + stock_id + '/' + dayParm, None, headers)

            response = conn.getresponse()
            respJson = json.loads(response.read().decode())
            log.debug('predictTodaySell for ' + stock_id + 'is ' + str(respJson))

            if 'S' in respJson['sellFlagsTitle']:
                log.debug(stock_id + ' Sell@'+str(respJson['hc5']))
                #TODO: to check if respJson['updatedTime'] is outof dated
                return float(respJson['hc5'])
                
        #        
        log.debug('Can not get ' + buyOrSell + ' indocator_from_easystogu')
        
        return None
        
    except Exception as ex:
        log.exception(ex)
        log.error('get_' + buyOrSell + '_indocator_from_easystogu End with exception')
        return None
        

if __name__ == "__main__":
    price = get_suggested_sell_price('600547')
    print('Result is ' + str(price))