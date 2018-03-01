#
# fxcmpy_oco_order -- A Python Wrapper Class for the
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
from fxcmpy.fxcmpy_order import fxcmpy_order


class fxcmpy_oco_order(object):
    """ A class to realize oco orders of the FXCM API.

    Caution:

    Do not initialize fxcm oco order object manually, these orders will not
    registered by the fxcm server, use the create_oco_order() method of the
    fxcm class instead.
    """

    def __init__(self, bulk_id, orders, connection, logger):
        self.orders = dict()
        self.logger = logger
        self.__con = connection

        try:
            self.bulk_id = int(bulk_id)
        except:
            raise TypeError('bulk_id must be an integer.')

        for order in orders:
            if not isinstance(order, fxcmpy_order):
                raise TypeError('orders must be of type fxcmpy_orders.')
            order_id = order.get_orderId()
            self.orders[order_id] = order
            self.logger.info('Add order with id %s to oco order.' % order_id)

    def get_ocoBulkId(self):
        """ Return the id. """
        return self.bulk_id

    def get_orders(self):
        """ Return all orders of the oco order."""
        return list(self.orders.values())

    def get_order_ids(self):
        """ Return all ids of the containing orders."""
        return list(self.orders.keys())

    def add_order(self, orders):
        """ Add orders to the oco order.

        Arguments:

        orders: list,
            list of the orders to add to the oco order.

        """

        order_ids = list()
        for order in orders:
            if not isinstance(order, fxcmpy_order):
                self.logger.error('Invalid order in add_order: %s.' % order)
                raise ValueError('order must be of type fxcmpy_order.')
            if order.get_ocoBulkId() == self.bulk_id:
                self.logger.warn('order allready member of oco order.')
            else:
                order_ids.append(order.get_orderId())
        self.__con.add_to_oco(order_ids, self.bulk_id)
        self.logger.info('Orders %s aded to oco order %s.'
                         % (order_ids, self.bulk_id))

    def remove_order(self, orders):
        """ Remove orders from the oco order.

        Arguments:

        orders: list,
            list of the order to remove from the oco order.

        """

        order_ids = list()
        for order in orders:
            if not isinstance(order, fxcmpy_order):
                self.logger.error('Invalid order in add_order: %s.' % order)
                raise ValueError('order must be of type fxcmpy_order.')
            if order.get_ocoBulkId() != self.bulk_id:
                self.logger.warn('order not member of oco order.')
            else:
                order_ids.append(order.get_orderId())

        self.__con.remove_from_oco(order_ids)
        self.logger.info('Orders %s removed from oco order %s.'
                         % (order_ids, self.bulk_id))

    def edit_order(self, add_orders, remove_orders):
        """ Add or remove orders to / from the oco order.

        Arguments:

        add_orders: list,
            list of the orders to add to the oco order.

        remove_orders: list,
            list of the order to remove from the oco order.

        """

        add_order_ids = list()
        remove_order_ids = list()

        for order in add_orders:
            if not isinstance(order, fxcmpy_order):
                self.logger.error('Invalid order in add_orders: %s.' % order)
                raise ValueError('order must be of type fxcmpy_order.')
            if order.get_ocoBulkId() == self.bulk_id:
                self.logger.warn('order allready member of oco order.')
            else:
                add_order_ids.append(order.get_orderId())

        for order in remove_orders:
            if not isinstance(order, fxcmpy_order):
                self.logger.error('Invalid order in remove_orders: %s' % order)
                raise ValueError('order must be of type fxcmpy_order.')
            if order.get_ocoBulkId() != self.bulk_id:
                self.logger.warn('order is not member of oco order.')
            else:
                remove_order_ids.append(order.get_orderId())

        self.__con.edit_oco(self.bulk_id, add_order_ids=add_order_ids,
                            remove_order_ids=remove_order_ids)

    def __add__(self, order):
        if not isinstance(order, fxcmpy_order):
                raise TypeError('orders must be of type fxcmpy_orders.')
        order_id = order.get_orderId()
        self.orders[order_id] = order

    def __remove__(self, order):
        if not isinstance(order, fxcmpy_order):
                raise TypeError('orders must be of type fxcmpy_orders.')
        order_id = order.get_orderId()
        del self.orders[order_id]
