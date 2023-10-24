import http.client
import json
from datetime import datetime, timedelta

conn = http.client.HTTPConnection('192.168.10.200:8080')

headers = {'Content-type': 'application/json'}

body = ''  # '{"trendModeName": "Zhang2GeDian", "nDays": "1", "repeatTimes": "2"}
json_data = json.dumps(body)

stockId = '300059'
days_before_120 = (datetime.today() - timedelta(days=120)).strftime('%Y-%m-%d')  # use 120 days data for prediction
today = datetime.today().strftime('%Y-%m-%d')
dayParm = days_before_120 + '_' + today

# Buy
conn.request('POST', '/portal/indv3/predictTodayBuy/' + stockId + '/' + dayParm, None, headers)

response = conn.getresponse()
respJson = json.loads(response.read().decode())
print(respJson)

if 'B' in respJson['sellFlagsTitle']:
    print(stockId + ' Buy@'+str(respJson['hc6']))


# Sell
conn.request('POST', '/portal/indv3/predictTodaySell/' + stockId + '/' + dayParm, None, headers)

response = conn.getresponse()
respJson = json.loads(response.read().decode())
print(respJson)

if 'S' in respJson['sellFlagsTitle']:
    print(stockId + ' Sell@'+str(respJson['hc5']))
