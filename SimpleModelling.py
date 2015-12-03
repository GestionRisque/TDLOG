__author__ = 'sihanyou'

import GlobalValue
import arch
import math
import statsmodels.api as sm

def main():
    GlobalValue.init()
    GlobalValue.modelParams = []
    for actif in GlobalValue.yahooData:
        print(actif)
        arma = ARMA(actif)
        garch = GARCH(actif)
        GlobalValue.modelParams.append({'arma':arma,'garch':garch})
        #print(priceMvt)


def returns(share):

    r = []
    n = len(share)
    for i in range(1,n-1):
        r.append(math.log(share[i]/share[i-1]))
    return r


def ARMA(share):

    r = returns(share)
    arma_mod30 = sm.tsa.ARMA(r, (3,0))
    res = arma_mod30.fit()
    return res.params


def GARCH(share):

    r = returns(share)
    am = arch.arch_model(r)
    res = am.fit(update_freq=5)
    print(res.summary())

    return res.params


def SV(share):

    r = returns(share)

    return

if __name__ == '__main__':
    main()