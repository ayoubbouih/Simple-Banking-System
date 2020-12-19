import random
import sqlite3
from sqlite3.dbapi2 import Cursor

conn = sqlite3.connect('card.s3db')
cur: Cursor = conn.cursor()
cur.execute("drop table card")
cur.execute("create table card (id INTEGER PRIMARY KEY AUTOINCREMENT,number TEXT not NULL,pin TEXT not NULL,balance integer default 0)")
conn.commit()


class Account:
    card = None
    pin = None
    balance = 0
    def __init__(self):
        old = '400000' + str(random.randrange(10 ** 8, 10 ** 9 - 1))
        odd = list()
        for x in range(len(old)):
            if x % 2 == 0:
                odd.append(str(int(old[x]) * 2))
            else:
                odd.append(old[x])
        for x in range(len(odd)):
            if int(odd[x]) > 9:
                odd[x] = str(int(odd[x]) - 9)
        result = sum([int(x) for x in odd])
        last_digit = 10 - result % 10 if result % 10 != 0 else 0
        self.card = old + str(last_digit)
        self.pin = str((random.randrange(1000, 10000)))
        cur.execute("insert into card (number,pin) values(" + self.card + ", " + self.pin + ")")
        conn.commit()


def verify_card(card):
    odd = list()
    old = card[:len(card)-1]
    for x in range(len(old)):
        if x % 2 == 0:
            odd.append(str(int(old[x]) * 2))
        else:
            odd.append(old[x])
    for x in range(len(odd)):
        if int(odd[x]) > 9:
            odd[x] = str(int(odd[x]) - 9)
    result = sum([int(x) for x in odd])
    last_digit = 10 - result % 10 if result % 10 != 0 else 0
    if str(last_digit) == card[-1]:
        return True
    return False


def menu():
    print("""1. Create an account
2. Log into account
0. Exit""")
    return int(input())


def create_account():
    acc = Account()
    print(f"""Your card has been created
Your card number:
{acc.card}
Your card PIN:
{acc.pin}
""")


def get_balance(card):
    print()
    print("Balance :", card[3])
    print()


def add_income(data):
    global card
    print("Enter income:")
    income = int(input())
    cur.execute("update card set balance = " + str(data[3] + income) + " where id = " + str(data[0]))
    conn.commit()
    card = cur.execute("select * from card where id ="+str(data[0])).fetchone()
    print("Income was added!")
    print()


def do_transfer(data):
    global card
    print("""Transfer
Enter card number:""")
    receiver = input()
    if receiver == data[1]:
        print("You can't transfer money to the same account!")
    elif not verify_card(receiver):
        print("Probably you made a mistake in the card number. Please try again!")
        print()
    else:
        to_card = cur.execute("select * from card where number = "+receiver).fetchone()
        if to_card is not None:
            amount = int(input("Enter how much money you want to transfer:"))
            if amount > data[3]:
                print("Not enough money!")
            else:
                cur.execute("update card set balance = " + str(data[3] - amount) + " where id = " + str(data[0]))
                cur.execute("update card set balance = " + str(to_card[3] + amount) + " where id = " + str(to_card[0]))
                conn.commit()
                card = cur.execute("select * from card where id ="+str(card[0])).fetchone()
                print("Success!")
        else:
            print("Such a card does not exist.")
            print()
    return False


def close_account(card):
    print()
    cur.execute("delete from card where id = " + str(card[0]))
    conn.commit()
    print("The account has been closed!")
    print()


def login():
    global card
    print("Enter your card number:")
    number = input()
    print("Enter your PIN:")
    pin = input()
    card = cur.execute("select * from card where number =" + number + " and pin =" + pin + "").fetchone()
    if card:
        print()
        print("You have successfully logged in!")
        print()
        choice2 = 5
        while choice2 != 0:
            print("""1. Balance
2. add income
3. Do transfer
4. close account
0. Exit""")
            choice2 = int(input())
            if choice2 == 1:
                get_balance(card)
            elif choice2 == 2:
                add_income(card)
            elif choice2 == 3:
                do_transfer(card)
            elif choice2 == 4:
                close_account(card)
                return 2
        else:
            print()
            return 0
    else:
        print()
        print("Wrong card number or PIN!")
        print()


while True:
    choice = menu()
    if choice == 1:
        create_account()
    elif choice == 2:
        if login() == 0:
            print("Bye!")
            break
    elif choice == 0:
        print("Bye!")
        break
