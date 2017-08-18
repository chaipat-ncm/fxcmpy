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


class fxcmpy(object):
    """ A wrapper class for the FXCM API. """

    # Class attributes

    auth_url = 'https://www-beta2.fxcorporate.com/oauth/token'
    trading_url = 'https://www-beta3.fxcorporate.com'
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
        self.add_callbacks = dict()

        self.connect()

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

    def get_prices(self, symbol):
        """ Return the prices of a given subscriped instrument.

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
        data = self.__handle_request__(method='subscribe', params=params)

        self.socket.on(symbol, self.__on_price_update__)

    def subscribe_data_model(self, model='', add_callbacks=()):
        # To do, Add callbacks
        """ Stream data of a model .

        Arguments:
        ==========

        model:  string,
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
                                       params=params)
        print(data)
        self.socket.on(model, self.__on_model_update__)

    def unsubscribe_market_data(self, symbol=''):

        if symbol == '':
            raise ValueError('No symbol given')

        self.logger.info('Try to unsubscribe for %s' % symbol)

        params = {'pairs': symbol}
        data = self.__handle_request__(method='unsubscribe', params=params)

        if symbol in self.prices:
            del self.prices[symbol]
        if symbol in self.add_callbacks:
            del self.add_callbacks[symbol]

    def unsubscribe_data_model(self, model=''):

        if model == '':
            raise ValueError('No symbol given')

        self.logger.info('Try to unsubscribe for %s' % model)

        params = {'models': model}
        data = self.__handle_request__(method='trading/unsubscribe',
                                       params=params)

        if model in self.add_callbacks:
            del self.add_callbacks[model]

    def close_all_for_symbol(self, account_id, for_symbol, symbol,
                             order_type, time_in_force):
        params = {
                  'account_id': account_id,
                  'forSymbol': for_symbol,
                  'symbol': symbol,
                  'order_type': order_type,
                  'time_in_force': time_in_force
                 }

        data = self.__handle_request__(method='trading/close_for_all_symbols',
                                       params=params)

    # To Do: Parameter checdk
    # To do: Add is_in_pips, at_market and order_type, limit to arguments
    def open_trade(self, account_id, symbol, side,
                   amount, time_in_force, rate=0,
                   stop=None, trailing_step=None):
        params = {
                  'account_id': account_id,
                  'symbol': symbol,
                  # Not sure about the parmeter name and syntax of is_buy
                  'is_buy': side,
                  # not sure about syntax of rate
                  'rate': rate,
                  'amount': amount,
                  'at_market': 0,
                  'order_type': 'AtMarket',
                  # Not sure about time_in_force
                  'time_in_force': time_in_force
                 }
        if stop is not None:
            params['stop'] = stop
        if trailing_step is not None:
            params['trailing_step'] = trailing_step

        data = self.__handle_request__(method='trading/open_trade',
                                       params=params)
        print(data)

    def change_order(self, order_id, amount, rate=0, order_range=0,
                     trailing_step=None):
        params = {
                  'order_id': order_id,
                  'rate': rate,
                  'range': order_range,
                  'amount': amount
                 }
        if trailing_step is not None:
            params['trailing_step'] = trailing_step

        data = self.__handle_request__(method='trading/change_order',
                                       params=params)
        print(data)

    def delete_order(self, order_id):
        params = {
                  'order_id': order_id
                 }

        data = self.__handle_request__(method='trading/delete_order',
                                       params=params)
        print(data)

    def create_entry_order(self, account_id, symbol, side, amount, limit,
                           is_in_pips, time_in_force,
                           rate=0, stop=None, trailing_step=None):
        params = {
                  'account_id': account_id,
                  'symbol': symbol,
                  # Not sure about the parmeter name and syntax of is_buy
                  'is_buy': side,
                  # not sure about syntax of rate
                  'rate': rate,
                  'amount': amount,
                  'limit': limit,
                  'order_type': 'Entry',
                  'is_in_pips': is_in_pips,
                  # Not sure about time_in_force
                  'time_in_force': time_in_force
                 }
        if stop is not None:
            params['stop'] = stop
        if trailing_step is not None:
            params['trailing_step'] = trailing_step

        data = self.__handle_request__(method='trading/create_entry_order',
                                       params=params)
        print(data)

    def create_oco_order(self, account_id, symbol, side, side2, amount,
                         is_in_pips, time_in_force, at_market, order_type,
                         expiration, limit, limit2, rate, rate2, stop, stop2,
                         trailing_step, trailing_step2, trailing_stop_step,
                         trailing_stop_step2):

        params = {
                  'account_id': account_id,
                  'symbol': symbol,
                  'amount': amount,
                  'at_market': at_market,
                  'order_type': order_type,
                  'is_in_pips': is_in_pips,
                  'time_in_force': time_in_force,
                  'expiration': expiration,
                  # Not sure about the parmeter name and syntax of is_buy
                  'is_buy': side,
                  'is_buy2': side2,
                  # not sure about syntax of rate
                  'rate': rate,
                  'rate2': rate2,
                  'stop': stop,
                  'stop2': stop2,
                  'limit': limit,
                  'limit2': limit2,
                  # Not sure about time_in_force
                  'trailing_step':  trailing_step,
                  'trailing_step2':  trailing_step2,
                  'trailing_stop_step': trailing_stop_step,
                  'trailing_stop_step2': trailing_stop_step2,
                 }
        data = self.__handle_request__(method='trading/simple_oco',
                                       params=params)
        print(data)

    def add_to_oco(self, order_ids, oco_bulk_id=0):
        params = {
                  'oderIds': order_ids,
                  'ocoBulkId': oco_bulk_id
                 }
        data = self.__handle_request__(method='trading/add_to_oco',
                                       params=params)

    def remove_from_oco(self, order_ids):
        params = {
                  'oderIds': order_ids
                 }
        data = self.__handle_request__(method='trading/remove_from_oco',
                                       params=params)

    def edit_oco(self, oco_bulk_id, add_order_ids, remove_order_ids):
        params = {
                  'ocoBulkId': oco_bulk_id,
                  'addOrderIds': add_order_ids,
                  'removeOrderIds': remove_order_ids
                 }
        data = self.__handle_request__(method='trading/edit_oco',
                                       params=params)

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

    def __connect__(self):
        try:
            self.socket = SocketIO(self.trading_url, self.port,
                                   params={'access_token': self.access_token})
            self.socket_id = self.socket._engineIO_session.id
        except:
            self.logger.error('Can not connect to FXCM server')
        else:
            self.logger.info('Connection established')

        self.socket.on('message', self.__on_message__)
        self.socket.on('error', self.__on_error__)
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

        req = requests.post(self.auth_url, data=params)

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

        req = requests.get(self.trading_url+'/authenticate',
                           params=auth2_params)
        if req.status_code != 200:
            self.loggin.error('FXCM reject request for temporay access token')
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

    def __handle_request__(self, method='', params={}):
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
        req = requests.get('%s/%s' % (self.trading_url, method), params=params)
        if req.status_code != 200:
            self.logger.error('FXCM reject req %s with status %s and msg %s'
                              % (method, req.status_code, req.text))

            raise ServerError('Request returns status code %s and message "%s"'
                              % (req.status_code,
                                 urllib.parse.unquote(req.text)))

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
        data = data['pairs']
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
        print(msg)
        self.logger.debug(msg)

    def __on_message__(self, msg):
        # Answers not allways json objects, so we have to log the plain answer
        # data = json.loads(msg)
        self.logger.debug(msg)

    def __on_error__(self, ws, msg):
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
