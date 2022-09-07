from cs50 import SQL
from datetime import datetime
from helpers import lookup
db = SQL("sqlite:///finance.db")
import os
import requests
import urllib.parse
from functools import wraps

stock = db.execute("SELECT symbol FROM orders WHERE user_id = 21")
stocks = [stocks['symbol'] for stocks in stock]
print(stocks)
#History = db.execute("SELECT symbol, stock_name, shares, trans, price, total, dtime FROM history WHERE user_id = 21")
#symbol, stock_name, shares, trans, price, total, dtime = [], [], [], [], [], [], []
#lists = ['symbol', 'stock_name', 'shares', 'trans', 'price', 'total', 'dtime']
#for record in History:
 #   for listy in lists:
  #      exec(f"{listy}.append({record}['{listy}'])")
#nlist = []
#algo = ""
#for i in lists:
 #   algo += "<td>{{"
  #  algo += f"{i}[i]"
   # algo += "}}</td>\n"
#print(algo)
#print(History)

#cash = db.execute(f"SELECT cash FROM users WHERE id = 21")
#print(cash)
#print("Cash is : ", cash[0]['cash'])
#url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"

#shares = db.execute("SELECT symbol,shares FROM orders WHERE user_id = 21")
#print("shares is:\n",shares)
#stock = {}
#for share in shares:
 #   stock[f"{share['symbol']}"] = share['shares']
#print("stocks are:\n", stock,"\n")

#reverse engineering the sell function














#found = db.execute("SELECT shares FROM orders WHERE user_id = 1 AND symbol='ADA1'")
#not_found =db.execute("SELECT shares FROM orders WHERE user_id = 1 AND symbol='NFLX'")
#print(found[0]["shares"])
#print(len(not_found))



#user= 21
#draft the enquiries
#dict_list = db.execute(f"SELECT symbol,stock_name, shares FROM orders WHERE user_id = {user}")
#print(dict_list)
#1-names
#stock_name = [name["stock_name"] for name in dict_list]
#print("\n", stock_name)
    #2-shares
#shares = [name["shares"] for name in dict_list]
#print("\n",shares)
    #3-PRICE (lookup_current)
#symbol = [name["symbol"] for name in dict_list]
#print("\n",symbol)
#current_price = [lookup(s) for s in symbol]
#print(current_price)
    #4-total_price = [(current_price[i] * shares[i]) for i in len(shares)]
    #5-Cash
#cash = db.execute(f"SELECT cash FROM users WHERE id = {session['user_id']}")
    #6-Grand_total = Cash + SUM(total_price)
#Grand_total = Cash + SUM(total_price)








#sympol = input("please enter the stock symbol")
#print(lookup("NFLX"))

#x = None

#stored_users = [ user["username"] for user in db.execute("SELECT username FROM users")]

#for user in stored_users:
 #   stored_users_list.append(user["username"])
#print(stored_users_list)