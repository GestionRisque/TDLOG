__author__ = 'dhy'

import matplotlib.pyplot as plt
import numpy
import math
import pickle
import SimpleModelling


########   Plot_ARMA take the parameters of ARMA model ...
# and calculate the fitted value then compare with historical data######
def Plot_ARMA(Params, Share):
    Share = SimpleModelling.returns(Share)
    N = len(Share)
    share = [Params[0]] * N
    n = 4
    returns_global = []
    for j in range(1000):
        share = [Params[0]] * N
        for i in range(n - 1):
            share[i] = Share[i]
        for i in range(n - 1, N):
            share[i] = Params[1] * share[i - 1] + Params[2] * share[i - 2] + Params[3] * share[
                i - 3] + numpy.random.normal(0, Params[4])

        returns_global.append(sum(share))
    print(returns_global)
    real_global_returns = sum(Share)
    plt.figure(1)
    plt.boxplot([returns_global])
    plt.plot([real_global_returns] * len(Share))
    plt.title("boxplot_ARMA")
    plt.ylabel("returns")
    plt.show()


def Plot_GARCH(param, Share):
    returns = SimpleModelling.returns(Share)
    N = len(returns)
    global_returns = []
    for j in range(1000):

        sigma = [param[4]]
        epsilon = [param[4], numpy.random.normal(0, 1)]
        simu_r = [param[0] + epsilon[0]]
        for i in range(1, N):
            sigma.append(param[1] + param[2] * (epsilon[i - 1]) ** 2 + param[3] * (sigma[i - 1]) ** 2)
            epsilon.append(sigma[i] * numpy.random.normal(0, 1))
            simu_r.append(param[0] + epsilon[i])

        global_returns.append(sum(simu_r))
    pickle.dump(global_returns, open("global_returns.dat", "wb"))
    real_returns = sum(returns)
    plt.figure(1)
    plt.boxplot([global_returns])
    plt.plot([real_returns] * len(Share))
    plt.title("boxplot_GARCH")
    plt.ylabel("returns")
    plt.show()


def Plot_SV(param, returns):
    global_returns = []
    N = len(returns)
    for j in range(1000):
        h = [numpy.random.normal(param[0] / (1 - param[1]), param[2] ** (2) / (1 - param[1] ** (2)))]
        simu_returns = [math.exp(h[0]) / 2 * numpy.random.normal(0, 1)]

        for i in range(1, N):
            h.append(param[0] + param[1] * h[i - 1] + param[2] * numpy.random.normal(0, 1))
            simu_returns.append(math.exp(h[i]) / 2 * numpy.random.normal(0, 1))
        global_returns.append(sum(simu_returns))

    real_returns = sum(returns)

    plt.figure(3)
    plt.boxplot(global_returns)
    plt.plot([real_returns] * 500)
    plt.title("boxplot_SV")
    plt.ylabel("returns")
    plt.show()


def chose_SV(param):
    global_returns = []

    for j in range(1000):
        h = [numpy.random.normal(param[0] / (1 - param[1]), param[2] ** (2) / (1 - param[1] ** (2)))]
        simu_returns = [math.exp(h[0]) / 2 * numpy.random.normal(0, 1)]

        for i in range(1, 250):
            h.append(param[0] + param[1] * h[i - 1] + param[2] * numpy.random.normal(0, 1))
            simu_returns.append(math.exp(h[i]) / 2 * numpy.random.normal(0, 1))
        global_returns.append(sum(simu_returns))

    return global_returns


def chose_GARCH(param):
    global_returns = []
    for j in range(1000):
        sigma = [param[4]]
        epsilon = [param[4 * numpy.random.normal(0, 1)]]
        simu_r = [param[0] + epsilon[0]]
        for i in range(1, 250):
            sigma.append(param[1] + param[2] * (epsilon[i - 1]) ** (2) + param[3] * (sigma[i - 1]) ** (2))
            epsilon.append(sigma[i] * numpy.random.normal(0, 1))
            simu_r.append(param[0] + epsilon[i])

        global_returns.append(sum(simu_r))

    return global_returns


def chose_ARMA(Params, returns):  ##### 3 lastest days' returns
    returns_global = []
    n = 3
    simu_returns = returns
    for j in range(1000):
        for i in range(n, 250 + n):
            simu_returns.append(
                    Params[1] * simu_returns[i - 1] + Params[2] * simu_returns[i - 2] + Params[3] * simu_returns[
                        i - 3] + numpy.random.normal(0, Params[4]))

        returns_global.append(sum(simu_returns))
    return returns_global


import main
import GlobalValue

if __name__ == '__main__':
    main.readFile('Portfolio structure.csv')
    main.readHistData(r'F:\Users\Administrator\workspace\TDLOGprojet\TDLOG\Historical Data.csv')

    modelp = pickle.load(open("globalValue_modelParams.data", "rb"))
    yahoodata = pickle.load(open("globalValue_yahooData.data", "rb"))
    #Plot_ARMA(modelp[0]['arma'], yahoodata[0])
    Plot_GARCH(modelp[0]['garch'], yahoodata[0])
    returns = pickle.load(open("global_returns.dat", "rb"))
    plt.figure(1)
    plt.boxplot(returns[1:21])
    print(returns[21:24])
    plt.show()
