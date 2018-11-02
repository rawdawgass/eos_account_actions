from extract import store, db_to_csv
import pandas as pd
import time, sys

#make a config.py file and account_lst = [list of accounts]

def app():
    #auto: runs from list in config.py
    #manual: user inputs comma separated account list
    script = sys.argv[0]
    mode = sys.argv[1]
    if mode == 'manual':
        user_input = input('enter accounts comma separated: ')
        account_lst = user_input.replace(' ','').split(',')
        print ('You selected: {} \n'.format(account_lst))

    if mode == 'auto':
        from config import account_lst



    for account in account_lst:
        store(account)
        time.sleep(6)
        print ('{} extracted! \n'.format(account))

app()
