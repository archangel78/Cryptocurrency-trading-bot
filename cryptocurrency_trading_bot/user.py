import socket
import requests
from binance import Client

class User():
    def __init__(self):
        #Creates a binance client object using api key and secret

        api_file = open("config/api_keys","r")
    
        self._api_key = str(api_file.readline())[:-1]
        self._api_secret = str(api_file.readline())

        self.open_orders = []
        self.new_trade_flag = True
        self.continue_trading_flag = True
        self.buffer_period = False
        
        try:    
            self._client = Client(self._api_key, self._api_secret, {"verify": True, "timeout": 20})
        except socket.timeout:
            print("[x] socket timed out while creating client object, try again")
            exit()
        except requests.exceptions.Timeout:
            print("[x] request timed out while creating client object, try again")
            exit()
        except requests.exceptions.ConnectionError:
            print("[x] Connection error occurred while trying to create client object, try again")
            exit()
    
    def set_trading_details(self, paper_balance, investment_amount, holding_amount, trades, leverage):
        self.paper_balance = paper_balance
        self.investment_amount = float(investment_amount)
        self.holding_amount = holding_amount
        self.trades = trades
        self.leverage = leverage

    def get_client(self):
        return self._client

if __name__=="__main__":
    user = User()
    