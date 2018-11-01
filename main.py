from extract import store
from config_actual import account_lst
import time

for account in account_lst:
    store(account)
    time.sleep(6)
