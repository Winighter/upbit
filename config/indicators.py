import math

class Indicator():

    ### Don't Use ###

    # Pivot Points High Low
    def pivots_hl(_high, _low, _close, _leftBars: int = 20, _rightBars: int = 20):
        '''
        [tradingview] Pivot Points High Low ~ Om Borda by omborda2002

        tradingview default value : _leftBars = 10, _rightBars = 10

        !!! Warning !!!
        leftBars 값은 상관없지만 RightBars의 경우 값이 증가할수록
        매매 타이밍이 매우 느려지므로 매매에 사용하기엔 부적합하다.
        그래서 0으로 설정하자니 오류 신호만 증가하기 때문에
        어디까지나 참고용
        '''
        pivot_list = []

        for i in range(len(_high)):

            index = len(_high) - i - 1

            if i >= _leftBars:

                low_list = []
                high_list = []
                center_low = 0.0
                center_high = 0.0
                
                for ii in range(_leftBars + _rightBars + 1):

                    iindex = index+ii-_leftBars

                    if ii == _rightBars:
                        center_low = _low[iindex]
                        center_high = _high[iindex]

                    low_list.append(_low[iindex])
                    high_list.append(_high[iindex])

                minlow = min(low_list)
                maxhigh = max(high_list)

                if maxhigh == center_high:
                    pivot_list.insert(0, [maxhigh, 0])

                elif minlow == center_low:
                    pivot_list.insert(0, [0, minlow])

                else:
                    pivot_list.insert(0, [0, 0])

                if index == _leftBars:
                    break

        for i in range(len(_high)):

            index = len(_high) - i - 1

            if i > _leftBars:
                iindex = index+_leftBars

                if index <= len(pivot_list) - 1:

                    sp = sum(pivot_list[index])

                    if sp != 0:
                        # SHort Signal
                        if (_high[iindex] >= _high[iindex + 1]) and (_high[iindex] >= _high[iindex - 1]) and (_low[iindex] >= _close[iindex - 1]):
                            print("[High]",iindex,_high[iindex],_low[iindex],_close[iindex],pivot_list[index])

                        # LongSignal
                        if (_low[iindex] < _low[iindex + 1]) and (_low[iindex] <= _low[iindex - 1]) and (_high[iindex] <= _close[iindex - 1]):
                            print("[Low]",iindex,_high[iindex],_low[iindex],_close[iindex],pivot_list[index])

    # Market Structure with Inducements & Sweeps [LuxAlgo]
    def swing_hl(_high, _low, _len):
        # Pivot 과 같은 원리
        os = 0
        cnt = 0
        os_list = []
        upper_list = []
        lower_list = []

        for i in range(len(_high)):

            if i >= _len -1:

                min_list = []
                max_list = []
                for ii in range(_len):

                    iindex = i - ii
                    min_list.append(_low[iindex])
                    max_list.append(_high[iindex])

                lowest = min(min_list)
                highest = max(max_list)
                lower_list.append(lowest)
                upper_list.append(highest)

        for i in range(len(upper_list)):
            cnt += 1

            index = len(upper_list) - i - 1

            upper = upper_list[index]
            lower = lower_list[index]

            if i >= 1:

                highl = _high[index+_len]
                lowl = _low[index+_len]

                if highl > upper:
                    os = 0

                elif lowl < lower:
                    os = 1

                elif os_list != []:
                    os = os_list[0]

                else:
                    pass

                os_list.insert(0, os)

            if os == 0 and len(os_list) > 1:
                if os_list[1] != 0:
                    top = highl
            else:
                top = None

            if os == 1 and len(os_list) > 1:
                if os_list[1] != 1:
                    btm = lowl
            else:
                btm = None

        return top, btm

    # Nadaraya-Watson Envelope [LuxAlgo]
    def nwe(_src, _mult:int = 3):

        y2 = 0.
        nwe_list = []

        length = min(499, len(_src))

        sae = 0.

        for i in range(length):

            sum = 0.
            sumw = 0.

            for j in range(length):

                w = Indicator.gauss(i -j)
                sum += _src[j] * w
                sumw += w
            
            y2 = sum / sumw
            sae += abs(_src[i] - y2)
            nwe_list.append(y2)

        sae = sae / length * _mult

        result = None

        for i in range(length):

            if _src[i] > nwe_list[i] + sae and _src[i+1] < nwe_list[i] + sae:
                # print(i, "SHORT", _src[i], _src[i+1])
                if i == 1:
                    result = "SHORT"

            if _src[i] < nwe_list[i] - sae and _src[i+1] > nwe_list[i] - sae:
                # print(i, "LONG", _src[i], _src[i+1])
                if i == 1:
                    result = "LONG"

            if i == length - 2:
                break

        return result

    # Nadaraya-Watson Envelope [LuxAlgo] Config
    def gauss(_x, _h:int = 8):

        f = math.exp(-(pow(_x, 2)/(_h * _h * 2)))
        f = round(f, 6)
        return f

    #########################

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
                fEma = round(fEma, float_len)
                sum_list.append(fEma)
                ema_list.append(fEma)

            if i < len(_src)-_length:

                ema = alpha * _src[i] + (1 - alpha) * sum_list[len(sum_list)-1]
                ema = round(ema, float_len)
                sum_list.append(ema)
                ema_list.insert(0, ema)

        result = ema_list

        if _array != None:
            result = ema_list[_array]

        return result

    # Relative Moving Average
    def rma(_src:list, _length:int, _array:int = 0):

        alpha = round(1 / (_length), 4)

        if len(_src) == 2:
            rma = alpha * _src[0] + (1 - alpha) * _src[1]
            rma = round(rma, 4)
            return rma
        else:
            first_rma = []
            rma_list = []

            for i in range(len(_src) + 1):

                if i == _length-1:

                    for ii in range(i+1):
                        ii = (len(_src)-1 - ii)
                        first_rma.append(_src[ii])

                    first = round(sum(first_rma)/(i+1),4)
                    rma_list.append(first)

                if i > _length-1 and i < len(_src):
                    index = i - _length
                    rma = (alpha * _src[len(_src)-i -1]) + ((1 - alpha) * (rma_list[index]))
                    rma = round(rma, 4)
                    rma_list.append(rma)

            result = rma_list

            if _array != None:
                result = rma_list[_array-1]
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
    
    # Candle
    def min_max(_src:list, _array:int = 0):

        min = 0.0
        max = 0.0
        min_list = []
        max_list = []

        for i in range(90):

            index = 89 - i

            close = _src[index]

            if i == 0:
                min = close
                max = close
                min_list.insert(0, min)
                max_list.insert(0, max)
                print(max)
            else:
                if close < min:
                    min = close

                if close > max:
                    max = close

                min_list.insert(0, min)
                max_list.insert(0, max)
        # print(max_list)
        if _array != None:
            return min_list[_array], max_list[_array]
        else:
            return min_list, max_list
        
    def asgma(_src:list):

        smooth_length = 72

        change_list = []
        pchange_list = []
        norm_list = []

        for i in range(len(_src)):

            index = len(_src)-i-1

            if i == 0:
                pass
            else:
                c = round(_src[index]-_src[index+1],4)
                change_list.append(c)
                
        for i in range(len(change_list)):

            if i >= smooth_length - 1:

                index = len(_src)-i-2

                sum_list = []

                for ii in range(smooth_length):
                    sum_list.append(change_list[i-ii])

                p = sum(sum_list)
                p = round(p, 4)
                pchange = p / _src[index] * 100
                pchange = round(pchange, 4)
                pchange_list.append(pchange)


        weight, length1 = Indicator.alma(pchange_list)

        test = 0.0
        test_list = []
        sum_test = []
        rr = []
        avpchange_list = []
        for i in range(len(pchange_list)):
            a = round(pchange_list[i]*weight, 3)
            test = test + a
            test = round(test, 2)

            test_list.append(a)
            sum_test.append(test)

            if i > 0:
                b = round(sum_test[i]-sum_test[i-1], 2)
                rr.append(b)

        for i in range(15):
            '''
            가장첫봉 = 현재 종가*length
            이전 norm + 전일종가차이*length
            '''
            pass
            # print(weight)

        for i in range(len(rr)):
            avpchange = round(rr[i]/weight, 2)
            avpchange_list.append(avpchange)
        high_avpchange = max(avpchange_list)
        low_avpchange = min(avpchange_list)
        sigma_list = Indicator.stdev(_src)
        last_weight = 0.0
        for i in range(14):
            a = 2 * sigma_list[i]
            weight = (math.exp(-math.pow(((i - (13)) / a), 2) / 2))

            last_weight = weight

        value = high_avpchange + low_avpchange
        max_min_list = []



        print((avpchange_list))

    def alma(_series, _length:int = 2, _offset:float = 0.85, _sigma:float = 7):

        m = round(_offset * (_length - 1), 4)
        s = round(_length / _sigma, 4)

        last_weight = 0.0

        for i in range(_length):
            a = round(math.pow(i - m, 2), 4)
            b = round(math.pow(s, 2), 4)
            weight = round(math.exp((-1 * a) / (2 * b)),4)
            last_weight = weight

        return last_weight, _length

    def stdev(_src):
        _length = 5

        sigma_list = []

        for i in range(len(_src)):

            if i >= _length - 1:
                s_list = []
                for ii in range(_length):

                    index = i - ii
                    index = len(_src) - index - 1
                    s_list.append(_src[index])

                sigma = numpy.std(s_list)
                sigma = round(float(sigma), 4)
                sigma_list.append(sigma)
        return sigma_list

    def test(_src):
        pass


    def test(_src):
        pass

