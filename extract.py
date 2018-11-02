import os, platform, subprocess, json, sys, time
import pandas as pd
from models import dbcon

#so we can do a while loop to extract all account actions
def get_last_action_account(account):
    call = 'cleos -u https://eos.greymass.com:443 get actions {} -j -1 -1'.format(account)
    output = json.loads(subprocess.check_output(call, shell=True).decode('utf-8'))
    last_account_seq = output['actions'][-1]['account_action_seq']
    return last_account_seq

#make this better
def get_last_action_db(account):
    try:
        last_action = pd.read_sql('''SELECT last_action_seq from last_actions
            where account = "{}"'''.format(account), dbcon)['last_action_seq'].iloc[0]
        print ('    last_seq = {}'.format(last_action))
        return last_action

    except IndexError:
        try:
            print ('{} is a new account'.format(account))
            dbcon.cursor().execute('''INSERT INTO accounts (account_id) VALUES ('{}')
                                '''.format(account))
            dbcon.commit()
            return 0

        except:
            return 0

def parse_account_json(account, account_json):
    data = account_json
    row_data = []
    for a in data['actions']:
        try:
            row = {
            'global_action_seq': a['global_action_seq'],
            'account_action_seq': a['account_action_seq'],
            'block_num': a['block_num'],
            'block_time': a['block_time'],
            'trx_id': a['action_trace']['trx_id'],
            'type': a['action_trace']['act']['name'],
            'sender': a['action_trace']['act']['data']['from'],
            'receiver': a['action_trace']['act']['data']['to'],
            'quantity': a['action_trace']['act']['data']['quantity'],
            'memo': a['action_trace']['act']['data']['memo'],
            }
        except (KeyError, TypeError):
            row = {
            'global_action_seq': a['global_action_seq'],
            'account_action_seq': a['account_action_seq'],
            'block_num': a['block_num'],
            'block_time': a['block_time'],
            'trx_id': a['action_trace']['trx_id'],
            'type': a['action_trace']['act']['name'],
            }

        row_data.append(row)
    df = pd.DataFrame(row_data)

    df = df.reindex(columns = ['global_action_seq', 'account_action_seq', 'block_num', 'block_time',
             'trx_id', 'type', 'sender', 'receiver', 'quantity', 'currency',  'memo', 'query'])


    df['query'] = account

    df['currency'] = df['quantity'].apply(lambda x: str(x).split(' ')[1]
                                            if pd.notnull(x) else x)

    def quantity_clean(row):
        if pd.notnull(row['quantity']):
            quantity = float(str(row['quantity'].split(' ')[0]))
        #return quantity
        if row['query'] == row['sender']:
            return -quantity

        elif row['query'] == row['receiver']:
            return quantity
        else:
            try:
                return float(str(row['quantity'].split(' ')[0]))
            except:
                pass

    df['quantity'] = df.apply(quantity_clean, axis=1)
    df = df[['global_action_seq', 'account_action_seq', 'block_num', 'block_time',
             'trx_id', 'type', 'sender', 'receiver', 'quantity', 'currency',  'memo', 'query']]
    return df

def extract_json(account, pos, offset):
    call = 'cleos -u https://eos.greymass.com:443 get actions {} {} {} -j'.format(account, pos, offset)
    output = json.loads(subprocess.check_output(call, shell=True).decode('utf-8'))
    df = parse_account_json(account, output)
    return df


#how do i deduplicate from here?
def store(account):
    print ('{} extracting...'.format(account))
    #like actual from cleos
    last_action_actual = get_last_action_account(account)
    last_action_db = get_last_action_db(account)

    #this is where i need to fix the thing
    while last_action_db <= last_action_actual:
        if last_action_actual == last_action_db:
            print ('    no new actions')
            break

        if last_action_db == 0:
            last_action_db = 0
        else:
            last_action_db = last_action_db + 1

        df = extract_json(account, last_action_db, +1000)
        df = df.drop_duplicates(subset=['trx_id', 'quantity', 'memo'])
        df.to_sql('actions', dbcon, if_exists='append', index=False)
        last_action_db = get_last_action_db(account)

    dbcon.cursor().execute(
        '''
        DELETE  from actions
        WHERE   rowid not in
             (
             select  min(rowid)
             from    actions
             group by trx_id, quantity, memo
             )
        ''')

    dbcon.commit()

def db_to_csv():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    extract_df = pd.read_sql("SELECT * from actions where type='transfer'", dbcon)
    extract_df.to_csv('db_extract_{}.csv'.format(timestr), index=False)
    print ('db extracted to csv')
