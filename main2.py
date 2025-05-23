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

        self.min_time = 5
        self.symbol = 'KRW-PEPE'
        self.INDICATOR = 2

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

    def get_balance(self):

        position = 50 # 10 ~ 20 전체자산 기준 투자할 금액 비율 (%)
        SL = 5 # [0.25-1] [0.5-1.5] 투자금액 기준 손절할 금액 비율 (%)
        TP = 10
        self.TP = TP
        balance = self.exchange.fetch_balance()

        symbol_list = []

        for i in balance["info"]:

            locked = float(i["locked"])
            balance = float(i["balance"])
            symbol = f"{i["unit_currency"]}-{i["currency"]}"
            avg_buy_price = i['avg_buy_price']

            if symbol == "KRW-KRW":
                balance = math.trunc(balance)
                self.deposit = math.trunc(balance*(position/100))
                # self.SL = math.trunc(self.deposit*(SL/100))*-1 # 보유자산 기준
                self.SL = SL # 매수한 금액 기준
            else:
                symbol_list.append(symbol)
                locked = float(format(locked,'.8f'))
                balance = float(format(balance,'.8f'))
                avg_buy_price = float(avg_buy_price)

                self.balance_dict.update({symbol:{"balance":balance,"locked":locked,"avg_buy_price":avg_buy_price}})

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
                self.buy_order_list.append(_symbol)
                self.exchange.create_market_buy_order_with_cost(_symbol, _amount)

            if _side == "SELL":
                self.sell_order_list.append(_symbol)
                self.exchange.create_market_sell_order(_symbol, _amount)

    def min_candle_chart(self):

        _close = []
        _high = []
        _low = []
        _open = []

        url = f"https://api.upbit.com/v1/candles/minutes/{self.min_time}" # 1, 3, 5, 10, 15, 30, 60, 240
        querystring = {"market": self.symbol,"count": "200", "to": ""}

        for i in range(6):

            data = requests.request("GET", url, params=querystring).json()

            for ii in data:

                open = float(ii['opening_price'])
                high = float(ii['high_price'])
                low = float(ii['low_price'])
                close = float(ii['trade_price'])
                last_time = str((ii['candle_date_time_kst']))
                
                _open.append(open)
                _high.append(high)
                _low.append(low)
                _close.append(close)

            querystring = {"market": self.symbol,"count": "200", "to": f"{last_time}+09:00"}

        ### INDICATOR DATA ###
        if self.INDICATOR == 1:
            _ema1 = Indicator.ema(_close, 8, None, 7)
            _ema2 = Indicator.ema(_close, 24, None, 7)

            _ema_short = Indicator.ema(_close, 50, None, 7)
            _ema_long = Indicator.ema(_close, 200, None, 7)

            emaDiff1 = _ema1[1] - _ema2[1]
            emaDiff2 = _ema1[2] - _ema2[2]

            long = _ema_long[1] < _ema_short[1] and emaDiff1 > emaDiff2 and emaDiff1 > 0 and emaDiff2 < 0 and _open[1] < _close[1]
            long_end = _low[0] < _ema_long[0] and _ema_short[0] > _ema_long[0] and _open[0] > _close[0]

        elif self.INDICATOR == 2:

            buy, sell = Indicator.ut_bot(_high, _low, _close, 1)

            long = buy != sell and buy == True
            long_end = buy != sell and sell == True

        # BUY
        if self.symbol not in self.balance_dict.keys() and long:

            Message(f'[{self.symbol}] Entry Position')
            self.order("BUY", self.symbol, self.deposit)

        # SELL
        if self.symbol in self.balance_dict.keys():
            
            balance = self.balance_dict[self.symbol]['balance']
            buy_price = self.balance_dict[self.symbol]['avg_buy_price']

            profit = round(((_close[0]-buy_price)/buy_price)*100,2)

            if self.INDICATOR == 2 and profit <= self.SL:

                Message(f"[{self.symbol}] SL & Close Position ${profit}")

                self.order("SELL", self.symbol, balance)

            if long_end:

                Message(f"[{self.symbol}] TP & Close Position ${profit}")

                self.order("SELL", self.symbol, balance)

            if self.INDICATOR == 1 and profit >= self.TP:

                Message(f"[{self.symbol}] TP & Close Position ${profit}")

                self.order("SELL", self.symbol, balance)

        threading.Timer(3, self.min_candle_chart).start()

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
