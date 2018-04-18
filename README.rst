
Quick Start
===========

Disclaimer
----------

Trading forex/CFDs on margin carries a high level of risk and may not be
suitable for all investors as you could sustain losses in excess of
deposits. Leverage can work against you. Due to the certain restrictions
imposed by the local law and regulation, German resident retail
client(s) could sustain a total loss of deposited funds but are not
subject to subsequent payment obligations beyond the deposited funds. Be
aware and fully understand all risks associated with the market and
trading. Prior to trading any products, carefully consider your
financial situation and experience level. Any opinions, news, research,
analyses, prices, or other information is provided as general market
commentary, and does not constitute investment advice. FXCM Forex
Capital Markets Ltd. (henceforth "FXCM", see http://fxcm.com) will not
accept liability for any loss or damage, including without limitation
to, any loss of profit, which may arise directly or indirectly from use
of or reliance on such information.

Introduction
------------

FXCM provides a **RESTful API** (henceforth the "API" to interact with
its trading platform. Among others, it allows the retrieval of
**historical data** as well as of **streaming data**. In addition, it
allows to place different types of **orders** and to read out **account
information**. The overall goal is to allow the implementation
**automated, algortithmic trading programs**.

In this documentation, you learn all about the ``fxcmpy.py`` Python
wrapper package (henceforth just ``fxcmpy.py`` or "package").

Demo Account
------------

To get started with the the API and the package, a **demo account** with
FXCM is sufficient. You can open such an account under
https://www.fxcm.com/uk/forex-trading-demo/.

Package Installation
--------------------

Installation happens via ``pip`` install on the command line.

::

    pip install fxcmpy

Working in an interactive context (e.g. ``IPython`` or ``Jupyter``), you
can then check whether the package is installed via:

.. code:: ipython3

    import fxcmpy

.. code:: ipython3

    fxcmpy.__version__

API Token
---------

To connect to the API, you need an **API token** that you can create or
revoke from within your (demo) account in the Trading Station
https://tradingstation.fxcm.com/.

In an interactive context, you can use e.g. a variable called ``TOKEN``
to reference your unique API token.

::

    TOKEN = YOUR_FXCM_API_TOKEN

Connecting to the server, then boils down to the following line of code.

::

    con = fxcmpy.fxcmpy(access_token=TOKEN, log_level='error')

However, it is recommended to store the API token in a **configuration
file** which allows for re-usability and hides the token on the GUI
level. The file should contain the following lines.

::

    [FXCM]
    log_level = error
    log_file = PATH_TO_AND_NAME_OF_LOG_FILE
    access_token = YOUR_FXCM_API_TOKEN

It is assumed onwards that this file is in the current working directory
and that its name is ``fxcm.cfg``.

With such a configuration file in the current working directory, only
the filename need to be passed as a parameter to **connect to the API**.

.. code:: ipython3

    con = fxcmpy.fxcmpy(config_file='fxcm.cfg')

First Steps
-----------

Having established the connection to the API, data retrieval is
straightforward.

For example, you can look up which **instruments** are available via the
``con.get_instruments()`` method.

.. code:: ipython3

    print(con.get_instruments())


.. parsed-literal::

    ['EUR/USD', 'USD/JPY', 'GBP/USD', 'USD/CHF', 'EUR/CHF', 'AUD/USD', 'USD/CAD', 'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'CHF/JPY', 'GBP/CHF', 'EUR/AUD', 'EUR/CAD', 'AUD/CAD', 'AUD/JPY', 'CAD/JPY', 'NZD/JPY', 'GBP/CAD', 'GBP/NZD', 'GBP/AUD', 'AUD/NZD', 'USD/SEK', 'EUR/SEK', 'EUR/NOK', 'USD/NOK', 'USD/MXN', 'AUD/CHF', 'EUR/NZD', 'USD/ZAR', 'USD/HKD', 'ZAR/JPY', 'USD/TRY', 'EUR/TRY', 'NZD/CHF', 'CAD/CHF', 'NZD/CAD', 'TRY/JPY', 'USD/CNH', 'AUS200', 'ESP35', 'FRA40', 'GER30', 'HKG33', 'JPN225', 'NAS100', 'SPX500', 'UK100', 'US30', 'Copper', 'EUSTX50', 'USDOLLAR', 'USOil', 'UKOil', 'NGAS', 'Bund', 'XAU/USD', 'XAG/USD']


Simlarly, **historical data** is retrieved via the ``con.get_cancles()``
method.

.. code:: ipython3

    data = con.get_candles('EUR/USD', period='m1', number=250)

.. code:: ipython3

    data.head()




.. raw:: html

    <div>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>bidopen</th>
          <th>bidclose</th>
          <th>bidhigh</th>
          <th>bidlow</th>
          <th>askopen</th>
          <th>askclose</th>
          <th>askhigh</th>
          <th>asklow</th>
          <th>tickqty</th>
        </tr>
        <tr>
          <th>date</th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2018-02-23 17:50:00</th>
          <td>1.23033</td>
          <td>1.23044</td>
          <td>1.23044</td>
          <td>1.23033</td>
          <td>1.23034</td>
          <td>1.23045</td>
          <td>1.23045</td>
          <td>1.23034</td>
          <td>60</td>
        </tr>
        <tr>
          <th>2018-02-23 17:51:00</th>
          <td>1.23045</td>
          <td>1.23057</td>
          <td>1.23057</td>
          <td>1.23044</td>
          <td>1.23046</td>
          <td>1.23058</td>
          <td>1.23058</td>
          <td>1.23044</td>
          <td>148</td>
        </tr>
        <tr>
          <th>2018-02-23 17:52:00</th>
          <td>1.23057</td>
          <td>1.23058</td>
          <td>1.23059</td>
          <td>1.23054</td>
          <td>1.23058</td>
          <td>1.23059</td>
          <td>1.23060</td>
          <td>1.23053</td>
          <td>56</td>
        </tr>
        <tr>
          <th>2018-02-23 17:53:00</th>
          <td>1.23058</td>
          <td>1.23054</td>
          <td>1.23059</td>
          <td>1.23049</td>
          <td>1.23059</td>
          <td>1.23054</td>
          <td>1.23061</td>
          <td>1.23049</td>
          <td>62</td>
        </tr>
        <tr>
          <th>2018-02-23 17:54:00</th>
          <td>1.23053</td>
          <td>1.23056</td>
          <td>1.23063</td>
          <td>1.23053</td>
          <td>1.23053</td>
          <td>1.23055</td>
          <td>1.23065</td>
          <td>1.23053</td>
          <td>125</td>
        </tr>
      </tbody>
    </table>
    </div>



.. code:: ipython3

    data.tail()




.. raw:: html

    <div>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>bidopen</th>
          <th>bidclose</th>
          <th>bidhigh</th>
          <th>bidlow</th>
          <th>askopen</th>
          <th>askclose</th>
          <th>askhigh</th>
          <th>asklow</th>
          <th>tickqty</th>
        </tr>
        <tr>
          <th>date</th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>2018-02-23 21:55:00</th>
          <td>1.22962</td>
          <td>1.22965</td>
          <td>1.22966</td>
          <td>1.22958</td>
          <td>1.22973</td>
          <td>1.22977</td>
          <td>1.22978</td>
          <td>1.22971</td>
          <td>61</td>
        </tr>
        <tr>
          <th>2018-02-23 21:56:00</th>
          <td>1.22965</td>
          <td>1.22948</td>
          <td>1.22969</td>
          <td>1.22931</td>
          <td>1.22977</td>
          <td>1.22970</td>
          <td>1.22980</td>
          <td>1.22946</td>
          <td>138</td>
        </tr>
        <tr>
          <th>2018-02-23 21:57:00</th>
          <td>1.22948</td>
          <td>1.22942</td>
          <td>1.22949</td>
          <td>1.22934</td>
          <td>1.22970</td>
          <td>1.22971</td>
          <td>1.22977</td>
          <td>1.22965</td>
          <td>52</td>
        </tr>
        <tr>
          <th>2018-02-23 21:58:00</th>
          <td>1.22942</td>
          <td>1.22936</td>
          <td>1.22948</td>
          <td>1.22931</td>
          <td>1.22971</td>
          <td>1.22978</td>
          <td>1.22988</td>
          <td>1.22964</td>
          <td>77</td>
        </tr>
        <tr>
          <th>2018-02-23 21:59:00</th>
          <td>1.22937</td>
          <td>1.22933</td>
          <td>1.22938</td>
          <td>1.22926</td>
          <td>1.22979</td>
          <td>1.22987</td>
          <td>1.22987</td>
          <td>1.22979</td>
          <td>14</td>
        </tr>
      </tbody>
    </table>
    </div>



Such data can be **visualized** with standard functionality of Python
and pandas, for instance.

.. code:: ipython3

    from pylab import plt
    plt.style.use('seaborn')
    %matplotlib inline

.. code:: ipython3

    data['askclose'].plot(figsize=(10, 6));



.. image:: images/output_30_0.png


Resources
---------

If you have questions regarding **demo or full accounts**, reach out to:

-  info@fxcm.co.uk
-  +44 (0) 207 398 4050

If you have questions regarding the **RESTful API**, reach out to:

-  api@fxcm.com

The **detailed documentation of this wrapper** is found under:

-  http://fxcmpy.tpq.io

The **detailed documentation of the API** is found under:

-  https://github.com/fxcm/RestAPI

The book *Python for Finance — Mastering Data-Driven Finance* (O'Reilly)
provides detailed information about the use of **Python in Finance**:

-  http://pff.tpq.io/.

In-depth courses and programs about **Python for Algorithmic Trading**:

-  http://pyalgo.tpq.io
-  http://certificate.tpq.io.
