#
# fxcmpy -- A Python Wrapper Class for the
# RESTful API as provided by FXCM Forex Capital Markets Ltd.
#
# Proof-of-Concept | Prototype Version for Illustration
# by The Python Quants GmbH
#
# The codes contained herein come without warranties or representations,
# to the extent permitted by applicable law.
#
# Read the RISK DISCLAIMER carefully.
#
# (c) FXCM Forex Capital Markets Ltd.
#

import requests
from socketIO_client import SocketIO
from socketIO_client.exceptions import ConnectionError
from threading import Thread
import json
import pandas as pd
import sys
import time
import datetime as dt
import configparser
import logging
import os

from fxcmpy.fxcmpy_closed_position import fxcmpy_closed_position
from fxcmpy.fxcmpy_open_position import fxcmpy_open_position
from fxcmpy.fxcmpy_oco_order import fxcmpy_oco_order
from fxcmpy.fxcmpy_order import fxcmpy_order

from urllib.parse import unquote


MISSING_ACCESS_TOKEN = "Cannot find access token. Please provide \
the token either as parameter in the class constructor or within a \
a configuration file and provide the file's path as parameter in the \
class constructor."

LOG_LEVELS = {'error': 40, 'warn': 30, 'info': 20, 'debug': 10}


class ServerError(Exception):
    pass


class fxcmpy(object):
    """ A wrapper class for the FXCM API. """

    # Class attributes

    #auth_url = 'https://www-beta2.fxcorporate.com'
    #trading_url = 'https://api-demo.fxcm.com'
    #port = 443
    models = ['Offer', 'Account', 'Order', 'OpenPosition', 'ClosedPosition',
              'Summary', 'Properties', 'LeverageProfile']
    PERIODS = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8',
               'D1', 'W1', 'M1']
    CANDLES_COLUMNS = ['date', 'bidopen', 'bidclose', 'bidhigh', 'bidlow',
                       'askopen', 'askclose', 'askhigh', 'asklow', 'tickqty']
    CANDLES_COLUMNS_ASK = ['date', 'askopen', 'askclose', 'askhigh', 'asklow']
    CANDLES_COLUMNS_BID = ['date', 'bidopen', 'bidclose', 'bidhigh', 'bidlow']

    debug = False

    def __init__(self, access_token='', config_file='',
                 log_file=None, log_level='', server='demo'):
        """ Constructor.

        Arguments:

        access_token: string (default: ''),
            an access token for your FXCM account. To create an access token
            visit https://tradingstation.fxcm.com/
        config_file: string (default: ''),
            path of an optional configuration file, fxcm tries to read all
            other parameter which are not given from that file. The file must
            be readable by configparser.
        log_file: string (default: ''),
            path of an optional log file. If not given (and not found in the
            optional configuration file), log messages are printed to stdout.
        log_level: string (default: ''),
            the log level. Must be one of 'error', 'warn', 'info' or 'debug'.
            If not given (and not found in the optional configuration file),
            'warn' is used.
        server: one of 'demo' or 'real' (default: 'demo'),
            wheter to use the fxcm demo or real trading server.
        """

        self.logger = None
        self.config_file = ''
        if server == 'demo':
            #self.auth_url = 'https://www-beta2.fxcorporate.com'
            self.trading_url = 'https://api-demo.fxcm.com'
            self.port = 443
        elif server == 'real':
            #self.auth_url = 'https://www-beta2.fxcorporate.com'
            self.trading_url = 'https://api.fxcm.com'
            self.port = 443


        if access_token != '':
            self.access_token = access_token
        elif config_file != '':
            if os.path.isfile(config_file):
                self.config_file = config_file
            else:
                raise IOError('Can not find configuration file: %s.'
                              % config_file)
            try:
                self.access_token = self.__get_config_value__('FXCM',
                                                              'access_token')
            except:
                msg = 'Can not find access token in configuration file %s.'
                raise ValueError(msg % self.config_file)
        else:
            raise ValueError(MISSING_ACCESS_TOKEN)

        if log_level != '':
            if log_level in LOG_LEVELS:
                log_level = LOG_LEVELS[log_level]
            else:
                raise ValueError('log_level must be one of %s.'
                                 % LOG_LEVELS.keys())
        elif self.config_file != '':
            try:
                log_level = LOG_LEVELS[
                             self.__get_config_value__('FXCM', 'log_level')]
            except:
                log_level = LOG_LEVELS['warn']
        else:
            log_level = LOG_LEVELS['warn']

        if log_file is not None:
            log_path = log_file
        elif self.config_file != '':
            try:
                log_path = self.__get_config_value__('FXCM', 'log_file')
            except:
                log_path = ''
        else:
            log_path = ''

        if log_path == '':
            form = '|%(levelname)s|%(asctime)s|%(message)s'
            logging.basicConfig(level=log_level, format=form)
        else:
            form = '|%(levelname)s|%(asctime)s|%(message)s'
            logging.basicConfig(filename=log_path, level=log_level,
                                format=form)

        self.logger = logging.getLogger('FXCM')
        self.socket = None
        self.request_header = None
        self.default_account = None
        self.instruments = None
        self.prices = dict()
        self.account_ids = set()
        self.orders = dict()
        self.old_orders = dict()
        self.offers = dict()
        self.open_pos = dict()
        self.closed_pos = dict()
        self.oco_orders = dict()
        self.add_callbacks = dict()
        self.connection_status = 'unset'
        self.connect()

        count = 0
        while self.connection_status == 'pending' and count < 100:
            count += 1
            time.sleep(0.1)

        if self.connection_status == 'pending' and count == 100:
            raise ServerError('Can not find FXCM Server.')
        elif self.connection_status == 'aborted':
            raise ServerError('Can not connect to FXCM Server.')

        time.sleep(5)
        self.__collect_account_ids__()
        self.default_account = self.account_ids[0]
        msg = 'Default account set to %s, to change use set_default_account().'
        self.logger.warn(msg % self.default_account)
        self.__collect_orders__()
        self.__collect_oco_orders__()
        self.__collect_offers__()
        self.__collect_positions__()
        self.instruments = self.get_instruments()
        self.subscribe_data_model('Order')
        self.subscribe_data_model('OpenPosition')
        self.subscribe_data_model('ClosedPosition')

    def close(self):
        if self.is_connected():
            self.socket.disconnect()

    def connect(self):
        """ Connect to the FXCM server."""
        self.connection_status = 'pending'
        self.logger.info('Connecting FXCM Server')

        self.socket_thread = Thread(target=self.__connect__)
        self.socket_thread.start()

    def is_connected(self):
        """ Return True if socket connection is established and False else."""

        if (self.socket is not None and self.socket.connected and
                self.socket_thread.is_alive()):
            return True
        else:
            return False

    def get_default_account(self):
        """ Return the default account id."""
        return self.default_account

    def set_default_account(self, account_id):
        """" Set the default account id to account_id."""
        if account_id not in self.account_ids:
            raise ValueError("Unknown account id")
        else:
            self.default_account = account_id

    def get_instruments(self):
        """ Return the tradeable instruments of FXCM as a list."""

        self.logger.debug('Fetching available instruments')

        data = self.__handle_request__(method='trading/get_instruments')

        if 'data' in data and 'instrument' in data['data']:
            instruments = [ins['symbol'] for ins in data['data']['instrument']]
        else:
            instruments = list()

        return instruments

    def get_model(self, models=list(), summary=False):
        """ Return a snapshot of the the specified model(s).

        Arguments:

        models: list,
            list of the required models, entries must be out of
            ['Offer', 'Account', 'Order', 'OpenPosition', 'ClosedPosition',
             'Summary', 'Properties', 'LeverageProfile'].

        Returns:

        The current data of the specified model(s) in a json like manner.

        """

        if len(models) == 0:
            raise ValueError('Please specify one or more models')
        for model in models:
            if model not in self.models:
                raise ValueError('Models have to be of %s' % self.models)

        data = self.__handle_request__(method='trading/get_model',
                                       params={'models': list(models)})

        total = dict()
        for table in data:
            total[table] = list()
            for dataset in data[table]:
                if 'isTotal' in dataset and dataset['isTotal'] is True:
                    total[table].append(dataset)
                    data[table].remove(dataset)
        if summary:
            return total
        else:
            return data

    def get_open_positions(self, kind='dataframe'):
        """ Return a snapshot of the 'Open Position' model.

        Arguments:

        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a pandas DataFrame.

        Returns:

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

        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a pandas DataFrame.

        Returns:

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

        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a pandas DataFrame.

        Returns:

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

        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a pandas DataFrame.

        Returns:

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

        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a pandas DataFrame.

        Returns:

        The current data of the 'Summary' model.

        """
        data = self.get_model(('Summary',))
        summary = data['summary']
        if kind == 'list':
            return summary
        else:
            return pd.DataFrame(summary)

    def get_open_positions_summary(self, kind='dataframe'):
        """ Return a summary of the 'Open Position' model.

        Arguments:

        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a pandas DataFrame.

        Returns:

        The summary of the current data of the 'Open Position' model.

        """
        data = self.get_model(('OpenPosition',), summary=True)
        open_pos = data['open_positions']
        if kind == 'list':
            return open_pos
        else:
            return pd.DataFrame(open_pos)

    def get_closed_positions_summary(self, kind='dataframe'):
        """ Return a summary of the 'Closed Position' model.

        Arguments:

        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a pandas DataFrame.

        Returns:

        The summary of the current data of the 'Closed Position' model.

        """
        data = self.get_model(('ClosedPosition',), summary=True)
        closed_pos = data['closed_positions']
        if kind == 'list':
            return closed_pos
        else:
            return pd.DataFrame(closed_pos)

    def get_accounts(self, kind='dataframe'):
        """ Return a snapshot of the 'Account' model.

        Arguments:

        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a pandas DataFrame.

        Returns:

        The current data of the 'Account' model.

        """
        data = self.get_model(('Account',))
        accounts = data['accounts']
        if kind == 'list':
            return accounts
        else:
            return pd.DataFrame(accounts)

    def get_accounts_summary(self, kind='dataframe'):
        """ Return a summary of the 'Account' model.

        Arguments:

        kind: one of 'dataframe' (default) or 'list',
            how to return the data, either as list or as a pandas DataFrame.

        Returns:

        The summary of the current data of the 'Account' model.

        """
        data = self.get_model(('Account',), summary=True)
        accounts = data['accounts']
        if kind == 'list':
            return accounts
        else:
            return pd.DataFrame(accounts)

    def get_account_ids(self):
        """ Return a list of available account ids."""

        return self.account_ids

    def get_order_ids(self):
        """ Return a list of available order ids."""

        return list(self.orders.keys())

    def get_open_trade_ids(self):
        """ Return a list of all available trade ids of open positions."""

        return list(self.open_pos.keys())

    def get_closed_trade_ids(self):
        """ Return a list of all available trade ids of closed positions."""

        return list(self.closed_pos.keys())

    def get_all_trade_ids(self):
        """Returns a list of all available trade ids."""

        ids = set(self.get_open_trade_ids())
        ids = ids.union(set(self.get_closed_trade_ids()))
        ids = list(ids)
        ids.sort()

        return ids

    def get_open_position(self, position_id):
        """ Return the open position with given id.

        Arguments:

        position_id: (integer),
            the id of the position.

        Returns:

        The fxcmpy_open_position object.
        """
        try:
            position_id = int(position_id)
        except:
            self.logger.error('position id must be an integer.')
            raise TypeError('position id must be an integer.')

        if position_id in self.open_pos:
            return self.open_pos[position_id]
        else:
            self.logger.warn('No open position with id %s.' % position_id)
            raise ValueError('No open position with id %s.' % position_id)

    def get_closed_position(self, position_id):
        """ Return the closed position with given id.

        Arguments:

        position_id: (integer),
            the id of the position.

        Returns:

        The fxcmpy_open_position object.
        """
        try:
            position_id = int(position_id)
        except:
            self.logger.error('position id must be an integer.')
            raise TypeError('position id must be an integer.')

        if position_id in self.closed_pos:
            return self.closed_pos[position_id]
        else:
            self.logger.warn('No closed position with given id %s.'
                             % position_id)
            raise ValueError('No closed position with given id %s.'
                             % position_id)

    def get_order(self, order_id):
        """ Returns the order object for a given order id.

        Arguments:

        order_id: (integer),
            the id of the order.

        Returns:

        The fxcmpy_order object.
        """

        if order_id in self.orders:
            return self.orders[order_id]
        elif order_id in self.old_orders:
            return self.old_orders[order_id]
        else:
            raise ValueError('No order with id %s' % order_id)

    def get_oco_order_ids(self):
        """ Return a list of the available oco order ids."""

        return list(self.oco_orders.keys())

    def get_oco_order(self, order_id):
        """ Returns the oco order object for a given order id.

        Arguments:

        order_id: (integer),
            the id of the oco order.

        Returns:

        The fxcmpy_oco_order_object.
        """

        if order_id not in self.oco_orders:
            raise ValueError('No oco order with id %s' % order_id)
        else:
            return self.oco_orders[order_id]

    def get_prices(self, symbol):
        """ Return the prices of a given subscribed instrument.

        Arguments:

        symbol: string,
            the symbol of the instrument as given by get_instruments().

        """

        if symbol in self.prices:
            return self.prices[symbol]
        else:
            return pd.DataFrame(columns=['Bid', 'Ask', 'High', 'Low'])

    def get_last_price(self, symbol):
        """ Return the last prices of a given subscribed instrument.

        Arguments:

        symbol: string,
            the symbol of the instrument as given by get_instruments().

        """

        if symbol in self.prices:
            return self.prices[symbol].iloc[-1]
        else:
            raise ValueError('Symbol %s is not subscripted' % symbol)

    def get_subscribed_symbols(self):
        """ Returns a list of symbols for the subscribed instruments."""

        return list(self.prices.keys())

    def is_subscribed(self, symbol):
        """ Returns True if the instrument is subscribed and False else.

        Arguments:

        symbol:  string,
            the symbol of the instrument in question as given by
            get_instruments().

        """

        return symbol in self.prices

    def subscribe_market_data(self, symbol='', add_callbacks=()):
        """ Stream the prices of an instrument.

        Arguments:

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
            raise ValueError('No symbol given.')

        self.logger.info('Try to subscribe for %s.' % symbol)

        for func in add_callbacks:
            if not callable(func):
                self.logger.error('Callback method is not callable.')
                raise ValueError('Content of add_callbacks is not callable.')
            else:
                if symbol not in self.add_callbacks:
                    self.add_callbacks[symbol] = dict()
                self.logger.info('Adding callback method %s for symbol %s.'
                                 % (func.__name__, symbol))
                self.add_callbacks[symbol][func.__name__] = func

        params = {'pairs': symbol}
        self.__handle_request__(method='subscribe', params=params,
                                       protocol='post')
        self.socket.on(symbol, self.__on_price_update__)

    def subscribe_data_model(self, model='', add_callbacks=()):
        """ Stream data of a model.

        Arguments:

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
            raise ValueError('No model given.')

        if model not in ['Offer', 'Account', 'Order', 'OpenPosition',
                         'ClosedPosition', 'Summary']:
            msg = "model must on of 'Offer', 'Account', 'Order',"
            msg += "'OpenPosition', 'ClosedPosition' or 'Summary'"
            raise ValueError(msg)

        self.logger.info('Try to subscribe for %s.' % model)

        for func in add_callbacks:
            if not callable(func):
                self.logger.error('Callback method is not callable.')
                raise ValueError('Content of add_callbacks must be callable.')
            else:
                if model not in self.add_callbacks:
                    self.add_callbacks[model] = dict()
                self.logger.info('Adding callback method %s for model %s.'
                                 % (func.__name__, model))
                self.add_callbacks[model][func.__name__] = func

        params = {'models': model}
        self.__handle_request__(method='trading/subscribe',
                                       params=params, protocol='post')
        if model == 'Order':
            self.socket.on('Order', self.__on_order_update__)
        elif model == 'OpenPosition':
            self.socket.on('OpenPosition', self.__on_open_pos_update__)
        elif model == 'ClosedPosition':
            self.socket.on('ClosedPosition', self.__on_closed_pos_update__)

        else:
            self.socket.on(model, self.__on_model_update__)

    def unsubscribe_market_data(self, symbol=''):
        """ Unsubscribe for instrument prices of the given symbol."""

        if symbol == '':
            raise ValueError('No symbol given.')

        self.logger.info('Try to unsubscribe for %s.' % symbol)

        params = {'pairs': symbol}
        self.__handle_request__(method='unsubscribe', params=params,
                                       protocol='post')

        if symbol in self.prices:
            del self.prices[symbol]
        if symbol in self.add_callbacks:
            del self.add_callbacks[symbol]

    def unsubscribe_data_model(self, model=''):
        """ Unsubscribe for the given model.

        Arguments:

        model: string,
            the model, must be one of ['Offer', 'Account', 'Order',
            'OpenPosition', 'ClosedPosition', 'Summary', 'Properties',
            'LeverageProfile'].

        """

        if model == '':
            raise ValueError('No symbol given.')

        self.logger.info('Try to unsubscribe for %s.' % model)
        if model not in ['Order', 'OpenPosition', 'ClosedPosition']:
            params = {'models': model}
            self.__handle_request__(method='trading/unsubscribe',
                                           params=params, protocol='post')
        else:
            msg = 'Model %s is used by intern routines, cancel unsubscibtion, '
            msg += 'only remove custom callbacks.'
            self.logger.warn(msg % model)

        if model in self.add_callbacks:
            del self.add_callbacks[model]

    def close_all_for_symbol(self, symbol, order_type='AtMarket',
                             time_in_force='GTC', account_id=None):
        """ Close all positions for a given symbol.

        Arguments:

        account_id: string,
            the order's account id.

        symbol: string,
            the trades symbol as given by get_instruments.

        order_type: string (default: 'AtMarket'),
            the type of order execution, one of 'AtMarket' or 'MarketRange'.

        time_in_force: string (default: 'GTC'),
            the time in force of the order execution, must be one of
            'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'.

        account_id: integer (Default None),
            the order's account id. If not given, the default account is used.

        """

        if account_id is None:
            account_id = self.default_account
        else:
            try:
                account_id = int(account_id)
            except:
                raise TypeError('account_id must be an integer.')
        if account_id not in self.account_ids:
            raise ValueError('Unknown account id %s.' % account_id)

        if order_type not in ['AtMarket', 'MarketRange']:
            msg = "order_type must be 'AtMarket' or 'MarketRange'."
            raise ValueError(msg)

        if time_in_force not in ['IOC', 'GTC', 'FOK', 'DAY', 'GTD']:
            msg = "time_in_force must be in 'IOC', 'GTC', 'FOK', 'DAY', 'GTD'"
            raise ValueError(msg)

        params = {
                  'account_id': account_id,
                  'forSymbol': 'true',
                  'symbol': symbol,
                  'order_type': order_type,
                  'time_in_force': time_in_force
                 }

        self.__handle_request__(method='trading/close_all_for_symbol',
                                       params=params, protocol='post')

    def close_all(self, order_type='AtMarket', time_in_force='GTC',
                  account_id=None):
        """ Close all positions.

        Arguments:

        account_id: string,
            the order's account id.

        order_type: string (default: 'AtMarket'),
            the type of order execution, one of 'AtMarket' or 'MarketRange'.

        time_in_force: string (default: 'GTC'),
            the time in force of the order execution, must be one of
            'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'.

        account_id: integer (Default None),
            the order's account id. If not given, the default account is used.

        """

        if account_id is None:
            account_id = self.default_account
        else:
            try:
                account_id = int(account_id)
            except:
                raise TypeError('account_id must be an integer.')
        if account_id not in self.account_ids:
            raise ValueError('Unknown account id %s.' % account_id)

        if order_type not in ['AtMarket', 'MarketRange']:
            msg = "order_type must be 'AtMarket' or 'MarketRange'."
            raise ValueError(msg)

        if time_in_force not in ['IOC', 'GTC', 'FOK', 'DAY', 'GTD']:
            msg = "time_in_force must be in 'IOC', 'GTC', 'FOK', 'DAY', 'GTD'"
            raise ValueError(msg)

        params = {
                  'account_id': account_id,
                  'forSymbol': 'false',
                  'symbol': '',
                  'order_type': order_type,
                  'time_in_force': time_in_force
                 }

        self.__handle_request__(method='trading/close_all_for_symbol',
                                       params=params, protocol='post')

    def open_trade(self, symbol, is_buy,
                   amount, time_in_force, order_type, rate=0,
                   is_in_pips=True, limit=None, at_market=0, stop=None,
                   trailing_step=None, account_id=None):
        """ Opens a trade for a given instrument.

        Arguments:

        account_id: integer,
            the id of the trading account.

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
            the time in force of the order execution, must be one of
            'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'.

        rate: float (default 0),
            the trades rate.

        is_in_pips: boolean (default True),
            whether the trades stop/limit rates are in pips.

        limit: float (default 0),
            the trades limit rate.

        at_market: float (default 0),
            the markets range.

        stop: float or None (default None),
            the trades stop rate.

        trailing_step: float or None (default None),
            the trailing step for the stop rate.

        account_id: integer (Default None),
            the trade's account id. If not given, the default account is used.

        """

        if account_id is None:
            account_id = self.default_account
        else:
            try:
                account_id = int(account_id)
            except:
                raise TypeError('account_id must be an integer.')
        if account_id not in self.account_ids:
            raise ValueError('Unknown account id %s.' % account_id)

        try:
            amount = int(amount)
        except:
            raise TypeError('amount must be an integer.')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number.')

        if limit is not None:
            try:
                limit = float(limit)
            except:
                raise TypeError('limit must be a number.')

        try:
            at_market = float(at_market)
        except:
            raise TypeError('at_market must be a number.')

        if order_type not in ['AtMarket', 'MarketRange']:
            msg = "order_type must be 'AtMarket' or 'MarketRange'."
            raise ValueError(msg)

        if time_in_force not in ['IOC', 'GTC', 'FOK', 'DAY', 'GTD']:
            msg = "time_in_force must be in 'IOC', 'GTC', 'FOK', 'DAY', 'GTD'"
            raise ValueError(msg)

        if is_in_pips is True:
            is_in_pips = 'true'
        elif is_in_pips is False:
            is_in_pips = 'false'
        else:
            raise ValueError('is_in_pips must be True or False.')

        if is_buy is True:
            is_buy = 'true'
        elif is_buy is False:
            is_buy = 'false'
        else:
            raise ValueError('is_buy must be True or False.')

        if stop is not None:
            try:
                stop = float(stop)
            except:
                raise TypeError('stop must be a number.')

        if trailing_step is not None:
            try:
                trailing_step = float(trailing_step)
            except:
                raise ValueError('trailing step must be a number.')

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

        if limit is not None:
            params['limit'] = limit
        if stop is not None:
            params['stop'] = stop
        if trailing_step is not None:
            params['trailing_step'] = trailing_step

        data = self.__handle_request__(method='trading/open_trade',
                                       params=params, protocol='post')
        if 'data' in data and 'orderId' in data['data']:
            order_id = int(data['data']['orderId'])
        else:
            self.logger.warn('Missing orderId in servers answer.')
            return 0

        try:
            order = self.get_order(order_id)
        except:
            time.sleep(1)
            order = self.get_order(order_id)

        return order

    def change_trade_stop_limit(self, trade_id, is_stop, rate, is_in_pips=True,
                                trailing_step=0):
        """ Change an trade's stop or limit rate.

        Arguments:

        trade_id: integer,
            the id of the trade to change.

        is_stop: boolean,
            defines whether the trade's limit (False) or the stop rate (True)
            is to be changed.

        rate: float,
            the new stop or limit rate.

        is_in_pips: boolean (Default True),
            whether the trade's stop/limit rates are in pips.

        trailing_step: float (Default 0),
            the trailing step for the stop rate.
        """

        try:
            trade_id = int(trade_id)
        except:
            raise TypeError('trade_id must be an integer.')

        if is_stop is True:
            is_stop = 'true'
        elif is_stop is False:
            is_stop = 'false'
        else:
            raise ValueError('is_stop must be a boolean.')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number.')

        if is_in_pips is True:
            is_in_pips = 'true'
        elif is_in_pips is False:
            is_in_pips = 'false'
        else:
            raise ValueError('is_in_pips must be a boolean.')

        try:
            trailing_step = float(trailing_step)
        except:
            raise TypeError('trailing_step must be a number.')

        params = {
                  'trade_id': trade_id,
                  'is_in_pips': is_in_pips,
                  'is_stop': is_stop,
                  'rate': rate,
                  'trailing_step': trailing_step,
                 }

        meth = 'trading/change_trade_stop_limit'
        self.__handle_request__(method=meth, params=params,
                                protocol='post')

    def close_trade(self, trade_id, amount, order_type='AtMarket',
                    time_in_force='IOC', rate=0, at_market=0):
        """ Close a given trade.

        Arguments:

        trade_id: integer,
            the id of the trade.

        amount: integer (default 0),
            the trades amount in lots.

        order_type: string (default 'AtMarket'),
            the order type, must be 'AtMarket' or 'MarketRange'.

        time_in_force: string (default 'IOC'),
            the time in force of the order execution, must be one of
            'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'.

        rate: float (default 0),
            the trades rate.

        at_market: float (default 0),
            the markets range.
        """

        try:
            trade_id = int(trade_id)
        except:
            raise TypeError('trade_id must be an integer.')

        try:
            amount = float(amount)
        except:
            raise TypeError('amount must be a number.')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number.')

        try:
            at_market = float(at_market)
        except:
            raise TypeError('at_market must be a number.')

        if order_type not in ['AtMarket', 'MarketRange']:
            msg = "order_type must be 'AtMarket' or 'MarketRange'."
            raise ValueError(msg)

        if time_in_force not in ['IOC', 'GTC', 'FOK', 'DAY', 'GTD']:
            msg = "time_in_force must be in 'IOC', 'GTC', 'FOK', 'DAY', 'GTD'."
            raise ValueError(msg)

        params = {
                  'trade_id': trade_id,
                  'rate': rate,
                  'amount': amount,
                  'at_market': at_market,
                  'order_type': order_type,
                  'time_in_force': time_in_force
                 }

        self.__handle_request__(method='trading/close_trade',
                                       params=params, protocol='post')

    def change_order(self, order_id, amount, rate, order_range=0,
                     trailing_step=None):
        """ Change amount, rate, order_range and / or trailling_step of an
        order.

        Arguments:

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
            the new trailing step for the order. Defaults to None.

        """

        try:
            order_id = int(order_id)
        except:
            raise TypeError('order_id must be an integer.')

        try:
            amount = float(amount)
        except:
            raise TypeError('amount must be a number.')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number.')

        try:
            order_range = float(order_range)
        except:
            raise TypeError('order_range must be a number.')

        if trailing_step is not None:
            try:
                trailing_step = float(trailing_step)
            except:
                raise ValueError('trailing step must be a number.')

        params = {
                  'order_id': order_id,
                  'rate': rate,
                  'range': order_range,
                  'amount': amount
                 }
        if trailing_step is not None:
            params['trailing_step'] = trailing_step

        self.__handle_request__(method='trading/change_order',
                                       params=params, protocol='post')

    def delete_order(self, order_id):
        """ Delete an order.

        Arguments:

        order_id: integer,
            the id of the order to delete.

        """

        try:
            order_id = int(order_id)
        except:
            raise TypeError('order_id must be an integer.')

        if order_id in self.old_orders:
            self.logger.warn('Order is allready deleted.')
            return

        if order_id not in self.orders:
            raise ValueError('No order with order id %s' % order_id)

        params = {
                  'order_id': order_id
                 }

        self.__handle_request__(method='trading/delete_order',
                                       params=params, protocol='post')

    def create_market_buy_order(self, symbol, amount, account_id=None):
        """ Create an order to buy at market price.

        Arguments:

        symbol: string,
            the symbol of the instrument to trade as given by
            get_instruments().

        amount: integer,
            the trades amount in lots.

        account_id: integer (Default None),
            the trade's account id. If not given, the default account is used.

        """

        if account_id is None:
            account_id = self.default_account
        else:
            try:
                account_id = int(account_id)
            except:
                raise TypeError('account_id must be an integer.')
        if account_id not in self.account_ids:
            raise ValueError('Unknown account id %s.' % account_id)

        if symbol not in self.instruments:
            raise ValueError('Unknown symbol %s.' % symbol)

        try:
            amount = int(amount)
        except:
            raise TypeError('amount must be an integer.')

        order = self.open_trade(symbol, True, amount, 'FOK', 'AtMarket',
                                account_id)

        return order

    def create_market_sell_order(self, symbol, amount, account_id=None):
        """ Create an order to sell at market price.

        Arguments:

        symbol: string,
            the symbol of the instrument to trade as given by
            get_instruments().

        amount: integer,
            the trades amount in lots.

        account_id: integer (Default None),
            the trade's account id. If not given, the default account is used.

        """

        if account_id is None:
            account_id = self.default_account
        else:
            try:
                account_id = int(account_id)
            except:
                raise TypeError('account_id must be an integer.')
        if account_id not in self.account_ids:
            raise ValueError('Unknown account id %s.' % account_id)

        if symbol not in self.instruments:
            raise ValueError('Unknown symbol %s.' % symbol)

        try:
            amount = int(amount)
        except:
            raise TypeError('amount must be an integer.')

        order = self.open_trade(symbol, False, amount, 'FOK', 'AtMarket',
                                account_id)

        return order

    def create_entry_order(self, symbol, is_buy, amount, time_in_force,
                           order_type="Entry", limit=0, is_in_pips=True,
                           rate=0, stop=None, trailing_step=None,
                           account_id=None):
        """ Creates an entry order for a given instrument.

        Arguments:

        account_id: integer (Default None),
            the trading account's id. If None, the default account is used.

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
            the time in force of the order execution, must be one of
            'GTC', 'DAY' or 'GTD'.

        rate: float (default 0),
            the trades rate.

        is_in_pips: boolean (default True),
            whether the trade's stop/limit rates are in pips.

        limit: float (default 0),
            the trades limit rate.

        stop: float or None (default None),
            the trades stop rate.

        trailing_step: float or None (default None),
            the trailing step for the stop rate.

        Returns:

        The id of the new order.
        """
        if account_id is None:
            account_id = self.default_account
        else:
            try:
                account_id = int(account_id)
            except:
                raise TypeError('account_id must be an integer.')
        if account_id not in self.account_ids:
            raise ValueError('Unknown account id %s.' % account_id)

        try:
            amount = int(amount)
        except:
            raise TypeError('amount must be an integer.')

        if symbol not in self.instruments:
            raise ValueError('Unknown symbol %s.' % symbol)

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number.')

        try:
            limit = float(limit)
        except:
            raise TypeError('limit must be a number.')

        if order_type not in ['Entry']:
            msg = "order_type must be 'Entry'."
            raise ValueError(msg)

        if time_in_force not in ['GTC', 'DAY', 'GTD']:
            msg = "time_in_force must be in 'GTC', 'DAY' or 'GTD'."
            raise ValueError(msg)

        if is_in_pips is True:
            is_in_pips = 'true'
        elif is_in_pips is False:
            is_in_pips = 'false'
        else:
            raise ValueError('is_in_pips must be True or False.')

        if is_buy is True:
            is_buy = 'true'
        elif is_buy is False:
            is_buy = 'false'
        else:
            raise ValueError('is_buy must be True or False.')

        if stop is not None:
            try:
                stop = float(stop)
            except:
                raise TypeError('stop must be a number.')

        if trailing_step is not None:
            try:
                trailing_step = float(trailing_step)
            except:
                raise ValueError('trailing step must be a number.')

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

        data = self.__handle_request__(method='trading/create_entry_order',
                                       params=params, protocol='post')

        if 'data' in data and 'orderId' in data['data']:
            order_id = int(data['data']['orderId'])

        else:
            self.logger.warn('Missing orderId in servers answer.')
            return 0

        try:
            order = self.get_order(order_id)
        except:
            time.sleep(1)
            order = self.get_order(order_id)

        return order

    def change_order_stop_limit(self, order_id, stop=None, limit=None,
                                is_stop_in_pips=True, is_limit_in_pips=True):
        """ Change an order's stop and / or limit rate. To let an attribute
        unchanged set the values parameter to None.

        Arguments:

        order_id: integer,
            the id of the order to change.

        stop: float or None (Default),
            the new stop rate.

        limit: float or None (Default),
            the new limit rate.

        is_stop_in_pips: boolean (Default True),
            whether the order's stop rate is in pips.

        is_limit_in_pips: boolean (Default True),
            whether the order's limit rate is in pips.
        """

        try:
            order_id = int(order_id)
        except:
            raise TypeError('order_id must be an integer.')

        params = {
                  'order_id': order_id
                 }

        if stop is not None:
            if is_stop_in_pips is True:
                is_stop_in_pips = 'true'
            elif is_stop_in_pips is False:
                is_stop_in_pips = 'false'
            else:
                raise ValueError('is_stop_in_pips must be a boolean.')

            try:
                stop = float(stop)
            except:
                raise TypeError('stop must be a number.')

            params['is_stop_in_pips'] = is_stop_in_pips
            params['stop'] = stop

        if limit is not None:
            if is_limit_in_pips is True:
                is_limit_in_pips = 'true'
            elif is_limit_in_pips is False:
                is_limit_in_pips = 'false'
            else:
                raise ValueError('is_limit_in_pips must be a boolean.')

            try:
                limit = float(limit)
            except:
                raise TypeError('limit')

            params['is_limit_in_pips'] = is_limit_in_pips
            params['limit'] = limit

        meth = 'trading/change_order_stop_limit'
        self.__handle_request__(method=meth, params=params,
                                protocol='post')

    def create_oco_order(self, symbol, is_buy, is_buy2, amount, is_in_pips,
                         time_in_force, at_market, order_type, expiration,
                         limit=0, limit2=0, rate=0, rate2=0, stop=0, stop2=0,
                         trailing_step=0, trailing_step2=0,
                         trailing_stop_step=0, trailing_stop_step2=0,
                         account_id=None):

        """ Creates an entry order for a given instrument.

        Arguments:

        account_id: integer (Default None),
            the id of the trading account. If None, the default account is
            used.

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
            whether the order's stop/limit rates are in pips.

        time_in_force: string,
            the time in force of the order execution, must be one of
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
            the second order's stop rate.

        trailing_step: float (default 0),
            the trailing step for the first order.

        trailing_step2: float (default 0),
            the trailing step for the second order.

        trailing_stop_step: float (default 0),
            the trailing step for the first order's stop rate.

        trailing_stop_step: float (default 0),
            the trailing step for the second order's stop rate.

        Returns:

        The id of the new order.
        """
        if account_id is None:
            account_id = self.default_account
        else:
            try:
                account_id = int(account_id)
            except:
                raise TypeError('account_id must be an integer.')

        if account_id not in self.account_ids:
            raise ValueError('Unknown account id %s.' % account_id)

        if is_buy is True:
            is_buy = 'true'
        elif is_buy is False:
            is_buy = 'false'
        else:
            raise ValueError('is_buy must be a boolean.')

        if is_buy2 is True:
            is_buy2 = 'true'
        elif is_buy2 is False:
            is_buy2 = 'false'
        else:
            raise ValueError('is_buy2 must be a boolean.')

        try:
            amount = int(amount)
        except:
            raise TypeError('amount must be an integer.')

        if is_in_pips is True:
            is_in_pips = 'true'
        elif is_in_pips is False:
            is_in_pips = 'false'
        else:
            raise ValueError('is_in_pips must be a boolean.')

        if time_in_force not in ['IOC', 'GTC', 'FOK', 'DAY', 'GTD']:
            msg = "time_in_force must be 'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'."
            raise ValueError(msg)

        try:
            at_market = float(at_market)
        except:
            raise TypeError('at_market must be a number.')

        if order_type not in ['AtMarket', 'MarketRange']:
            msg = "order_type must one of 'AtMarket' or 'MarketRange'."
            raise ValueError(msg)

        try:
            limit = float(limit)
        except:
            raise TypeError('limit must be a number.')

        try:
            limit2 = float(limit2)
        except:
            raise TypeError('limit2 must be a number.')

        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number.')

        try:
            rate2 = float(rate2)
        except:
            raise TypeError('rate2 must be a number.')

        try:
            stop = float(stop)
        except:
            raise TypeError('stop must be a number.')

        try:
            stop2 = float(stop2)
        except:
            raise TypeError('stop2 must be a number.')

        try:
            trailing_step = float(trailing_step)
        except:
            raise ValueError('trailing step must be a number.')

        try:
            trailing_step2 = float(trailing_step2)
        except:
            raise ValueError('trailing step must be a number.')

        try:
            trailing_stop_step = float(trailing_stop_step)
        except:
            raise ValueError('trailing_stop_step must be a number.')

        try:
            trailing_stop_step2 = float(trailing_stop_step2)
        except:
            raise ValueError('trailing_stop_step2 must be a number.')

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

        data = self.__handle_request__(method='trading/simple_oco',
                                       params=params, protocol='post')

        if 'data' not in data:
            self.logger.error('Missing data in server response: %s.' % data)
            raise ServerError('Missing data in server response.')

        orders = list()
        for data_set in data['data']:
            count = 0
            while count < 100:
                if int(data_set['orderId']) not in self.orders:
                    time.sleep(1)
                    count += 1
                else:
                    orders.append(self.get_order(int(data_set['orderId'])))
                    break
            else:
                raise ValueError('No order with id %s' % data_set['orderId'])

        bulk_id = orders[0].__ocoBulkId__
        oco_order = fxcmpy_oco_order(bulk_id, orders, self,  self.logger)
        self.oco_orders[bulk_id] = oco_order
        return oco_order

    def add_to_oco(self, order_ids, oco_bulk_id=0):
        """ Add orders to OCO Orders.

        Arguments:

        order_ids: list of order_ids,
            the ids of the orders to add to the OCO Order.

        co_bulk_id: integer, default = 0,
            the id of the OCO Order, if 0 a new OCO Order will be created.

        """

        try:
            _ = (int(i) for i in order_ids)
        except:
            raise TypeError('order_ids must be a list of integers.')

        try:
            oco_bulk_id = int(oco_bulk_id)
        except:
            raise TypeError('oco_bulk_id must be an integer.')

        params = {
                  'orderIds': order_ids,
                  'ocoBulkId': oco_bulk_id
                 }
        self.__handle_request__(method='trading/add_to_oco',
                                       params=params, protocol='post')

    def remove_from_oco(self, order_ids):
        """ Remove orders from OCO Orders.

        Arguments:

        order_ids: list of order_ids,
            the ids of the orders to remove from OCO Orders.

        """
        try:
            _ = (int(i) for i in order_ids)
        except:
            raise TypeError('order_ids must be a list of integers.')

        params = {
                  'orderIds': order_ids
                 }
        self.__handle_request__(method='trading/remove_from_oco',
                                       params=params, protocol='post')

    def edit_oco(self, oco_bulk_id, add_order_ids=list(),
                 remove_order_ids=list()):
        """Add or remove orders to or from OCO Orders.

        Arguments:

        oco_bulk_id: integer,
            the id of the OCO Order.

        add_order_ids: list of order_ids,
            the id's of the orders to add to OCO Orders.

        remove_order_ids: list of order_ids,
            the id's of the orders to remove from OCO Orders.

        """
        try:
            _ = (int(i) for i in add_order_ids)
        except:
            raise TypeError('add_order_ids must be a list of integers.')

        try:
            _ = (int(i) for i in remove_order_ids)
        except:
            raise TypeError('remove_order_ids must be a list of integers.')

        params = {
                  'ocoBulkId': oco_bulk_id,
                  'addOrderIds': add_order_ids,
                  'removeOrderIds': remove_order_ids
                 }
        self.__handle_request__(method='trading/edit_oco',
                                       params=params, protocol='post')

    def get_instruments_for_candles(self):
        """ Return a list of all available instruments to receive historical
        data for."""

        return list(self.offers.keys())

    def get_candles(self, instrument, period, number=10, start=None, end=None,
                    with_index=True, columns=[], stop=None):
        """Return historical data from the fxcm database as pandas.DataFrame.

        Arguments:

        instrument: string:
            the instrument for which data is requested. For a list of all
            available instruments for historical data, use
            get_instruments_for_candles().

        period: string,
            the granularity of the data. Must be one of
            'm1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8',
            'D1', 'W1', or 'M1'.

        number: integer (default 10),
            the number of candles to receive.

        start: datetime.datetime, datetime.date or string (defaut None),
            the first date to receive data for. If it is a string, the date is 
            in format YYYY-MM-DD hh:mm. 

        end: datetime.datetime, datetime.date or string (default None),
            the last date to receive data for. If it is a string, the date is 
            in format YYYY-MM-DD hh:mm. 

        with_index: boolean (default True),
            whether the column 'date' should server as index in the resulting
            pandas.DataFrame.

        columns: list (default list()),
            a list of column labels the result should include. If empty, all
            columns are returned.

            Available column labels are

            'date', 'bidopen', 'bidclose', 'bidhigh', 'bidlow',
            'askopen', 'askclose', 'askhigh', 'asklow', 'tickqty'.

            Also available is 'asks' as shortcut for all ask related columns
            and 'bids' for all bid related columns, respectively.

            The column 'date' is always included.

        Returns:

        A pandas DataFrame containing the requested data.

        """

        if instrument == '':
            self.logger.error('Error in get_candles: No instrument given!.')
            raise ValueError('Please provide a intrument.')
        if instrument in self.offers:
            offer_id = self.offers[instrument]
        else:
            raise ValueError('Instrument must be one of %s.'
                             % str(tuple(self.offers.keys())))
        if period not in self.PERIODS:
            self.logger.error('Error in get_candles: Illegal period: %s.'
                              % period)
            raise ValueError('period must be one of %s.' % self.PERIODS)
        if type(number) != int or number < 1 or number > 10000:
            self.logger.error('Error in get_candles: Illegal param. number: %s'
                              % number)
            raise ValueError('number must be a integer betwenn 0 and 10000.')

        params = {
                  'num': number,
                 }

        if start:
            if isinstance(start, str):
                try:
                    start = dt.datetime.strptime(start, '%Y-%m-%d %H:%M')
                except:
                    msg = "start must either be a datetime object or a string"
                    msg += " in format 'YYYY-MM-DD hh:mm'."
                    raise ValueError(msg)

            elif isinstance(start, dt.datetime) or isinstance(start, dt.date):
                pass
            else:
                msg = "start must either be a datetime object or a string"
                msg += " in format 'YYYY-MM-DD hh:mm'."
                raise ValueError(msg)

            start = ((start - dt.datetime(1970, 1, 1)) / 
                     dt.timedelta(seconds=1))
            try:
                start = int(start)
            except:
                self.logger.error('Error in get_candles:')
                self.logger.error('Illegal value for start: %s.' % start)
                raise ValueError('start must be a datetime object.')
            params['from'] = start

        if end == None and stop is not None:
            end = stop

        if end:
            if isinstance(end, str):
                try:
                    end = dt.datetime.strptime(end, '%Y-%m-%d %H:%M')
                except:
                    msg = "end must either be a datetime object or a string"
                    msg += " in format 'YYYY-MM-DD hh:mm'."
                    raise ValueError(msg)

            elif isinstance(end, dt.datetime) or isinstance(end, dt.date):
                pass
            else:
                msg = "end must either be a datetime object or a string"
                msg += " in format 'YYYY-MM-DD hh:mm'."
                raise ValueError(msg)

            end = ((end - dt.datetime(1970, 1, 1)) / dt.timedelta(seconds=1))
            try:
                end = int(end)
            except:
                self.logger.error('Error in get_candles:')
                self.logger.error('Illegal value for end: %s.' % stop)
                raise ValueError('end must be a datetime object.')
            params['to'] = end

        data = self.__handle_request__(method='candles/%s/%s'
                                       % (offer_id, period), params=params)

        if len(columns) == 0:
            to_add = self.CANDLES_COLUMNS
        else:
            to_add = ['date', ]
        for field in columns:
            if field == 'asks':
                for ask_field in self.CANDLES_COLUMNS_ASK:
                    if ask_field not in to_add:
                        to_add.append(ask_field)
            elif field == 'bids':
                for bid_field in self.CANDLES_COLUMNS_BID:
                    if bid_field not in to_add:
                        to_add.append(bid_field)
            elif field in self.CANDLES_COLUMNS:
                if field not in to_add:
                    to_add.append(field)
            else:
                msg = "Unknown field '%s', please use one or more of \
'%s', 'asks', 'bids'."
                raise ValueError(msg % (field,
                                        "','".join(self.CANDLES_COLUMNS)))

        if 'candles' in data:
            ret = pd.DataFrame(data['candles'], columns=self.CANDLES_COLUMNS)
            ret['date'] = pd.to_datetime(ret['date'], unit='s')
        else:
            ret = pd.DataFrame(columns=self.CANDLES_COLUMNS)

        ret = ret[to_add]

        if with_index:
            ret.set_index('date', inplace=True)
        return ret

    def __collect_account_ids__(self):
        """ Collects account ids and stores them in self.account_ids."""

        self.account_ids = set()
        data = self.get_accounts('list')
        for acc in data:
            if 'accountId' in acc and acc['accountId'] != '':
                self.account_ids.add(int(acc['accountId']))
        self.account_ids = list(self.account_ids)

    def __collect_orders__(self):
        """ Collects available orders and stores them in self.orders."""

        data = self.get_orders('list')
        for order in data:
            if 'orderId' in order and order['orderId'] != '':
                self.orders[int(order['orderId'])] = fxcmpy_order(self, order)

    def __collect_oco_orders__(self):
        """ Collect available oco orders and stores them in self.oco_orders."""

        for order in self.orders.values():
            if order.__ocoBulkId__ != 0:
                if order.__ocoBulkId__ in self.oco_orders:
                    self.oco_orders[order.__ocoBulkId__].__add__(order)
                else:
                    oco = fxcmpy_oco_order(order.__ocoBulkId__, [order, ], self,
                                         self.logger)
                    self.oco_orders[order.__ocoBulkId__] = oco

    def __collect_offers__(self):
        """ Collect available offers and stores them in self.offers, a dict
        with key symbol and value offer_id."""
        self.offers = dict()
        offers = self.get_offers('list')
        for offer in offers:
            if 'currency' in offer and 'offerId' in offer:
                self.offers[offer['currency']] = int(offer['offerId'])

    def __collect_positions__(self):
        data = self.get_open_positions('list')
        for pos in data:
            if 'tradeId' in pos and pos['tradeId'] != '':
                self.open_pos[int(pos['tradeId'])] = fxcmpy_open_position(self,
                                                                        pos)
        data = self.get_closed_positions('list')
        for po in data:
            if 'tradeId' in po and po['tradeId'] != '':
                self.closed_pos[int(po['tradeId'])] = fxcmpy_closed_position(self,
                                                                           po)

    def __connect__(self):
        try:
            self.logger.debug('Access token: %s.' % self.access_token)
            self.socket = SocketIO(self.trading_url+':443', self.port,
                                   params={'access_token': self.access_token,
                                            'agent': 'pythonquants'},
                                   wait_for_connection=False)
            self.logger.debug('Socket established: %s.' % self.socket)
            self.socket_id = self.socket._engineIO_session.id
            self.logger.debug('Got socket session id: %s.' % self.socket_id)
        except ConnectionError as inst:
            self.connection_status = 'aborted'
            self.logger.error('Socket returns an error: %s.'
                              % inst.args[0])
        except:
            self.connection_status = 'aborted'
            self.logger.error('Socket returns unknown error.')
        else:
            self.connection_status = 'established'
            self.logger.info('Connection established.')

            self.bearer_token = 'Bearer '+self.socket_id+self.access_token

            self.request_headers = {
                                    'User-Agent': 'request',
                                    'Authorization': self.bearer_token,
                                    'Accept': 'application/json',
                                    'Content-Type':
                                    'application/x-www-form-urlencoded'
                                   }

            time.sleep(2)
            self.socket.wait()

    def __reconnect__(self, count):
        self.logger.warn('Not connected, try to reconnect. (%s)' % count)
        self.connect()
        time.sleep(5)
        self.subscribe_data_model('Order')
        self.subscribe_data_model('OpenPosition')
        self.subscribe_data_model('ClosedPosition')
        for symbol in self.prices:
            params = {'pairs': symbol}
            self.__handle_request__(method='subscribe', params=params,
                                    protocol='post')
            self.socket.on(symbol, self.__on_price_update__)

    def __handle_request__(self, method='', params={}, protocol='get'):
        """ Sends server requests. """

        if method == '':
            self.logger.error('Error in __handle__requests__: No method given')
            raise ValueError('No method given.')
        if type(params) is not dict:
            self.logger.debug('Error in __handle__requests__:')
            self.logger.debig('params must be of type dict.')
            raise TypeError('params must be of type dict.')

        if not self.is_connected():
            count = 1
            while not self.is_connected() and count < 11:
                self.__reconnect__(count)
                count += 1

        if method == 'trading/close_all_for_symbol':
            if ('forSymbol' in params and params['forSymbol'] == 'false'
                 and len(self.open_pos) == 0):
                self.logger.warn('No open positions to close')
                return False
            elif ('forSymbol' in params and params['forSymbol'] == 'true'):
                count = 0
                for pos in self.open_pos.values():
                    if pos.__currency__ == params['symbol']:
                        count += 1
                if count == 0:
                    self.logger.warn('No open positions to close.')
                    return False

        self.logger.info('Sending request to %s/%s, parameter: %s.'
                         % (self.trading_url, method, params))
        if protocol == 'post':
            req = requests.post('%s:443/%s' % (self.trading_url, method),
                                headers=self.request_headers, data=params)
            self.logger.info('Sending POST Request:')
            self.logger.info('URL: %s' % req.url)
            self.logger.info('Payload: %s' % req.request.body)
            self.logger.info('Headers: %s' % req.request.headers)
            self.logger.info('Params: %s' % params)

        else:
            req = requests.get('%s:443/%s' % (self.trading_url, method),
                               headers=self.request_headers, params=params)
            self.logger.info('Sending GET Request:')
            self.logger.info('URL: %s' % req.url)
            self.logger.info('Headers: %s' % req.request.headers)
            self.logger.info('Params: %s' % params)

        if req.status_code != 200:
            self.logger.error('FXCM reject req %s with status %s and msg %s.'
                              % (method, req.status_code, req.text))

            raise ServerError('Request returns status code %s and message "%s"'
                              % (req.status_code,
                                 unquote(req.text)))

        try:
            data = req.json()
        except:
            self.logger.error('Can not parse server answer to json object: %s.'
                              % req.text)

        if 'response' not in data or 'executed' not in data['response']:
            self.logger.error('Malformed response %s' % data)
            raise ServerError('Malformed response')

        if not data['response']['executed']:
            if 'error' in data['response'] and data['response']['error'] != '':
                self.logger.error('Server reports an error: %s.'
                                  % data['response'])
                raise ServerError('FXCM Server reports an error: %s.'
                                  % data['response']['error'])
            else:
                self.logger.error('FXCM Server reports an unknown error: %s.'
                                  % data['response'])
                raise ServerError('FXCM Server returns an unknown error.')

        self.logger.debug('Server answer: %s.' % data)
        return data

    def __on_price_update__(self, msg):
        data = json.loads(msg)

        symbol = data['Symbol']
        date = pd.to_datetime(int(data['Updated']), unit='ms')
        temp_data = pd.DataFrame([data['Rates']],
                                 columns=['Bid', 'Ask', 'High', 'Low'],
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
                    self.logger.error('Call of %s raised an error:' % func)
                    self.logger.error(sys.exc_info()[0])
                    self.logger.error(sys.exc_info()[1])
                    raise

    def __on_model_update__(self, msg):
        # Answers not always json objects, so we have to log the raw answer
        # data = json.loads(msg)
        try:
            self.logger.debug(msg)
        except:
            pass

    def __on_message__(self, msg):
        # Answers not always json objects, so we have to log the raw answer
        try:
            data = json.loads(msg)
            self.logger.debug(data)
        except:
            pass

    def __on_order_update__(self, msg):
        """ Gets called when the order stream sends new data for the order
        table.

        Arguments:

        msg: string,
            a json like data object.
        """

        try:
            data = json.loads(msg)
        except:
            self.logger.warn('Got a non json answer in order stream, ignoring')
            self.logger.warn(msg)
            return -1
        if 'action' in data and data['action'] == 'I':
            self.logger.info('Got a insert event for orders: %s.' % data)
            order_id = int(data['orderId'])
            self.orders[order_id] = fxcmpy_order(self, data)

        elif 'action' in data and data['action'] == 'D':
            self.logger.warn('Got a delete event for orders: %s.' % data)
            order_id = int(data['orderId'])
            if order_id in self.orders:
                order = self.orders[order_id]
                if order.get_ocoBulkId() != 0:
                    try:
                        self.oco_orders[order.get_ocoBulkId()].__remove__(order)
                    except:
                        pass

                self.old_orders[order_id] = order
                del self.orders[order_id]

        elif ('action' in data and
              data['action'] != 'I' and data['action'] != 'D' and
              data['action'] != 'U'):
            msg = 'Found an unknown action in Order stream: %s.' % data
            self.logger.error(msg)
        else:
            self.logger.debug('Update data without action:')
            self.logger.debug(data)
            if 'orderId' in data:
                order = self.orders[int(data['orderId'])]
                for field in data:
                    if (field == 'ocoBulkId' and
                         order.get_ocoBulkId() != data['ocoBulkId']):
                        if data['ocoBulkId'] == 0:
                            bulkId = order.get_ocoBulkId()
                            self.oco_orders[bulkId].__remove__(order)
                        else:
                            if data['ocoBulkId'] not in self.oco_orders:
                                self.__collect_oco_orders__()
                            self.oco_orders[data['ocoBulkId']].__add__(order)

                        value = data['ocoBulkId']
                    else:
                        value = data[field]
                    order.__set_attribute__(field, value)

        if 'Order' in self.add_callbacks:
            callbacks = self.add_callbacks['Order']
            for func in callbacks:
                try:
                    callbacks[func](data)
                except:
                    self.logger.error('Call of %s raised an error:' % func)
                    self.logger.error(sys.exc_info()[0])
                    self.logger(sys.exc_info()[1])
                    self.logger(sys.exc_info()[2])

    def __on_open_pos_update__(self, msg):
        """ Gets called when the open_position stream sends new data.

        Arguments:

        msg: string,
            a json like data object.
        """

        try:
            data = json.loads(msg)
        except:
            msg = 'Got non json answer in open pos stream, ignoring.'
            self.logger.warn(msg)
            self.logger.warn(msg)
            return -1

        if 'tradeId' in data and data['tradeId'] != '':
            trade_id = int(data['tradeId'])
            if 'action' in data and data['action'] == 'I':
                self.logger.warn('Got a insert event for open positions: %s.'
                                 % data)
                self.open_pos[trade_id] = fxcmpy_open_position(self, data)
            elif 'action' in data and data['action'] == 'D':
                self.logger.warn('Got a delete event for open posi: %s' % data)
                del self.open_pos[trade_id]

            elif ('action' in data and
                  data['action'] != 'I' and data['action'] != 'D' and
                  data['action'] != 'U'):
                msg = 'Found an unknown action in open pos stream: %s.' % data
                self.logger.error(msg)
            else:
                self.logger.debug('Update data without action:')
                self.logger.debug(data)
                pos = self.open_pos[trade_id]
                for field in data:
                    pos.__set_attribute__(field, data[field])

        if 'OpenPosition' in self.add_callbacks:
            callbacks = self.add_callbacks['OpenPosition']
            for func in callbacks:
                try:
                    callbacks[func](data)
                except:
                    self.logger.error('Call of %s raised an error:' % func)
                    self.logger.error(sys.exc_info()[0])
                    self.logger(sys.exc_info()[1])
                    self.logger(sys.exc_info()[2])

    def __on_closed_pos_update__(self, msg):
        """ Gets called when the closed_position stream sends new data.

        Arguments:

        msg: string,
            a json like data object.
        """

        try:
            data = json.loads(msg)
        except:
            msg = 'Got non json answer in close pos stream, ignoring.'
            self.logger.warn(msg)
            self.logger.warn(msg)
            return -1

        if 'tradeId' in data and data['tradeId'] != '':
            trade_id = int(data['tradeId'])
            if 'action' in data and data['action'] == 'I':
                self.logger.warn('Got a insert event for closed positions: %s.'
                                 % data)
                self.closed_pos[trade_id] = fxcmpy_closed_position(self, data)
            elif 'action' in data and data['action'] == 'D':
                self.logger.warn('Got delete event for closed pos: %s' % data)
                del self.closed_pos[trade_id]

            elif ('action' in data and
                  data['action'] != 'I' and data['action'] != 'D' and
                  data['action'] != 'U'):
                msg = 'Found unknown action in closed pos stream: %s.' % data
                self.logger.error(msg)
            else:
                self.logger.debug('Update data without action:')
                self.logger.debug(data)
                pos = self.closed_pos[trade_id]
                for field in data:
                    pos.__set_attribute__(field, data[field])

        if 'ClosedPosition' in self.add_callbacks:
            callbacks = self.add_callbacks['ClosedPosition']
            for func in callbacks:
                try:
                    callbacks[func](data)
                except:
                    self.logger.error('Call of %s raised an error:' % func)
                    self.logger.error(sys.exc_info()[0])
                    self.logger(sys.exc_info()[1])
                    self.logger(sys.exc_info()[2])

    def __on_error__(self, msg):
        print('Error: %s' % msg)

    def __get_config_value__(self, section, key):
        config = configparser.ConfigParser()
        try:
            config.read(self.config_file)
        except:
            if self.logger:
                self.logger.error('Can not open config file, no such file: %s.'
                                  % self.config_file)
            raise IOError('Can not open config file, no such file: %s.'
                          % self.config_file)

        if section not in config.sections():
            if self.logger:
                self.logger.error('Can not find section %s in %s.'
                                  % (section, self.config_file))
            raise ValueError('Can not find section %s in %s.'
                             % (section, self.config_file))

        if key not in config[section]:
            if self.logger:
                self.logger.error('Can not find key %s in section %s of %s.'
                                  % (key, section, self.config_file))
            raise ValueError('Can not find key %s in section %s of %s.'
                             % (key, section, self.config_file))
        if self.logger:
            self.logger.debug('Found config value %s for key %s in section %s.'
                              % (config[section][key], key, section))
        return config[section][key]
