import math

class Indicator():

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

                    sma = round(sum(src)/_length,4)

                    result.append(sma)
                else:
                    break

        if _array != None:
            result = result[_array]
           
        return result

    # Exponential Moving Average
    def ema(_src:list, _length:int, _array:int = 0):

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
        

    

