__author__ = 'sihanyou'

import GlobalValue
import arch
import math
import statsmodels.api as sm

def main():
    for actif in GlobalValue.yahooData:
        priceMvt = decode(actif)
        ARMA(priceMvt)
        #print(priceMvt)



def decode(ac):

    prices = []
    for item in ac:
        prices.append(float(item['Adj_Close']))
    return prices

def ARMA(share):

    r = []
    n = len(share)
    for i in range(1,n-1):
        r.append(math.log(share[i]/share[i-1]))

    arma_mod30 = sm.tsa.ARMA(r, (3,0)).fit()
    print(arma_mod30.params)



    return

def GARCH(share):

    return

def ARCH(share):

    return

def SV(share):

    return

if __name__ == '__main__':
    main()