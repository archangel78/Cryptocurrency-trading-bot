import time
import pandas as pd

class Trading_Strategies:
    status = "Waiting for Trading to start"
    trades = []

    #Gets ticker(Ticker name of crypto to be traded), binance endpoint, investment_amount(amount of usdt to be invested in each trade), 
    # initial_balance(incase of paper trading), real_trading(bool value indicating whether the bot should do paper trading or real trading)
    def __init__(self, ticker, binance_end_point, user,  paper_trading):
        self.ticker = ticker
        self.binance_end_point = binance_end_point
        self.user = user
        self.paper_trading = paper_trading      
    
    #Creates a paper buy order
    def paper_buy(self, rsi_status):
        if(self.user.investment_amount < self.user.paper_balance):
            price, time = self.binance_end_point.get_last_close()
            self.user.holding_amount += round(self.user.investment_amount*self.user.leverage/float(price), 8)
            self.user.paper_balance -= self.user.investment_amount

            inv_str = str(self.user.investment_amount)
            if(len(inv_str[inv_str.index(".")+1:]) < 8):
                inv_str += "0"*(8 - len(inv_str[inv_str.index(".")+1:]))
            
            self.user.trades.insert(0, {"symbol":self.ticker, "executedQty":round(self.user.investment_amount*self.user.leverage/float(price), 8),"cummulativeQuoteQty": inv_str ,"side": "BUY" ,"type":"PAPR", "leverage": self.user.leverage, "btc_balance": self.user.holding_amount ,"time":time, "price":price, "trade_type":"Paper BUY"})
            self.user.open_orders.insert(0, {"symbol":self.ticker, "btc_amount":round(self.user.investment_amount*self.user.leverage/float(price), 8),"cummulativeQuoteQty": inv_str  ,"time":time, "trade_type":"Paper BUY", "profits":"+0.0%", "rsi_status": rsi_status, "order_id": "PAPRBUY"+str(len(self.user.trades))})
            self.user.new_trade_flag = True

    def paper_sell(self, rsi_status):
        if(self.user.holding_amount > 0.0):
            price, time = self.binance_end_point.get_last_close()
            bin_amount = ((self.user.investment_amount*(self.user.leverage - 1))*len(self.user.open_orders))/float(price)
            self.user.paper_balance += float(price)*(self.user.holding_amount - bin_amount)
            self.user.trades.insert(0, {"symbol":self.ticker, "executedQty": round(self.user.holding_amount, 8), "cummulativeQuoteQty": round(float(price)*(self.user.holding_amount - bin_amount), 8), "side": "SELL" ,"type":"PAPR", "account_balance": self.user.paper_balance, "btc_balance": self.user.holding_amount ,"time":time, "price":price, "trade_type":"Paper SELL", "rsi_status": rsi_status})
            self.user.holding_amount = 0.0
            self.user.new_trade_flag = True
            self.user.open_orders = []

    def wait(self, sleep_time):
        ti = sleep_time/115
        i = 0
        while(self.user.continue_trading_flag and i < 115):
                time.sleep(ti)
                i += 1 
    def rsi_trader(self, window_length):
        while(self.user.continue_trading_flag):
            rsi_val = self.get_rsi(window_length)
            curr_val = int(float(rsi_val))
            if(curr_val > 50):
                self.status = "Selling Assets"
                self.paper_sell(rsi_val)
            elif(curr_val < 50):
                self.status = "Buying Assets"
                self.paper_buy(rsi_val)           
            self.wait(60)

    
    def get_rsi(self, window_length):
        df = self.binance_end_point.get_historical_prices_dataframe(200)
        pd.options.mode.chained_assignment = None
        df['diff'] = df["Close"].diff(1)

        df['gain'] = df['diff'].clip(lower=0)
        df['loss'] = df['diff'].clip(upper=0).abs()

        df['avg_gain'] = df['gain'].rolling(window=window_length, min_periods=window_length).mean()[:window_length+1]
        df['avg_loss'] = df['loss'].rolling(window=window_length, min_periods=window_length).mean()[:window_length+1]

        for i, row in enumerate(df['avg_gain'].iloc[window_length+1:]):
            df['avg_gain'].iloc[i + window_length + 1] =\
                (df['avg_gain'].iloc[i + window_length] *
                (window_length - 1) +
                df['gain'].iloc[i + window_length + 1])\
                / window_length

        for i, row in enumerate(df['avg_loss'].iloc[window_length+1:]):
            df['avg_loss'].iloc[i + window_length + 1] =\
                (df['avg_loss'].iloc[i + window_length] *
                (window_length - 1) +
                df['loss'].iloc[i + window_length + 1])\
                / window_length

        df['rs'] = df['avg_gain'] / df['avg_loss']
        df['rsi'] = 100 - (100 / (1.0 + df['rs']))

        curr_val = df.iloc[-1][-1]

        self.rsi_str = str(round(curr_val, 2))

        return self.rsi_str

