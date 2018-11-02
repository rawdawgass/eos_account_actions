from extract import store, db_to_csv
import pandas as pd
import time, sys
from models import dbcon


def export_to_csv(account):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    extract_df = pd.read_sql("SELECT * from actions where type='transfer' and query='{}'".format(account), dbcon)
    extract_df.to_csv('{}_extract_{}.csv'.format(account, timestr), index=False)
    print ('{} exported to csv'.format(account))

#make a config.py file and account_lst = [list of accounts]
def app():
    #auto: runs from list in config.py
    #manual: user inputs comma separated account list
    script = sys.argv[0]
    mode = sys.argv[1]

    try:
        export = sys.argv[2]
    except IndexError:
        export = None

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
        if export == 'csv':
            export_to_csv(account)

try:
    app()
except IndexError:
    #raise
    print ('example: python3 main.py [manual or auto] csv')
