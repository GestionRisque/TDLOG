__author__ = 'dhy'

import matplotlib.pyplot as plt
import numpy
import math
########   Plot_ARMA take the parameters of ARMA model ...
# and calculate the fitted value then compare with historical data######
def Plot_ARMA(Params,Share):

    N=len(Share)
    share=[Params[0]]*N
    n=4
    returns_global=[]
    for i in range(n-1):
        share[i]=Share[i]
    for j in range(1000):
        for i in range(n-1,N):
            share[i]=Params[1]*share[i-1]+Params[2]*share[i-2]+Params[3]*share[i-3]+numpy.random.normal(0,Params[4])

        returns_global.append(sum(share))
    print(returns_global)
    real_global_returns=sum(Share)
    plt.figure(1)
    plt.boxplot([returns_global])
    plt.plot([real_global_returns]*500)
    plt.title("boxplot_ARMA")
    plt.ylabel("returns")
    plt.show()

def Plot_GARCH(param,returns):

    N=len(returns)
    global_returns=[]
    for j in range(1000):

        sigma=[param[4]]
        epsilon=[param[4*numpy.random.normal(0,1)]
        simu_r=[param[0]+epsilon[0]]
        for i in range(1,N):
            sigma.append(param[1]+param[2]*(epsilon[i-1])**(2)+param[3]*(sigma[i-1])**(2))
            epsilon.append(sigma[i]*numpy.random.normal(0,1)
            simu_r.append(param[0]+epsilon[i])

        global_returns.append(sum(simu_r))

    real_returns=sum(returns)
    plt.figure(2)
    plt.boxplot(global_returns)
    plt.plot([real_returns]*500)
    plt.title("boxplot_GARCH")
    plt.ylabel("returns")
    plt.show())

def Plot_SV(param,returns):
    global_returns=[]
    N=len(returns)
    for j in range(1000):
        h=[numpy.random.normal(param[0]/(1-param[1]),param[2]**(2)/(1-param[1]**(2)))]
        simu_returns=[math.exp(h[0])/2*numpy.random.normal(0,1)]

        for i in range(1,N):
            h.append(param[0]+param[1]*h[i-1]+param[2]*numpy.random.normal(0,1))
            simu_returns.append(math.exp(h[i])/2*numpy.random.normal(0,1))
        global_returns.append(sum(simu_returns))

    real_returns=sum(returns)

    plt.figure(3)
    plt.boxplot(global_returns)
    plt.plot([real_returns]*500)
    plt.title("boxplot_SV")
    plt.ylabel("returns")
    plt.show())


def chose_SV(params):
    global_returns=[]

    for j in range(1000):
        h=[numpy.random.normal(param[0]/(1-param[1]),param[2]**(2)/(1-param[1]**(2)))]
        simu_returns=[math.exp(h[0])/2*numpy.random.normal(0,1)]

        for i in range(1,250):
            h.append(param[0]+param[1]*h[i-1]+param[2]*numpy.random.normal(0,1))
            simu_returns.append(math.exp(h[i])/2*numpy.random.normal(0,1))
        global_returns.append(sum(simu_returns))

    return global_returns

def chose_GARCH(params):
    global_returns=[]
    for j in range(1000):
        sigma=[param[4]]
        epsilon=[param[4*numpy.random.normal(0,1)]
        simu_r=[param[0]+epsilon[0]]
        for i in range(1,N):
            sigma.append(param[1]+param[2]*(epsilon[i-1])**(2)+param[3]*(sigma[i-1])**(2))
            epsilon.append(sigma[i]*numpy.random.normal(0,1)
            simu_r.append(param[0]+epsilon[i])

        global_returns.append(sum(simu_r))

    return global_returns

def chose_ARMA(param,returns):    ##### 3 lastest days' returns
    returns_global=[]
    n=3
    simu_returns=returns
    for j in range(1000):
        for i in range(n,250+n):
            simu_returns.append(Params[1]*simu_returns[i-1]+Params[2]*simu_returns[i-2]+Params[3]*simu_returns[i-3]+numpy.random.normal(0,Params[4]))

        returns_global.append(sum(simu_returns))
    return returns_global












