__author__ = 'dhy'
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import numpy
import math
import pickle
import SimpleModelling
import GlobalValue

########   Plot_ARMA take the parameters of ARMA model ...
# and calculate the fitted value then compare with historical data######
def Plot_ARMA(Params,returns):
    N=len(returns)
    n=4
    returns_global=[]
    for j in range(1000):
        sim_r=[Params[0]]*250
        for i in range(n-1):
            sim_r[i]=returns[i+N-251]
        for i in range(n-1,250):
            sim_r[i]=Params[1]*(sim_r[i-1]-Params[0])+Params[2]*(sim_r[i-2]-Params[0])+Params[3]*(sim_r[i-3]-Params[0])+numpy.random.normal(0,math.sqrt(Params[4]))

        returns_global.append(sum(sim_r))
    return returns_global



def Plot_GARCH(param, returns):

    N=len(returns)
    global_returns=[]

    for j in range(1000):

        sigma=[math.sqrt(param[4])]
        epsilon=[param[4]*numpy.random.normal(0,1)]
        simu_r=[param[0]+epsilon[0]]
        for i in range(1,250):
            sigma.append(param[1]+param[2]*(epsilon[i-1])**(2)+param[3]*(sigma[i-1])**(2))
            epsilon.append(math.sqrt(sigma[i])*numpy.random.normal(0,1))
            simu_r.append(param[0]+epsilon[i])

        global_returns.append(sum(simu_r))

    return global_returns


def Plot_SV(param, returns):

    global_returns = []
    N = len(returns)
    for j in range(1000):
        h = [numpy.random.normal(param[0] / (1 - param[1]), param[2] / math.sqrt(1 - param[1] ** (2)))]
        simu_returns = [math.exp(h[0] / 2) * numpy.random.normal(0, 1)]

        for i in range(1, 250):
            h.append(param[0] + param[1] * h[i - 1] + param[2] * numpy.random.normal(0, 1))
            simu_returns.append(math.exp(h[i] / 2) * numpy.random.normal(0, 1))
        global_returns.append(sum(simu_returns))

    return global_returns


def chose_SV(param):
    global_returns = []

    for j in range(1000):
        h = [numpy.random.normal(param[0] / (1 - param[1]), param[2] / math.sqrt(1 - param[1] ** (2)))]
        simu_returns = [math.exp(h[0] / 2) * numpy.random.normal(0, 1)]

        for i in range(1, 250):
            h.append(param[0] + param[1] * h[i - 1] + param[2] * numpy.random.normal(0, 1))
            simu_returns.append(math.exp(h[i]/2) * numpy.random.normal(0, 1))
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
        for i in range(n ,250+n):
            simu_returns.append(Params[1]*simu_returns[i-1]+Params[2]*simu_returns[i-2]+Params[3]*simu_returns[i-3]+numpy.random.normal(0,Params[4]))

        returns_global.append(sum(simu_returns))
    return returns_global

def plot_simulation(params,hist):
    hist = SimpleModelling.returns(hist)
    sim_arma = Plot_ARMA(params['arma'],hist)
    sim_garch = Plot_GARCH(params['garch'],hist)
    sim_sv = Plot_SV(params['sv'],hist)

    real_global_returns = sum(hist[(len(hist)-251):])
    plt.subplot(1,3,1)
    plt.boxplot([sim_arma])
    plt.plot([real_global_returns] * len(hist))
    plt.title("boxplot_ARMA")

    plt.subplot(1,3,2)
    plt.boxplot([sim_garch])
    plt.plot([real_global_returns] * len(hist))
    plt.title("boxplot_GARCH")

    plt.subplot(1,3,3)
    plt.boxplot(sim_sv)
    plt.plot([real_global_returns]*500)
    plt.title("boxplot_SV")

    plt.show()


#for test
import main
import GlobalValue

if __name__ == '__main__':
    main.readFile('Portfolio structure.csv')
    main.readHistData('Historical Data.csv')
    modelp = pickle.load(open("globalValue_modelParams.dat", "rb"))
    yahoodata = pickle.load(open("globalValue_yahooData.dat", "rb"))
    #print(modelp[0])
    #plot_simulation(modelp[0],yahoodata[0])
    #plot_simulation(modelp[1],yahoodata[1])
    #plot_simulation(modelp[2],yahoodata[2])
    chose_SV(modelp[0])
    #returns = pickle.load(open("global_returns.dat", "rb"))
