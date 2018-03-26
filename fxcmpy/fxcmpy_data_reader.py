#
# fxcm_data_reader
#
# a class for fetching historical data provided by
# FXCM
#
# by the Pathon Quants GmbH
# September 2017
#

import datetime as dt
from io import BytesIO, StringIO
import gzip
import urllib.request
import pandas as pd


class fxcmpy_tick_data_reader(object):
    """ fxcm_tick_data_reader(A class to fetch hsitorical data provided by FXCM """
    symbols = ('AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'CADCHF', 'EURAUD',
               'EURCHF', 'EURGBP', 'EURJPY', 'EURUSD', 'GBPCHF', 'GBPJPY',
               'GBPNZD', 'GBPUSD', 'GBPCHF', 'GBPJPY', 'GBPNZD', 'NZDCAD',
               'NZDCHF', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY')

    def __init__(self, symbol, start, stop):
        """ Constructor of the class.

        Arguments:
        ==========

        symbol: string, one of fxcm_data_reader.symbols,
            defines the instrument to deliver data for.

        start: datetime.date,
            the first day to delivers data for.

        stop: datetime.date,
            the last day to delivers data for.

        """

        if not (isinstance(start, dt.datetime) or isinstance(start, dt.date)):
            raise TypeError('start must be a datetime object')
        else:
            self.start = start

        if not (isinstance(stop, dt.datetime) or isinstance(stop, dt.date)):
            raise TypeError('stop must be a datetime object')
        else:
            self.stop = stop

        if self.start > self.stop:
            raise ValueError('Invalid date range')

        if symbol not in self.symbols:
            msg = 'Symbol %s is not supported. For a list of supported'
            msg += ' symbols, see get_available_symbols()'
            raise ValueError(msg % symbol)
        else:
            self.symbol = symbol

        self.data = None
        self.url = 'https://tickdata.fxcorporate.com/%s/%s/%s.csv.gz'
        self.codec = 'utf-16'
        if not isinstance(self, fxcmpy_candles_data_reader):
            self.__fetch_data__()

    def get_data(self):
        """ Returns the fetched data as Pandas DataFrame"""
        return self.data

    @classmethod
    def get_available_symbols(cls):
        """ Return all symbols available"""
        return cls.symbols

    def __fetch_data__(self):
        """ Fetch the data for the given symbol and the given time window. """
        self.data = pd.DataFrame()
        running_date = self.start
        seven_days = dt.timedelta(days=7)
        while running_date <= self.stop:
            year, week, noop = running_date.isocalendar()
            url = self.url % (self.symbol, year, week)
            data = self.__fetch_dataset__(url)
            if len(self.data) == 0:
                self.data = data
            else:
                self.data = pd.concat((self.data, data))
            running_date = running_date + seven_days
        
        self.data = self.data[(self.data.index > self.start) & 
                              (self.data.index < self.stop)]

    def __fetch_dataset__(self, url):
        """ Fetch the data for the given symbol and for one week."""
        print('Fetching data from: %s' % url)
        requests = urllib.request.urlopen(url)
        buf = BytesIO(requests.read())
        f = gzip.GzipFile(fileobj=buf)
        data = f.read()
        data_str = data.decode(self.codec)
        data_pandas = pd.read_csv(StringIO(data_str), index_col=0,
                                  parse_dates=True)
        return data_pandas

class fxcmpy_candles_data_reader(fxcmpy_tick_data_reader):
    def __init__(self, symbol, start, stop, period):
        fxcmpy_tick_data_reader.__init__(self, symbol, start, stop)
        if period not in ['m1', 'H1', 'D1']:
            raise ValueError("period must be one of 'm1', 'H1' or 'D1'")
        self.period = period
        self.codec = 'utf-8'
        self.url = 'https://candledata.fxcorporate.com/%s/%s/%s/%s.csv.gz'
        self.__fetch_data__()


    def __fetch_data__(self):
        """ Fetch the data for the given symbol, period 
        and the given time window. """
        self.data = pd.DataFrame()
        if self.period != 'D1':
            running_date = self.start
            seven_days = dt.timedelta(days=7)
            while running_date <= self.stop:
                year, week, noop = running_date.isocalendar()
                url = self.url % (self.period, self.symbol, year, week)
                data = self.__fetch_dataset__(url)
                if len(self.data) == 0:
                    self.data = data
                else:
                    self.data = pd.concat((self.data, data))
                running_date = running_date + seven_days
        else:
            start, noop, noop2 = self.start.isocalendar()
            stop, noop, noop2 = self.stop.isocalendar()
            if stop >= dt.datetime.now().year:
                msg = "Candles with period 'D1' are restricted to years before %s"
                raise ValueError(msg % dt.datetime.now().year ) 
            for year in range(start, stop+1):
                url = 'https://candledata.fxcorporate.com/%s/%s/%s.csv.gz'
                data = self.__fetch_dataset__(url % (self.period, self.symbol,
                                                     year) )

                if len(self.data) == 0:
                    self.data = data
                else:
                    self.data = pd.concat((self.data, data))

        self.data = self.data[(self.data.index > self.start) & 
                              (self.data.index < self.stop)]
