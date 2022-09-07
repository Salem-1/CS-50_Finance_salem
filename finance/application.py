import os
#BISM Ellah ELRA7MANI EL RA7eem
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from helpers import apology, login_required, lookup, usd
#I am really proud of finishing this assignemnt
#the special feature I implementd is password registration checking
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#make table for orders and table for history to handle each user id and transactions
# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks""" # SQL SELECT * + {{}} loop to veiw till I got ajax inshalla
    #getting listdict with stock names, shares, prices
    dict_list = db.execute(f"SELECT symbol,stock_name, shares FROM orders WHERE user_id = {session['user_id']}")
    #1- stock_name
    stock_name = [name["stock_name"] for name in dict_list]
    #2-shares
    shares = [name["shares"] for name in dict_list]
    #3-PRICE (lookup_current)
    price = [lookup(name["symbol"]) for name in dict_list]
    #4-total_price = PRICE * shares
    total_price = [(price[i]["price"] * shares[i]) for i in range(len(dict_list))]
    #5-Cash
    cashes = db.execute(f"SELECT cash FROM users WHERE id = {session['user_id']}")
    cash = round(cashes[0]['cash'], 2)
    #6-Grand_total = Cash + SUM(total_price)
    grand_total = round(cash + sum(total_price), 2)
    num_of_stocks = len(stock_name)
    prices = [ pric['price'] for pric in price]
    return render_template("index.html", name=stock_name, st_number = num_of_stocks, share=shares, price=prices, total=total_price, cash=cash, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock""" # SQL update the stock number and recalculate the money according to the stock price
    message = ""
    cash = float(db.execute(f"SElECT cash FROM users WHERE id = {session['user_id']}")[0]["cash"])
    if request.method == 'POST':
        #getting the stock quote from the api as json (dict)
        bsymbol = request.form.get("symbol").strip()
        quote = lookup(bsymbol)
        shares = request.form.get("shares")
        try :
            shares = float(shares)
            if float(shares) == "" or float(shares) <= 0:
                return apology(f"I cannot process buying {shares} number of shares, make sure you are buying number of shares more than 0.",400)
        except ValueError:
            return apology(f"I cannot process buying {shares} number of shares, make sure you are buying number of shares more than 0.",400)

        if quote:
            NAME = quote["name"]
            PRICE = float(quote["price"])
            # session['user_id'], cash
            total_price = PRICE * shares
            if total_price > cash:
                return apology("You don't have enough cash to finalize the payement")
            #do the db calculations here
            else:
                #inserting the transaction to the orders template
                #check weather the user already have stocks or npt
                #update if have or insert
                have_share = db.execute(f"""SELECT shares FROM orders WHERE
                             user_id = {session['user_id']}
                             AND symbol like '{bsymbol}' """)
                if len(have_share) == 0:
                    db.execute(f"""INSERT INTO orders(
                        user_id,
                        symbol,
                        stock_name,
                        shares,
                        price,
                        total) VALUES (?, ?, ?, ?, ?, ?)""",
                        session['user_id'], bsymbol, NAME,
                        shares, PRICE, total_price)
                    #saving this transactoin in the history table
                    db.execute(f"""INSERT INTO history
                       (user_id, symbol, stock_name, shares,
                        trans, price, total, dtime)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        session['user_id'], bsymbol, NAME,
                        shares,"buy", PRICE, total_price,f"{datetime.datetime.now()}")
                    #updating the user cash
                    new_cash = cash - total_price
                    db.execute(f"UPDATE users SET cash = ? WHERE user_id = {session['user_id']}", new_cash)
                    return render_template("index.html")
                else:
                    #adding the new shares to the old shares then calculating the new price
                    bought_shares = db.execute(f"""SELECT shares FROM orders WHERE user_id = {session['user_id']} AND symbol = '{bsymbol}' """)
                    old_shares = float(bought_shares[0]["shares"])
                    new_shares = float(shares) + old_shares
                    new_price = PRICE * new_shares
                    db.execute(f"""UPDATE orders SET shares = ?, price = ?,total = ? WHERE user_id = {session['user_id']} AND symbol = '{bsymbol}' """, new_shares, PRICE, new_price)

                    #saving this transactoin in the history table
                    db.execute(f"""INSERT INTO history
                       (user_id, symbol, stock_name, shares,
                        trans, price, total, dtime)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        session['user_id'], bsymbol, NAME,
                        shares,"buy", PRICE, total_price,f"{datetime.datetime.now()}")

                    #updating the user cash
                    new_cash = cash - total_price
                    db.execute(f"UPDATE users SET cash = ? WHERE id = {session['user_id']}", new_cash)

                    return redirect("/")

            return render_template("buy.html",cash = cash, shares=shares, name=NAME, price=PRICE)
        else:
            return apology("Invalid Stock sympol, please enter valid stock sympol.")
        user_id = session["user_id"]
        cash = db.execute(f"SELECT cash FROM users WHERE id = {user_id}")

    else:
        return render_template("buy.html")
    return apology("This is going no here")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    History = db.execute("SELECT symbol, stock_name, shares, trans, price, total, dtime FROM history WHERE user_id = 21")
    symbol, stock_name, shares, trans, price, total, dtime = [], [], [], [], [], [], []
    lists = ['symbol', 'stock_name', 'shares', 'trans', 'price', 'total', 'dtime']
    for record in History:
        for listy in lists:
            exec(f"{listy}.append({record}['{listy}'])")
    tall = len(symbol)
    return render_template("history.html",tall=tall,symbol=symbol, stock_name=stock_name, shares=shares, trans=trans, price=price, total=total, dtime=dtime)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote.""" #SELECT * from the new IEX table (name and price X number needed)
    message = ""
    if request.method == 'POST':
       #getting the stock quote from the api as json (dict)
        quote = lookup(request.form.get("symbol"))
        if quote:
            NAME = quote["name"]
            PRICE = usd(quote["price"])
            symbol = quote["symbol"]
            return render_template("quoted.html",symbol=symbol,name=NAME, price=PRICE)
        else:
            return apology("invalid symbol",400)
            #return render_template("quote.html", message = "Invalid Stock sympol, please enter valid stock sympol.")

    else:
        return render_template("quote.html",message = "Please enter stock sympol.")
    return apology("This is going no here")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Update the data base with username and password (Don't forget to hash)
    if request.method == 'POST':
        message = " "
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        stored_users = [ user["username"] for user in db.execute("SELECT username FROM users")]
        #Checking username is not null or existed before
        if  username.strip() == message.strip():
            return apology("Username cannot be blank, please use a valid username.",400)
        elif username  in stored_users:
            return apology("Username already exists.",400)
        
        if (password != confirmation) :
            return apology("Passwords doesn't match",400)

        a,x,y,z,n = 0,0,0,0,0
        special = [i for i in """[@_!#$%^&*()<>?/|}{~:]"""]
        for letter in password:
            n += 1
            if letter.isalpha:
                x = 1
            if letter.isnumeric():
                y = 1
            if letter in special:
                z = 1
        if n >= 8:
            a = 1
        key = x + y + z + a
        if key != 4 :
            return render_template('register.html', message="Password must be more than 8 characters and contain at least letter,number and special character like [@_!#$%^&*()<>?/|}{~:]")


        if password.strip() == "":
            return apology("Passwords cannot be blank.",400)
        else:
            db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", username, generate_password_hash(password) )
            return render_template("login.html")
     #   if password != confirmation:
    #       return apology("The two passwords doesn't match, please enter same password.",400)
   #     db.execute('INSERT INTO users (username, hash) VALUES(?,?)', username, generate_password_hash(password))
  #      return render_template("login.html")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    #######getting the list with symbols and dict with shares
    #getting listdict with stock names, shares, prices
    dict_list = db.execute(f"SELECT symbol ,shares FROM orders WHERE user_id = {session['user_id']}")
    stock = db.execute(f"SELECT symbol FROM orders WHERE user_id = {session['user_id']}")
    stocks = [stocks['symbol'] for stocks in stock]
    shares_list = [name["shares"] for name in dict_list]

    symbol_list = [name["symbol"] for name in dict_list]

    #making dictionary with key symbol and value shares
    stock_share = {}
    for share in dict_list:
        stock_share[f"{share['symbol']}"] = float(share['shares'])

    if request.method == 'POST':
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        shares = request.form.get("shares")
        try :
            shares = float(shares)
            checker = int(shares) - float(shares) 
            if float(shares) == "" or float(shares) <= 0 or checker != 0:
                return apology(f"I cannot process buying {shares} number of shares, make sure you are buying number of shares more than 0.",400)
        except ValueError:
            return apology(f"I cannot process buying {shares} number of shares, make sure you are buying number of shares more than 0.",400)

        if quote:
            NAME = quote["name"]
            PRICE = float(quote["price"])
            # session['user_id'], cash
            total_price = PRICE * shares
        else:
            return apology("Couldn't find the stock price")
     #   if symbol not in symbol_list:
      #      return apology(f"You don't have any stocks from {symbol} to sell")
        if shares == "":
            return apology(f"You cannot sell Null shares, make sure you are selling number of shares more than 0.")
        if shares <= 0:
            return apology(f"Cannot process selling {shares} number of shares.")
        if stock_share[f'{symbol}'] < shares:
            return apology(f"you tried to buy {shares} You don't have enough shares to sell from {symbol} stokc, all what you have are {stock_share[f'{symbol}']} shares.")

        #update the orders db, and insert into history db,you are done
        else:
            new_share = stock_share[f'{symbol}'] - shares
            current_cash = db.execute(f"SELECT cash FROM users WHERE id = {session['user_id']}")
            new_cash = total_price + float(current_cash[0]['cash'])
            if new_share < 0:
                return apology(f"You don't have enough stocks from {symbol} to sell")
            db.execute(f"UPDATE orders SET shares = {new_share} WHERE user_id = {session['user_id']} AND symbol ='{symbol}' ")
            db.execute(f"UPDATE users SET cash = {new_cash} WHERE id  = {session['user_id']}")
            db.execute(f"""INSERT INTO history
                       (user_id, symbol, stock_name, shares,
                        trans, price, total, dtime)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        session['user_id'], symbol, NAME,
                        shares,"sell", PRICE, total_price,f"{datetime.datetime.now()}")

            return redirect("/")
    return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
