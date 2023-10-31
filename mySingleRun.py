import schedule
import time
import mySanityCheck as sanity
import myLog as myLogger
log = myLogger.setup_custom_logger(__name__)

def my_easy_trade():
    try:
        log.info('my_easy_trade start')
        balance_data = sanity.sanity_check()
        if balance_data:
            sanity.deal_with_easy_trade(balance_data)
        else:
            log.warn('sanity_result is false, skip deal_with_easy_trade')    
            
        log.info('my_easy_trade end')    
            
    except Exception as ex:
        log.exception(ex)
        log.error('my_easy_trade end with exception')        
    

if __name__ == "__main__":
    my_easy_trade()