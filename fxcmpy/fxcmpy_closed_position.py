#
# fxcmpy_closed_position -- A Python Wrapper Class for the
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


class fxcmpy_closed_position(object):
    """ A convenience class for a better handling of closed positions. """
    position_parameter = ['tradeId', 'accountName', 'roll', 'com',
                          'open', 'valueDate', 'grossPL', 'close', 'visiblePL',
                          'currency', 'isBuy', 'amountK',
                          'currencyPoint', 'closeTime', 'openTime']

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
        elif attribute in ['closeTime', 'openTime', 'valueDate']:
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

    def get_close_time(self):
        """Return the value of the attribute closeTime."""

        return self.__closeTime__

    def get_open_time(self):
        """Return the value of the attribute openTime."""

        return self.__openTime__
