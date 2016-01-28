__author__ = 'sihanyou'

import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import csv
import scipy.stats as st
import math
from scipy.interpolate import griddata
import GlobalValue


def price(r,init):
    prix = []
    n = len(r)
    for i in range(0, n):
        prix.append(math.exp(r[i])*init)
    return prix

def agregation():
    histData = GlobalValue.yahooData
    rankmatrix = generateRanking(histData)
    sims = []
    i = 0
    actual_value = 0
    for actif in histData:
        print(GlobalValue.ptf[i].quantity)
        sims.append(price(GlobalValue.simulations[i],actif[len(actif)-1]*GlobalValue.ptf[i].quantity))
        actual_value = actual_value + actif[len(actif)-1]*GlobalValue.ptf[i].quantity
        i = i + 1

    ordering = reorder(sims)
    ordered = reordered(rankmatrix,ordering)

    agre = np.sum(ordered,0)

    pnl = agre - actual_value

    estimated_value = np.mean(agre)

    estimated_pnl = np.mean(pnl)

    VaR = - np.percentile(pnl, 1)

    loss = []
    for item in agre:
        if item<actual_value:
            loss.append(actual_value - item)
    loss = np.array(loss)
    expected_shortfall = np.mean(loss[np.where(loss > VaR)])

    print(actual_value,estimated_pnl, VaR, estimated_pnl, expected_shortfall)

    textstring = '$Initial=%.0f$\n$Expected P&L=%.0f$\n$VaR_{99}=%.0f$\n$Expected Value=%.0f$\n$Expected Shortfall=%.0f$'%(actual_value,estimated_pnl, VaR, estimated_value, expected_shortfall)
    fig = plt.figure(figsize=(20,10))
    plt.hist(agre,bins = 100)
    plt.title('Distribution of portfolio value in 1 year')
    fig.text(0.13, 0.7,textstring)
    plt.show()



# Data and histograms
def plotData(x,y):

    fig = plt.figure()
    fig.add_subplot(2,2,1)
    plt.hist(x,bins=20,color='green',alpha=0.8,align='mid')
    plt.title('X variable distribution')
    fig.add_subplot(2,2,3)
    plt.scatter(x,y,marker="o",alpha=0.8)
    fig.add_subplot(2,2,4)
    plt.title('Joint X,Y')
    plt.hist(y,bins=20,orientation='horizontal',color='red',alpha=0.8,align='mid')
    plt.title('Y variable distribution')
    plt.show()


def generateRanking(matrix):

    ranking = []
    for item in matrix:
        ranking.append(st.rankdata(item))
    ranking = np.array(ranking)

    ranking = 1000/np.max(ranking[0])* ranking-1
    rankings = []

    for item in ranking:
        rankings.append([int(i) for i in item])
    print(rankings)

    # plotData(rankings[0],rankings[1])
    # plotData(matrix[0],matrix[1])
    # clayton = Copula(histData,family='clayton')
    # rank2 = clayton.generate_uv(1000)
    # print(rank2)
    return (rankings)

def reorder(matrix):
    order = []
    for item in matrix:
        order.append(np.sort(item))
    return order

def reordered(rank,order):
    ranked = []
    j = 0
    for item in order:
        ranked.append(item[rank[j]])
        j=j+1

    return ranked
#-------------------------------------------------------------------------------
# Run the functions

# plotData()
# plotData1()
# generateCopulas()



# plotProcess()

if __name__ == '__main__':
    agregation()
# generateRanking()