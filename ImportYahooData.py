__author__ = 'sihanyou'

from yahoo_finance import Share
import GlobalValue
import datetime
import logging


def main():
    GlobalValue.init()
    GlobalValue.yahooData = []
    today = datetime.date.today()
    for actif in GlobalValue.ptf:
        sh = Share(actif.nom)
        price = sh.get_historical('2013-01-01',str(today))
        if not price:
            logging.debug('{}           WARNING:         {} is not a valid share name.'.format(datetime.datetime.now(),actif.nom))
            return 0
        GlobalValue.yahooData.append(decode(price))

    #print(GlobalValue.yahooData[0])


def decode(ac):

    prices = []
    for item in ac:
        prices.append(float(item['Adj_Close']))
    return prices