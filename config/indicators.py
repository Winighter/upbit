class Indicator():

    ### Developing ###

    def linreg(_source, _length, _offset):
        linreg = intercept + slope * (_length - 1 - _offset)
        return linreg

    def sqzmom(_high, _low, _close, _length: int = 20):

        # val = Indicator.linreg(close - avg(avg(highest(high, _length), lowest(low, _length)), sma(close, _length)), _length, 0)
        '''
        0이하일때 이전보다 작으면 찐빨, 크면 연한 빨
        0이상일때 이전보다 크면 찐초, 작으면 연한 초
        '''
        
        cnt = 0
        _sma = Indicator.sma(_close, _length, None)

        for i in range(len(_close)):
            
            index = len(_close)-i-_length+2

            if i >= _length - 1:

                cnt += 1
                high_list = []
                low_list = []

                for ii in range(_length):
                    iindex = len(_close) - i - ii + 1

                    low_list.append(_low[iindex])
                    high_list.append(_high[iindex])

                lowest = min(low_list)
                highest = max(high_list)
    
                sma = _sma[index]

                avg_lh = (highest+lowest)/2
                avg_lh = round(avg_lh, 6)

                avg_lhs = (avg_lh + sma)/2
                avg_lhs = round(avg_lhs, 6)

                avg_clhs = format(_close[index] - avg_lhs, 'f')

                print(avg_clhs)

            if i >= len(_close)-_length+2:
                break
            print("")

    ########################

    ### Use ###

    # Simple Moving Average 
    def sma(_src:list, _length:int, _array:int = 0):

        l = _length

        result = []

        if len(_src) < l:
            return
        else:
            for i in range(len(_src)):

                src = _src[i:i+l]

                if len(src) == l:

                    sma = round(sum(src)/_length,6)

                    result.append(sma)
                else:
                    break

        if _array != None:
            result = result[_array]
           
        return result

    # Exponential Moving Average
    def ema(_src:list, _length:int, _array:int = 0, _price_length:int = 0):

        float_len = _price_length

        for i in _src:

            i = str(i)
            splt = i.split(".")
            slen = len(splt[1])
            if float_len <= slen:
                float_len = slen

        alpha = 2 / (_length + 1)

        ema_list = []
        sum_list = []

        for i in range(len(_src)):

            i = len(_src)-i-1

            if i == len(_src)-_length:

                first = []

                for ii in range(len(_src)-i):

                    f = _src[len(_src)-ii-1]
                    first.append(f)
                fEma = sum(first)/_length
                fEma = round(fEma, 7)
                sum_list.append(fEma)
                ema_list.append(fEma)

            if i < len(_src)-_length:

                ema = alpha * _src[i] + (1 - alpha) * sum_list[len(sum_list)-1]
                ema = round(ema, 7)
                sum_list.append(ema)
                ema_list.insert(0, ema)

        result = ema_list

        if _array != None:
            result = ema_list[_array]

        return result

    # Relative Moving Average
    def rma(_src:list, _length:int, _array:int = 0):

        alpha = round(1 / (_length), 6)

        sums = []

        result = []

        for i in range(len(_src)):

            index = len(_src) - i - 1

            if i >= _length - 1:

                srcs = []

                for ii in range(_length):

                    srcs.append(_src[index-ii])

                if i == _length - 1:
                    sum = Indicator.sma(srcs, _length)
                    sum = round(sum, 7)
                    sums.append(sum)
                    result.append(sum)
                else:
                    a = round(alpha * _src[len(_src)-i-_length], 7)
                    b = round((1 - alpha) * sums[i-_length], 7)
                    sum = a + b
                    sum = round(sum, 7)
                    sums.append(sum)
                    result.insert(0, sum)
        
            if index == _length - 1:
                break

        if _array != None:

            result = result[_array]

        return result

    # Relative Strength Index
    def rsi(_src:list, _length:int, _array:int = 0):

        up_list = []
        down_list = []

        for i in range(len(_src)):
            index = len(_src) - i - 1

            u = max(round(_src[index-1] - _src[index], 5), 0)
            up_list.append(u)

            d = max(round(_src[index] - _src[index-1], 5), 0)
            down_list.append(d)

            if i == len(_src) - 2:
                break

        rma_up_list = []
        rma_down_list = []

        for i in range(len(up_list)):

            if i >= _length -1:
                up_sum = []
                down_sum = []

                if i == _length - 1:

                    for ii in range(_length):

                        up_sum.append(up_list[i-ii])
                        down_sum.append(down_list[i-ii])

                    rma_up_list.append(round(sum(up_sum)/_length, 5))
                    rma_down_list.append(round(sum(down_sum)/_length, 5))
                else:
                    rma_up = (up_list[i] + rma_up_list[i-_length] * (_length-1)) / _length
                    rma_up = round(rma_up, 5)
                    rma_up_list.append(rma_up)

                    rma_down = (down_list[i] + rma_down_list[i-_length] * (_length-1)) / _length
                    rma_down = round(rma_down, 5)
                    rma_down_list.append(rma_down)

        rsi_list = []

        for i in range(len(rma_up_list)):
            r = rma_up_list[i]
            s = rma_down_list[i]

            rs = round(r / s, 5)
            res = 100 - 100 / (1 + rs)
            res = round(res, 2)

            rsi_list.insert(0, res)

        if _array != None:
            return rsi_list[_array]
        else:
            return rsi_list

    def macd(_src:list, _array:int = 0):

        _fast_len = 12
        _slow_len = 26
        _signal_len = 9

        macd_list = []
        signal_list = []
        his_list=[]

        fast_ma = Indicator.ema(_src, _fast_len, None)
        slow_ma = Indicator.ema(_src, _slow_len, None)

        min_len = min(len(fast_ma), len(slow_ma))

        for i in range(min_len):

            index = min_len - i - 1

            fama = fast_ma[index]
            slma = slow_ma[index]

            macd = fama - slma
            macd_list.insert(0, macd)

        _macd = Indicator.ema(macd_list, _signal_len, None)

        ms_len = min(len(_macd),len(macd_list))

        for i in range(ms_len):

            index = ms_len - i - 1

            signal = _macd[index]
            macd = macd_list[index]

            signal_list.insert(0, signal)

            hist = macd - signal
            his_list.insert(0, hist)

        result = macd_list, signal_list, his_list

        if _array != None:
            result = macd_list[_array], signal_list[_array], his_list[_array]
        return result

    # Ribbon
    def ribbon(_src:list, _length:int = 60, _array:int = 0):

        ema_src = Indicator.ema(_src, _length, None)

        ribbon_list = []

        for i in range(len(ema_src)):
            
            r = 0

            long = ema_src[i]
            short = ema_src[i+2]

            if long < short:
                r = 1

            ribbon_list.append(r)
            
            if i == len(ema_src) - 3:
                break

        result = ribbon_list

        if _array != None:
            result = ribbon_list[_array]

        return result

    def atr(_high, _low, _close, _length, _array:int = 0):

        tr_list = []

        for i in range(len(_high)):

            index = len(_close) - i - 1

            if i == 0:
                trueRange = _high[index] - _low[index]
            else:
                trueRange = max(max(_high[index] - _low[index], abs(_high[index] - _close[index+1])), abs(_low[index] - _close[index+1]))

            trueRange = round(trueRange, 7)
            tr_list.insert(0, trueRange)

        result = Indicator.rma(tr_list, _length, None)

        if _array != None:
            result = result[_array]
        return result
    
    def atoi(_open, _high, _low , _close):

        ema_length1 = 8
        ema_length2 = 24
        emaDiff_list = []
        _ema1 = Indicator.ema(_close, ema_length1, None)
        _ema2 = Indicator.ema(_close, ema_length2, None)

        ema_length = min(len(_ema1),len(_ema2))

        for i in range(ema_length):

            index = ema_length - i - 1

            ema1 = _ema1[index]
            ema2 = _ema2[index]

            emaDiff = ema1 - ema2

            emaDiff_list.insert(0, emaDiff)

        m, s, h = Indicator.macd(_close, None)

        my_leng = min(len(emaDiff_list),len(_low),len(h))

        for i in range(my_leng):

            if i > 1:

                index = my_leng - i - 1

                long = _open[index+1] > _close[index+1] and _open[index] < _close[index]
                short = _open[index+1] < _close[index+1] and _open[index] > _close[index]

                long = long and emaDiff_list[index+1] < 0 and emaDiff_list[index+2] > emaDiff_list[index+1]
                short = short and emaDiff_list[index+1] > 0 and emaDiff_list[index+2] < emaDiff_list[index+1]

                long = long and h[index+2] > h[index+1]
                short = short and h[index+2] < h[index+1]

    def marubozu(_open, _high, _low, _close, _array:int = 0, _C_Len = 14):

        c_body_list = []

        result = []

        for i in range(len(_open)):

            index = len(_open) - i - 1

            open = _open[index]
            close = _close[index]

            C_BodyHi = max(open, close)
            C_BodyLo = min(open, close)
            C_Body = C_BodyHi - C_BodyLo
            c_body_list.insert(0, C_Body)

        _C_BodyAvg = Indicator.ema(c_body_list, _C_Len, None)

        min_len = min(len(_C_BodyAvg),len(c_body_list))

        for i in range(min_len):

            index = min_len - i -1

            C_BodyHi = max(_open[index], _close[index])
            C_BodyLo = min(_open[index], _close[index])
            C_Body = C_BodyHi - C_BodyLo

            C_LongBody = C_Body > _C_BodyAvg[index]
            C_UpShadow = _high[index] - C_BodyHi
            C_DnShadow = C_BodyLo - _low[index]

            C_WhiteBody = _open[index] < _close[index]
            C_BlackBody = _open[index] > _close[index]

            C_MarubozuShadowPercentWhite = 5.0
            C_MarubozuShadowPercentBearish = 5.0

            C_MarubozuWhiteBullish = C_WhiteBody and C_LongBody and C_UpShadow <= C_MarubozuShadowPercentWhite/100*C_Body and C_DnShadow <= C_MarubozuShadowPercentWhite/100*C_Body and C_WhiteBody
            C_MarubozuBlackBearish = C_BlackBody and C_LongBody and C_UpShadow <= C_MarubozuShadowPercentBearish/100*C_Body and C_DnShadow <= C_MarubozuShadowPercentBearish/100*C_Body and C_BlackBody

            result.insert(0, [C_MarubozuBlackBearish,C_MarubozuWhiteBullish])

        if _array != None:
            result = result[_array]

        return result

    def ut_bot(_high, _low, _close, _array:int = 0):

        _keyValue = 20
        _atrLength = 5

        x_list = [0.]
        xx_list = [0.]

        result = []

        _xAtr = Indicator.atr(_high, _low, _close, _atrLength, None)

        _ema = Indicator.ema(_close, 1, None)

        for i in range(len(_xAtr)):
            index = len(_xAtr) - i - 1
            xAtr = _xAtr[index]
            nLoss = round(_keyValue * xAtr, 7)

            if _close[index] > x_list[i] and _close[index+1] > x_list[i]:
                
                xATRTrailingStop = max(x_list[i], _close[index] - nLoss)

            elif _close[index] < x_list[i] and _close[index+1] < x_list[i]:

                xATRTrailingStop = min(x_list[i], _close[index] + nLoss)

            elif _close[index] > x_list[i]:

                xATRTrailingStop = _close[index] - nLoss
            else:
                xATRTrailingStop = _close[index] + nLoss

            xATRTrailingStop = round(xATRTrailingStop, 7)

            x_list.append(xATRTrailingStop)
            xx_list.insert(0, xATRTrailingStop)
        
        my_len = min(len(xx_list),len(_close),len(_ema))

        for i in range(my_len):

            index = my_len - i - 1

            if i > 0:

                above = xx_list[index+1] >= _ema[index+1] and xx_list[index] < _ema[index]
                below = xx_list[index+1] <= _ema[index+1] and xx_list[index] > _ema[index]

                buy  = _close[index] > xx_list[index] and above 
                sell = _close[index] < xx_list[index] and below

                result.append([buy, sell])

        if _array != None:
            result = result[_array]
        return result


