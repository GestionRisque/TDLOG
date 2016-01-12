__author__ = 'sihanyou'

from yahoo_finance import Share
import GlobalValue
import datetime
import logging


def importData():
    GlobalValue.init()
    GlobalValue.yahooData = []
    today = datetime.date.today()
    for actif in GlobalValue.ptf:
        sh = Share(actif.stockCode)
        price = sh.get_historical('2013-01-01',str(today))
        if not price:
            logging.debug('{}\tWARNING:\t{} is not a valid share name.'.format(datetime.datetime.now(),actif.stockCode))
            return False
        GlobalValue.yahooData.append(decode(price))

    return True


def decode(ac):

    prices = []
    for item in ac:
        prices.append(float(item['Adj_Close']))
    return prices