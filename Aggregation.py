__author__ = 'sihanyou'

import numpy as np
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
import csv
import scipy.stats as st
import math
from scipy.interpolate import griddata

sims = []
sims.append(np.random.normal(0,1,1000))
sims.append(np.random.normal(0,1,1000))
sims.append(np.random.normal(0,1,1000))

with open('/Users/sihanyou/GitHub/TDLOG/Historical Data.csv', 'r') as csvfile:
    pf = csv.reader(csvfile)
    pf = list(pf)

hisData = list(map(list, zip(*pf[1:])))
histData = []
numItem = len(hisData)
for item in hisData:
    histData.append([float(i) for i in item])

histData = np.array(histData)

from copulalib.copulalib import Copula
plt.style.use('ggplot')



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

def plotProcess():

    for i in range(0,numItem-1):
        for j in range(i+1,numItem):
            plotData(histData[i],histData[j])


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

    plotData(rankings[0],rankings[1])
    plotData(matrix[0],matrix[1])
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
        j+=1

    return ranked
#-------------------------------------------------------------------------------
# Run the functions

# plotData()
# plotData1()
# generateCopulas()



# plotProcess()

if __name__ == '__main__':

    plt.hist(histData[0]*500+histData[1]*100+histData[2]*300,bins =100)
    rankmatrix = generateRanking(histData)
    ordering = reorder(sims)
    ordered = reordered(rankmatrix,ordering)
    print(ordered)
    plotData(ordered[0],ordered[1])
    plotData(np.random.normal(0,1,1000),np.random.normal(0,1,1000))
    plt.hist(histData[0]+histData[1]+histData[2])

# generateRanking()