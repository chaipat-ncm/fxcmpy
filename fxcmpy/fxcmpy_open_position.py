#
# fxcmpy_open_position -- A Python Wrapper Class for the
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


import datetime as dt


class fxcmpy_open_position(object):
    """ A convenience class for a better handling of open positions. """
    position_parameter = ['tradeId', 'accountName', 'accountId', 'roll', 'com',
                          'open', 'valueDate', 'grossPL', 'close', 'visiblePL',
                          'isDisabled', 'currency', 'isBuy', 'amountK',
                          'currencyPoint', 'time', 'usedMargin', 'stop',
                          'stopMove', 'limit']

    def __init__(self, connection, kwargs):
        self.__con__ = connection
        self.parameter = set()
        for keyword in self.position_parameter:
            if keyword not in kwargs:
                raise TypeError('__init__() required argument %s.' % keyword)
            else:
                self.__set_attribute__(keyword,  kwargs[keyword])

    def __str__(self):
        ret_str = ''
        para_list = list(self.parameter)
        para_list.sort()
        for para in para_list:
            ret_str += '{:18}{}\n'.format(para+':',
                                          getattr(self, '__%s__' % para))
        return ret_str

    def __set_attribute__(self, attribute, value):
        if attribute in ['accountId', 'tradeId']:
            try:
                value = int(value)
            except:
                raise ValueError('value must be an integer.')
        elif attribute in ['time']:
            if value != '':
                try:
                    value = dt.datetime.strptime(value+'000', '%m%d%Y%H%M%S%f')
                except:
                    raise ValueError('Can not parse value %s to datetime.'
                                     % value)
        elif attribute in ['t', 'ratePrecision']:
            return 0
        self.parameter.add(attribute)
        setattr(self, '__'+attribute+'__', value)

    def get_tradeId(self):
        """Return the value of the attribute tradeId."""

        return self.__tradeId__

    def get_accountName(self):
        """Return the value of the attribute accountName."""

        return self.__accountName__

    def get_accountId(self):
        """Return the value of the attribute accountId."""

        return self.__accountId__

    def get_roll(self):
        """Return the value of the attribute roll."""

        return self.__roll__

    def get_com(self):
        """Return the value of the attribute com."""

        return self.__com__

    def get_open(self):
        """Return the value of the attribute open."""

        return self.__open__

    def get_valueDate(self):
        """Return the value of the attribute valueDate."""

        return self.__valueDate__

    def get_grossPL(self):
        """Return the value of the attribute grossPL."""

        return self.__grossPL__

    def get_close(self):
        """Return the value of the attribute close."""

        return self.__close__

    def get_visiblePL(self):
        """Return the value of the attribute visiblePL."""

        return self.__visiblePL__

    def get_isDisabled(self):
        """Return the value of the attribute isDisabled."""

        return self.__isDisabled__

    def get_currency(self):
        """Return the value of the attribute currency."""

        return self.__currency__

    def get_isBuy(self):
        """Return the value of the attribute isBuy."""

        return self.__isBuy__

    def get_amount(self):
        """Return the value of the attribute amountK."""

        return self.__amountK__

    def get_currencyPoint(self):
        """Return the value of the attribute currencyPoint."""

        return self.__currencyPoint__

    def get_time(self):
        """Return the value of the attribute time."""

        return self.__time__

    def get_usedMargin(self):
        """Return the value of the attribute usedMargin."""

        return self.__usedMargin__

    def get_stop(self):
        """Return the value of the attribute stop."""

        return self.__stop__

    def get_stopMove(self):
        """Return the value of the attribute stopMove."""

        return self.__stopMove__

    def get_limit(self):
        """Return the value of the attribute limit."""

        return self.__limit__

    def close(self, amount=0, order_type='AtMarket', time_in_force='FOK',
              rate=0, at_market=0):
        """ Close the trade.

        Arguments:

        amount: integer (default: 0),
            the trades amount in lots. If 0, the whole position is closed.

        order_type: string (default : 'AtMarket'),
            the order type, must be 'AtMarket' or 'MarketRange'.

        time_in_force: string (default: 'FOK'),
            the time in force of the order execution, must be one of
            'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'.

        rate: float (default 0),
            the trades rate.

        at_market: float (default 0),
            the markets range.

        """

        try:
            amount = float(amount)
        except:
            raise TypeError('amount must be a number.')
        if amount == 0:
            amount = self.__amountK__

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

        self.__con__.close_trade(self.__tradeId__, amount, order_type,
                                 time_in_force, rate, at_market)
