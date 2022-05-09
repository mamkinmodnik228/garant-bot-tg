import sqlite3
from datetime import datetime


class SQLite:

    def __init__(self, database_file):
        """ Подключаемся к БД """
        self.database = sqlite3.connect(database_file)
        self.cursor = self.database.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
				user_id INT,
				username TEXT,
				balance INT,
				deals_seller INT,
				deals_customer INT
			)""")
        self.database.commit()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS deals (
            seller_id INT,
            customer_id INT,
            money INT,
            active INT,
            cancelled INT,
            end INT
            
        )""")
        self.database.commit()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS payment (
        		bill_id INT,
        		user_id INT,
        		amount INT,
        		comment INT,
        		status TEXT
        	)""")
        self.database.commit()

    def checkMember(self, user_id):
        return self.cursor.execute(f"SELECT user_id FROM users WHERE user_id = '{user_id}'").fetchone()

    def addMember(self, user_id, username):
        self.cursor.execute('INSERT INTO users (`user_id`, `username`, `balance`, `deals_seller`, `deals_customer`) VALUES (?, ?, ?, ?, ?)',
                            (user_id, username, 0, 0, 0))
        self.database.commit()

    def checkUser(self,username):
        return self.cursor.execute(f"SELECT username FROM users WHERE username = '{username}'").fetchone()

    def stats(self,user_id):
        return self.cursor.execute(f"SELECT user_id,balance,deals_seller,deals_customer FROM users WHERE user_id = '{user_id}'").fetchone()

    def stats_by_username(self,username):
        return self.cursor.execute(f"SELECT user_id,deals_seller,deals_customer FROM users WHERE username = '{username}'").fetchone()

    def getCash(self,user_id):
        return self.cursor.execute(f"SELECT balance FROM users WHERE user_id = '{user_id}'").fetchone()

    def getDealsActiveSeller(self,user_id):
        return self.cursor.execute(f"SELECT seller_id,customer_id,money FROM deals WHERE seller_id = '{user_id}' AND active = 1").fetchall()

    def getDealsActiveCustomer(self,user_id):
        return self.cursor.execute(f"SELECT seller_id,money FROM deals WHERE customer_id = '{user_id}' AND active = 1").fetchall()

    def getDealsSeller(self,user_id):
        return self.cursor.execute(f"SELECT customer_id,money,cancelled FROM deals WHERE seller_id = '{user_id}' LIMIT 10").fetchall()

    def getDealsCustomer(self,user_id):
        return self.cursor.execute(f"SELECT seller_id,money,cancelled FROM deals WHERE customer_id = '{user_id}' LIMIT 10").fetchall()

    def getNameByID(self,user_id):
        return self.cursor.execute(f"SELECT username FROM users WHERE user_id = '{user_id}'").fetchone()

    def addDeal(self, seller_id, customer_id, money):
        self.cursor.execute("INSERT INTO deals (`seller_id`,`customer_id`,`money`,`active`,`cancelled`,`end`) VALUES (?,?,?,?,?,?)", (seller_id, customer_id, money, 0, 0, 0))
        self.database.commit()

    def getDealSeller(self, seller_id):
        return self.cursor.execute(f"SELECT seller_id,customer_id,money,active,cancelled,end FROM deals WHERE seller_id = '{seller_id}' AND end = 0").fetchone()

    def getDealCustomer(self, customer_id):
        return self.cursor.execute(f"SELECT seller_id,customer_id,money,active,cancelled,end FROM deals WHERE customer_id = '{customer_id}' AND end = 0").fetchone()

    def getDealLikeSeller(self, seller_id):
        return self.cursor.execute(f"SELECT customer_id,money,active,cancelled,end FROM deals WHERE seller_id = '{seller_id}' AND end = 0").fetchone()

    def getDealLikeCustomer(self, customer_id):
        return self.cursor.execute(f"SELECT seller_id,money,active,cancelled,end FROM deals WHERE customer_id = '{customer_id}' AND end = 0").fetchone()

    def getBalance(self, user_id):
        return self.cursor.execute(f"SELECT balance FROM users WHERE user_id = '{user_id}'").fetchone()

    def giveBalance(self, user_id, amount):
        balance = int(self.getBalance(user_id)[0])
        self.cursor.execute(f"UPDATE users SET balance = '{balance+amount}' WHERE user_id = '{user_id}'")
        self.database.commit()

    def withdrawBalance(self, user_id, amount):
        balance = int(self.getBalance(user_id)[0])
        self.cursor.execute(f"UPDATE users SET balance = '{balance-amount}' WHERE user_id = '{user_id}'")
        self.database.commit()

    def setDealActive(self, user_id, active):
        self.cursor.execute(f"UPDATE deals SET active = {active} WHERE seller_id = '{user_id}'")
        self.database.commit()

    def setDealEnd(self, user_id, end):
        self.cursor.execute(f"UPDATE deals SET end = {end} WHERE seller_id = '{user_id}'")
        self.database.commit()

    def deleteDeal(self, seller_id):
        self.cursor.execute(f"DELETE FROM deals WHERE seller_id = '{seller_id}' AND end = 0")
        self.database.commit()


    def getCustomerDeals(self,user_id):
        return self.cursor.execute(f"SELECT deals_customer FROM users WHERE user_id = '{user_id}'").fetchone()

    def setDealsCustomer(self, user_id):
        deals = int(self.getCustomerDeals(user_id))
        self.cursor.execute(f"UPDATE users SET deals_customer = '{deals+1}' WHERE user_id = '{user_id}'")
        self.database.commit()

    def getSellerDeals(self,user_id):
        return self.cursor.execute(f"SELECT deals_seller FROM users WHERE user_id = '{user_id}'").fetchone()

    def setDealsSeller(self, user_id):
        deals = int(self.getSellerDeals(user_id))
        self.cursor.execute(f"UPDATE users SET deals_seller = '{deals+1}' WHERE user_id = '{user_id}'")
        self.database.commit()

    def deposit(self, bill_id, user_id, amount, comment, status):
        self.cursor.execute("INSERT INTO payment (bill_id,user_id,amount,comment,status) VALUES (?,?,?,?,?)",
                            (bill_id, user_id, amount, comment, status))
        self.database.commit()

    def updatePaymentStatus(self, bill_id, status):
        self.cursor.execute(f"UPDATE payment SET status = '{status}' WHERE bill_id = '{bill_id}'")
        self.database.commit()

    def getAllPayments(self):
        return self.cursor.execute("SELECT bill_id FROM payment WHERE status = 'wait'").fetchall()

    def getUserIdFromPayment(self, bill_id):
        return self.cursor.execute(f"SELECT user_id FROM payment WHERE bill_id = '{bill_id}'").fetchone()

    def getAmountFromPayment(self, bill_id):
        return self.cursor.execute(f"SELECT amount FROM payment WHERE bill_id = '{bill_id}'").fetchone()

    def selectAmount(self):
        return self.cursor.execute(f"SELECT amount FROM payment WHERE status = 'success'").fetchall()


    def close(self):
        self.database.close()
