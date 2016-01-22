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
        if share[i]==share[i-1]:
            share[i]=share[i]+0.01
        r.append(math.log(share[i] / share[i - 1]))
    return r


##  From here the functions are used for SV models

def vctPower(v, p):
    res = []
    for i in range(0, len(v) - 1):
        if math.fabs(v[i]) <= 0.0001:
            v[i]=math.fabs(v[i])+0.0001
        res.append(math.log(v[i] ** p))
    return res


def pseudoData(theta, u, e):
    a = theta[0]
    b = theta[1]
    s = theta[2]

    h = []
    y = []
    h.append(e[0] * s / math.sqrt(1 - b ** 2) + a / (1 - b))
    y.append(math.exp(h[0] / 2) * u[0])
    for i in range(1, len(e) - 1):
        h.append(a + b * h[i - 1] + s * e[i])
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

    bnds = ((-10, 0), (-0.999, 0.999), (0.001, 10))

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
    # print(res.summary())

    params = res.params.tolist()
    params.append(var)
    return params


if __name__ == '__main__':
    b = [117.339996, 118.300003, 117.809998, 118.029999, 118.879997, 117.75, 119.300003, 118.779999, 117.290001, 113.690002, 114.18, 112.339996, 115.720001, 116.110001, 116.769997, 120.57, 121.059998, 120.919998, 121.480003, 122.047573, 120.663499, 118.990659, 120.016268, 118.761636, 114.06176, 114.788644, 118.572451, 115.007708, 113.275126, 113.285078, 111.25378, 110.566719, 111.383223, 109.740254, 111.313522, 111.124329, 111.642117, 109.033282, 110.307825, 110.835564, 110.307825, 109.909528, 109.112942, 109.829875, 108.595155, 111.960753, 114.221074, 114.509839, 113.832737, 112.91666, 114.718943, 112.966443, 113.434441, 115.913833, 115.784382, 114.818515, 113.723205, 112.090196, 109.680513, 111.831302, 108.804259, 109.899576, 111.861173, 107.26087, 112.279389, 112.807129, 112.438703, 109.222474, 103.29783, 102.680478, 105.309225, 112.169857, 114.519799, 116.003446, 116.660636, 115.465746, 114.659201, 114.748814, 113.006273, 119.209722, 115.027619, 114.639282, 114.390352, 113.636999, 117.403756, 120.238734, 121.299372, 121.913943, 122.30053, 121.695866, 123.410734, 124.064963, 124.124435, 129.606052, 130.91451, 128.485933, 127.385644, 125.710435, 124.511023, 124.560588, 122.201406, 119.019492, 121.497619, 124.590325, 124.89761, 125.333763, 125.492359, 124.332597, 123.44047, 125.641048, 126.384486, 126.98915, 125.918597, 126.493524, 125.492359, 126.761159, 126.186239, 126.48361, 125.809559, 126.057372, 127.464946, 127.752417, 126.305184, 126.681865, 127.524419, 128.228213, 128.981559, 128.82297, 129.397882, 129.140162, 130.627039, 130.884759, 128.485933, 131.380384, 130.240452, 128.922086, 128.932008, 129.050954, 127.643379, 127.821797, 124.907525, 124.76875, 125.21481, 126.503439, 124.164086, 123.400816, 124.180648, 127.043312, 127.290094, 123.539013, 126.984086, 128.87937, 130.942462, 128.602975, 128.000827, 126.96434, 125.27636, 125.957473, 123.144161, 124.54588, 125.148029, 124.674212, 125.217127, 125.463909, 124.930859, 123.983218, 124.387944, 125.710691, 123.706823, 122.650597, 122.82828, 124.74331, 121.66347, 122.640724, 121.791793, 125.059191, 125.572494, 124.279359, 125.858762, 126.816277, 125.404684, 123.341583, 121.999089, 122.84802, 120.666469, 122.907252, 125.503395, 124.970345, 124.782796, 126.885368, 127.694819, 127.428291, 126.806411, 128.741172, 127.13215, 130.468645, 131.287963, 127.833017, 126.79653, 127.063058, 126.184516, 125.44417, 124.832148, 123.272485, 120.449299, 118.178911, 117.399079, 118.39608, 117.557021, 116.66227, 116.642601, 115.197234, 116.908082, 113.378221, 107.311588, 111.205246, 111.087261, 110.516976, 107.714723, 106.898626, 104.214358, 105.030455, 107.960535, 108.373497, 107.419746, 110.13351, 110.015518, 105.944875, 104.479839, 104.470005, 107.498407, 108.530812, 110.634961, 112.001681, 112.080335, 110.13351, 110.65463, 111.04793, 109.90736, 110.762787, 107.577069, 104.961628, 106.416837, 107.891708, 109.750044, 110.07451, 112.208162, 110.516976, 113.073417, 113.555206, 113.987837, 112.709613, 113.142244, 116.937578, 117.006405, 115.629858, 116.642601, 114.518791, 114.361468, 112.748943, 113.535544, 112.080335, 112.267154, 110.929938, 109.38624, 107.862204, 107.006784, 107.183769, 106.878957, 106.574152, 106.319609, 107.102814, 105.732209, 104.733631, 105.086065, 104.498665, 102.902894, 103.010585, 102.628775, 100.827408, 100.31833, 97.665236, 95.619118, 94.238729, 95.49185, 96.676442, 97.714181, 98.614869, 98.898773, 98.683398, 96.676442, 97.528176, 97.528176, 97.802295, 97.097413, 98.634445, 98.007885, 98.634445, 95.814922, 99.613447, 100.484758, 98.937934, 98.840035, 99.652608, 99.447019, 98.742136, 99.495964, 99.525341, 99.300167, 98.879196, 95.932398, 96.294631, 96.891823, 96.059673, 96.862454, 101.130903, 100.347699, 100.102948, 99.985465, 98.771505, 99.407858, 99.192476, 98.468017, 98.458225, 98.419064, 97.077836, 95.922613, 95.452689, 95.198146, 93.954817, 93.974394, 92.750642, 92.496107, 92.505895, 92.661763, 93.11961, 93.645656, 93.129354, 95.613456, 95.837508, 96.460967, 95.145858, 94.522398, 94.678267, 92.272099, 91.512258, 91.989593, 90.684219, 92.330546, 92.856591, 93.957386, 92.759177, 92.583829, 92.924782, 92.885815, 93.489795, 91.599929, 91.064147, 91.103107, 90.528358, 89.602913, 88.550822, 88.024776, 87.946842, 88.482631, 88.560565, 89.486011, 89.797741, 89.700327, 89.817221, 88.920999, 89.904899, 91.434324, 91.814244, 91.278455, 89.840885, 90.088594, 89.736507, 88.723383, 87.486208, 88.091577, 88.422787, 86.840481, 87.06593, 85.465527, 84.510851, 84.377257, 84.154595, 84.137894, 83.152604, 81.943255, 82.646039, 82.630736, 82.501311, 81.486798, 81.827751, 81.97387, 82.261732, 83.168195, 82.008474, 81.856243, 81.663872, 81.97387, 82.217446, 79.152052, 78.57496, 72.621327, 73.583154, 73.509807, 72.647624, 71.826956, 71.681642, 72.196458, 71.909993, 72.44557, 73.392172, 72.440034, 72.444181, 73.599762, 74.564354, 75.084706, 74.960154, 74.280645, 74.297252, 74.38029, 74.70136, 75.422383, 74.619712, 73.745068, 73.167976, 73.52226, 73.541632, 72.896728, 72.613019, 73.437841, 74.262655, 74.19069, 73.475202, 73.40878, 73.451677, 73.674492, 73.519489, 73.037888, 72.827527, 73.025434, 71.597223, 72.249052, 73.008826, 72.690521, 73.507035, 74.367836, 75.560779, 75.283995, 75.344882, 74.167165, 74.1727, 73.208108, 71.919675, 70.927404, 70.516381, 69.993622, 68.994868, 68.866928, 68.754123, 68.887566, 69.678584, 75.731617, 75.122186, 76.513003, 75.870555, 75.534887, 74.379312, 76.247499, 76.675334, 75.166209, 73.699725, 73.315905, 73.808402, 74.763132, 74.292647, 74.827786, 74.421961, 76.093418, 77.178837, 76.284638, 77.050897, 77.575037, 78.093666, 78.426587, 75.52801, 74.900697, 75.768756, 76.349298, 76.694598, 76.272258, 77.112802, 77.225607, 77.802021, 77.923084, 77.041265, 78.12531, 77.726362, 77.90795, 75.832042]

    s = SV(b)

    print(s)