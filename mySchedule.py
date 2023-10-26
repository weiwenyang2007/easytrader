import schedule
import time
import mySanityCheck as sanity
import myLog as myLogger
log = myLogger.setup_custom_logger(__name__)

def my_easy_trade():
    try:
        balance_data = sanity.sanity_check()
        if balance_data:
            sanity.deal_with_easy_trade(balance_data)
        else:
            log.warn('sanity_result is false, skip deal_with_easy_trade')    
            
    except Exception as ex:
        log.exception(ex)
        log.error('my_easy_trade end with exception')        
    

# Task scheduling
# After every 4 mins Sanity Check is called.
schedule.every(4).minutes.do(my_easy_trade)

# Loop so that the scheduling task
# keeps on running all time.
while True:
    # Checks whether a scheduled task
    # is pending to run or not
    sleep_seconds = 30
    log.debug('Scheduler is running, will sleep ' + str(sleep_seconds))
    schedule.run_pending()
    time.sleep(sleep_seconds)