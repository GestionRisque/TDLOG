__author__ = 'sihanyou'

import GlobalValue
import arch
import statsmodels.api as sm
import random
import numpy as np
import math
from scipy import stats as st
from scipy.optimize import minimize
import warnings
import plot

warnings.filterwarnings("ignore")


def main(processPercentSignal, currentPercent):
    GlobalValue.init()
    GlobalValue.modelParams = []
    n = len(GlobalValue.yahooData)
    stepPercent = (90 - currentPercent) // n
    for actif in GlobalValue.yahooData:
        arma = ARMA(actif)
        garch = GARCH(actif)
        currentPercent += stepPercent / 2
        processPercentSignal.emit(currentPercent)
        sv = SV(actif)
        currentPercent += stepPercent / 2
        processPercentSignal.emit(currentPercent)
        GlobalValue.modelParams.append({'arma': arma, 'garch': garch, 'sv': sv})


# From here are the functions to calculate different models

##  From here the function is used for all models

def returns(share):
    r = []
    n = len(share)
    for i in range(1, n - 1):
        r.append(math.log(share[i] / share[i - 1]))
    return r


##  From here the functions are used for SV models

def vctPower(v, p):
    res = []
    for i in range(0, len(v) - 1):
        if v[i] != 0:
            res.append(math.log(v[i] ** p))
    return res


def pseudoData(theta, u, e):
    a = theta[0]
    b = theta[1]
    s = theta[2]

    h = []
    y = []
    h.append(e[0] * s ** 2 / (1 - b ** 2) + a / (1 - b))
    y.append(math.exp(h[0] / 2) * u[0])
    for i in range(1, len(e) - 1):
        h.append(a + b * h[i - 1] + e[i])
        y.append(math.exp(h[i] / 2) * u[i])
    return y


def distance(mu, nu):
    return (mu[0] - nu[0]) ** 2 + (mu[1] - nu[1]) ** 2 + (mu[2] - nu[2]) ** 2


def mu(r):
    ts = vctPower(r, 2)

    x = ts[0:-1]

    y = ts[1:]

    mod = st.linregress(x, y)

    nu = []
    nu.append(mod[0])
    nu.append(mod[1])
    nu.append(mod[4])

    return nu


def target(theta):
    p = pseudoData(theta, u, e)

    mus = mu(p)

    return distance(mus, nus)


def SV_opt(share, i):
    r = returns(share)

    length = len(r)

    random.seed(i)

    global u

    u = np.random.normal(0, 1, 20 * length)

    global e

    e = np.random.normal(0, 1, 20 * length)

    global nus

    nus = mu(r)

    bnds = ((-10, 0.999), (-1, 0.999), (0.001, 10))

    params = minimize(target, (-5, 0.3, 0.5), bounds=bnds, method='SLSQP')

    return params.x


# From here we calibrate the models


def SV(share):
    params = []
    for i in range(1, 20):
        params.append(SV_opt(share, i))

    return np.mean(params, axis=0).tolist()


def ARMA(share):
    r = returns(share)
    arma_mod30 = sm.tsa.ARMA(r, (3, 0))
    res = arma_mod30.fit()
    sigma = res.sigma2.tolist()
    params = res.params.tolist()
    params.append(sigma)
    return params


def GARCH(share):
    r = returns(share)
    am = arch.arch_model(r)
    res = am.fit(update_freq=5)
    var = res.conditional_volatility[len(r) - 251]
    print(res.summary())

    params = res.params.tolist()
    params.append(var)
    return params


if __name__ == '__main__':
    main()
