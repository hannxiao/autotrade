from abc import ABCMeta
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import datetime
import pandas as pd
import numpy as np
from mpl_finance import candlestick_ohlc
import tushare as ts

from . import indicators, strategies 

    
class Generic(metaclass=ABCMeta):
    def __init__(self, symbols, start, end, interval='1d'):
        if True: #any([char.isdigit() for char in symbols]): # China market, default interval=1d
            pro = ts.pro_api()
            df = pro.daily(ts_code=symbols, start_date=start.replace('-', ''),
                                           end_date=end.replace('-', ''))
            df['Date'] = df['trade_date'].apply(lambda s: datetime.datetime.strptime(s, "%Y%m%d"))
            df.drop(columns=['ts_code', 'pre_close', 'change', 'pct_chg', 'trade_date'], inplace=True)
            df.set_index('Date', inplace=True)
            df.rename(columns={"open": "Open", "high": "High", "low": "Low",
                               "close": "Close", "vol": "Volume", "amount": "Amount"}, inplace=True)
            self._data = df.iloc[::-1]
        elif interval in ['1d', '5d', '1wk', '1mo', '3mo']: # US stock market
            self._data = yf.download(symbols, start=start, end=end, interval=interval)
        else:
            if interval in ['60m', '1h']:
                data_range = 730
            elif interval in ['2m', '5m', '15m', '30m', '90m']:    
                data_range = 60
            else:
                data_range = 30
                
            today = mdates.date2num(datetime.date.today())
            available_after = today-data_range+1 # foremost available start date number
            end_num = mdates.date2num(datetime.datetime.strptime(end, '%Y-%m-%d'))
            start_num = mdates.date2num(datetime.datetime.strptime(start, '%Y-%m-%d'))
            
            if end_num < available_after+2:
                raise Exception('period out of range, no data fetched')
            elif end_num < start_num+2:
                raise Exception('period length < 1, no data fetched')
            else:
                adjusted_start_num = max(available_after,start_num) 
                adjusted_start = mdates.DateFormatter('%Y-%m-%d')(adjusted_start_num)
                
                if interval == '1m' and end_num-adjusted_start_num>7:
                    i_start = adjusted_start_num
                    temp_data = pd.DataFrame()
                    while i_start < end_num:
                        to_append = yf.download(symbols, 
                                                start=mdates.DateFormatter('%Y-%m-%d')(i_start), 
                                                end=mdates.DateFormatter('%Y-%m-%d')(i_start+7), 
                                                interval=interval)
                        temp_data = temp_data.append(to_append)
                        i_start+=6
                    self._data = temp_data
                else:
                    self._data = yf.download(symbols, start=adjusted_start, end=end, interval=interval)
                if start_num < available_after:
                    print('start date out of range, all available data fetched')     
                    
        self.symbols = symbols
        self.interval = interval
        self.period = 'from '+start+' to '+end
        self.close = self._data.Close.reset_index(drop=True)
        self.open = self._data.Open.reset_index(drop=True)
        self.high = self._data.High.reset_index(drop=True)
        self.low = self._data.Low.reset_index(drop=True)
        self.volume = self._data.Volume.reset_index(drop=True)


    def figure_framework(self, n):
        # set a figure framework which has basic setting, used to make time-series plot
        # n is the number of subplots, taking values from 1 to 3
        if n == 1:
            fig, ax1 = plt.subplots(figsize=(12,5))
        elif n == 2:           
            fig, (ax1, ax2) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [7, 3]}, figsize=(12,6))
        elif n == 3:         
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, gridspec_kw={'height_ratios': [3, 5, 3]}, figsize=(12,7))

        data = self._data.reset_index()
        time_column_name = 'Datetime' if self.interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m'] else 'Date'
        timezone = data[time_column_name][0].tzinfo
        time = mdates.date2num(data[time_column_name])
        
        if self.interval in ['1mo', '3mo']:       
            dateformatter = mdates.DateFormatter('%Y-%m', tz=timezone)
        elif self.interval in ['1h', '1d', '5d', '1wk']:
            dateformatter = mdates.DateFormatter('%Y-%m-%d', tz=timezone)
        else:
            dateformatter = mdates.DateFormatter('%Y-%m-%d %H:%M', tz=timezone)
        
        def tickformatter(x, pos):
            if x<len(time):
                return dateformatter(time[int(x)])
            else:
                return ''
        TickFormatter = mticker.FuncFormatter(tickformatter)

        if n==1:        
            for label in ax1.xaxis.get_ticklabels():
                label.set_rotation(45)
            ax1.xaxis.set_major_formatter(TickFormatter)
            ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
            ax1.grid(True)
            ax1.set_xlabel('Time')
            
        elif n==2:
            for label in ax2.xaxis.get_ticklabels():
                label.set_rotation(45)  
            ax2.xaxis.set_major_formatter(TickFormatter)
            ax2.xaxis.set_major_locator(mticker.MaxNLocator(10))
            ax1.set_xticklabels([])
            ax1.grid(True)
            ax2.set_xlabel('Time')            
            
        elif n==3:
            for label in ax3.xaxis.get_ticklabels():
                label.set_rotation(45)  
            ax3.xaxis.set_major_formatter(TickFormatter)
            ax3.xaxis.set_major_locator(mticker.MaxNLocator(10))
            ax1.set_xticklabels([])
            ax2.set_xticklabels([])
            ax2.grid(True)
            ax3.set_xlabel('Time')                  
        
        plt.close()
        return fig
    
    def stock_chart(self, chart_type='candlestick', has_volume=False, n=1):
        fig = self.figure_framework(n=n)
        if n == 1:
            ax1 = fig.axes[0]
        elif n == 2:
            ax1 = fig.axes[0]
        elif n == 3:
            ax1 = fig.axes[1]
            
        data = self._data.reset_index()
        time_column_name = 'Datetime' if self.interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m'] else 'Date'
        data[time_column_name] = mdates.date2num(data[time_column_name])
        data = data.values
        time, openp, highp, lowp, closep, adj_closep, volume = [data[:,i] for i in range(data.shape[1])]

        if chart_type == 'candlestick':
            x = 0
            ohlc = []
        
            while x < len(time):
                append_me = x, openp[x], highp[x], lowp[x], closep[x], volume[x]
                ohlc.append(append_me)
                x+=1        
            candlestick_ohlc(ax1, ohlc, width=0.75, colorup='#77d879', colordown='#db3f3f')
        elif chart_type =='line':
            ax1.plot(range(len(time)), closep) 
            
        ax1.set_ylabel('Price')
        ax1.set_title(self.symbol)
        
        if has_volume:
            ax2 = ax1.twinx()
            ax2.set_ylabel('Volume')
            ax2.yaxis.set_label_position("right")
            ax2.yaxis.tick_right()
            ax2.bar(range(len(time)), volume, width=1, alpha=0.15)
            
            nticks = 11
            ax1.yaxis.set_major_locator(mticker.LinearLocator(nticks))
            ax2.yaxis.set_major_locator(mticker.LinearLocator(nticks))
            # aligning ticks of both y-axis, but the label numbers are not clean
            # delete above 3 lines to get cleaner labels and not aligning ticks
            
        plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
        plt.close()
        return fig
    
    def backtest(self, strategy, strategy_type, get_figure=False):
        # return virtual account balance and trading figure 
        # initial cash is 100
        
        # 'strategy' deliver the information of trading:
        # strategy is an array, the number of which indicates:
        # negative(long position), positive(short position), zero(keep position: do nothing, not zero position)
        
        # strategy_type: 'stock', 'money', 'percentage'
        # number of stocks to trade, amount of money used to trade, percentage of asset used to trade
        close = self.close
        if get_figure == 'signal':
            fig = self.stock_chart(chart_type='line')
            ax1 = fig.axes[0] 
            x_buy = np.nonzero(np.array(strategy<0))[0]
            y_buy = close[x_buy]
            x_sell = np.nonzero(np.array(strategy>0))[0]
            y_sell = close[x_sell]            
            ax1.plot(x_buy, y_buy, 'o', color='Red', markersize=5) 
            ax1.plot(x_sell, y_sell, 'o', color='Green', markersize=5) 
            return fig                
        
        l = len(strategy)
        cash, stock_shares, asset = pd.Series(np.zeros(l)), pd.Series(np.zeros(l)), pd.Series(np.zeros(l))
        last_cash, last_stock, last_total = 100, 0, 100
        
        for i in range(l):
            if strategy[i]:
                if strategy_type == 'stock':
                    changed_amount = strategy[i]*close[i]
                elif strategy_type == 'cash':
                    changed_amount = strategy[i]                   
                elif strategy_type == 'percentage':
                    changed_amount = strategy[i]*last_total
                else:
                    raise ValueError('strategy_type not input')
                cash[i] = last_cash + last_stock*close[i] + changed_amount
                stock_shares[i] = - changed_amount/close[i]
            else:
                cash[i] = last_cash
                stock_shares[i] = last_stock    
            asset[i] = cash[i] + stock_shares[i] * close[i]
            
            last_cash = cash[i]
            last_stock = stock_shares[i]
            last_total = asset[i]
        
        summary = pd.DataFrame({'cash': cash, 'stock_shares': stock_shares,
                              'asset': asset})
        if get_figure == 'return':
            fig = self.figure_framework(n=1)
            ax1 = fig.axes[0] 
            ax1.plot(range(l), summary['asset'])
            ax1.set_title('Return')
            return fig
        else:
            return summary
    
    
    
    def statistic1_MMD(self, get_figure=False):
        return indicators.statistic1_MMD(self, get_figure)
    
    def indicator1_EMA(self, N, get_figure=False):
        return indicators.indicator1_EMA(self, N, get_figure)
    
    def indicator2_SO(self, N, get_figure=False):
        return indicators.indicator2_SO(self, N, get_figure)
        
    def indicator3_Top_Bottom(self, K, get_figure=False, show_price_change=False, recognition_method='height'):
        return indicators.indicator3_Top_Bottom(self, K, get_figure, show_price_change, recognition_method)
     
    def best_K(self, left, right, recognition_method):
        return indicators.best_K(self, left, right, recognition_method)
    
    def indicator4_high_volume(self, K, get_figure=False, recognition_method='height'):
        return indicators.indicator4_high_volume(self, K, get_figure, recognition_method)      
        
    def candlestick_pattern_detector(self):
        return indicators.candlestick_pattern_detector(self)
        
    def future_trend(self, array, K):
        is_extreme, _ = indicators.indicator3_Top_Bottom(self, K, get_figure=False,
                                                         show_price_change=False, recognition_method='height')
        price = self._data.Close.reset_index()['Close']
        return indicators.future_trend(array, K, is_extreme, price)

    def indicator5_MACD(self, fast_period=12, slow_period=26, signal_period=9, get_figure=False): 
        return indicators.indicator5_MACD(self, fast_period, slow_period, signal_period, get_figure)
     
    def Strategy1_MACD_based(self, weight, fast_period=12, slow_period=26, signal_period=9, K=4):
        return strategies.Strategy1_MACD_based(self, weight, fast_period, slow_period, signal_period, K)

    def Strategy2_AIP(self, K):
        return strategies.Strategy2_AIP(self, K)
    
    def price_by_volume(self, get_figure=False, y_length=20):
        # for y_length value, 10, 20, 25, 50, 100 are suggeste. 50, 100 for small time interval
        # increase y_length will make chart less informative and more accurate 
        close = self.close
        volume = self.volume
        accumulate_volume = np.zeros(y_length)
        M, m = close.max(), close.min()
        L, l = len(close), (M-m)/y_length
        
        for i in range(L):
            accumulate_volume[min(int((close[i] - m)//l), y_length-1)] += volume[i]
        accu_max = accumulate_volume.max()
        width = np.array([v*L/accu_max for v in accumulate_volume]) 
        y = np.array([m+l*(0.5+i) for i in range(y_length)])
        
        fig = self.stock_chart(chart_type='candlestick')
        ax1 = fig.axes[0]
        ax1.barh(y, width, height=l, alpha=0.15, color='orange')
        if get_figure:
            return fig
        else:
            return pd.DataFrame({'price': y, 'volume': accumulate_volume})
        # this chart is accurate when price changes within time interval are less than l
         
         
         
         
         
         
         
         
         
         
         

        
        
        
        
        
        