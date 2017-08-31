import requests
from socketIO_client import SocketIO
from threading import Thread
import json
import pandas as pd
import sys
import time
import datetime as dt
import configparser
import logging
import os
from urllib.parse import unquote

NO_CREDENTIALS = 'Can not find login credentials. Please provide \
them either as parameter in the class constructor or within a \
a configuration file and provice the files path as parameter in the \
class constructor.'

LOG_LEVELS = {'error': 40, 'warn': 30, 'info': 20, 'debug': 10}


class ServerError(Exception):
    pass


class fxcm(object):
    """ A wrapper class for the FXCM API. """

    # Class attributes

    auth_url = 'https://www-beta2.fxcorporate.com'
    trading_url = 'https://api.fxcm.com'
    port = 443
    models = ['Offer', 'Account', 'Order', 'OpenPosition', 'ClosedPosition',
              'Summary', 'Properties', 'LeverageProfile']
    PERIODS = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8',
               'D1', 'W1', 'M1']
    CANDLES_COLUMNS = ['date', 'bidopen', 'bidclose', 'bidhigh', 'bidlow',
                       'askopen', 'askclose', 'askhigh', 'asklow', 'tickqty']

    debug = False

    def __init__(self, user='', password='', config_file='',
                 log_file='', log_level=''):
        """ Constructor

        Arguments:
        ===========

        user: string (default: ''),
            username of the users FXCM acount.
        password: string (default: ''),
            password of the FXCM account given by username.
        config_file: string (default: ''),
            path of an optional configuration file, fxcmpy tries to read all
            other parameter which are not given from that file. The file must
            be readable by configparser.
        log_file: string (default: ''),
            path of an optional log file. If not given (and not found in the
            optional configuration file), log messages are printed to stdout.
        log_level: string (default: ''),
            the log level. Must be one of 'error', 'warn', 'info' or 'debug'.
            If not given (and not found in the optional configuration file),
            'warn' is used.
        """

        self.logger = None
        self.config_file = ''

        if user != '' and password != '':
            self.user = user
            self.password = password
        elif config_file != '':
            if os.path.isfile(config_file):
                self.config_file = config_file
            else:
                raise IOError('Can not find configiguration file: %s'
                              % config_file)
            try:
                self.user = self.__get_config_value__('FXCM', 'user')
            except:
                raise ValueError('Can not find user in configuration file %s'
                                 % self.config_file)
            try:
                self.password = self.__get_config_value__('FXCM', 'password')
            except:
                raise ValueError(
                           'Can not find %s password in configuration file %s'
                           % (self.user, self.config_file))
        else:
            raise ValueError(NO_CREDENTIALS)

        if log_level != '':
            if log_level in LOG_LEVELS:
                log_level = LOG_LEVELS[log_level]
            else:
                raise ValueError('log_level must be one of %s'
                                 % LOG_LEVELS.keys())
        elif self.config_file != '':
            try:
                log_level = LOG_LEVELS[
                             self.__get_config_value__('FXCM', 'log_level')]
            except:
                log_level = LOG_LEVELS['warn']
        else:
            log_level = LOG_LEVELS['warn']

        if log_file != '':
            log_path = log_file
        elif self.config_file != '':
            try:
                log_path = self.__get_config_value__('FXCM', 'log_file')
            except:
                log_path = ''
        else:
            log_path = ''

        if log_path == '':
            form = '|%(levelname)s|%(asctime)s|%(message)s|'
            logging.basicConfig(level=log_level, format=form)
        else:
            form = '|%(levelname)s|%(asctime)s|%(message)s|'
            logging.basicConfig(filename=log_path, level=log_level,
                                format=form)

        self.logger = logging.getLogger('FXCM')
        self.socket = None
        self.access_token = None
        self.prices = dict()
        self.account_ids = set()
        self.orders = dict()
        self.add_callbacks = dict()
        self.waiting_for_id = 0
        self.pending_id = None
        self.pending_id_2 = None

        self.connect()
        count = 0
        while not self.is_connected() and count < 100:
            count += 1
            time.sleep(0.1)

        if count == 100:
            raise ServerError('Can not connect to FXCM Server')
        self.__collect_account_ids__()
        self.__collect_orders__()
        self.subscribe_data_model('Order')

    def connect(self):
        """ Connect to the FXCM server."""

        self.logger.info('Connecting FXCM Server for user %s' % self.user)

        if self.access_token is None:
            self.logger.info('Requesting access token...')
            self.__request_access_token__()

        socket_thread = Thread(target=self.__connect__)
        socket_thread.start()

    def is_connected(self):
        """ Return True if socket connection is established and False else."""

        if self.socket is not None and self.socket.connected:
            return True
        else:
            return False

    def get_instruments(self):
        """ Return the tradeable instruments of FXCM as a list."""

        self.logger.debug('Fetching available instruments')

        data = self.__handle_request__(method='trading/get_instruments')

        if 'data' in data and 'instrument' in data['data']:
            instruments = [ins['symbol'] for ins in data['data']['instrument']]
        else:
            instruments = list()

        return instruments

    def get_model(self, models=list()):
        """ Return a snapshot of the the specified model(s)

        Arguments:
        ===========
        models: list,
            list of the required models, entries must be out of
            ['Offer', 'Account', 'Order', 'OpenPosition', 'ClosedPosition',
             'Summary', 'Properties', 'LeverageProfile'].

        Returns:
        ========
        The current data of the specified model(s) in a json like manner.

        """

        if len(models) == 0:
            raise ValueError('Please specify one or more models')
        for model in models:
            if model not in self.models:
                raise ValueError('Models have to be of %s' % self.models)

        data = self.__handle_request__(method='trading/get_model',
                                       params={'models': models})

        return data

    def get_open_positions(self, kind='dataframe'):
        """ Return a snapshot of the 'Open Position' model.

        Arguments:
        ==========
        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a Pandas Dataframe.

        Return:
        =======
        The current data of the 'Open Position' model.

        """
        data = self.get_model(('OpenPosition',))
        open_pos = data['open_positions']
        if kind == 'list':
            return open_pos
        else:
            return pd.DataFrame(open_pos)

    def get_closed_positions(self, kind='dataframe'):
        """ Return a snapshot of the 'Closed Position' model.

        Arguments:
        ==========
        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a Pandas Dataframe.

        Return:
        =======
        The current data of the 'Closed Position' model.

        """
        data = self.get_model(('ClosedPosition',))
        closed_pos = data['closed_positions']
        if kind == 'list':
            return closed_pos
        else:
            return pd.DataFrame(closed_pos)

    def get_offers(self, kind='dataframe'):
        """ Return a snapshot of the 'Offer' model.

        Arguments:
        ==========
        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a Pandas Dataframe.

        Return:
        =======
        The current data of the 'Offer' model.

        """
        data = self.get_model(('Offer',))
        offers = data['offers']
        if kind == 'list':
            return offers
        else:
            return pd.DataFrame(offers)

    def get_orders(self, kind='dataframe'):
        """ Return a snapshot of the 'Order' model.

        Arguments:
        ==========
        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a Pandas Dataframe.

        Return:
        =======
        The current data of the 'Order' model.

        """
        data = self.get_model(('Order',))
        orders = data['orders']
        if kind == 'list':
            return orders
        else:
            return pd.DataFrame(orders)

    def get_summary(self, kind='dataframe'):
        """ Return a snapshot of the 'Summary' model.

        Arguments:
        ==========
        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a Pandas Dataframe.

        Return:
        =======
        The current data of the 'Summary' model.

        """
        data = self.get_model(('Summary',))
        summary = data['summary']
        if kind == 'list':
            return summary
        else:
            return pd.DataFrame(summary)

    def get_accounts(self, kind='dataframe'):
        """ Return a snapshot of the 'Account' model.

        Arguments:
        ==========
        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a Pandas Dataframe.

        Return:
        =======
        The current data of the 'Account' model.

        """
        data = self.get_model(('Account',))
        accounts = data['accounts']
        if kind == 'list':
            return accounts
        else:
            return pd.DataFrame(accounts)

    def get_account_ids(self):
        """ Return a list of available account ids"""

        return self.account_ids

    def get_order_ids(self):
        """ Return a list of available order ids"""

        return list(self.orders.keys())

    def get_order(self, order_id):
        """ Returns the order data for a given order id

        Argument:
        =========

        order_id: (integer),
            the id of the order.

        Returns:
        ========

        A dictionary containing the defining data of the order.
        """

        if order_id not in self.orders:
            raise ValueError('No order with id %s' % order_id)
        else:
            return self.orders[order_id]

    def get_prices(self, symbol):
        """ Return the prices of a given subscribed instrument.

        Arguments:
        ==========

        symbol: string,
            the symbol of the instrument as given by get_instruments().

        """

        if symbol in self.prices:
            return self.prices[symbol]
        else:
            return pd.DataFrame(columns=['Bid', 'High', 'Low', 'Close'])

    def get_subscribed_symbols(self):
        """ Return a list of symbols for the subscriped instruments."""

        return list(self.prices.keys())

    def is_subscribed(self, symbol):
        """ Returns True if the instrument is subscripted and False else.

        Arguments:
        ==========

        symbol:  string,
            the symbol of the instrument in question as given by
            get_instruments().

        """

        return symbol in self.prices

    def subscribe_market_data(self, symbol='', add_callbacks=()):
        """ Stream the prices of an instrument.

        Arguments:
        ==========

        symbol:  string,
            the symbol of the instrument in question as given by
            get_instruments().

        add_callbacks: list of callables,
            all methods in that list will be called for every incoming dataset
            of the instrument. Such a method has to accept two positional
            arguments, data and dataframe, say. The first should be a json like
            object with the new price data received by the stream and the
            second should be a Pandas DataFrame with the collected price data
            as given by get_prices().

        """

        if symbol == '':
            raise ValueError('No symbol given')

        self.logger.info('Try to subscribe for %s' % symbol)

        for func in add_callbacks:
            if not callable(func):
                self.logger.error('Callback method is not callable')
                raise ValueError('Content of add_callbacks is not callable')
            else:
                if symbol not in self.add_callbacks:
                    self.add_callbacks[symbol] = dict()
                self.logger.info('Adding callback method %s for symbol %s'
                                 % (func.__name__, symbol))
                self.add_callbacks[symbol][func.__name__] = func

        params = {'pairs': symbol}
        data = self.__handle_request__(method='subscribe', params=params,
                                       protocol='post')
        self.socket.on(symbol, self.__on_price_update__)

    def subscribe_data_model(self, model='', add_callbacks=()):
        """ Stream data of a model.

        Arguments:
        ==========

        model: string,
            the model, must be one of ['Offer', 'Account', 'Order',
            'OpenPosition', 'ClosedPosition', 'Summary', 'Properties',
            'LeverageProfile'].

        add_callbacks: list of callables,
            all methods in that list will be called for every incoming dataset
            of the model. Such a method has to accept two positional
            arguments, data and dataframe, say. The first should be a json like
            object with the new data received by the stream and the second
            should be a Pandas DataFrame with the collected data.

        """

        if model == '':
            raise ValueError('No model given')

        if model not in ['Offer', 'Account', 'Order', 'OpenPosition',
                         'ClosedPosition', 'Summary']:
            msg = "model must on of 'Offer', 'Account', 'Order',"
            msg += "'OpenPosition', 'ClosedPosition' or 'Summary'"
            raise ValueError(msg)

        self.logger.info('Try to subscribe for %s' % model)

        for func in add_callbacks:
            if not callable(func):
                self.logger.error('Callback method is not callable')
                raise ValueError('Content of add_callbacks must be callable')
            else:
                if model not in self.add_callbacks:
                    self.add_callbacks[model] = dict()
                self.logger.info('Adding callback method %s for model %s'
                                 % (func.__name__, model))
                self.add_callbacks[model][func.__name__] = func

        params = {'models': model}
        data = self.__handle_request__(method='trading/subscribe',
                                       params=params, protocol='post')
        if model == 'Order':
            self.socket.on('Order', self.__on_order_update__)
        else:
            self.socket.on(model, self.__on_model_update__)
            self.socket.on(model, self.__on_message__)

    def unsubscribe_market_data(self, symbol=''):
        """ Unsubscribe for instrument prices of the given symbol"""

        if symbol == '':
            raise ValueError('No symbol given')

        self.logger.info('Try to unsubscribe for %s' % symbol)

        params = {'pairs': symbol}
        data = self.__handle_request__(method='unsubscribe', params=params,
                                       protocol='post')

        if symbol in self.prices:
            del self.prices[symbol]
        if symbol in self.add_callbacks:
            del self.add_callbacks[symbol]

    def unsubscribe_data_model(self, model=''):
        """ Unsubscribe for the given model

        Arguments:
        ==========

        model: string,
            the model, must be one of ['Offer', 'Account', 'Order',
            'OpenPosition', 'ClosedPosition', 'Summary', 'Properties',
            'LeverageProfile'].

        """

        if model == '':
            raise ValueError('No symbol given')

        self.logger.info('Try to unsubscribe for %s' % model)

        params = {'models': model}
        data = self.__handle_request__(method='trading/unsubscribe',
                                       params=params, protocol='post')

        if model in self.add_callbacks:
            del self.add_callbacks[model]

    def close_all_for_symbol(self, account_id, for_symbol, symbol,
                             order_type, time_in_force):
        """ Close all positions for a given symbol.

        Arguments:
        ==========

        account_id: string,
            the order's account id.

        for_symbol: boolean,
            true, if trades should be closed for the specific symbol.

        symbol: string,
            the trades symbol as given by get_instruments.

        order_type: string
            the type of order execution, one of 'AtMarket' or 'MarketRange'.

        time_in_force: string,
            the time in force of the order exectution, must be one of
            'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'.
        """

        try:
            account_id = int(account_id)
        except:
            raise TypeError('trade_id must be an integer')

        if for_symbol is True:
            for_symbol = 'true'
        elif for_symbol is False:
            for_symbol = 'false'
        else:
            raise TypeError('for_symbol must be a boolean')

        if order_type not in ['AtMarket', 'MarketRange']:
            msg = "order_type must be 'AtMarket' or 'MarketRange'"
            raise ValueError(msg)

        if time_in_force not in ['IOC', 'GTC', 'FOK', 'DAY', 'GTD']:
            msg = "time_in_force must be in 'IOC', 'GTC', 'FOK', 'DAY', 'GTD'"
            raise ValueError(msg)

        params = {
                  'account_id': account_id,
                  'forSymbol': for_symbol,
                  'symbol': symbol,
                  'order_type': order_type,
                  'time_in_force': time_in_force
                 }

        data = self.__handle_request__(method='trading/close_all_for_symbol',
                                       params=params, protocol='post')

    def open_trade(self, account_id, symbol, is_buy,
                   amount, time_in_force, order_type, rate=0,
                   is_in_pips=True, limit=0,
                   at_market=0, stop=None, trailing_step=None):
        """ Opens a trade for a given instrument

        Arguments:
        ==========

        account_id: integer,
            the id of the tradings account.

        symbol: string,
            the symbol of the instrument to trade as given by
            get_instruments().

        is_buy: boolean,
            True if the trade is a buy, False else.

        amount: integer,
            the trades amount in lots.

        order_type: string,
            the order type, must be 'AtMarket' or 'MarketRange'.

        time_in_force: string,
            the time in force of the order exectution, must be one of
            'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'.

        rate: float (default 0),
            the trades rate.

        is_in_pips: boolean (default True),
            wheter the trades stop/limit rates are in pips.

        limit: float (default 0),
            the trades limit rate.

        at_market: float (default 0),
            the markets range.

        stop: float or None (default None),
            the trades stop rate.

        trailing_step: float or None (default None),
            the trailing step for the stop rate.
        """

        try:
            account_id = int(account_id)
        except:
            raise TypeError('trade_id must be an integer')

        try:
            amount = int(amount)
        except:
            raise TypeError('amount must be an integer')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number')

        try:
            limit = float(limit)
        except:
            raise TypeError('limit must be a number')

        try:
            at_market = float(at_market)
        except:
            raise TypeError('at_market must be a number')

        if order_type not in ['AtMarket', 'MarketRange']:
            msg = "order_type must be 'AtMarket' or 'MarketRange'"
            raise ValueError(msg)

        if time_in_force not in ['IOC', 'GTC', 'FOK', 'DAY', 'GTD']:
            msg = "time_in_force must be in 'IOC', 'GTC', 'FOK', 'DAY', 'GTD'"
            raise ValueError(msg)

        if is_in_pips is True:
            is_in_pips = 'true'
        elif is_in_pips is False:
            is_in_pips = 'false'
        else:
            raise ValueError('is_in_pips must be True or False')

        if is_buy is True:
            is_buy = 'true'
        elif is_buy is False:
            is_buy = 'false'
        else:
            raise ValueError('is_buy must be True or False')

        if stop is not None:
            try:
                stop = float(stop)
            except:
                raise TypeError('stop must be a number')

        if trailing_step is not None:
            try:
                trailing_step = float(trailing_step)
            except:
                raise ValueError('trailing step must be a number')

        params = {
                  'account_id': account_id,
                  'symbol': symbol,
                  'is_buy': is_buy,
                  'rate': rate,
                  'amount': amount,
                  'at_market': at_market,
                  'order_type': order_type,
                  'time_in_force': time_in_force,
                  'limit': limit,
                  'is_in_pips': is_in_pips
                 }
        if stop is not None:
            params['stop'] = stop
        if trailing_step is not None:
            params['trailing_step'] = trailing_step

        data = self.__handle_request__(method='trading/open_trade',
                                       params=params, protocol='post')

    def change_trade_stop_limit(self, trade_id, is_stop, rate, is_in_pips=True,
                                trailing_step=0):
        """ Change an trades's stop or limit rate.

        Arguments:
        ==========

        trade_id: integer,
            the id of the trade to change.

        is_stop: boolean,
            defines wheter the trades's limit (False) or the stop rate (True)
            is to be changed.

        rate: float,
            the new stop or limit rate.

        is_in_pips: boolean (Default True),
            wheter the trade's stop/limit rates are in pips.

        trailing_step: float (Default 0),
            the trailing step for the stop rate.
        """

        try:
            trade_id = int(trade_id)
        except:
            raise TypeError('trade_id must be an integer')

        if is_stop is True:
            is_stop = 'true'
        elif is_stop is False:
            is_stop = 'false'
        else:
            raise ValueError('is_stop must be a boolean')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number')

        if is_in_pips is True:
            is_in_pips = 'true'
        elif is_in_pips is False:
            is_in_pips = 'false'
        else:
            raise ValueError('is_in_pips must be a boolean')

        try:
            trailing_step = float(trailing_step)
        except:
            raise TypeError('trailing_step must be a number')

        params = {
                  'trade_id': trade_id,
                  'is_in_pips': is_in_pips,
                  'is_stop': is_stop,
                  'rate': rate,
                  'trailing_step': trailing_step,
                 }

        meth = 'trading/change_trade_stop_limit'
        data = self.__handle_request__(method=meth, params=params,
                                       protocol='post')

    def close_trade(self, trade_id, amount, order_type, time_in_force, rate=0,
                    at_market=0):
        """ Close a given trade

        Arguments:
        ==========

        trade_id: integer,
            the id of the trade.

        amount: integer,
            the trades amount in lots.

        order_type: string,
            the order type, must be 'AtMarket' or 'MarketRange'.

        time_in_force: string,
            the time in force of the order exectution, must be one of
            'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'.
        """

        try:
            trade_id = int(trade_id)
        except:
            raise TypeError('trade_id must be an integer')

        try:
            amount = float(amount)
        except:
            raise TypeError('amount must be a number')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number')

        try:
            at_market = float(at_market)
        except:
            raise TypeError('rate must be a number')

        if order_type not in ['AtMarket', 'MarketRange']:
            msg = "order_type must be 'AtMarket' or 'MarketRange'"
            raise ValueError(msg)

        if time_in_force not in ['IOC', 'GTC', 'FOK', 'DAY', 'GTD']:
            msg = "time_in_force must be in 'IOC', 'GTC', 'FOK', 'DAY', 'GTD'"
            raise ValueError(msg)

        params = {
                  'trade_id': trade_id,
                  'rate': rate,
                  'amount': amount,
                  'at_market': at_market,
                  'order_type': order_type,
                  'time_in_force': time_in_force
                 }

        data = self.__handle_request__(method='trading/close_trade',
                                       params=params, protocol='post')

    def change_order(self, order_id, amount, rate, order_range=0,
                     trailing_step=None):
        """ Change amount, rate, order_range and / or trailling_step of an
        order.

        Arguments:
        ==========

        order_id: int,
            the id of the order to change.

        amount: int,
            the new amount of the order.

        rate: float,
            the new rate of the order.

        order_range: float,
            the new range of the order. Only used for 'RangeEntry' orders,
            for other orders, it is 0 (default).

        trailing_step: float,
            the new trailling step for the order. Defaults to None.

        """

        try:
            order_id = int(order_id)
        except:
            raise TypeError('order_id must be an integer')

        try:
            amount = float(amount)
        except:
            raise TypeError('amount must be a number')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number')

        try:
            order_range = float(order_range)
        except:
            raise TypeError('order_range must be a number')

        if trailing_step is not None:
            try:
                trailing_step = float(trailing_step)
            except:
                raise ValueError('trailing step must be a number')

        params = {
                  'order_id': order_id,
                  'rate': rate,
                  'range': order_range,
                  'amount': amount
                 }
        if trailing_step is not None:
            params['trailing_step'] = trailing_step

        data = self.__handle_request__(method='trading/change_order',
                                       params=params, protocol='post')

    def delete_order(self, order_id):
        """ Delete an order

        Arguments:
        ==========

        order_id: integer,
            the id of the order to delete

        """

        try:
            order_id = int(order_id)
        except:
            raise TypeError('order_id must be an integer')

        params = {
                  'order_id': order_id
                 }

        data = self.__handle_request__(method='trading/delete_order',
                                       params=params, protocol='post')

    def create_entry_order(self, account_id, symbol, is_buy, amount,
                           time_in_force, order_type="Entry",
                           limit=0, is_in_pips=True,
                           rate=0, stop=None, trailing_step=None):
        """ Creates an entry order for a given instrument

        Arguments:
        ==========

        account_id: integer,
            the id of the tradings account.

        symbol: string,
            the symbol of the instrument to trade as given by
            get_instruments().

        is_buy: boolean,
            True if the trade is a buy, False else.

        amount: integer,
            the trades amount in lots.

        order_type: string,
            the order type, must be 'Entry'.

        time_in_force: string,
            the time in force of the order exectution, must be one of
            'GTC', 'DAY' or 'GTD'.

        rate: float (default 0),
            the trades rate.

        is_in_pips: boolean (default True),
            wheter the trades stop/limit rates are in pips.

        limit: float (default 0),
            the trades limit rate.

        stop: float or None (default None),
            the trades stop rate.

        trailing_step: float or None (default None),
            the trailing step for the stop rate.

        Returns:
        ========

        The id of the new order.
        """

        try:
            account_id = int(account_id)
        except:
            raise TypeError('trade_id must be an integer')

        try:
            amount = int(amount)
        except:
            raise TypeError('amount must be an integer')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number')

        try:
            limit = float(limit)
        except:
            raise TypeError('limit must be a number')

        if order_type not in ['Entry']:
            msg = "order_type must be 'Entry'"
            raise ValueError(msg)

        if time_in_force not in ['GTC', 'DAY', 'GTD']:
            msg = "time_in_force must be in 'GTC', 'DAY' or 'GTD'"
            raise ValueError(msg)

        if is_in_pips is True:
            is_in_pips = 'true'
        elif is_in_pips is False:
            is_in_pips = 'false'
        else:
            raise ValueError('is_in_pips must be True or False')

        if is_buy is True:
            is_buy = 'true'
        elif is_buy is False:
            is_buy = 'false'
        else:
            raise ValueError('is_buy must be True or False')

        if stop is not None:
            try:
                stop = float(stop)
            except:
                raise TypeError('stop must be a number')

        if trailing_step is not None:
            try:
                trailing_step = float(trailing_step)
            except:
                raise ValueError('trailing step must be a number')

        params = {
                  'account_id': account_id,
                  'symbol': symbol,
                  'is_buy': is_buy,
                  'rate': rate,
                  'amount': amount,
                  'limit': limit,
                  'order_type': order_type,
                  'is_in_pips': is_in_pips,
                  'time_in_force': time_in_force
                 }

        if stop is not None:
            params['stop'] = stop
        if trailing_step is not None:
            params['trailing_step'] = trailing_step

        self.waiting_for_id = 1
        data = self.__handle_request__(method='trading/create_entry_order',
                                       params=params, protocol='post')
        while self.pending_id is None:
            pass
        self.waiting_for_id = 0
        new_id = self.pending_id
        self.pending_id = None

        return new_id

    def change_order_stop_limit(self, order_id, is_stop, rate, is_in_pips=True,
                                trailing_step=0):
        """ Change an order's stop or limit rate.

        Arguments:
        ==========

        order_id: integer,
            the id of the order to change.

        is_stop: boolean,
            defines wheter the order's limit (False) or the stop rate (True)
            is to be changed.

        rate: float,
            the new stop or limit rate.

        is_in_pips: boolean (Default True),
            wheter the order's stop/limit rates are in pips.

        trailing_step: float (Default 0),
            the trailing step for the stop rate.
        """

        try:
            order_id = int(order_id)
        except:
            raise TypeError('order_id must be an integer')

        if is_stop is True:
            is_stop = 'true'
        elif is_stop is False:
            is_stop = 'false'
        else:
            raise ValueError('is_stop must be a boolean')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number')

        if is_in_pips is True:
            is_in_pips = 'true'
        elif is_in_pips is False:
            is_in_pips = 'false'
        else:
            raise ValueError('is_in_pips must be a boolean')

        try:
            trailing_step = float(trailing_step)
        except:
            raise TypeError('trailing_step must be a number')

        params = {
                  'order_id': order_id,
                  'is_in_pips': is_in_pips,
                  'is_stop': is_stop,
                  'rate': rate,
                  'trailing_step': trailing_step,
                 }

        meth = 'trading/change_order_stop_limit'
        data = self.__handle_request__(method=meth, params=params,
                                       protocol='post')

    def create_oco_order(self, account_id, symbol, is_buy, is_buy2, amount,
                         is_in_pips, time_in_force, at_market, order_type,
                         expiration, limit=0, limit2=0, rate=0, rate2=0,
                         stop=0, stop2=0, trailing_step=0,
                         trailing_step2=0, trailing_stop_step=0,
                         trailing_stop_step2=0):

        """ Creates an entry order for a given instrument

        Arguments:
        ==========

        account_id: integer,
            the id of the trading's account.

        symbol: string,
            the symbol of the instrument to trade as given by
            get_instruments().

        is_buy: boolean,
            True if the first order is a buy, False else.

        is_buy2: boolean,
            True if the second order is a buy, False else.

        amount: integer,
            the trades amount in lots.

        is_in_pips: boolean (default True),
            wheter the order's stop/limit rates are in pips.

        time_in_force: string,
            the time in force of the order exectution, must be one of
            'GTC', 'DAY' or 'GTD'.

        at_market: float (default 0),
            the order's markets range.

        order_type: string,
            the order type, must be 'Entry'.

        expiration: string,
            the order's expiration date.

        limit: float (default 0),
            the first order's limit rate.

        limit2: float (default 0),
            the second order's limit rate.

        rate: float (default 0),
            the first order's rate.

        rate:2 float (default 0),
            the second order's rate.

        stop: float (default 0),
            the first order's stop rate.

        stop2: float (default 0),
            the second orders's stop rate.

        trailing_step: float (default 0),
            the trailing step for the first order.

        trailing_step2: float (default 0),
            the trailing step for the second order.

        trailing_stop_step: float (default 0),
            the trailing step for the first order's stop rate.

        trailing_stop_step: float (default 0),
            the trailing step for the second order's stop rate.

        Returns:
        ========

        The id of the new order.
        """

        try:
            account_id = int(account_id)
        except:
            raise TypeError('trade_id must be an integer')

        if is_buy is True:
            is_buy = 'true'
        elif is_buy is False:
            is_buy = 'false'
        else:
            raise ValueError('is_buy must be a boolean')

        if is_buy2 is True:
            is_buy2 = 'true'
        elif is_buy2 is False:
            is_buy2 = 'false'
        else:
            raise ValueError('is_buy2 must be a boolean')

        try:
            amount = int(amount)
        except:
            raise TypeError('amount must be an integer')

        if is_in_pips is True:
            is_in_pips = 'true'
        elif is_in_pips is False:
            is_in_pips = 'false'
        else:
            raise ValueError('is_in_pips must be a boolean')

        if time_in_force not in ['IOC', 'GTC', 'FOK', 'DAY', 'GTD']:
            msg = "time_in_force must be 'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'"
            raise ValueError(msg)

        try:
            at_market = float(at_market)
        except:
            raise TypeError('at_market must be a number')

        if order_type not in ['AtMarket', 'MarketRange']:
            msg = "order_type must one of 'AtMarket' or 'MarketRange'"
            raise ValueError(msg)

        try:
            limit = float(limit)
        except:
            raise TypeError('limit must be a number')

        try:
            limit2 = float(limit2)
        except:
            raise TypeError('limit2 must be a number')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number')

        try:
            rate2 = float(rate2)
        except:
            raise TypeError('rate2 must be a number')

        try:
            stop = float(stop)
        except:
            raise TypeError('stop must be a number')

        try:
            stop2 = float(stop2)
        except:
            raise TypeError('stop2 must be a number')

        try:
            trailing_step = float(trailing_step)
        except:
            raise ValueError('trailing step must be a number')

        try:
            trailing_step2 = float(trailing_step2)
        except:
            raise ValueError('trailing step must be a number')

        try:
            trailing_stop_step = float(trailing_stop_step)
        except:
            raise ValueError('trailing_stop_step must be a number')

        try:
            trailing_stop_step2 = float(trailing_stop_step2)
        except:
            raise ValueError('trailing_stop_step2 must be a number')

        params = {
                  'account_id': account_id,
                  'symbol': symbol,
                  'amount': amount,
                  'at_market': at_market,
                  'order_type': order_type,
                  'is_in_pips': is_in_pips,
                  'time_in_force': time_in_force,
                  'expiration': expiration,
                  'is_buy': is_buy,
                  'is_buy2': is_buy2,
                  'rate': rate,
                  'rate2': rate2,
                  'stop': stop,
                  'stop2': stop2,
                  'limit': limit,
                  'limit2': limit2,
                  'trailing_step': trailing_step,
                  'trailing_step2': trailing_step2,
                  'trailing_stop_step': trailing_stop_step,
                  'trailing_stop_step2': trailing_stop_step2,
                 }

        self.waiting_for_id = 2
        data = self.__handle_request__(method='trading/simple_oco',
                                       params=params, protocol='post')

        while self.pending_id is None or self.pending_id_2 is None:
            pass
        self.waiting_for_id = 0
        new_id = self.pending_id
        new_id_2 = self.pending_id_2
        self.pending_id = None
        self.pending_id_2 = None

        return (new_id, new_id_2)

    def add_to_oco(self, order_ids, oco_bulk_id=0):
        """ Add orders to OCO Orders.

        Arguments:
        ==========

        order_ids: list of order_ids,
            the id'S of the orders to add to the OCO Order.

        co_bulk_id: integer, default = 0,
            the id of the OCO Order, if 0 a new OCO Order will be created.

        """

        try:
            _ = (int(i) for i in order_ids)
        except:
            raise TypeError('order_ids must be a list of integers')

        try:
            oco_bulk_id = int(oco_bulk_id)
        except:
            raise TypeError('oco_bulk_id must be an integer')

        order_string = ','.join([str(order) for order in order_ids])

        params = {
                  'oderIds': order_string,
                  'ocoBulkId': oco_bulk_id
                 }
        data = self.__handle_request__(method='trading/add_to_oco',
                                       params=params, protocol='post')

    def remove_from_oco(self, order_ids):
        """ Remove orders from OCO Orders.

        Arguments:
        ==========

        order_ids: list of order_ids,
            the id'S of the orders to remove from OCO Orders.

        """
        try:
            _ = (int(i) for i in order_ids)
        except:
            raise TypeError('order_ids must be a list of integers')

        order_string = ','.join([str(order) for order in order_ids])

        params = {
                  'oderIds': order_string
                 }
        data = self.__handle_request__(method='trading/remove_from_oco',
                                       params=params, protocol='post')

    def edit_oco(self, oco_bulk_id, add_order_ids, remove_order_ids):
        """Add or remove orders to or from OCO Orders.
   
        Arguments:
        ==========
        
         co_bulk_id: integer,
            the id of the OCO Order.

        add_order_ids: list of order_ids,
            the id's of the orders to add to OCO Orders.

        remove_order_ids: list of order_ids,
            the id's of the orders to remove from OCO Orders.

        """
        try:
            _ = (int(i) for i in add_order_ids)
        except:
            raise TypeError('add_order_ids must be a list of integers')

        try:
            _ = (int(i) for i in remove_order_ids)
        except:
            raise TypeError('remove_order_ids must be a list of integers')

        add_order_string =  ','.join([str(order) for order in add_order_ids])
        remove_order_string =  ','.join([str(order) 
                                        for order in remove_order_ids])

        params = {
                  'ocoBulkId': oco_bulk_id,
                  'addOrderIds': add_order_string,
                  'removeOrderIds': remove_order_string
                 }
        data = self.__handle_request__(method='trading/edit_oco',
                                       params=params, protocol='post')

    def get_candles(self, offer_id, period, number='', start=None, stop=None):
        if offer_id == '':
            self.logger.error('Error in get_candles: No offer_id given!')
            raise ValueError('Please provide a offer_id')
        if period not in self.PERIODS:
            self.logger.error('Error in get_candles: Illegal period: %s'
                              % period)
            raise ValueError('period must be one of %s' % self.PERIODS)
        if number != '' and (type(number) != int or number > 10000):
            self.logger.error('Error in get_candles: Illegal param. number: %s'
                              % number)
            raise ValueError('number must be a integer smaller than 10001')

        params = {
                  'num': number,
                 }

        if start:
            if isinstance(start, dt.datetime) or isinstance(start, dt.date):
                start = ((start - dt.datetime(1970, 1, 1)) /
                         dt.timedelta(seconds=1))
            try:
                start = int(start)
            except:
                self.logger.error('Error in get_candles:')
                self.logger.error('Illegal value for start: %s' % start)
                raise ValueError('start must be an integer')
            params['From'] = start

        if stop:
            if isinstance(stop, dt.datetime) or isinstance(stop, dt.date):
                stop = ((stop - dt.datetime(1970, 1, 1)) /
                        dt.timedelta(seconds=1))
            try:
                stop = int(stop)
            except:
                self.logger.error('Error in get_candles:')
                self.logger.error('Illegal value for stop: %s' % stop)
                raise ValueError('stop must be an integer')
            params['To'] = stop

        data = self.__handle_request__(method='candles/%s/%s'
                                       % (offer_id, period), params=params)

        if 'candles' in data:
            ret = pd.DataFrame(data['candles'], columns=self.CANDLES_COLUMNS)
            ret['date'] = pd.to_datetime(ret['date'], unit='s')
            ret.set_index('date')
        else:
            ret = pd.DataFrame(columns=self.CANDLES_COLUMNS)
            ret.set_index('date')
        return ret

    def __collect_account_ids__(self):
        """ Collect account ids and stores them in self.account_ids"""

        data = self.get_accounts('list')
        for acc in data:
            if 'accountId' in acc and acc['accountId'] != '':
                self.account_ids.add(int(acc['accountId']))

    def __collect_orders__(self):
        """ Collect available orders and stores them in self.orders"""

        data = self.get_orders('list')
        for order in data:
            if 'orderId' in order and order['orderId'] != '':
                self.orders[int(order['orderId'])] = order

    def __collect_order_ids__(self):
        """ Collect available order ids and stores them in self.order_ids"""

        order_ids = set()
        data = self.get_orders('list')
        for order in data:
            if 'orderId' in order and order['orderId'] != '':
                order_ids.add(int(order['orderId']))
        return order_ids

    def __connect__(self):
        try:
            self.socket = SocketIO(self.trading_url, self.port,
                                   params={'access_token': self.access_token})
            self.socket_id = self.socket._engineIO_session.id
        except:
            self.logger.error('Can not connect to FXCM server')
        else:
            self.logger.info('Connection established')

        # self.socket.on('message', self.__on_message__)
        # self.socket.on('error', self.__on_error__)
        time.sleep(2)
        self.socket.wait()

    def __request_access_token__(self):
        """ Requests access token from FXCM server"""

        params = {
            'client_id': 'Titan',
            'client_secret': 'qqq',
            'grant_type': 'password',
            'username': self.user,
            'password': self.password
        }

        req = requests.post(self.auth_url+'/oauth/token', data=params)

        if req.status_code != 200:
            self.logger.error('FXCM reject request for temporay access token')
            self.logger.error('with status %s and message %s'
                              % (req.status_code, req.text))
            raise ServerError('Access denied')

        try:
            data = req.json()
        except:
            self.logger.error('Can not parse server answer to json object: %s'
                              % req.text)

        if 'access_token' in data:
            temp_token = data['access_token']
            self.logger.info('Received temporary token %s' % temp_token)
        else:
            self.logger.error('Did not received temporary token')
            raise ServerError('Server does not deliver temporary token')

        # Step 2

        auth2_params = {
            'client_id': 'TRADING',
            'access_token': temp_token
        }

        req = requests.post(self.trading_url+'/authenticate',
                            data=auth2_params)
        if req.status_code != 200:
            self.logger.error('FXCM reject request for temporay access token')
            self.logger.error('with status %s and message %s'
                              % (req.status_code, req.text))
            raise ServerError('Request returns status code %s'
                              % req.status_code)

        try:
            data = req.json()
        except:
            self.logger.error('Can not parse server answer to json object: %s'
                              % req.text)

        if 'response' not in data or 'executed' not in data['response']:
            self.logger.error('Malformed response %s' % data)
            raise ServerError('Malformed response')

        if not data['response']['executed']:
            if 'error' in data['response'] and data['response']['error'] != '':
                self.logger.error('Server reports an error: %s'
                                  % data['response']['error'])
                raise ServerError('FXCM Server reports an error: %s'
                                  % data['response']['error'])
            else:
                self.logger.error('FXCM Server reports an unknown error: %s'
                                  % data['response'])
                raise ServerError('FXCM Server returns an unknown error')

        if 'access_token' not in data:
            self.logger.error('Can not find access token in server answer: %s'
                              % data)
            raise ServerError('No access token in server answer')
        else:
            self.access_token = data['access_token']

        self.logger.info('Received access token')

    def __handle_request__(self, method='', params={}, protocol='get'):
        """ Sends server requests. """

        if method == '':
            self.logger.error('Error in __handle__requests__: No method given')
            raise ValueError('No method given')
        if type(params) is not dict:
            self.logger.debug('Error in __handle__requests__:')
            self.logger.debig('params must be of type dict')
            raise TypeError('params must be of type dict')

        if not self.is_connected():
            self.logger.warn('Not connected, try to reconnect')
            self.connect()

        params['socket_id'] = self.socket_id
        params['access_token'] = self.access_token

        self.logger.debug('Sending request to %s/%s, paramerter: %s'
                          % (self.trading_url, method, params))
        if protocol == 'post':
            req = requests.post('%s/%s' % (self.trading_url, method),
                                data=params)
        else:
            req = requests.get('%s/%s' % (self.trading_url, method),
                               params=params)
        if req.status_code != 200:
            self.logger.error('FXCM reject req %s with status %s and msg %s'
                              % (method, req.status_code, req.text))

            raise ServerError('Request returns status code %s and message "%s"'
                              % (req.status_code,
                                 unquote(req.text)))

        try:
            data = req.json()
        except:
            self.logger.error('Can not parse server answer to json object: %s'
                              % req.text)

        if 'response' not in data or 'executed' not in data['response']:
            self.logger.error('Malformed response %s' % data)
            raise ServerError('Malformed response')

        if not data['response']['executed']:
            if 'error' in data['response'] and data['response']['error'] != '':
                self.logger.error('Server reports an error: %s'
                                  % data['response']['error'])
                raise ServerError('FXCM Server reports an error: %s'
                                  % data['response']['error'])
            else:
                self.logger.error('FXCM Server reports an unknown error: %s'
                                  % data['response'])
                raise ServerError('FXCM Server returns an unknown error')

        self.logger.debug('Server answer: %s' % data)
        return data

    # To check
    def __on_price_update__(self, msg):
        data = json.loads(msg)

        symbol = data['Symbol']
        date = pd.to_datetime(int(data['Updated']), unit='s')
        temp_data = pd.DataFrame([data['Rates']],
                                 columns=['Bid', 'High', 'Low', 'Close'],
                                 index=[date])
        if symbol not in self.prices:
            self.prices[symbol] = temp_data
        else:
            self.prices[symbol] = pd.concat([self.prices[symbol], temp_data])

        if symbol in self.add_callbacks:
            callbacks = self.add_callbacks[symbol]
            for func in callbacks:
                try:
                    callbacks[func](data, self.prices[symbol])
                except:
                    print('Call of %s raised an error:' % func)
                    print(sys.exc_info()[0])

    def __on_model_update__(self, msg):
        # Answers not allways json objects, so we have to log the plain answer
        # data = json.loads(msg)
        print("Update: "+msg)
        self.logger.debug(msg)

    def __on_message__(self, msg):
        # Answers not allways json objects, so we have to log the plain answer
        print('On standart message:')
        try:
            data = json.loads(msg)
            print(data)
        except:
            print(msg)
        self.logger.debug(msg)

    def __on_order_update__(self, msg):
        """ Gets called when the market_data stream sends new data for the order
        table

        Arguments:
        ==========

        msg: string,
            a json like data object.
        """

        try:
            data = json.loads(msg)
        except:
            print('Got a non json answer:')
            print(msg)
        if 'action' in data and data['action'] == 'I':
            self.logger.info('Got a insert event for orders: %s' % data)
            order_id = int(data['orderId'])
            doubble_insert = order_id in self.orders
            self.orders[order_id] = data
            if self.waiting_for_id > 0 and doubble_insert is False:
                if self.pending_id is None:
                    self.pending_id = order_id
                elif self.waiting_for_id > 1:
                    self.pending_id_2 = order_id
        elif 'action' in data and data['action'] == 'D':
            self.logger.info('Got a delete event for orders: %s' % data)
            order_id = int(data['orderId'])
            if order_id in self.orders:
                del self.orders[order_id]
        elif ('action' in data and
              data['action'] != 'I' and data['action'] != 'D'):
            msg = 'Found an unknown action in Order stream: %s' % data
            self.logger.error(msg)
        else:
            if 'orderId' in data:
                for field in data:
                    value = data[field]
                    self.orders[int(data['orderId'])][field] = value

    def __on_error__(self, msg):
        print('Error: %s' % msg)

    def __get_config_value__(self, section, key):
        config = configparser.ConfigParser()
        try:
            config.read(self.config_file)
        except:
            if self.logger:
                self.logger.error('Can not open config file, no such file: %s'
                                  % self.config_file)
            raise IOError('Can not open config file, no such file: %s'
                          % self.config_file)

        if section not in config.sections():
            if self.logger:
                self.logger.error('Can not find section %s in %s'
                                  % (section, self.config_file))
            raise ValueError('Can not find section %s in %s'
                             % (section, self.config_file))

        if key not in config[section]:
            if self.logger:
                self.logger.error('Can not find key %s in section %s of %s'
                                  % (key, section, self.config_file))
            raise ValueError('Can not find key %s in section %s of %s'
                             % (key, section, self.config_file))
        if self.logger:
            self.logger.debug('Found config value %s for key %s in section %s'
                              % (config[section][key], key, section))
        return config[section][key]
