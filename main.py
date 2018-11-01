import pandas as pd
from extract import store, db_to_csv
import time

#make a config.py file and account_lst = [list of accounts]
from config import account_lst


for account in account_lst:
    store(account)
    time.sleep(6)
    print ('{} extracted! \n'.format(account))

db_to_csv()
