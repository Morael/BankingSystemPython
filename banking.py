from random import randint
import sqlite3

STATE = "main_menu"
LOGGED = False
turn_on = True
USER_ID = ''


def menu():
    """ print interface for the user """
    global STATE
    if STATE == "main_menu":
        return "\n1. Create an account\n2. Log into account\n0. Exit"
    elif STATE == "create_an_account":
        return "\nYour card has been created\nYour card number:"
    elif STATE == "log_into":
        return "\nEnter your card number:"
    elif STATE == "logged":
        return "1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit"
    elif STATE == "logging":
        return "\nYou have successfully logged in!\n"
    elif STATE == "logout":
        return "\nYou have successfully logged out!"
    elif STATE == "logging_failure":
        return "\nWrong card number or PIN!"
    elif STATE == "add_income":
        return "\nEnter income:"
    elif STATE == "income_added":
        return "\nIncome was added!\n"
    elif STATE == "transfer":
        return "\nTransfer\nEnter card number:"
    elif STATE == "luhn_transfer_mistake":
        return "\nProbably you made mistake in the card number. Please try again! \n"
    elif STATE == "transfer_same_account":
        return "\nYou can't transfer money to the same account!\n"
    elif STATE == "transfer_mistake":
        return "\nSuch a card does not exist.\n"
    elif STATE == "transfer_amount_of_money":
        return "\nEnter how much money you want to transfer:"
    elif STATE == "not_enough_money":
        return "Not enough money!\n"
    elif STATE == "transfer_successful":
        return "Success!\n"
    elif STATE == "closing_account":
        return "\nThe account has been closed!"
    elif STATE == "exit":
        return "\nBye!"
    else:
        return None


def state_logic():
    """ logic of the program depending on states """
    print(menu())
    entry = my_input()
    global STATE
    global USER_ID
    if STATE == "main_menu":
        if entry == "1":
            STATE = "create_an_account"
            print(menu())
            val1 = create_card_number()
            print(val1)
            val2 = create_pin()
            print(f"Your card PIN:\n{val2}")
            adding_to_database(val1, val2, 0)
            # for security reasons clear card/pin values:
            val1, val2 = "", ""
            STATE = "main_menu"
        elif entry == "2":
            STATE = "log_into"
            print(menu())
            log_in()
        else:
            STATE = "exit"
            print(menu())
            exit()
    elif STATE == "logged":
        if entry == "1":
            print(balance())
        elif entry == "2":
            STATE = "add_income"
            print(menu())
            add_income()
            STATE = "income_added"
            print(menu())
            STATE = "logged"
        elif entry == "3":
            STATE = "transfer"
            print(menu())
            do_transfer()
        elif entry == "4":
            STATE = "closing_account"
            close_account()
            print(menu())
            STATE = "main_menu"
        elif entry == "5":
            USER_ID = ""
            STATE = "logout"
            print(menu())
            STATE = "main_menu"
        elif entry == "0":
            USER_ID = ""
            STATE = "exit"
            print(menu)
            exit()
        else:
            STATE = "logged"
            print()

    else:
        STATE = "exit"
        print(menu())
        exit()


def do_transfer():
    """ transfers money from my account to other account of my choice """
    global STATE, USER_ID
    if STATE == "transfer":
        transfer_account = (my_input(),)
        if transfer_same_account(transfer_account):
            STATE = "transfer_same_account"
            print(menu())
            STATE = "logged"
        elif luhn_algorithm_check(transfer_account):
            STATE = "luhn_transfer_mistake"
            print(menu())
            STATE = "logged"
        elif loading_for_transfer(transfer_account) is None:
            STATE = "transfer_mistake"
            print(menu())
            STATE = "logged"
        else:
            STATE = "transfer_amount_of_money"
            print(menu())
            transfer_steps(transfer_account)


def transfer_steps(account):
    """ every step to finish a transaction """
    global STATE
    if STATE == "transfer_amount_of_money":
        money_to_transfer = (my_input(),)
        to_transfer = str(money_to_transfer).strip("<>,/',&^$#@!&()[]")
        if loading_from_database() >= int(to_transfer):
            take_income(int(to_transfer))
            give_income(int(to_transfer), account)
            STATE = "transfer_successful"
            print(menu())
            STATE = "logged"
        else:
            STATE = "not_enough_money"
            print(menu())
            STATE = "logged"


def take_income(to_transfer):
    """ take income from my account for transfer """
    global STATE
    if STATE == "transfer_amount_of_money":
        account_new_state = loading_from_database() - to_transfer
        cur.execute(f'UPDATE card SET balance={account_new_state} WHERE number=?', USER_ID,)
        conn.commit()


def give_income(to_transfer, account):
    """ take income from my account for transfer """
    global STATE
    if STATE == "transfer_amount_of_money":
        account_new_state = loading_for_transfer(account) + to_transfer
        cur.execute(f'UPDATE card SET balance={account_new_state} WHERE number=?', account,)
        conn.commit()


def loading_from_database():
    """ load balance from database """
    if STATE == "logged" or "add_income":
        for row in cur.execute('SELECT balance FROM card WHERE number =?', USER_ID,):
            data = int(str(row).strip("(),"))
            return data


def loading_for_transfer(transfer_id):
    """ load balance from database """
    if STATE == "logged" or "add_income":
        for row in cur.execute('SELECT balance FROM card WHERE number =?', transfer_id,):
            data = int(str(row).strip("(),"))
            return data


def transfer_same_account(transfer_account):
    """ checks if transfer account is not an user account """
    global STATE
    if transfer_account == USER_ID:
        STATE = "transfer_same_account"
        return True
    else:
        return False


def luhn_algorithm_check(transfer_card_number):
    """ check luhn algorithm of the transfer card """
    numb = ''.join(transfer_card_number)
    check_matrix = [int(i) for i in numb]
    print(check_matrix)
    for i in range(0, 15, 2):
        check_matrix[i] *= 2
    print(check_matrix)
    for i in range(0, 15):
        if check_matrix[i] > 9:
            check_matrix[i] -= 9
    print(check_matrix)
    print(check_matrix[15])
    control_number = 10 - ((sum(check_matrix) - check_matrix[15]) % 10)
    if control_number < 10:
        luhn_number = control_number
    else:
        luhn_number = "0"
    if check_matrix[15] == luhn_number:
        return False
    else:
        return True


def log_in():
    """ log to the program using created account and function my_input() """
    global STATE, USER_ID
    card_number = (my_input(),)
    print("Enter your PIN:")
    pin_number = (my_input(),)
    check_user(card_number, pin_number)
    if check_user(card_number, pin_number):
        STATE = "logging"
        print(menu())
        STATE = "logged"
        USER_ID = card_number
    else:
        STATE = "logging_failure"
        print(menu())
        STATE = "main_menu"


def check_user(card_number, pin_number):
    """ check if inserted login data is correct """
    for row in cur.execute('SELECT pin FROM card WHERE number =? ;', card_number, ):
        if row == pin_number:
            return True
        else:
            return False


def my_input():
    """ user input main function """
    answer = input()
    return answer


def create_card_number():
    """ create new card number and return to the logic """
    card_number = "400000" \
                  + str(randint(000000000, 999999999)).zfill(9)
    matrix = []
    # save as number
    for i in card_number:
        matrix.append(int(i))
    for i in range(0, len(card_number), 2):
        matrix[i] *= 2
    for i in range(0, len(card_number)):
        if matrix[i] > 9:
            matrix[i] -= 9
    control_number = str(10 - (sum(matrix) % 10))
    if int(control_number) < 10:
        card_number += control_number
    else:
        card_number += "0"
    return card_number


def create_pin():
    """ create PIN for new user and return to the logic """
    pin_number = str(randint(0, 9999)).zfill(4)
    return pin_number


def balance():
    """ check balance on the account """
    global STATE
    if STATE == "logged":
        return f"\nBalance: {loading_from_database()}\n"


def adding_to_database(val1, val2, b):
    """ put data in card table """
    cur.execute('INSERT INTO card VALUES(NULL, ?, ?, ?)', (val1, val2, b,))
    conn.commit()


def add_income():
    """ adds income to my account """
    global STATE
    if STATE == "add_income":
        my_income = int((my_input().strip("(),'<>$&%/@")))
        account_new_state = my_income + loading_from_database()
        cur.execute(f'UPDATE card SET balance={account_new_state} WHERE number=?', USER_ID,)
        conn.commit()


def close_account():
    """ closes my bank account """
    if STATE == "closing_account":
        cur.execute('DELETE FROM card WHERE number=?', USER_ID)
        conn.commit()


while turn_on:
    """ turn program on """
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS card('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'number TEXT UNIQUE, pin TEXT, '
                'balance INTEGER DEFAULT 0);')
    state_logic()
