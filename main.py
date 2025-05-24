import ccxt, math, requests, threading
from config import *


class Upbit:

    def __init__(self, _access:str, _secret:str, _symbols:list=[], _minutes:int = 5):

        # EXCHAGE CCXT
        self.exchange = ccxt.upbit(config={
        'apiKey': _access,
        'secret': _secret,
        'enableRateLimit': True
        })

        ### SETTINGS ###

        # DICTIONALY
        self.balance_dict = {}

        # LIST
        self.buy_order_list = []
        self.sell_order_list = []

        # RUN
        print("Start Upbit...")

        self.get_balance()

        symbols = self.inquiry_symbol()
        if _symbols == []:
            _symbol = self.create_symbol_portfolio(symbols)
        else:
            _symbol = _symbols[0]

        self.min_candle_chart(_symbol, _minutes)

        ws_all = WebSocketAll(_access, _secret, symbols)
        while True:
            data = ws_all.get()
            self.on_ws_private_data(data)
        ws_all.terminate()

    ### BALANCE ###
    def get_balance(self):

        position = 90 # 10 ~ 20 예수금 기준 투자할 금액 비율 (%)
        self.SL = 4.5 # [0.25-1] [0.5-1.5] 투자금액 기준 손절할 금액 비율 (%)
        self.TP = 10 # [0.25-1] [0.5-1.5] 투자금액 기준 익절할 금액 비율 (%)
        balance = self.exchange.fetch_balance()

        for i in balance["info"]:

            locked = float(i["locked"])
            balance = float(i["balance"])
            avg_buy_price = float(i['avg_buy_price'])
            symbol = f"{i["unit_currency"]}-{i["currency"]}"

            if symbol == "KRW-KRW":
                balance = math.trunc(balance)
                self.deposit = math.trunc(balance*(position/100))
            else:
                locked = float(format(locked,'.8f'))
                balance = float(format(balance,'.8f'))
                self.balance_dict.update({symbol:{"balance":balance,"locked":locked,"avg_buy_price":avg_buy_price}})

    ### SYMBOLS ###
    def inquiry_symbol(self, _market:str = 'KRW'):
        '''
        _market = KRW or BTC or USDT
        '''
        _symbols = []
        url = "https://api.upbit.com/v1/market/all"
        params = {'is_details':'False'}
        headers = {"Accept":"application/json"}
        response = requests.request("GET", url, headers = headers, params = params)
        response = response.text
        result = json.loads(response)

        for i in range(len(result)):
            symbol = str(result[i]['market'])
            if symbol not in _symbols and symbol.startswith(_market):
                _symbols.append(symbol)

        return _symbols

    def create_symbol_portfolio(self, _tickers:list[str], _minPrice:float = 0, _maxPrice:float = 1):

        rate = 0.0
        url = "https://api.upbit.com/v1/ticker"
        symbols = str(_tickers).replace("',", ",").replace("'KRW","KRW").replace("[KRW","KRW").replace("']","")
        querystring = {'markets':f'{symbols}'}
        headers = {"Accept":"application/json"}
        response = requests.request("GET",url,headers=headers,params=querystring)
        response = json.loads(response.text)

        for i in range(len(response)):

            data = response[i]
            symbol = data['market']
            close = data['trade_price']
            acc_trade_price_24h = data['acc_trade_price_24h']
            
            if rate < acc_trade_price_24h and _minPrice < close and close < _maxPrice:

                last_symbol = symbol

        return last_symbol

    ### ORDER ###
    def order_symbol(self, _side:str, _symbol:str, _amount:float, _ORDER_LOCK=False):

        if _ORDER_LOCK == False:

            if _side == "SELL":
                self.sell_order_list.append(_symbol)
                self.exchange.create_market_sell_order(_symbol, _amount)

            if _side == "BUY":
                self.buy_order_list.append(_symbol)
                self.exchange.create_market_buy_order_with_cost(_symbol, _amount)

    ### CHART ###
    def min_candle_chart(self, _symbol, _minutes):

        _open = []
        _low = []
        _high = []
        _close = []

        url = f"https://api.upbit.com/v1/candles/minutes/{_minutes}" # 1, 3, 5, 10, 15, 30, 60, 240
        querystring = {"market": _symbol,"count": "200", "to": ""}

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

            querystring = {"market": _symbol,"count": "200", "to": f"{last_time}+09:00"}

        ### INDICATOR ###
        _utbot = Indicators.ut_bot(_high, _low, _close, 1)

        ### CONDITION ###
        long = _utbot[0]
        exit_long = _utbot[1]
        short = False
        exit_short = False

        # BUY
        if _symbol not in self.balance_dict.keys() and long:

            Message(f'[{_symbol}] Entry Position')
            self.order_symbol("BUY", _symbol, self.deposit)

        # SELL
        if _symbol in self.balance_dict.keys():
            
            balance = self.balance_dict[_symbol]['balance']
            buy_price = self.balance_dict[_symbol]['avg_buy_price']
            profit = round(((_close[0] - buy_price) / buy_price) * 100, 2)

            if profit <= self.SL:
                Message(f"[{_symbol}] SL & Close Position ${profit}")
                self.order_symbol("SELL", _symbol, balance)

            elif exit_long:
                Message(f"[{_symbol}] TP & Close Position ${profit}")
                self.order_symbol("SELL", _symbol, balance)

        threading.Timer(1, self.min_candle_chart, args=[_symbol,_minutes]).start()

    ### WebSocket ###
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
                            # if _symbols == []:
                            # self.inquiry_symbol()
                else:
                    self.get_balance()

if __name__ == "__main__":

    with open("./upbit.key") as f:
        l = f.readlines()
        access = l[0].strip()
        secret = l[1].strip()
        Upbit(access, secret, ['KRW-BONK'])
