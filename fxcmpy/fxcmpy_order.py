#
# fxcmpy_order -- A Python Wrapper Class for the
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
import time


class fxcmpy_order(object):
    """ A class to realize entry orders of the FXCM API.

    Caution:

    Do not initialize fxcm order object manually, these orders will not
    registered by the fxcm server, use the create_entry_order() method of the
    fxcm class instead.
    """

    order_parameter = ['orderId', 'time', 'accountName',
                       'accountId', 'timeInForce', 'currency', 'isBuy', 'buy',
                       'sell', 'type', 'status', 'amountK', 'currencyPoint',
                       'stopMove', 'stop', 'stopRate', 'limit', 'limitRate',
                       'isEntryOrder', 'ocoBulkId', 'isNetQuantity',
                       'isLimitOrder', 'isStopOrder', 'isELSOrder',
                       'stopPegBaseType', 'limitPegBaseType', 'range']
    status_values = {0: 'Unknown', 1: 'Waiting', 2: 'In Process',
                     3: 'Canceled', 4: 'Requoted', 5: 'Margin Call',
                     6: 'Executing', 7: 'Pending', 8: 'Equity Stop',
                     9: 'Executed', 10: 'Activated'}

    def __init__(self, connection, kwargs):
        self.__con__ = connection
        self.logger = self.__con__.logger
        self.parameter = set()
        self.__tradeId__ = 0
        for keyword in self.order_parameter:
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

    def get_orderId(self):
        """Return the value of attribute orderId."""
        return self.__orderId__

    def get_time(self):
        """Return the value of attribute time."""
        return self.__time__

    def get_accountName(self):
        """Return the value of attribute accountName."""
        return self.__accountName__

    def get_accountId(self):
        """Return the value of attribute accountId."""
        return self.__accountId__

    def get_timeInForce(self):
        """Return the value of attribute timeInForce."""
        return self.__timeInForce__

    def get_currency(self):
        """Return the value of attribute currency."""
        return self.__currency__

    def get_isBuy(self):
        """Return the value of attribute isBuy."""
        return self.__isBuy__

    def get_buy(self):
        """Return the value of attribute buy."""
        return self.__buy__

    def get_sell(self):
        """Return the value of attribute sell."""
        return self.__sell__

    def get_type(self):
        """Return the value of attribute type."""
        return self.__type__

    def get_status(self):
        """Return the value of attribute status."""
        return self.__status__

    def get_amount(self):
        """Return the value of attribute amountK."""
        return self.__amountK__

    def get_currencyPoint(self):
        """Return the value of attribute currencyPoint."""
        return self.__currencyPoint__

    def get_stopMove(self):
        """Return the value of attribute stopMove."""
        return self.__stopMove__

    def get_stop(self):
        """Return the value of attribute stop."""
        return self.__stop__

    def get_stopRate(self):
        """Return the value of attribute stopRate."""
        return self.__stopRate__

    def get_limit(self):
        """Return the value of attribute limit."""
        return self.__limit__

    def get_limitRate(self):
        """Return the value of attribute limitRate."""
        return self.__limitRate__

    def get_isEntryOrder(self):
        """Return the value of attribute isEntryOrder."""
        return self.__isEntryOrder__

    def get_ocoBulkId(self):
        """Return the value of attribute ocoBulkId."""
        return self.__ocoBulkId__

    def get_isNetQuantity(self):
        """Return the value of attribute isNetQuantity."""
        return self.__isNetQuantity__

    def get_isLimitOrder(self):
        """Return the value of attribute isLimitOrder."""
        return self.__isLimitOrder__

    def get_isStopOrder(self):
        """Return the value of attribute isStopOrder."""
        return self.__isStopOrder__

    def get_isELSOrder(self):
        """Return the value of attribute isELSOrder."""
        return self.__isELSOrder__

    def get_stopPegBaseType(self):
        """Return the value of attribute stopPegBaseType."""
        return self.__stopPegBaseType__

    def get_limitPegBaseType(self):
        """Return the value of attribute limitPegBaseType."""
        return self.__limitPegBaseType__

    def get_range(self):
        """Return the value of attribute range."""
        return self.__range__

    def get_tradeId(self):
        """ Return the trade id."""
        return self.__tradeId__

    def get_associated_trade(self):
        """ Returns the potial assoziated trade object."""

        if self.__tradeId__ in self.__con__.open_pos:
            return self.__con__.open_pos[self.__tradeId__]
        elif self.__tradeId__ in self.__con__.closed_pos:
            return self.__con__.closed_pos[self.__tradeId__]
        else:
            self.logger.warn('No trade assoziated to order %s.'
                             % self.__orderId__)
            return None

    def set_amount(self, amount):
        """ Set a value for the attribute amount."""
        try:
            amount = int(amount)
        except:
            raise TypeError('amount must be an interger.')
        if self.__isBuy__:
            rate = self.__buy__
        else:
            rate = self.__sell__
        self.__con__.change_order(self.__orderId__, amount, rate)

    def set_rate(self, rate):
        """ Set a value for the attribute rate."""
        try:
            rate = float(rate)
        except:
            raise TypeError('rate must be a number.')
        self.__con__.change_order(self.__orderId__, self.__amountK__, rate)

    def set_range(self, order_range):
        """ Set a value for the attribute range."""
        try:
            order_range = float(order_range)
        except:
            raise TypeError('order_range must be a number.')
        if self.__isBuy__:
            rate = self.__buy__
        else:
            rate = self.__sell__
        self.__con__.change_order(self.__orderId__, self.__amountK__, rate,
                                  order_range=order_range)

    def set_trailing_step(self, trailing_step):
        """ Set a value for the attribute trailingStep."""
        try:
            trailing_step = int(trailing_step)
        except:
            raise TypeError('trailingStep must be a number.')
        if self.__isBuy__:
            rate = self.__buy__
        else:
            rate = self.__sell__
        self.__con__.change_order(self.__orderId__, self.__amountK__, rate,
                                  trailing_step=trailing_step)

    def set_stop_rate(self, stop_rate, is_in_pips=True):
        """ Set a new value for the stop rate.

        Arguments:

        stop_rate: float,
            the new stop rate.

        is_in_pips: bool (default=True),
            whether the new rate is in pips or not.
        """

        try:
            stop_rate = float(stop_rate)
        except:
            raise TypeError('stop_rate must be a number.')

        try:
            is_in_pips = bool(is_in_pips)
        except:
            raise ValueError('is_in_pips must be a boolean.')

        self.__con__.change_order_stop_limit(self.__orderId__, stop=stop_rate,
                                             limit=None,
                                             is_stop_in_pips=is_in_pips,
                                             is_limit_in_pips=None)

    def set_limit_rate(self, limit_rate, is_in_pips=True):
        """ Set a new value for the limit rate.

        Arguments:

        limit_rate: float,
            the new limit rate.

        is_in_pips: bool (default=True),
            whether the new rate is in pips or not.
        """

        try:
            limit_rate = float(limit_rate)
        except:
            raise TypeError('limit_rate must be a number.')

        try:
            is_in_pips = bool(is_in_pips)
        except:
            raise ValueError('is_in_pips must be a boolean.')

        self.__con__.change_order_stop_limit(self.__orderId__,
                                             stop=None,
                                             limit=limit_rate,
                                             is_stop_in_pips=None,
                                             is_limit_in_pips=False)

    def delete(self):
        """ Delete the order."""
        self.__con__.delete_order(self.__orderId__)
        count = 0
        while count < 300:
            if self.__orderId__ in self.__con__.orders:
                time.sleep(1)
                count += 1
            else:
                break

    def __set_attribute__(self, attribute, value):
        if attribute in ['orderId', 'accountId', 'tradeId', 'ocoBulkId']:
            try:
                value = int(value)
            except:
                raise ValueError('value must be an integer.')
        elif attribute in ['time', 'expireDate']:
            if value != '':
                try:
                    value = dt.datetime.strptime(value+'000', '%m%d%Y%H%M%S%f')
                except:
                    raise ValueError('Can not parse value %s to datetime'
                                     % value)
        elif attribute == 'status':
            try:
                value = self.status_values[int(value)]
            except:
                raise ValueError('Unknown status: %s.' % value)
        elif attribute in ['t', 'ratePrecision']:
            return 0
        self.parameter.add(attribute)
        setattr(self, '__'+attribute+'__', value)
