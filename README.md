
<img src="http://hilpisch.com/tpq_logo.png" alt="The Python Quants" width="35%" align="right" border="0"><br>

# fxcmpy  - a python wrapper for the FXCM API

#### By
#### Michael Schwed
#### The Python Quants GmbH
#### August 2017

The import 


```python
import fxcmpy
import importlib
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
%matplotlib notebook

```


```python
importlib.reload(fxcmpy)
```

## Creating an instance of fxcmpy.

This is, as usually, done by the class constructor. 

**fxcmpy(user='', password='', config_file='', log_file='', log_level='')**, where

* **user**: is the user name as provided by **FXCM**
* **password**: is the user's password
* **config_file**: the path to an optional configuration file containing values for the other parameter.
* **log_file**: the path to a log file. If not given, log messages are print to stdout.
* **log_level**: Determines the granularity of the log messages. Possible values are : *error*, *warn*, *info* and *debug*. Default is *warn*

If one or more of the arguments *user*, *password*, *log_file* or *log_level* are not given, fxcmpy checks the value of config_file, if it points to an existing configuration file, fxcmpy tries to read the missing arguments from that file. 


```python
con = fxcmpy.fxcmpy(user='XXXXXXX', password='XXXX', log_level='info')
```

    |INFO|2017-08-11 14:16:47,169|Connecting FXCM Server for user d101537826|
    |INFO|2017-08-11 14:16:47,170|Requesting access token...|
    |INFO|2017-08-11 14:16:47,544|Received temporary token 13b1f829ca898628925ec0f30ee7a88dbc7df2e0|
    |INFO|2017-08-11 14:16:50,334|Received access token|
    |INFO|2017-08-11 14:16:51,138|Connection established|



```python
con.is_connected()
```




    True



## Available instruments

To get the available instruments, use the method 

**get_instruments()**

Returns a list of the symbols of the available instruments.


```python
con.get_instruments()
```




    ['EUR/USD',
     'USD/JPY',
     'GBP/USD',
     'USD/CHF',
     'EUR/CHF',
     'AUD/USD',
     'USD/CAD',
     'NZD/USD',
     'EUR/GBP',
     'EUR/JPY',
     'GBP/JPY',
     'CHF/JPY',
     'GBP/CHF',
     'EUR/AUD',
     'EUR/CAD',
     'AUD/CAD',
     'AUD/JPY',
     'CAD/JPY',
     'NZD/JPY',
     'GBP/CAD',
     'GBP/NZD',
     'GBP/AUD',
     'AUD/NZD',
     'USD/SEK',
     'EUR/SEK',
     'EUR/NOK',
     'USD/NOK',
     'USD/MXN',
     'AUD/CHF',
     'EUR/NZD',
     'EUR/CZK',
     'USD/CZK',
     'USD/ZAR',
     'USD/HKD',
     'ZAR/JPY',
     'USD/TRY',
     'EUR/TRY',
     'NZD/CHF',
     'CAD/CHF',
     'NZD/CAD',
     'TRY/JPY',
     'USD/CNH',
     'AUS200',
     'ESP35',
     'FRA40',
     'GER30',
     'HKG33',
     'JPN225',
     'NAS100',
     'SPX500',
     'UK100',
     'US30',
     'Copper',
     'EUSTX50',
     'USDOLLAR',
     'USOil',
     'UKOil',
     'NGAS',
     'Bund',
     'XAU/USD',
     'XAG/USD']



## Subscribing for market data

You can subscribe for market data with the method 

**subscribe_market_data(symbol, add_callbacks=list())**, where

* **symbol**: is the symbol of an available instrument as given by *get_instruments()*
* **add_callbacks**: a list of methods. Default is an empty list. A typical callback function has to     
  look as follows:
  
  **callback_function(data, dataframe)**, where
  * **data**: is a *json* object.
  * **dataframe**: is a *Pandas DataFrame* object.


The method creates a stream of the symbols data. That data will be stored in a *Pandas DataFrame* object. After that, the methods found in *add_callbacks* are called with the data send by the server and the *Pandas DataFrame*, the data is stored in.



```python
con.subscribe_market_data('EUR/USD')
```

    |INFO|2017-08-11 14:16:58,086|Try to subscribe for EUR/USD|


The object will remember subscribed symbols and their values. 


```python
symbols = con.get_subscribed_symbols()
```


```python
print(symbols)
```

    ['EUR/USD']



```python
con.is_subscribed('EUR/USD')
```




    True



Prices for a symbol are collected in a *Pandas DataFrame*


```python
con.get_prices('EUR/USD')
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Bid</th>
      <th>High</th>
      <th>Low</th>
      <th>Close</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2017-08-11 12:16:58</th>
      <td>1.17646</td>
      <td>1.17671</td>
      <td>1.17806</td>
      <td>1.17476</td>
    </tr>
    <tr>
      <th>2017-08-11 12:16:59</th>
      <td>1.17646</td>
      <td>1.17671</td>
      <td>1.17806</td>
      <td>1.17476</td>
    </tr>
    <tr>
      <th>2017-08-11 12:16:59</th>
      <td>1.17646</td>
      <td>1.17669</td>
      <td>1.17806</td>
      <td>1.17476</td>
    </tr>
    <tr>
      <th>2017-08-11 12:16:59</th>
      <td>1.17645</td>
      <td>1.17669</td>
      <td>1.17806</td>
      <td>1.17476</td>
    </tr>
    <tr>
      <th>2017-08-11 12:17:00</th>
      <td>1.17645</td>
      <td>1.17668</td>
      <td>1.17806</td>
      <td>1.17476</td>
    </tr>
    <tr>
      <th>2017-08-11 12:17:01</th>
      <td>1.17646</td>
      <td>1.17669</td>
      <td>1.17806</td>
      <td>1.17476</td>
    </tr>
    <tr>
      <th>2017-08-11 12:17:01</th>
      <td>1.17648</td>
      <td>1.17672</td>
      <td>1.17806</td>
      <td>1.17476</td>
    </tr>
    <tr>
      <th>2017-08-11 12:17:02</th>
      <td>1.17649</td>
      <td>1.17672</td>
      <td>1.17806</td>
      <td>1.17476</td>
    </tr>
    <tr>
      <th>2017-08-11 12:17:04</th>
      <td>1.17649</td>
      <td>1.17673</td>
      <td>1.17806</td>
      <td>1.17476</td>
    </tr>
    <tr>
      <th>2017-08-11 12:17:05</th>
      <td>1.17649</td>
      <td>1.17672</td>
      <td>1.17806</td>
      <td>1.17476</td>
    </tr>
  </tbody>
</table>
</div>



Unsubscribe works in the same way:


```python
con.unsubscribe_market_data('EUR/USD')
```

    |INFO|2017-08-11 14:17:09,169|Try to unsubscribe for EUR/USD|



```python
con.is_subscribed('EUR/USD')
```




    False




```python
con.get_prices('EUR/USD')
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Bid</th>
      <th>High</th>
      <th>Low</th>
      <th>Close</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>



### Additional callbacks

As an example, we define a method called test, that method prints new incoming data and also the length of the *Pandas DataFrame* storing the data.


```python
def test(data, dataframe):
    print('New values received for %s: %s, %s, %s, %s, %s' 
          %(data['Symbol'], pd.to_datetime(int(data['Updated']), unit='s'), 
            data['Rates'][0], data['Rates'][1], data['Rates'][2], data['Rates'][3]))
    print('Length of the Pandas Dataframe: %s' %len(dataframe))
```

Now, we subscribe to the 'EUR/USD' again. To stop the notebook from generating output, just execute the very next cell.


```python
con.subscribe_market_data('EUR/USD', (test,))
```

    |INFO|2017-08-11 13:47:05,866|Try to subscribe for EUR/USD|
    |INFO|2017-08-11 13:47:05,867|Adding callback method test for symbol EUR/USD|



```python
con.unsubscribe_market_data('EUR/USD')
```

    |INFO|2017-08-11 13:47:06,649|Try to unsubscribe for EUR/USD|


### Callbacks with global variables

To use other variables than the *json* and the *DataFrame* objects in your callbacks, use *globals*.
As an example, we create an empty plot and define a callback which updates that plot everytime new data is received. 


```python
x = np.arange(100)
y = 100*[1,]
fig,ax = plt.subplots(1,1)
ax.set_ylabel('Value 1')
ax.set_xlim(0,100)
ax.set_ylim(1,1.2)
ax.plot(x,y)
```


    <IPython.core.display.Javascript object>



<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAoAAAAHgCAYAAAA10dzkAAAgAElEQVR4nO3deZxV9X3/8XdMG5ufxKRtFhNbv2qSxq2KWTSSVkmaxGDSRJtYsyrWJE3UGm0Sv2hcRkWJxAUV96iIEUWjUfmyCAjDKgPIjuzrALLDsAjD9vn9ce7g9TLg3Ps958yd+no+HufRu3zvfE45Q3xx554zEgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAVex0Sf0krZBkks5+h/X/IWmIpDWSNkl6VdKZzaw7V9JsSdslTZd0VjNrLpG0uLCmTtIpZe89AAAAytZJUldJ56hlAdhD0pWSviDp05JukbRD0slFazpI2iXpt5KOlXRTYc0JRWvOk9Qo6UJJx0l6SNIGSR+N+v8GAAAAZWlJADZnpqTriu73lRRK1oyT9EDR/TpJPYvuHyRpuaQuFcwHAABAhSoJwIMkLZV0adFjSyVdXrLuBklTC7ffp+QdwtJZj0t6scz5AAAAiFBJAF4pab3e/qPbHZJ+ULLuYkmrCrc/UZh1Wsma7kreGdyfgyUdWrId2cxjbGxsbGxsbNW9HS7pPUJVKDcAfyhpq6SvljyeVQDWFF7HxsbGxsbG1va3w4WqYGp5AH5f0puSvtnMc1n9CLj0HcDDJVl9fb01NDSwsbGxsbGxtYGtvr6+KQAPbWFzIGMtDcAfSNom6Tv7eb6vkkvLFBurfU8Cuafo/kGSlqm8k0AOlWQNDQ0GAADahoaGBgKwCrST1L6wmaQrCrePKDzfTVLvovU/lLRTyY90DyvaPli0pkNhza8lHaPkR7fNXQZmu6QLlFwq5kEll4H5WBn7TgACANDGEIDVoaOa/7l8r8LzvSTVFq2vfYf1Tc6VNEfJtf5mqPkLQV8qaUlhTZ2kU8vcdwIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgBELAIQAIA2hgCsDqdL6idphZKDcfY7rP+4pD6S5kraI6lHM2tqC1+rdOtftKammednl7nvBCAAAG0MAVgdOknqKukctSwAj5R0l6TzJU1W8wH4d5IOK9qOl7RLUueiNTWSZpSs+3CZ+04AAgCQoj+NW2xfv2OEfe2O2ma3r98xws68M9m+0WOkdWpm++bdI+3f7xll3+452s6+d7Sdc+9o27h1x94ZBGD1aUkAFqtV8wFY6nJJmyQdUvRYjaQpZcxqDgEIAECKvnLbcHM+pL6t29K4dwYBWH2yCsDpkh4qeaxG0lYlP3peKOlJSUeUMVsiAAEASNW/3jrMnA/Wa8wiGzN/zdu3eWts9Lw1NmruGhs5d7WNmLPvVjtntQ2fvcqGzVplQ19faYNnrrRBM96wxp27984gAKtPFgF4SuHrnlLyeCdJ50o6UdKZksZKWiLpAwf4Wgcr+WZp2g4XAQgAQGo6dHvFnA82ZemGzGYQgNUniwB8UNK0FnytD0lqkHTRAdbUqJmTSwhAAADScerNQ835YNOXbcxsBgFYfdIOwEOURN2vWvj1JkjqdoDneQcQAIAMfe6mIeZ8sFlvZPffVgKw+qQdgJ0lbZf09y34Wu0kbZB0WRnz+QwgAAApan/Dy+Z8sHmrNmU2gwCsDu0ktS9sJumKwu2mEzK6Sepd8pqm9ROVnLzRXtJxzXztUZKe3s/c2ySdoeSyMh0kDZG0RtJHyth3AhAAgBSdcP0gcz7YwjVbMptBAFaHjmr+os29Cs/3UvJOX7Hm1i8uWfOZwuNf28/cp5WcAdwoaVnh/ifL3HcCEACAFB177UBzPtjSdVszm0EAIhYBCABAij79uwHmfLDlG97MbAYBiFgEIAAAKTr6qv7mfLBVDdsym0EAIhYBCABASvbs2bP3N3es2bw9szkEIGIRgAAApGTnrt17A3DD1sZ3fkGFCEDEIgABAEjJ9p279gbgpm07MptDACIWAQgAQEq2Nu7cG4BvNu7KbA4BiFgEIAAAKWnYtmNvADbu3J3dHAIQkQhAAABSsn5L494A3L17T2ZzCEDEIgABAEjJ6k3bzflgR3YJmc4hABGLAAQAICVvbNxmzgf71NX9M51DACIWAQgAQErq128154N95poBmc4hABGLAAQAICWL124x54Mdf92gTOcQgIhFAAIAkJL5qzeb88H++XoCENWNAAQAICVzVm4y54OdfOPgTOcQgIhFAAIAkJLXVzSY88E+33VIpnMIQMQiAAEASMn0ZRvN+WBfvGVopnMIQMQiAAEASMnkpRvM+WBf+v0rmc4hABGLAAQAICUTF68z54Od0X1YpnMIQMQiAAEASMm4BWvN+WBfuW14pnMIQMQiAAEASMmYeWvM+WBfv2NEpnMIQMQiAAEASMmIOavN+WCdeozMdA4BiFgEIAAAKRk2a5U5H+xbd4/KdA4BiFgEIAAAKRk8c6U5H+w7PUdnOocARCwCEACAlAycvsKcD/bd+8ZkOocARCwCEACAlISpSQD+5wNjM51DACIWAQgAQEpemLzMnA/2w4dfzXQOAYhYBCAAACl57rV6cz7YTx6py3QOAYhYBCAAACnpO2GpOR/swsfGZzqHAEQsAhAAgJT0qVtizgf76eMTMp1DACIWAQgAQEp6v7rYnA/2iycmZjqHAEQsAhAAgJQ8NnqhOR/skidfy3QOAYhYBCAAACl5eOQCcz7YZU9NynQOAYhYBCAAACl5oHa+OR/sir6TM51DACIWAQgAQEruHT7PnA/222enZDqHAEQsAhAAgJTcPXSuOR+sy3PTMp1DACIWAQgAQEruGDzHnA92zV+mZzqHAKwOp0vqJ2mFkoNx9jus/7ikPpLmStojqUczazoXvlbxtr2ZdZdIWlx4rk7SKWXuOwEIAEBK/jBotjkf7PoXZ2Q6hwCsDp0kdZV0jloWgEdKukvS+ZIma/8B2CDpsKLtYyVrzpPUKOlCScdJekjSBkkfLWPfCUAAAFLSbcAscz7YTf1mZjqHAKw+LQnAYrXafwBufIfX1knqWXT/IEnLJXUpYz4BCABASrqGmeZ8sFsGvJ7pHAKw+qQZgLskLZFUL+lFSccXPf++wvOlsx4vrG0pAhAAgJTUvDTDnA/WfdCsTOcQgNUnrQA8TcmPiNtLOkPJZwwbJP1D4flPFGadVvK67kreGdyfg5V8szRth4sABAAgFde+MN2cD3b7y7MznUMAVp+0ArDUX0uaL+mmwv1KA7BG+55cQgACAJCCq56fZs4H6zFkbqZzCMDqk1UAStKzkp4q3K70R8C8AwgAQEaufHaqOR+s57B5mc4hAKtPVgH4XkmzJd1R9FidpHuK7h8kaZk4CQQAgFbx62emmPPB7q+dn+kcArA6tFPyWb32Sg7GFYXbRxSe7yapd8lrmtZPlPRk4fZxRc9fJ+nrko6W9Fkl7/xtK1lznpLr/10g6VhJDyq5DEzp5WIOhAAEACAllz892ZwP9vDIBZnOIQCrQ0c187k6Sb0Kz/dS8k5fsebWLy56/k4lZwA3Slopqb+kk5uZfWnRujpJp5a57wQgAAApubTPJHM+2KOjF2Y6hwBELAIQAICU/PJPE835YL3HLsp0DgGIWAQgAAAp+dnjE8z5YE+OW5LpHAIQsQhAAABS8l+PjTfng/UdvzTTOQQgYhGAAACk5PxH6sz5YH+eWJ/pHAIQsQhAAABS8qOHx5nzwf4yaVmmcwhAxCIAAQBIyXkPjjXng700ZXmmcwhAxCIAAQBIybn3JwE4YNqKTOcQgIhFAAIAkJJz7h1tzgd7ecYbmc4hABGLAAQAICXfvmeUOR/slVkrM51DACIWAQgAQErOumukOR+sds7qTOcQgIhFAAIAkJIz7xxhzgcbPW9NpnMIQMQiAAEASMm/3V5rzgd7dcHaTOcQgIhFAAIAkJKOfxhuzgebsGhdpnMIQMQiAAEASMm/3PqKOR/stSXrM51DACIWAQgAQEpOu2WoOR9sav2GTOcQgIhFAAIAkJIvdB1izgebsXxjpnMIQMQiAAEASMnnbhpszgeb/camTOcQgIhFAAIAkJKTbnjZnA82b9XmTOcQgIhFAAIAkJITrhtkzgdbtGZLpnMIQMQiAAEASMkx1ww054MtXbc10zkEIGIRgAAApOTTVw8w54Ot2PhmpnMIQMQiAAEASMlRXYI5H2zVpm2ZziEAEYsABAAgBbt37zHnkwBct6Ux01kEIGIRgAAApGDHrt17A3Dj1h2ZziIAEYsABAAgBdt27NobgJu378x0FgGIWAQgAAAp2Lx9594A3LZjV6azCEDEIgABAEjBxjd37A3AHbt2ZzqLAEQsAhAAgBSs29K4NwB3796T6SwCELEIQAAAUrBq0zZzPthRXULmswhAxCIAAQBIwYqNb5rzwT599YDMZxGAiEUAAgCQgqXrtprzwY65ZmDmswhAxCIAAQBIwaI1W8z5YCdcNyjzWQQgYhGAAACkYN6qzeZ8sJNueDnzWQQgYhGAAACkYPYbm8z5YJ+9cXDmswhAxCIAAQBIwYzlG835YF/oOiTzWQQgYhGAAACkYFp9EoCn3TI081kEIGIRgAAApGDSkvXmfLB/ufWVzGcRgNXhdEn9JK1QcjDOfof1H5fUR9JcSXsk9Whmzc8kjZK0obANlXRKyZqawrzibXaZ+04AAgCQggmL1pnzwTr+YXjmswjA6tBJUldJ56hlAXikpLsknS9pspoPwCclXSypvaRjJD0maaOkw4vW1EiaIemwou3DZe47AQgAQApeXbDWnA/2b7fXZj6LAKw+LQnAYrVqPgBLvVfSJiXR2KRG0pQyZjWHAAQAIAWj560x54OdeeeIzGcRgNUnqwD8gKRtkr5V9FiNpK1KfvS8UMm7hke8w9c5WMk3S9N2uAhAAACi1c5Zbc4HO+uukZnPIgCrT1YBeJ+kBZL+puixTpLOlXSipDMljZW0REks7k+N9v3cIAEIAECkV2atNOeDffueUZnPIgCrTxYB2EXSeiWhdyAfktQg6aIDrOEdQAAAMvDyjDfM+WBn3zs681kEYPVJOwB/o+Tkj8+38OtNkNStjPl8BhAAgBQMmLbCnA/2vfvHZD6LAKw+aQbglUre0ftiC79WOyWXjLmsjPkEIAAAKXhpynJzPth5D47NfBYBWB3aKblcS3slB+OKwu2mEzK6Sepd8pqm9ROVnLzRXtJxRc97SY2Svqu3X+alXdGa2ySdoeSyMh0kDZG0RtJHyth3AhAAgBS8MHmZOR/sRw+Py3wWAVgdOqqZEysk9So830vJO33Fmlu/uOj5xftZU1O05mklZwA3SlpWuP/JMvedAAQAIAV/nlhvzgc7/5G6zGcRgIhFAAIAkIK+45ea88H+67Hxmc8iABGLAAQAIAVPjltizgf72eMTMp9FACIWAQgAQAp6j11kzgf75Z8mZj6LAEQsAhAAgBQ8OnqhOR/s0j6TMp9FACIWAQgAQAoeHrnAnA92+dOTM59FACIWAQgAQArur51vzgf7375TMp9FACIWAQgAQAp6Dptnzge78tmpmc8iABGLAAQAIAV3DZ1rzge76vlpmc8iABGLAAQAIAW3D55jzge79oXpmc8iABGLAAQAIAXdB80y54PVvDQj81kEIGIRgAAApOCWAa+b88G6hpmZzyIAEYsABAAgBTf1m2nOB+s2YFbmswhAxCIAAQBIwfUvzjDng/1h0OzMZxGAiEUAAgCQgmv+Mt2cD3bH4DmZzyIAEYsABAAgBV2em2bOB7tr6NzMZxGAiEUAAgCQgt8+O8WcD9Zz2LzMZxGA6ft/kjq09k7kiAAEACAFV/SdbM4He6B2fuazCMD0nSRpd2vvRI4IQAAAUvCrpyaZ88EeHrkg81kEYPoIQAAAULZLnnzNnA/22OiFmc8iAMu3+h22dSIAAQBAmX7xxERzPljvVxdnPosALN9WSXdIumg/2w0iAAEAQJl++vgEcz5Yn7olmc8iAMs3VtJlB3ieHwEDAICyXfjYeHM+WN8JSzOfRQCW71ol7/Ltzz9KeiKnfakGBCAAACn4ySN15nyw516rz3wWAYhYBCAAACn44cOvmvPBXpi8LPNZBCBiEYAAAKTgPx8Ya84H6zd1eeazCEDEIgABAEjBd+8bY84HGzh9ReazCEDEIgABAEjBd3qONueDDZ65MvNZBCBiEYAAAKTg3+8ZZc4HGzZrVeazCEDEIgABAEhBpx4jzflgI+asznwWARjnUEmdJd0k6W8Lj50k6eOttUOtgAAEACAFX79jhDkfbMy8NZnPIgArd4KklZIWStop6ejC47dIery1dqoVEIAAAKTgK7cNN+eDjVuwNvNZBGDlhij5lXDvkbRZbwXglyQtaq2dagUEIAAAKTij+zBzPtjExesyn0UAVm6jpE8VbhcH4JGStrfGDrUSAhAAgBR86fevmPPBJi/dkPksArByayS1L9wuDsCvSlrWKnvUOghAAABS8MVbhprzwabVb8x8FgFYuUclPSfpr5QE4FGSDpc0UdLdrbhfeSMAAQBIwee7DjHng81cnv1/UwnAyv2tpOGS1krapeRzf42SRktq14r7lTcCEACAFJx842BzPticlZsyn0UAxuso6TJJV0v6hpKTQsp1uqR+klYoORhnv8P6j0vqI2mupD2Seuxn3bmSZiv5TOJ0SWc1s+YSSYsLa+oknVLerhOAAACk4cSal835YPNXb858FgFYHTpJ6irpHLUsAI+UdJek8yVNVvMB2EHJO5O/lXSskmsV7lBy+Zom5yl51/JCScdJekjSBkkfLWPfCUAAAFJw/HWDzPlgi9duyXwWAVi5q99hq1RLArBYrZoPwL6SQslj4yQ9UHS/TlLPovsHSVouqUsZ8wlAAABS8JlrBpjzwerXb818FgFYuekl22xJ2yRtkjQt4uumFYBLJV1e8tgNkqYWbr9PyTuEpbMel/TiAeYdrOSbpWk7XAQgAADRPnV1f3M+2Bsbt2U+iwBM14ckvSDpRxFfI60A3CHpByWPXSxpVeH2JwqzTitZ013JO4P7U1N43ds2AhAAgDhHdgnmfLDVm7ZnPosATN+JivtNINUegLwDCABAynbv3mPOJwG4fktj5vMIwPR1UPJbQipV7T8CLsVnAAEAiNS4c/feAGzYtiPzeQRg5S4u2S5RciZvvZITMCqV5kkg/UoeG6t9TwK5p+j+QUp+iwkngQAAkKM3G3ftDcAt23dmPo8ArFx9ybZEyW8B6S7pg2V+rXZKfq1ceyUH44rC7SMKz3eT1LvkNU3rJ0p6snD7uKLnO0jaKenXko5R8tm95i4Ds13SBUouFfOgksvAfKyMfScAAQCItGnbjr0BuG3HrsznEYDVoaOaObFCUq/C872UvNNXrLn1i0vWnCtpjpJr/c1Q8xeCvlRJvDYqeUfw1DL3nQAEACDShq2NewNw567dmc8jABGLAAQAINLazdv3BuCePXsyn0cAlueZMrZ3CwIQAIBIqxq2mfPBjr6qfy7zCMDyPFHG9m5BAAIAEGn5hjfN+WCf/t2AXOYRgIhFAAIAEGnpuq3mfLBjrx2YyzwCELEIQAAAIi1cs8WcD3bC9YNymUcAxjlbUh9JoyWNL9neLQhAAAAizVu1yZwP1v6Gl3OZRwBW7lJJWyTdr+QSKg9LGq7kt4D8vhX3K28EIAAAkWa90WDOB/vcTYNzmUcAVm62pB8Vbm+WdHTh9s2S7m6VPWodBCAAAJGmL9tozgc75eYhucwjACv3piRXuL1G0kmF25+WtLZV9qh1EIAAAESasnSDOR+sQ7dXcplHAFZukaSTC7cnSvpZ4fZXJa1vlT1qHQQgAACRXluy3pwP9q+3DstlHgFYuUckXVe4/T+StkoaqCT+erXSPrUGAhAAgEjjF60z54N9+Q/Dc5lHAFburyQdXHT/x5Luk3RFyeP/1xGAAABEGjt/rTkf7Ku31+YyjwAs3wmtvQNVhgAEACDSqLlrzPlgZ945Ipd5BGD59kiqU/KZvw+08r5UAwIQAIBIw2evMueDffPukbnMIwDL96+SHpW0Scl1AB8vPPZuRQACABBp6Osrzflg3+45Opd5BGDlDpF0oaQRSt4VnCvJSzqsNXeqFRCAAABEGjTjDXM+2H/cNyaXeQRgOj6l5ALQSyXtkPRS6+5OrghAAAAi9Z+2wpwPdu79Y3OZRwCm5xBJP5e0TtLuVt6XPBGAAABEenHKcnM+2PcffDWXeQRgvNOVXPdvs6QGJb8T+IutuUM5IwABAIj0/KR6cz7Yj/84Lpd5BGBlPiHpaiWf+9sjabSSzwMe0po71UoIQAAAIj07MQnACx6ty2UeAVi+gZJ2SnpD0q2SPtO6u9PqCEAAACI9PX6JOR/sol7jc5lHAJbvJUnfkfTe1t6RKkEAAgAQ6U/jFpvzwX7ee0Iu8whAxCIAAQCI9PjYReZ8sIv/9Fou8whAxCIAAQCI9MioheZ8sP/pMymXeQQgYhGAAABEemjEAnM+2BVPT85lHgGIWAQgAACR7hs+35wP9ptnpuQyjwBELAIQAIBI97wy15wP5v88NZd5BCBiEYAAAES6c8gccz7Y1c9Py2UeAYhYBCAAAJFue3m2OR/suhem5zKPAEQsAhAAgEi3Dpxlzge74aWZucwjABGLAAQAINIt/V8354Pd3P/1XOYRgIhFAAIAEOnGfjPN+WC/Hzgrl3kEIGIRgAAARLr+xRnmfLDbXp6dyzwCELEIQAAAIv3uL9PM+WB3DpmTyzwCELEIQAAAInV5bqo5H+yeV+bmMo8ARCwCEACASL95Zoo5H+ze4fNymUcAVofTJfWTtELJwTi7Ba/pKGmSpEZJ8yV1Lnm+tvC1Srf+RWtqmnl+dpn7TgACABDpiqcnm/PBHhwxP5d5BGB16CSpq6Rz1LIAPErSVkm3SzpW0qWSdkk6s2jN30k6rGg7vrCmc9GaGkkzStZ9uMx9JwABAIj0P30mmfPB/jhqYS7zCMDq05IAvFVJuBV7WtKgA7zmckmbJB1S9FiNpCll7l8pAhAAgEgXP/maOR+s15hFucwjAKtPSwJwpKQeJY9dKKnhAK+ZLumhksdqlLyTuELSQklPSjqipTtaQAACABDpv3tPNOeDPfHq4lzmEYDVpyUBOFfSVSWPnVV47fubWX9K4blTSh7vJOlcSScq+fHxWElLJH3gALMPVvLN0rQdLgIQAIAoF/WaYM4He6puSS7zCMDqk0UAPihpWgtmf0jJu4gXHWBNjZo5uYQABACgcp0frTPngz0zYWku8wjA6pP2j4APKTz+qxbOnyCp2wGe5x1AAABS9uM/jjPngz0/qT6XeQRg9WnpSSDTSx7ro+ZPAuksabukv2/B7HaSNki6rAVrm/AZQAAAIv3goVfN+WAvTlmeyzwCsDq0k9S+sJmkKwq3m07I6Capd9H6psvAdJd0jKSLte9lYJqMUnKGcHNuk3SGpCMldZA0RNIaSR8pY98JQAAAIp37wFhzPlj/aStymUcAVoeOav6izb0Kz/dScmHn0tdMVnIh6AXa90LQkvSZwtf52n7mPq3kDOBGScsK9z9Z5r4TgAAARPqP+8aY88EGTn8jl3kEIGIRgAAARPp2z9HmfLAhM1fmMo8ARCwCEACASN+8e6Q5H2zY7FW5zCMAEYsABAAg0jd6JAE4cu7qXOYRgIhFAAIAEOlrd9Sa88HGzF+TyzwCELEIQAAAIn35tuHmfLC6hetymUcAIhYBCABApNO7DzPng01cvD6XeQQgYhGAAABE6tDtFXM+2JSlG3KZRwAiFgEIAECkU28eas4Hm75sYy7zCEDEIgABAIj0uZuGmPPBXl+Rz39PCUDEIgABAIjU/oaXzflgc1duymUeAYhYBCAAAJFOuH6QOR9swerNucwjABGLAAQAINJx1w4054MtWbs1l3kEIGIRgAAARPqn3w0w54Mt2/BmLvMIQMQiAAEAiPTJq/qb88FWNmzLZR4BiFgEIAAAEfbs2WPOB3M+2JrN23OZSQAiFgEIAECEXbvfCsANWxtzmUkAIhYBCABAhO07d+0NwE3bduQykwBELAIQAIAIWxt37g3ANxt35TKTAEQsAhAAgAgN23bsDcDtOwlAtA0EIAAAEdZvadwbgLt278llJgGIWAQgAAARVm/avjcA9+whANE2EIAAAERY2bDNnA/2yav65zaTAEQsAhAAgAjLNrxpzgf7p98NyG0mAYhYBCAAABGWrN1qzgc77tqBuc0kABGLAAQAIMKC1ZvN+WD/fP2g3GYSgIhFAAIAEGHuyk3mfLCTbxyc20wCELEIQAAAIry+osGcD/b5rkNym0kAIhYBCABAhOnLNprzwU69eWhuMwlAxCIAAQCIMHnpBnM+WIdur+Q2kwBELAIQAIAIE+xSPvsAABJsSURBVBevM+eDnd59WG4zCUDEIgABAIgwbsFacz7Yl28bnttMAhCxCEAAACKMmb/GnA/2tTtqc5tJACIWAQgAQISRc1eb88G+0WNkbjMJQMQiAAEAiDBs9ipzPti37h6V20wCELEIQAAAIgyZudKcD/adnqNzm0kAIhYBCABAhIHT3zDng333vjG5zSQAq8PpkvpJWqHkYJzdgtd0lDRJUqOk+ZI6lzzfufC1irftzXydSyQtLjxXJ+mU8nadAAQAIEaYusKcD/afD4zNbSYBWB06Seoq6Ry1LACPkrRV0u2SjpV0qaRdks4sWtNZUoOkw4q2j5V8nfOUBOSFko6T9JCkDZI+Wsa+E4AAAER4YfIycz7YDx56NbeZBGD1aUkA3ippRsljT0saVHS/s6SN7/B16iT1LLp/kKTlkrq8416+hQAEACDCc6/Vm/PBfvzHcbnNJACrT0sCcKSkHiWPXajkHb8mnZW8K7hEUr2kFyUdX/T8+wrPl856vLC2pQhAAAAi9J2w1JwP1vnRutxmEoDVpyUBOFfSVSWPnVV47fsL90+TdL6k9pLOUPIZwwZJ/1B4/hOF9aeVfJ3uSt4Z3J+DlXyzNG2HiwAEAKBiT9UtMeeDXdRrQm4zCcDqk1YAlvprJSeL3FS4X2kA1mjfk0sIQAAAKvTEq4vN+WD/3XtibjMJwOqT1o+Am/OspKcKtyv9ETDvAAIAkKJeYxaZ88EufvK13GYSgNWnpSeBTC95rI/efhJIqfdKmi3pjqLH6iTdU3T/IEnLxEkgAADk5o+jFprzwS57alJuMwnA6tBOyWf12is5GFcUbh9ReL6bpN5F65suA9Nd0jGSLta+l4G5TtLXJR0t6bNK3vnbpuRyL03OU3L9vwuUXE7mQSWXgSm9XMyBEIAAAER4cMR8cz7YFX0n5zaTAKwOHdXM5+ok9So830tSbTOvmazkOn4LtO+FoO9UcgZwo6SVkvpLOrmZ2ZcWrauTdGqZ+04AAgAQ4d7h88z5YL99dkpuMwlAxCIAAQCIcPfQueZ8sC7PTc1tJgGIWAQgAAAR7hg8x5wP9ru/TMttJgGIWAQgAAAR/jBotjkf7PoXZ+Q2kwBELAIQAIAI3QbMMueD3dhvZm4zCUDEIgABAIhwc//Xzflgt/R/PbeZBCBiEYAAAES44aWZ5nywWwfOym0mAYhYBCAAABGue2G6OR/s9pdn5zaTAEQsAhAAgAhXPz/NnA/WY8jc3GYSgIhFAAIAEMH/eao5H6znsHm5zSQAEYsABAAgwq+fmWLOB7u/dn5uMwlAxCIAAQCIcPnTk835YA+NWJDbTAIQsQhAAAAiXNpnkjkf7JFRC3ObSQAiFgEIAECEX/5pojkf7PGxi3KbSQAiFgEIAECEn/eeYM4H+9O4xbnNJAARiwAEACDCRb3Gm/PBnh6/JLeZBCBiEYAAAES44NE6cz7YsxPrc5tJACIWAQgAQIQf/3GcOR/sL5OW5TaTAEQsAhAAgAjff/BVcz7YS1OW5zaTAEQsAhAAgAjn3j/WnA82YNqK3GYSgIhFAAIAEOGce0eb88FenvFGbjMJQMQiAAEAiPDte0aZ88GGvr4yt5kEIGIRgAAARDjrrpHmfLDhs1flNpMARCwCEACACGfeOcKcDzZq7prcZhKAiEUAAgAQ4au315rzwcbOX5vbTAIQsQhAAAAifPkPw835YOMXrcttJgGIWAQgAAAR/vXWYeZ8sNeWrM9tJgGIWAQgAAAROnR7xZwPNrV+Q24zCUDEIgABAIhwys1DzPlgM5ZvzG0mAYhYBCAAABE+d9Ngcz7Y7Dc25TaTAEQsAhAAgAgn3fCyOR9s3ioCEG0HAQgAQIQTrhtkzgdbuGZLbjMJQMQiAAEAiHDMNQPN+WBL123NbSYBiFgEIAAAET599QBzPtjyDW/mNpMARCwCEACACEdf1d+cD7aqYVtuMwlAxCIAAQCo0J49e8z5YM4HW7t5e25zCUDEIgABAKjQzl279wbgxq07cptLAFaH0yX1k7RCycE4uwWv6ShpkqRGSfMldS55/meSRknaUNiGSjqlZE1NYV7xNrvMfScAAQCo0LYdu/YG4ObtO3ObSwBWh06Suko6Ry0LwKMkbZV0u6RjJV0qaZekM4vWPCnpYkntJR0j6TFJGyUdXrSmRtIMSYcVbR8uc98JQAAAKrRl+869Abhtx67c5hKA1aclAXirknAr9rSkQQd4zXslbZJ0ftFjNZKmlLl/pQhAAAAqtPHNHXsDcMeu3bnNJQCrT0sCcKSkHiWPXSip4QCv+YCkbZK+VfRYjZJ3EldIWqjkXcMjythXiQAEAKBi67Y07g3A3bv35DaXAKw+LQnAuZKuKnnsrMJr37+f19wnaYGkvyl6rJOkcyWdqOTHx2MlLVESi/tzsJJvlqbtcBGAAABUZNWmbeZ8sCO7hFznEoDVJ4sA7CJpvZLQO5APKXkX8aIDrKnRvieOEIAAAFRgxcY3zflgn7q6f65zCcDqk/aPgH+j5OSPz7dw/gRJ3Q7wPO8AAgCQkvr1W835YJ+5ZkCucwnA6tPSk0CmlzzWR/ueBHKlkij8Ygtnt1NyyZjLWrhe4jOAAABUbPHaLeZ8sOOvG5TrXAKwOrRTcrmW9koOxhWF200nZHST1LtofdNlYLorucTLxdr3MjBeyTUCv6u3X+alXdGa2ySdIelISR0kDZG0RtJHyth3AhAAgArNX73ZnA92Ys3Luc4lAKtDRzXzuTpJvQrP95JU28xrJiuJvAXa90LQi/fzNWuK1jyt5AzgRknLCvc/Wea+E4AAAFRozspN5nywz944ONe5BCBiEYAAAFRo5vIGcz7YF7oOyXUuAYhYBCAAABWaVr/RnA922i1Dc51LACIWAQgAQIUmLVlvzgf70u9fyXUuAYhYBCAAABWasGidOR/sjO7Dcp1LACIWAQgAQIVeXbDWnA/2lduG5zqXAEQsAhAAgAqNnrfGnA/29TtG5DqXAEQsAhAAgAqNmLPanA/WqcfIXOcSgIhFAAIAUKFhs1aZ88H+/Z5Ruc4lABGLAAQAoEKDZ64054Odfe/oXOcSgIhFAAIAUKGB01eY88G+d/+YXOcSgIhFAAIAUKF+U5eb88HOe3BsrnMJQMQiAAEAqNALk5eZ88F+9PC4XOcSgIhFAAIAUKE/T6w354P95JG6XOcSgIhFAAIAUKG+45ea88EufGx8rnMJQMQiAAEAqNCT45aY88F++viEXOcSgIhFAAIAUKHery4254P94omJuc4lABGLAAQAoEKPjV5ozge75MnXcp1LACIWAQgAQIUeHrnAnA/2q6cm5TqXAEQsAhAAgAo9UDvfnA/2v32n5DqXAEQsAhAAgAr1HDbPnA925bNTc51LACIWAQgAQIXuGjrXnA921fPTcp1LACIWAQgAQIVuHzzHnA92zV+m5zqXAEQsAhAAgAp1HzTLnA92/Yszcp1LACIWAQgAQIVuGfC6OR/spn4zc51LACIWAQgAQIVu6jfTnA92y4DXc51LACIWAQgAQIVqXpphzgfrPmhWrnMJQMQiAAEAqNC1L0w354PdPnhOrnMJQMQiAAEAqNBVz08z54PdNXRurnMJQMQiAAEAqNCVz04154P1HDYv17kEIGIRgAAAVOh/+04x54M9UDs/17kEIGIRgAAAVOhXT00y54M9PHJBrnMJQMQiAAEAqNAlT75mzgd7dPTCXOcSgIhFAAIAUKFfPDHRnA/We+yiXOcSgIhFAAIAUKGfPj7BnA/25Lgluc4lABGLAAQAoEIXPjbenA/Wd/zSXOcSgIhFAAIAUKHzH6kz54P9eWJ9rnMJQMQiAAEAqNCPHh5nzgd7YfKyXOcSgNXhdEn9JK1QcjDObsFrOkqaJKlR0nxJnZtZc66k2ZK2S5ou6axm1lwiaXFhTZ2kU8rZcRGAAABU7LwHx5rzwfpNXZ7rXAKwOnSS1FXSOWpZAB4laauk2yUdK+lSSbsknVm0pkPhsd8W1twkaYekE4rWnKckIC+UdJykhyRtkPTRMvadAAQAoELfu3+MOR9s4PQVuc4lAKtPSwLwVkkzSh57WtKgovt9JYWSNeMkPVB0v05Sz6L7B0laLqlLS3dWBCAAABU7+97R5nywwTNX5jqXAKw+LQnAkZJ6lDx2oaSGovtLJV1esuYGSVMLt9+n5B3C0lmPS3rxALMPVvLN0rQdLsk6XPOMnd41sLGxsbGxsZWxHf2bP9s/Xv6MvTRhnjU0NOS21dfXE4BVpiUBOFfSVSWPnVV47fsL93dI+kHJmoslrSrc/kRh/Wkla7oreWdwf2oKr2NjY2NjY2Nr+9uRQlUwVXcANvsOYOH/HsrWqhvHono2jkV1bRyP6tk4FtWzNR2LQ4Wq0JIAbM0fAZc6VHwDVQuORfXgWFQXjkf14FhUD45FlWlJAN6q5LIuxfpo35NA+pWsGat9TwK5p+j+QZKWqYKTQMQ3UDXgWFQPjkV14XhUD45F9eBYVIF2ktoXNpN0ReH2EYXnu0nqXbS+6TIw3SUdo+RHu81dBmanpF8X1tSo+cvAbJd0gZJLxTyo5DIwHytj3/kGqh4ci+rBsaguHI/qwbGoHhyLKtBRzX8ws1fh+V6Sapt5zWQl1/FboP1fCHpOYc0MNX8h6EslLSmsqZN0apn7frCSuDy4zNchfRyL6sGxqC4cj+rBsageHAsAAAAAAAAAAAAAAAAAAAAAAADg/7JLJC1WcimZOkmntOrevDtcJWmCpM2SVkt6QdJnSta8R9KNkt6QtE3SUEmfznEf3626KDl7v/gi7RyLfB0u6U+S1in5854u6fNFz3M88vFeSTdJWqTkz3mBpGuV/Pk34Vhk43Ql1wBeoeavK9ySP/e/kXSvkr9HWyQ9p/IuD4f/485TcumYCyUdJ+khJdcQ/Ghr7tS7wCAll/w5XtJJkvoruYzPIUVrvKSNkr4j6UQlv9lloZK/1MjGF5T8x26q3h6AHIv8/K2Sf5A+puQfo0dJ+rqkTxat4Xjk42pJayV9U8nvmf2ekn+0Xla0hmORjU6Suko6R80HYEv+3O9X8tvEviLpc5JelTQm071Gm1InqWfR/YMkLVd5v0UE8T6i5C/56YX771HyL7vfFK35oJJ3ab+f7669a7RT8vu5v6rkep1NAcixyNfvJY06wPMcj/wESY+UPPackndnJY5FXkoDsCV/7h9U8ksjvle05pjC1/piZnuKNiOt3yOMeJ9S8hez6Te8HF24375k3QhJd+W4X+8mj0u6s3C7Vm8FIMciX68rOQ7PKvl4xGRJPyt6nuORn6uVvBv7T4X7J0laJelHhfsci3yUBmBL/ty/UljzoZI1S5T8ljK8y31CyTfIaSWPd1fyziDycZCSf2mPLnqsg5Jj8/GStc8o+f3QSNf3lXzOrOnHJ7V6KwA5FvnaXthukXSypJ8r+YzTBYXnOR75OUjJO7J7lPxK0j1KPr/chGORj9IAbMmf+w+VfLyr1HhJt6a9g2h7CMDqcL+Sf2X/Q9Fj/A9rfv5RybsaJxY9VisCsLXskDS25LG7lXx+SeJ45On7kuoL//efJf1EyQkFxHi+CECkjh8Bt76eSv4H9qiSx/nRSn7OVvJnvatoMyXvduxScvIBxyI/SyT9seSxXyr5bLLE34081Sv5PfPFrpE0u3CbY5EPfgSMTNRJuqfo/kGSlomTQLL2HiXxt1zNXzKh6UO+vy567FDx4eosfEDJZy+LtwmSnijc5ljkq4/2PQnkTr31riDHIz/rJP2i5LGrlJwsJXEs8rK/k0AO9OfedBLId4vWfEacBIIi5yn5prlA0rGSHlRyGRiuFZSt+5Scwn+GpMOKtvcXrfFKjsW3lfz45QVxeYW81Grfy8BwLPLxBSWfN7tayclRP5S0VW+deCBxPPLSS8kbAk2XgTlH0hq9/UeIHItstFPyDl97JdF2ReH2EYXnW/Lnfr+Sd/y+rOQyMGO178cr8C53qZJvkkYl7wie2rq7865g+9k6F61putDnSiWRPlRvnY2HbNWq+QtBcyzy8S0lJ+VslzRLbz8LWOJ45OUDSv4eLNFbF4LuquTjQ004FtnoqOb/G9Gr8HxL/tybLgS9Xsk/op5X8kYDAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACt4v8D63xJq1NqpkcAAAAASUVORK5CYII=" width="640">





    [<matplotlib.lines.Line2D at 0x7f109197c860>]



Here is the definition of the new callback method. Please note that we declared the variables *y*, *fig* and *ax* as *global*, which means that they refer to the according variables defined in the cell above.


```python
def update_plot(data, df):
    global y
    global fig
    global ax
    new_y = data['Rates'][0]
    y = y[1:]
    y.append(new_y)
    ax.lines[0].set_ydata(y)
    fig.canvas.draw()

```

Let's start the stream. After that you can observe how the plot above updates.


```python
con.subscribe_market_data('EUR/USD', (update_plot, ))
```

    |INFO|2017-08-11 13:47:19,769|Try to subscribe for EUR/USD|
    |INFO|2017-08-11 13:47:19,770|Adding callback method update_plot for symbol EUR/USD|



```python
con.unsubscribe_market_data('EUR/USD')
```

    |INFO|2017-08-11 13:47:29,706|Try to unsubscribe for EUR/USD|


### Models

Data about your account and the market are stored in so called *models*. To fetch that data,
use 

**get_model(models=list())**, where

* **models**: is a list containing the desired models. Thereby the single values have to be one of
  *Account*, *ClosedPosition*, *LeverageProfile*, *Offer*, *OpenPosition*, *Order*, *Properties* or *Summary*.


```python
con.get_model(models=('Account','Order'))
```




    {'accounts': [{'accountId': '2555956',
       'accountName': '02555956',
       'balance': 697145.51,
       'dayPL': -1833.87556,
       'equity': 699309.22444,
       'grossPL': 2163.71444,
       'hedging': 'N',
       'mc': 'N',
       'ratePrecision': 0,
       't': 6,
       'usableMargin': 662825.22444,
       'usableMargin3': 626341.22444,
       'usableMargin3Perc': 89.5657,
       'usableMarginPerc': 94.78285,
       'usdMr': 36484,
       'usdMr3': 72968},
      {'accountId': '',
       'accountName': '',
       'balance': 697145.51,
       'dayPL': -1833.87556,
       'equity': 699309.22444,
       'grossPL': 2163.71444,
       'hedging': '',
       'isTotal': True,
       'mc': '',
       'ratePrecision': 0,
       't': 6,
       'usableMargin': 662825.22444,
       'usableMargin3': 626341.22444,
       'usableMargin3Perc': 89.5657,
       'usableMarginPerc': 94.78285,
       'usdMr': 36484,
       'usdMr3': 72968}],
     'orders': [{'accountId': '2555956',
       'accountName': '02555956',
       'amountK': 100,
       'buy': 1,
       'currency': 'EUR/USD',
       'currencyPoint': 10,
       'isBuy': True,
       'isELSOrder': False,
       'isEntryOrder': True,
       'isLimitOrder': True,
       'isNetQuantity': False,
       'isStopOrder': False,
       'limit': 1.08,
       'limitPegBaseType': -1,
       'limitRate': 1.08,
       'ocoBulkId': 0,
       'orderId': '330277567',
       'range': 0,
       'ratePrecision': 5,
       'sell': 0,
       'status': 1,
       'stop': 0,
       'stopMove': 0,
       'stopPegBaseType': -1,
       'stopRate': 0,
       't': 3,
       'time': '08102017102933',
       'timeInForce': 'GTC',
       'type': 'LE'},
      {'accountId': '2555956',
       'accountName': '02555956',
       'amountK': 5,
       'buy': 1,
       'currency': 'EUR/USD',
       'currencyPoint': 0.5,
       'isBuy': True,
       'isELSOrder': False,
       'isEntryOrder': True,
       'isLimitOrder': True,
       'isNetQuantity': False,
       'isStopOrder': False,
       'limit': 1.08,
       'limitPegBaseType': -1,
       'limitRate': 1.08,
       'ocoBulkId': 0,
       'orderId': '330356342',
       'range': 0,
       'ratePrecision': 5,
       'sell': 0,
       'status': 1,
       'stop': 0,
       'stopMove': 0,
       'stopPegBaseType': -1,
       'stopRate': 0,
       't': 3,
       'time': '08112017113934',
       'timeInForce': 'GTC',
       'type': 'LE'},
      {'accountId': '2555956',
       'accountName': '02555956',
       'amountK': 5,
       'buy': 1,
       'currency': 'EUR/USD',
       'currencyPoint': 0.5,
       'isBuy': True,
       'isELSOrder': False,
       'isEntryOrder': True,
       'isLimitOrder': True,
       'isNetQuantity': False,
       'isStopOrder': False,
       'limit': 1.08,
       'limitPegBaseType': -1,
       'limitRate': 1.08,
       'ocoBulkId': 0,
       'orderId': '330356235',
       'range': 0,
       'ratePrecision': 5,
       'sell': 0,
       'status': 1,
       'stop': 0,
       'stopMove': 0,
       'stopPegBaseType': -1,
       'stopRate': 0,
       't': 3,
       'time': '08112017113839',
       'timeInForce': 'GTC',
       'type': 'LE'},
      {'accountId': '2555956',
       'accountName': '02555956',
       'amountK': 5,
       'buy': 1,
       'currency': 'EUR/USD',
       'currencyPoint': 0.5,
       'isBuy': True,
       'isELSOrder': False,
       'isEntryOrder': True,
       'isLimitOrder': True,
       'isNetQuantity': False,
       'isStopOrder': False,
       'limit': 1.08,
       'limitPegBaseType': -1,
       'limitRate': 1.08,
       'ocoBulkId': 0,
       'orderId': '330356382',
       'range': 0,
       'ratePrecision': 5,
       'sell': 0,
       'status': 1,
       'stop': 0,
       'stopMove': 0,
       'stopPegBaseType': -1,
       'stopRate': 0,
       't': 3,
       'time': '08112017114249',
       'timeInForce': 'GTC',
       'type': 'LE'},
      {'accountId': '2555956',
       'accountName': '02555956',
       'amountK': 5,
       'buy': 1,
       'currency': 'EUR/USD',
       'currencyPoint': 0.5,
       'isBuy': True,
       'isELSOrder': False,
       'isEntryOrder': True,
       'isLimitOrder': True,
       'isNetQuantity': False,
       'isStopOrder': False,
       'limit': 1.08,
       'limitPegBaseType': -1,
       'limitRate': 1.08,
       'ocoBulkId': 0,
       'orderId': '330356239',
       'range': 0,
       'ratePrecision': 5,
       'sell': 0,
       'status': 1,
       'stop': 0,
       'stopMove': 0,
       'stopPegBaseType': -1,
       'stopRate': 0,
       't': 3,
       'time': '08112017113849',
       'timeInForce': 'GTC',
       'type': 'LE'}],
     'response': {'executed': True}}



There are shortcuts for the models *ClosedPosition*, *Offer*, *OpenPosition* and *Order*, namely

**get_open_positions(kind='dataframe')**

**get_closed_positions(kind='dataframe')**

**get_offers(kind='dataframe')**

**get_orders(kind='dataframe')**,

where

* **kind**: is either *dataframe* (default) or *list* and determines the shape of the return. 


```python
con.get_orders()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>accountId</th>
      <th>accountName</th>
      <th>amountK</th>
      <th>buy</th>
      <th>currency</th>
      <th>currencyPoint</th>
      <th>isBuy</th>
      <th>isELSOrder</th>
      <th>isEntryOrder</th>
      <th>isLimitOrder</th>
      <th>...</th>
      <th>sell</th>
      <th>status</th>
      <th>stop</th>
      <th>stopMove</th>
      <th>stopPegBaseType</th>
      <th>stopRate</th>
      <th>t</th>
      <th>time</th>
      <th>timeInForce</th>
      <th>type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>100</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>10.0</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08102017102933</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113934</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113839</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017114249</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113849</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 29 columns</p>
</div>




```python
con.get_orders(kind='list')
```




    [{'accountId': '2555956',
      'accountName': '02555956',
      'amountK': 100,
      'buy': 1,
      'currency': 'EUR/USD',
      'currencyPoint': 10,
      'isBuy': True,
      'isELSOrder': False,
      'isEntryOrder': True,
      'isLimitOrder': True,
      'isNetQuantity': False,
      'isStopOrder': False,
      'limit': 1.08,
      'limitPegBaseType': -1,
      'limitRate': 1.08,
      'ocoBulkId': 0,
      'orderId': '330277567',
      'range': 0,
      'ratePrecision': 5,
      'sell': 0,
      'status': 1,
      'stop': 0,
      'stopMove': 0,
      'stopPegBaseType': -1,
      'stopRate': 0,
      't': 3,
      'time': '08102017102933',
      'timeInForce': 'GTC',
      'type': 'LE'},
     {'accountId': '2555956',
      'accountName': '02555956',
      'amountK': 5,
      'buy': 1,
      'currency': 'EUR/USD',
      'currencyPoint': 0.5,
      'isBuy': True,
      'isELSOrder': False,
      'isEntryOrder': True,
      'isLimitOrder': True,
      'isNetQuantity': False,
      'isStopOrder': False,
      'limit': 1.08,
      'limitPegBaseType': -1,
      'limitRate': 1.08,
      'ocoBulkId': 0,
      'orderId': '330356342',
      'range': 0,
      'ratePrecision': 5,
      'sell': 0,
      'status': 1,
      'stop': 0,
      'stopMove': 0,
      'stopPegBaseType': -1,
      'stopRate': 0,
      't': 3,
      'time': '08112017113934',
      'timeInForce': 'GTC',
      'type': 'LE'},
     {'accountId': '2555956',
      'accountName': '02555956',
      'amountK': 5,
      'buy': 1,
      'currency': 'EUR/USD',
      'currencyPoint': 0.5,
      'isBuy': True,
      'isELSOrder': False,
      'isEntryOrder': True,
      'isLimitOrder': True,
      'isNetQuantity': False,
      'isStopOrder': False,
      'limit': 1.08,
      'limitPegBaseType': -1,
      'limitRate': 1.08,
      'ocoBulkId': 0,
      'orderId': '330356235',
      'range': 0,
      'ratePrecision': 5,
      'sell': 0,
      'status': 1,
      'stop': 0,
      'stopMove': 0,
      'stopPegBaseType': -1,
      'stopRate': 0,
      't': 3,
      'time': '08112017113839',
      'timeInForce': 'GTC',
      'type': 'LE'},
     {'accountId': '2555956',
      'accountName': '02555956',
      'amountK': 5,
      'buy': 1,
      'currency': 'EUR/USD',
      'currencyPoint': 0.5,
      'isBuy': True,
      'isELSOrder': False,
      'isEntryOrder': True,
      'isLimitOrder': True,
      'isNetQuantity': False,
      'isStopOrder': False,
      'limit': 1.08,
      'limitPegBaseType': -1,
      'limitRate': 1.08,
      'ocoBulkId': 0,
      'orderId': '330356382',
      'range': 0,
      'ratePrecision': 5,
      'sell': 0,
      'status': 1,
      'stop': 0,
      'stopMove': 0,
      'stopPegBaseType': -1,
      'stopRate': 0,
      't': 3,
      'time': '08112017114249',
      'timeInForce': 'GTC',
      'type': 'LE'},
     {'accountId': '2555956',
      'accountName': '02555956',
      'amountK': 5,
      'buy': 1,
      'currency': 'EUR/USD',
      'currencyPoint': 0.5,
      'isBuy': True,
      'isELSOrder': False,
      'isEntryOrder': True,
      'isLimitOrder': True,
      'isNetQuantity': False,
      'isStopOrder': False,
      'limit': 1.08,
      'limitPegBaseType': -1,
      'limitRate': 1.08,
      'ocoBulkId': 0,
      'orderId': '330356239',
      'range': 0,
      'ratePrecision': 5,
      'sell': 0,
      'status': 1,
      'stop': 0,
      'stopMove': 0,
      'stopPegBaseType': -1,
      'stopRate': 0,
      't': 3,
      'time': '08112017113849',
      'timeInForce': 'GTC',
      'type': 'LE'}]



<div style='color:red'><b>Note about models:</b> Should we provide support for all models or should we drop the technical models as for example <i>properties</i></div>

## Historical data

To fetch market data for a given instrument use the method 

**get_candles(offer_id, period, number, start=None, stop=None)**

where

* **offer_id**: Is a reference to an member of the *Offer* model, which defines the instrument to fetch data for.
* **period_id**: Must be one of *m1*, *m5*, *m15*, *m30*, *H1*, *H2*, *H3*, *H4*, *H6*, *H8*, *D1*, *W1* or *M1* and determines the period of the candles.
* **number**: The number of candles to retrieve, maximum is 10000.
* **start**: A *datetime* object. The first date, candles are retrieved for. If not given, that date is derived from the *stop* date, the period and the number of candles.
* **stop**: A *datetime* object. The last date, candles are retrieved for. If not given, the day before the current date is used.


```python
offers = con.get_offers()
```


```python
offers[['currency', 'offerId']]
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>currency</th>
      <th>offerId</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>EUR/USD</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>USD/JPY</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>GBP/USD</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>USD/CHF</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>AUD/USD</td>
      <td>6</td>
    </tr>
    <tr>
      <th>5</th>
      <td>USD/CAD</td>
      <td>7</td>
    </tr>
    <tr>
      <th>6</th>
      <td>NZD/USD</td>
      <td>8</td>
    </tr>
    <tr>
      <th>7</th>
      <td>GER30</td>
      <td>1004</td>
    </tr>
    <tr>
      <th>8</th>
      <td>UK100</td>
      <td>1012</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Copper</td>
      <td>1016</td>
    </tr>
    <tr>
      <th>10</th>
      <td>USOil</td>
      <td>2001</td>
    </tr>
    <tr>
      <th>11</th>
      <td>UKOil</td>
      <td>2002</td>
    </tr>
    <tr>
      <th>12</th>
      <td>NGAS</td>
      <td>2015</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Bund</td>
      <td>3001</td>
    </tr>
    <tr>
      <th>14</th>
      <td>XAU/USD</td>
      <td>4001</td>
    </tr>
    <tr>
      <th>15</th>
      <td>XAG/USD</td>
      <td>4002</td>
    </tr>
  </tbody>
</table>
</div>




```python
candles = con.get_candles(offer_id=1, period='D1', number=10)
candles
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
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
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2017-07-30 21:00:00</td>
      <td>1.17447</td>
      <td>1.18403</td>
      <td>1.18444</td>
      <td>1.17221</td>
      <td>1.17523</td>
      <td>1.18428</td>
      <td>1.18473</td>
      <td>1.17244</td>
      <td>282104</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2017-07-31 21:00:00</td>
      <td>1.18402</td>
      <td>1.18009</td>
      <td>1.18433</td>
      <td>1.17839</td>
      <td>1.18428</td>
      <td>1.18033</td>
      <td>1.18463</td>
      <td>1.17863</td>
      <td>293101</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2017-08-01 21:00:00</td>
      <td>1.18009</td>
      <td>1.18545</td>
      <td>1.19092</td>
      <td>1.17924</td>
      <td>1.18033</td>
      <td>1.18582</td>
      <td>1.19121</td>
      <td>1.17949</td>
      <td>295923</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2017-08-02 21:00:00</td>
      <td>1.18545</td>
      <td>1.18666</td>
      <td>1.18918</td>
      <td>1.18294</td>
      <td>1.18582</td>
      <td>1.18700</td>
      <td>1.18944</td>
      <td>1.18317</td>
      <td>284911</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2017-08-03 21:00:00</td>
      <td>1.18666</td>
      <td>1.17720</td>
      <td>1.18882</td>
      <td>1.17270</td>
      <td>1.18700</td>
      <td>1.17757</td>
      <td>1.18904</td>
      <td>1.17294</td>
      <td>303251</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2017-08-05 21:00:00</td>
      <td>1.17677</td>
      <td>1.17700</td>
      <td>1.17785</td>
      <td>1.17677</td>
      <td>1.17752</td>
      <td>1.17768</td>
      <td>1.17870</td>
      <td>1.17734</td>
      <td>398</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2017-08-06 21:00:00</td>
      <td>1.17701</td>
      <td>1.17928</td>
      <td>1.18130</td>
      <td>1.17692</td>
      <td>1.17768</td>
      <td>1.17969</td>
      <td>1.18155</td>
      <td>1.17725</td>
      <td>205408</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2017-08-07 21:00:00</td>
      <td>1.17928</td>
      <td>1.17513</td>
      <td>1.18229</td>
      <td>1.17139</td>
      <td>1.17969</td>
      <td>1.17549</td>
      <td>1.18252</td>
      <td>1.17165</td>
      <td>249828</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2017-08-08 21:00:00</td>
      <td>1.17513</td>
      <td>1.17558</td>
      <td>1.17627</td>
      <td>1.16876</td>
      <td>1.17548</td>
      <td>1.17592</td>
      <td>1.17652</td>
      <td>1.16902</td>
      <td>323356</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2017-08-09 21:00:00</td>
      <td>1.17559</td>
      <td>1.17714</td>
      <td>1.17844</td>
      <td>1.17030</td>
      <td>1.17593</td>
      <td>1.17746</td>
      <td>1.17865</td>
      <td>1.17054</td>
      <td>304321</td>
    </tr>
  </tbody>
</table>
</div>




```python
start = dt.datetime(2017, 7, 1)
stop = dt.datetime(2017, 8, 1)
candles = con.get_candles(offer_id=1, period='W1', number=10, start=start, stop=stop)
candles
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
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
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2017-06-23 20:00:00</td>
      <td>1.11627</td>
      <td>1.11911</td>
      <td>1.12078</td>
      <td>1.11382</td>
      <td>1.11649</td>
      <td>1.11945</td>
      <td>1.12101</td>
      <td>1.11406</td>
      <td>783992</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2017-06-30 20:00:00</td>
      <td>1.11911</td>
      <td>1.14162</td>
      <td>1.14445</td>
      <td>1.11707</td>
      <td>1.11945</td>
      <td>1.14253</td>
      <td>1.14467</td>
      <td>1.11729</td>
      <td>2048632</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2017-06-30 20:00:00</td>
      <td>1.11918</td>
      <td>1.14162</td>
      <td>1.14445</td>
      <td>1.11707</td>
      <td>1.11996</td>
      <td>1.14253</td>
      <td>1.14467</td>
      <td>1.11729</td>
      <td>1656636</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2017-07-07 20:00:00</td>
      <td>1.14144</td>
      <td>1.13992</td>
      <td>1.14274</td>
      <td>1.13112</td>
      <td>1.14261</td>
      <td>1.14027</td>
      <td>1.14298</td>
      <td>1.13137</td>
      <td>1242984</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2017-07-07 20:00:00</td>
      <td>1.14162</td>
      <td>1.13992</td>
      <td>1.14274</td>
      <td>1.13112</td>
      <td>1.14254</td>
      <td>1.14027</td>
      <td>1.14298</td>
      <td>1.13137</td>
      <td>1242984</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2017-07-14 20:00:00</td>
      <td>1.14160</td>
      <td>1.14642</td>
      <td>1.14707</td>
      <td>1.13694</td>
      <td>1.14187</td>
      <td>1.14702</td>
      <td>1.14731</td>
      <td>1.13715</td>
      <td>1063886</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2017-07-21 20:00:00</td>
      <td>1.15744</td>
      <td>1.16622</td>
      <td>1.16817</td>
      <td>1.14781</td>
      <td>1.15767</td>
      <td>1.16658</td>
      <td>1.16843</td>
      <td>1.14804</td>
      <td>1959895</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2017-07-28 20:00:00</td>
      <td>1.16535</td>
      <td>1.17481</td>
      <td>1.17757</td>
      <td>1.16115</td>
      <td>1.16559</td>
      <td>1.17513</td>
      <td>1.17782</td>
      <td>1.16139</td>
      <td>1096528</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2017-07-28 20:00:00</td>
      <td>1.16622</td>
      <td>1.17481</td>
      <td>1.17757</td>
      <td>1.16115</td>
      <td>1.16658</td>
      <td>1.17513</td>
      <td>1.17782</td>
      <td>1.16139</td>
      <td>2586664</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2017-08-04 20:00:00</td>
      <td>1.17481</td>
      <td>1.17720</td>
      <td>1.19092</td>
      <td>1.17221</td>
      <td>1.17513</td>
      <td>1.17757</td>
      <td>1.19121</td>
      <td>1.17244</td>
      <td>1459453</td>
    </tr>
  </tbody>
</table>
</div>



<div style='color:red'><b>Notes to candles:</b> The parameter *start* and *stop*, (which become to *From* and *To* in the request to the FXCM Server) seems to have no effect. I have tried to omit the parameter *number* but then, the connection breaks and I am banned for several minutes (approx. 15)

## Trades and Orders

### Trades

To open a trade use the method

**open_trade(account_id, symbol, side, amount, time_in_force,rate=0, stop=None, trailing_step=None)**, where

* **account_id**: the id of the account the order is placed.
* **symbol**: the symbol of the instrument of the order.
* **side**: 'true' for a buy and 'false' for a sell.
* **amount**: the trade‘s amount in lots.
* **time_in_force**: time in force choices. One of 'IOC', 'GTC', 'FOK', 'DAY' or 'GTD'.
* **rate**: the trade's rate, default is 0.
* **stop**: the trade's stop rate. Default is *None*
* **trailing_step**: the trailing step for the stop rate Default is *None*

The effect of open_trade can be seen in the models closedPosition and / or openPosition, so let's have a look on both bevor creating an order:


```python
con.get_closed_positions()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>accountName</th>
      <th>amountK</th>
      <th>close</th>
      <th>closeTime</th>
      <th>com</th>
      <th>currency</th>
      <th>currencyPoint</th>
      <th>grossPL</th>
      <th>isBuy</th>
      <th>isTotal</th>
      <th>open</th>
      <th>openTime</th>
      <th>ratePrecision</th>
      <th>roll</th>
      <th>t</th>
      <th>tradeId</th>
      <th>valueDate</th>
      <th>visiblePL</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>02555956</td>
      <td>1000</td>
      <td>109.064</td>
      <td>08112017102912</td>
      <td>100</td>
      <td>USD/JPY</td>
      <td>91.68256</td>
      <td>-155.87</td>
      <td>False</td>
      <td>NaN</td>
      <td>109.047</td>
      <td>08112017102700</td>
      <td>3</td>
      <td>0</td>
      <td>2</td>
      <td>141906563</td>
      <td></td>
      <td>-1.7</td>
    </tr>
    <tr>
      <th>1</th>
      <td></td>
      <td>1000</td>
      <td>0.000</td>
      <td>None</td>
      <td>100</td>
      <td>USD/JPY</td>
      <td>0.00000</td>
      <td>-155.87</td>
      <td>False</td>
      <td>True</td>
      <td>0.000</td>
      <td>None</td>
      <td>0</td>
      <td>0</td>
      <td>2</td>
      <td></td>
      <td></td>
      <td>-1.7</td>
    </tr>
  </tbody>
</table>
</div>




```python
con.get_open_positions()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>accountId</th>
      <th>accountName</th>
      <th>amountK</th>
      <th>close</th>
      <th>com</th>
      <th>currency</th>
      <th>currencyPoint</th>
      <th>grossPL</th>
      <th>isBuy</th>
      <th>isDisabled</th>
      <th>...</th>
      <th>ratePrecision</th>
      <th>roll</th>
      <th>stop</th>
      <th>stopMove</th>
      <th>t</th>
      <th>time</th>
      <th>tradeId</th>
      <th>usedMargin</th>
      <th>valueDate</th>
      <th>visiblePL</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>50</td>
      <td>1.17641</td>
      <td>2.50</td>
      <td>EUR/USD</td>
      <td>5.00000</td>
      <td>99.50000</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-14.72</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017100412</td>
      <td>141848116</td>
      <td>650</td>
      <td></td>
      <td>19.9</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>1111</td>
      <td>1.17641</td>
      <td>55.55</td>
      <td>EUR/USD</td>
      <td>111.10000</td>
      <td>2299.77000</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-327.08</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017105006</td>
      <td>141848762</td>
      <td>14443</td>
      <td></td>
      <td>20.7</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>17</td>
      <td>1.17641</td>
      <td>0.85</td>
      <td>EUR/USD</td>
      <td>1.70000</td>
      <td>43.86000</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-5.00</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017111045</td>
      <td>141849008</td>
      <td>221</td>
      <td></td>
      <td>25.8</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17641</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.50000</td>
      <td>40.65000</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017112056</td>
      <td>141849136</td>
      <td>195</td>
      <td></td>
      <td>27.1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17641</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.50000</td>
      <td>40.20000</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017112247</td>
      <td>141849142</td>
      <td>195</td>
      <td></td>
      <td>26.8</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17641</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.50000</td>
      <td>34.80000</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017113258</td>
      <td>141849292</td>
      <td>195</td>
      <td></td>
      <td>23.2</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17641</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.50000</td>
      <td>38.40000</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017113458</td>
      <td>141849310</td>
      <td>195</td>
      <td></td>
      <td>25.6</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17641</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.50000</td>
      <td>38.70000</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017113515</td>
      <td>141849317</td>
      <td>195</td>
      <td></td>
      <td>25.8</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17641</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.50000</td>
      <td>36.90000</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017113641</td>
      <td>141849330</td>
      <td>195</td>
      <td></td>
      <td>24.6</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>1000</td>
      <td>109.08300</td>
      <td>50.00</td>
      <td>USD/JPY</td>
      <td>91.68214</td>
      <td>-412.52991</td>
      <td>False</td>
      <td>False</td>
      <td>...</td>
      <td>3</td>
      <td>0.00</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08112017102851</td>
      <td>141906575</td>
      <td>20000</td>
      <td></td>
      <td>-4.5</td>
    </tr>
    <tr>
      <th>10</th>
      <td></td>
      <td></td>
      <td>2268</td>
      <td>0.00000</td>
      <td>113.40</td>
      <td></td>
      <td>0.00000</td>
      <td>2260.25009</td>
      <td>False</td>
      <td>False</td>
      <td>...</td>
      <td>0</td>
      <td>-373.26</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>None</td>
      <td></td>
      <td>0</td>
      <td></td>
      <td>215.0</td>
    </tr>
  </tbody>
</table>
<p>11 rows × 23 columns</p>
</div>




```python
con.open_trade(account_id='2555956', symbol='USD/JPY' , side='true', 
               amount='1000', time_in_force='GTC')
```

    {'response': {'executed': True}, 'data': None}


And now a look on the updated models:


```python
con.get_closed_positions()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>accountName</th>
      <th>amountK</th>
      <th>close</th>
      <th>closeTime</th>
      <th>com</th>
      <th>currency</th>
      <th>currencyPoint</th>
      <th>grossPL</th>
      <th>isBuy</th>
      <th>isTotal</th>
      <th>open</th>
      <th>openTime</th>
      <th>ratePrecision</th>
      <th>roll</th>
      <th>t</th>
      <th>tradeId</th>
      <th>valueDate</th>
      <th>visiblePL</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>02555956</td>
      <td>1000</td>
      <td>109.064</td>
      <td>08112017102912</td>
      <td>100</td>
      <td>USD/JPY</td>
      <td>91.67752</td>
      <td>-155.87</td>
      <td>False</td>
      <td>NaN</td>
      <td>109.047</td>
      <td>08112017102700</td>
      <td>3</td>
      <td>0</td>
      <td>2</td>
      <td>141906563</td>
      <td></td>
      <td>-1.7</td>
    </tr>
    <tr>
      <th>1</th>
      <td>02555956</td>
      <td>1000</td>
      <td>109.084</td>
      <td>08112017114804</td>
      <td>100</td>
      <td>USD/JPY</td>
      <td>91.67752</td>
      <td>-421.69</td>
      <td>False</td>
      <td>NaN</td>
      <td>109.038</td>
      <td>08112017102851</td>
      <td>3</td>
      <td>0</td>
      <td>2</td>
      <td>141906575</td>
      <td></td>
      <td>-4.6</td>
    </tr>
    <tr>
      <th>2</th>
      <td></td>
      <td>2000</td>
      <td>0.000</td>
      <td>None</td>
      <td>200</td>
      <td>USD/JPY</td>
      <td>0.00000</td>
      <td>-577.56</td>
      <td>False</td>
      <td>True</td>
      <td>0.000</td>
      <td>None</td>
      <td>0</td>
      <td>0</td>
      <td>2</td>
      <td></td>
      <td></td>
      <td>-6.3</td>
    </tr>
  </tbody>
</table>
</div>




```python
con.get_open_positions()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>accountId</th>
      <th>accountName</th>
      <th>amountK</th>
      <th>close</th>
      <th>com</th>
      <th>currency</th>
      <th>currencyPoint</th>
      <th>grossPL</th>
      <th>isBuy</th>
      <th>isDisabled</th>
      <th>...</th>
      <th>ratePrecision</th>
      <th>roll</th>
      <th>stop</th>
      <th>stopMove</th>
      <th>t</th>
      <th>time</th>
      <th>tradeId</th>
      <th>usedMargin</th>
      <th>valueDate</th>
      <th>visiblePL</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>50</td>
      <td>1.17639</td>
      <td>2.50</td>
      <td>EUR/USD</td>
      <td>5.0</td>
      <td>98.50</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-14.72</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017100412</td>
      <td>141848116</td>
      <td>650</td>
      <td></td>
      <td>19.7</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>1111</td>
      <td>1.17639</td>
      <td>55.55</td>
      <td>EUR/USD</td>
      <td>111.1</td>
      <td>2277.55</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-327.08</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017105006</td>
      <td>141848762</td>
      <td>14443</td>
      <td></td>
      <td>20.5</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>17</td>
      <td>1.17639</td>
      <td>0.85</td>
      <td>EUR/USD</td>
      <td>1.7</td>
      <td>43.52</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-5.00</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017111045</td>
      <td>141849008</td>
      <td>221</td>
      <td></td>
      <td>25.6</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17639</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.5</td>
      <td>40.35</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017112056</td>
      <td>141849136</td>
      <td>195</td>
      <td></td>
      <td>26.9</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17639</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.5</td>
      <td>39.90</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017112247</td>
      <td>141849142</td>
      <td>195</td>
      <td></td>
      <td>26.6</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17639</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.5</td>
      <td>34.50</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017113258</td>
      <td>141849292</td>
      <td>195</td>
      <td></td>
      <td>23.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17639</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.5</td>
      <td>38.10</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017113458</td>
      <td>141849310</td>
      <td>195</td>
      <td></td>
      <td>25.4</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17639</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.5</td>
      <td>38.40</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017113515</td>
      <td>141849317</td>
      <td>195</td>
      <td></td>
      <td>25.6</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>15</td>
      <td>1.17639</td>
      <td>0.75</td>
      <td>EUR/USD</td>
      <td>1.5</td>
      <td>36.60</td>
      <td>True</td>
      <td>False</td>
      <td>...</td>
      <td>5</td>
      <td>-4.41</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>08092017113641</td>
      <td>141849330</td>
      <td>195</td>
      <td></td>
      <td>24.4</td>
    </tr>
    <tr>
      <th>9</th>
      <td></td>
      <td></td>
      <td>1268</td>
      <td>0.00000</td>
      <td>63.40</td>
      <td>EUR/USD</td>
      <td>0.0</td>
      <td>2647.42</td>
      <td>False</td>
      <td>False</td>
      <td>...</td>
      <td>0</td>
      <td>-373.26</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>None</td>
      <td></td>
      <td>0</td>
      <td></td>
      <td>217.7</td>
    </tr>
  </tbody>
</table>
<p>10 rows × 23 columns</p>
</div>



### Entry orders

To create an Entry Order, use the method 

**create_entry_order(account_id, symbol, side, amount, limit, is_in_pips, time_in_force, rate=0, stop=None, trailing_step=None)**

where

* **account_id**: the id of the trader's account.
* **symbol**: the symbol of the instrument of the order.
* **side**: 'true' for a buy and 'false' for a sell.
* **amount**: the trade‘s amount in lots.
* **limit**: the trade's limit rate.
* **is_in_pips**: defines if the trade's stop / limit rate is in pips. 
* **time_in_force**: time in force choices. One of 'GTC', 'DAY' or 'GTD'.
* **rate**: the trade's rate, default is 0.
* **stop**: the trade's stop rate. Default is *None*.
* **trailing_step**: the trailing step for the stop rate. Default is *None*.



Open orders can be found in the *Order* model. Let's have a look on the model before and after creating an Entry Order:


```python
con.get_orders()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>accountId</th>
      <th>accountName</th>
      <th>amountK</th>
      <th>buy</th>
      <th>currency</th>
      <th>currencyPoint</th>
      <th>isBuy</th>
      <th>isELSOrder</th>
      <th>isEntryOrder</th>
      <th>isLimitOrder</th>
      <th>...</th>
      <th>sell</th>
      <th>status</th>
      <th>stop</th>
      <th>stopMove</th>
      <th>stopPegBaseType</th>
      <th>stopRate</th>
      <th>t</th>
      <th>time</th>
      <th>timeInForce</th>
      <th>type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>100</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>10.0</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08102017102933</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113934</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113839</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017114249</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113849</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 29 columns</p>
</div>




```python
con.create_entry_order(account_id='2555956', symbol='EUR/USD', side='true', 
                       amount=111, limit=1.08, is_in_pips = 'false',
                       time_in_force='GCT', rate=1, stop=None, trailing_step=None)
```

    {'response': {'executed': True}, 'data': None}



```python
con.get_orders()
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>accountId</th>
      <th>accountName</th>
      <th>amountK</th>
      <th>buy</th>
      <th>currency</th>
      <th>currencyPoint</th>
      <th>isBuy</th>
      <th>isELSOrder</th>
      <th>isEntryOrder</th>
      <th>isLimitOrder</th>
      <th>...</th>
      <th>sell</th>
      <th>status</th>
      <th>stop</th>
      <th>stopMove</th>
      <th>stopPegBaseType</th>
      <th>stopRate</th>
      <th>t</th>
      <th>time</th>
      <th>timeInForce</th>
      <th>type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>100</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>10.0</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08102017102933</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113934</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113839</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017114249</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113849</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>111</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>11.1</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017114811335</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
  </tbody>
</table>
<p>6 rows × 29 columns</p>
</div>



To change an order use the method

**change_order(order_id, amount, rate=0, order_range=0, trailing_step=None)** 

where

* **order_id**: is the identifier of the order to change. Can be found in the *order* model.
* **amount**: the trades amount.
* **rate**: the order's new rate.
* **order_range**: the order's range.
* **trailing_step**: the trailing step for the stop rate. Default is *None*.

First, we want to find out the order id of the pervious created order.


```python
orders = con.get_orders()
orders
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>accountId</th>
      <th>accountName</th>
      <th>amountK</th>
      <th>buy</th>
      <th>currency</th>
      <th>currencyPoint</th>
      <th>isBuy</th>
      <th>isELSOrder</th>
      <th>isEntryOrder</th>
      <th>isLimitOrder</th>
      <th>...</th>
      <th>sell</th>
      <th>status</th>
      <th>stop</th>
      <th>stopMove</th>
      <th>stopPegBaseType</th>
      <th>stopRate</th>
      <th>t</th>
      <th>time</th>
      <th>timeInForce</th>
      <th>type</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>100</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>10.0</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08102017102933</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113934</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113839</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017114249</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>5</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>0.5</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017113849</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2555956</td>
      <td>02555956</td>
      <td>111</td>
      <td>1</td>
      <td>EUR/USD</td>
      <td>11.1</td>
      <td>True</td>
      <td>False</td>
      <td>True</td>
      <td>True</td>
      <td>...</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>-1</td>
      <td>0</td>
      <td>3</td>
      <td>08112017114811335</td>
      <td>GTC</td>
      <td>LE</td>
    </tr>
  </tbody>
</table>
<p>6 rows × 29 columns</p>
</div>




```python
orders[['orderId', 'currency', 'amountK', 'isBuy', 'buy']]
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>orderId</th>
      <th>currency</th>
      <th>amountK</th>
      <th>isBuy</th>
      <th>buy</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>330277567</td>
      <td>EUR/USD</td>
      <td>100</td>
      <td>True</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>330356342</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>330356235</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>330356382</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>330356239</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1</td>
    </tr>
    <tr>
      <th>5</th>
      <td>330356608</td>
      <td>EUR/USD</td>
      <td>111</td>
      <td>True</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



Let's change that order:


```python
con.change_order(330356608, amount=112, rate=1.07)
```

    {'response': {'executed': True}, 'data': None}



```python
orders = con.get_orders()
orders[['orderId', 'currency', 'amountK', 'isBuy', 'buy']]
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>orderId</th>
      <th>currency</th>
      <th>amountK</th>
      <th>isBuy</th>
      <th>buy</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>330277567</td>
      <td>EUR/USD</td>
      <td>100</td>
      <td>True</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>1</th>
      <td>330356342</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>330356235</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>3</th>
      <td>330356382</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>4</th>
      <td>330356239</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>5</th>
      <td>330356608</td>
      <td>EUR/USD</td>
      <td>112</td>
      <td>True</td>
      <td>1.07</td>
    </tr>
  </tbody>
</table>
</div>



To delete an order, you can use

**delete_order(order_id)** 

where

* **order_id**: is the identifier of the order to delete.


```python
con.delete_order(330356608)
```

    {'response': {'executed': True}, 'data': None}



```python
orders = con.get_orders()
orders[['orderId', 'currency', 'amountK', 'isBuy', 'buy']]
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>orderId</th>
      <th>currency</th>
      <th>amountK</th>
      <th>isBuy</th>
      <th>buy</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>330277567</td>
      <td>EUR/USD</td>
      <td>100</td>
      <td>True</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>330356342</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>330356235</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>330356382</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>330356239</td>
      <td>EUR/USD</td>
      <td>5</td>
      <td>True</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>



### OCO Orders

To create an oco order use 

**create_oco_order(account_id, symbol, side, side2,  amount, is_in_pips, time_in_force, at_market, order_type, expiration, limit, limit2, rate, rate2,  stop, stop2, 
trailing_step, trailing_step2, trailing_stop_step, trailing_stop_step2 )**

where

* **account_id**: the id of the trader's account.
* **symbol**: the symbol of the instrument of the order.
* **side**: 'true' for a buy and 'false' for a sell.
* **side2**: 'true' for a buy and 'false' for a sell, applies to the second order.
* **amount**: the order's amount in lots.
* **is_in_pips**: defines if the order's stop / limit rate is in pips. 
* **time_in_force**: time in force choices. One of 'GTC', 'DAY' or 'GTD'.
* **at_market**: defines the market range.
* **order_type**: the type of the order execution. One of 'AtMarket' or 'MarketRange'.
* **expiration**: the order's expiration rate.
* **limit**: the order's limit rate.
* **limit2**: the second order's limit rate.
* **rate**: the order's rate.
* **rate2**: the second order's rate.
* **stop**: the order's stop rate. 
* **stop2**: the second order's stop rate.
* **trailing_step**: the trailing step for the order's rate.
* **trailing_step2**: the trailing step for the second order's rate.
* **trailing_stop_step**: the trailing step for the order's stop rate.
* **trailing_stop_step2**: the trailing step for the second order's stop rate.



```python
oco = con.create_oco_order(account_id='2555956', symbol='EUR/USD', side='true', 
                           side2='false', amount=100, is_in_pips= 'false', 
                           time_in_force='GTC', at_market=1, order_type='MarketRange', 
                           expiration='01112017', limit=0, limit2=0, rate=0, rate2=0,
                           stop=0, stop2=0, trailing_step=0, trailing_step2=0, 
                           trailing_stop_step=0, trailing_stop_step2=0 )
```

    |ERROR|2017-08-11 13:49:06,321|Server reports an error: {"type":4,"sessionId":"U100D1_567885D046468795E053D5293C0A8344_08112017114636917059_BL6","requestId":"Request-94034.1","text":" failed to create order with type unknown.\n","code":20008,"stack":""}|



    ---------------------------------------------------------------------------

    ServerError                               Traceback (most recent call last)

    <ipython-input-43-eb79eadc6702> in <module>()
          4                            expiration='01112017', limit=0, limit2=0, rate=0, rate2=0,
          5                            stop=0, stop2=0, trailing_step=0, trailing_step2=0,
    ----> 6                            trailing_stop_step=0, trailing_stop_step2=0 )
    

    /notebooks/pyalgo/schwed/FXCM/fxcmpy.py in create_oco_order(self, account_id, symbol, side, side2, amount, is_in_pips, time_in_force, at_market, order_type, expiration, limit, limit2, rate, rate2, stop, stop2, trailing_step, trailing_step2, trailing_stop_step, trailing_stop_step2)
        367                   'trailing_stop_step2': trailing_stop_step2,
        368                  }
    --> 369         data = self.__handle_request__(method='trading/simple_oco', params=params)
        370         print(data)
        371 


    /notebooks/pyalgo/schwed/FXCM/fxcmpy.py in __handle_request__(self, method, params)
        541             if 'error' in data['response'] and data['response']['error'] != '':
        542                 self.logger.error('Server reports an error: %s' % data['response']['error'])
    --> 543                 raise ServerError('FXCM Server reports an error: %s' % data['response']['error'])
        544             else:
        545                 self.logger.error('FXCM Server reports an unknown error: %s' % data['response'])


    ServerError: FXCM Server reports an error: {"type":4,"sessionId":"U100D1_567885D046468795E053D5293C0A8344_08112017114636917059_BL6","requestId":"Request-94034.1","text":" failed to create order with type unknown.\n","code":20008,"stack":""}


<div style='color:red'><b>Notes:</b> Do not know if the choices of order_type are as stated in the User Guide, get an Error for all possible choices. <br> Also do not know the exact syntax of the *expiration* argument, only know that it should be a string.</div>


```python

```
