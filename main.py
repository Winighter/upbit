import ccxt, math, requests, threading
from config import *


class Upbit:

    def __init__(self, access:str, secret:str):

        # EXCHAGE CCXT
        self.exchange = ccxt.upbit(config={
        'apiKey': access,
        'secret': secret,
        'enableRateLimit': True
        })

        ### SETTINGS ###

        # DICTIONALY
        self.balance_dict = {}

        # LIST
        self.buy_order_list = []
        self.sell_order_list = []

        # CUSTOMIZE
        self.ORDER_LOCK = False

        self.min_time = 10
        self.symbol = 'KRW-BONK'

        # RUN
        print("Start Upbit...")
        
        self.get_symbol()
        self.get_balance()
        if self.symbol == "":
            self.get_low_symbol()
        self.min_candle_chart()
        ws_all = WebSocketAll(access, secret, self.symbol)
        while True:
            data = ws_all.get()
            self.on_ws_private_data(data)
        ws_all.terminate()

    def get_hoka(self, _symbol):

        url = "https://api.upbit.com/v1/orderbook"
        querystring = {"markets":_symbol,"level":"0"}
        response = requests.request("GET", url, params=querystring)
        data = response.json()

        for i in data:
            for h in i["orderbook_units"]:
                bid_price = float(h["bid_price"])
                break

        return bid_price

    def get_balance(self):

        position = 90 # 10 ~ 20 전체자산 기준 투자할 금액 비율 (%)
        risk = 5 # [0.25-1] [0.5-1.5] 투자금액 기준 손절할 금액 비율 (%)

        balance = self.exchange.fetch_balance()

        symbol_list = []

        for i in balance["info"]:

            locked = float(i["locked"])
            balance = float(i["balance"])
            symbol = f"{i["unit_currency"]}-{i["currency"]}"

            if symbol == "KRW-KRW":
                balance = math.trunc(balance)
                self.deposit = math.trunc(balance*(position/100))
                self.risk = math.trunc(balance*(risk/100))*-1
            else:
                symbol_list.append(symbol)
                locked = float(format(locked,'.8f'))
                balance = float(format(balance,'.8f'))

                self.balance_dict.update({symbol:{"balance":balance,"locked":locked}})

    def get_symbol(self):

        url = "https://api.upbit.com/v1/market/all"
        querystring = {'is_details':'False'}
        headers = {"Accept":"application/json"}
        response = requests.request("GET",url,headers=headers,params=querystring)
        response = response.text
        result = json.loads(response)

        self.symbols = []

        for i in range(len(result)):

            data = result[i]
            symbol = str(data['market'])

            if symbol.startswith('KRW') == True:
                self.symbols.append(symbol)

    def get_low_symbol(self):

        min_price = 1
        max_price = 500

        if self.balance_dict == {}:

            url = "https://api.upbit.com/v1/ticker"
            symbols = str(self.symbols).replace("',", ",").replace("'KRW","KRW").replace("[KRW","KRW").replace("']","")
            querystring = {'markets':f'{symbols}'}
            headers = {"Accept":"application/json"}
            response = requests.request("GET",url,headers=headers,params=querystring)
            response = json.loads(response.text)
            rate = 0.0

            last_symbol = ''
            for i in range(len(response)):

                data = response[i]
                symbol = data['market']
                close = data['trade_price']
                change_rate = data['signed_change_rate']*100 # 등락율 (UTC 0시 기준)
                change_rate = round(change_rate, 2)

                if change_rate < rate and min_price <= close and close <= max_price:
                    rate = change_rate
                    last_symbol = symbol

            self.symbol = last_symbol
        else:
            self.symbol = list(self.balance_dict.keys())
            self.symbol = self.symbol[0]

        threading.Timer(1,self.get_low_symbol).start()

    def order(self, _side:str, _symbol:str, _amount:float):

        if self.ORDER_LOCK == False:

            if _side == "BUY":
                self.exchange.create_market_buy_order_with_cost(_symbol, _amount)
                self.buy_order_list.append(_symbol)

            else:
                self.exchange.create_market_sell_order(_symbol, _amount)
                self.sell_order_list.append(_symbol)

    def min_candle_chart(self):

        _close = []
        # _high = []
        # _low = []

        url = f"https://api.upbit.com/v1/candles/minutes/{self.min_time}"
        querystring = {"market": self.symbol,"count": "200", "to": ""}

        for i in range(6):

            data = requests.request("GET", url, params=querystring).json()

            for ii in data:

                # high = float(ii['high_price'])
                # low = float(ii['low_price'])
                close = float(ii['trade_price'])
                last_time = str((ii['candle_date_time_kst']))

                # _high.append(high)
                # _low.append(low)
                _close.append(close)

            querystring = {"market": self.symbol,"count": "200", "to": f"{last_time}+09:00"}

        ### INDICATOR DATA ###
        nwe_condition = Indicator.nwe(_close)

        ### Add Condition ###

        # BUY
        if nwe_condition == 'LONG' and self.symbol not in self.balance_dict.keys():

            Message(f'[UPBIT] Entry Position')
            self.order("BUY", self.symbol, self.deposit)

        # SELL
        if nwe_condition == 'SHORT' and self.symbol in self.balance_dict.keys():

            Message(f"[UPBIT] Close Position")
            balance = self.balance_dict[self.symbol]['balance']
            self.order("SELL", self.symbol, balance)

        threading.Timer(1, self.min_candle_chart).start()

    def on_ws_private_data(self, data):

        if data["type"] == "myOrder":

            state = data["state"]
            symbol = data['code'] # KRW-BTC
            ask_bid = data['ask_bid']
            remaining_volume = data['remaining_volume']

            if state == "trade": # 체결 발생

                if (remaining_volume == None) or (remaining_volume == 0):

                    if ask_bid == 'BID' and symbol in self.buy_order_list:
                        self.buy_order_list.remove(symbol)

                    if ask_bid == 'ASK' and symbol in self.sell_order_list:
                        self.sell_order_list.remove(symbol)

        else:
            for s in data["assets"]:
                currency = s["currency"] # 종목 ex) KRW, XRP
                
                if currency != "KRW":
                    symbol = f"KRW-{currency}" # KRW-???
                    locked = float(s["locked"]) # 미체결
                    locked = float(format(locked, '.8f'))
                    balance = float(s["balance"]) # 주문가능
                    balance = float(format(balance, '.8f'))

                    if balance > 0:
                        self.get_balance()

                    if symbol in self.balance_dict.keys():
                        if balance == 0 and locked == 0:
                            self.balance_dict.pop(symbol)
                else:
                    self.get_balance()

if __name__ == "__main__":

    with open("./upbit.key") as f:
        lines = f.readlines()
        access = lines[0].strip()
        secret = lines[1].strip()
        upbit = Upbit(access, secret)
