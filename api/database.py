import sqlite3
import datetime
import uuid
from flask_table import Table, Col

class ItemTable(Table):
    uuid = Col('email_uuid')
    recipient = Col('recipient')
    sent_time = Col('sent')
    accessed_time = Col('opened at')

class Item(object):
    def __init__(self, uuid, recipient, sent_time, accessed_time=None):
        self.uuid = uuid
        self.recipient = recipient
        self.sent_time = sent_time
        self.accessed_time = accessed_time if accessed_time else "Not Yet Opened." 


mysql_schema = """
CREATE TABLE IF NOT EXISTS public_mails(
    `email_uuid` BIGINT PRIMARY KEY,
    `email_recipient` VARCHAR(255) NOT NULL,
    `sent_timpestamp` DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS opens_at(
    `email_uuid` BIGINT,
    `opened_at` DATETIME NOT NULL,
    FOREIGN KEY(`email_uuid`) REFERENCES public_mails(`email_uuid`)
);

"""


schema = {
    'public': 'public_mails',
    'open_table': 'opens_at',
    'uuid': 'email_uuid',
    'sent': 'sent_timpestamp',
    'opened': 'opened_at',
    'recipient': 'email_recipient'
}

INSERT_RECIPIENT = "INSERT INTO {0}({1}, {2}, {3}) VALUES (?, ?, ?);".format(
        schema['public'], schema['uuid'], schema['recipient'], schema['sent'])
OPENED_EMAIL = "INSERT INTO {0}({1}, {2}) VALUES (?, ?);".format(
    schema['open_table'], schema['uuid'], schema['opened'])

SELECT_QUERY = "SELECT {4}.{0}, {4}.{1}, {4}.{2}, {5}.{3} FROM {4} LEFT JOIN {5} ON {4}.{0} == {5}.{0};".format(
    schema['uuid'], 
    schema['recipient'], 
    schema['sent'], 
    schema['opened'], 
    schema['public'], 
    schema['open_table']
)
print(SELECT_QUERY)
print(INSERT_RECIPIENT)
print(OPENED_EMAIL)


class Database:
    def __init__(self, database_file:str):
        self.filename = database_file
        self.current_commits = 0
        self.current_timestamp = 0
        self.database = None
        self.cursor = None


    def init_database(self):
        self.database = sqlite3.connect(self.filename, check_same_thread=False)
        self.cursor = self.database.cursor()
    
    def create_schema(self):
        print(self.cursor.executescript(mysql_schema))
    
    def insert_email_recipient(self, email_uuid, email_recipient):
        print(f"SEND EMAIL UUID : {email_uuid}")
        date = datetime.datetime.now().timestamp()
        uuid_int = email_uuid%(1E+20)
        self.cursor.execute(INSERT_RECIPIENT, (uuid_int, email_recipient, date))
        self.database.commit()
    
    def update_user_time(self, email_uuid):
        print(f"OPEN EMAIL UUID : {email_uuid}")
        date = datetime.datetime.now().timestamp()
        uuid_int = email_uuid%(1E+20)
        self.cursor.execute(OPENED_EMAIL, (uuid_int, date))
        self.database.commit()
    
    def get_user_details(self):
        self.cursor.execute(SELECT_QUERY)
        data = self.cursor.fetchall()
        entry = []
        if data:
            for user in data:
                email_uuid, recipient, sent_time, access_time = user
                sent_time = datetime.datetime.fromtimestamp(sent_time).strftime("%d-%m-%Y :: %H:%M:%S")
                access_time = datetime.datetime.fromtimestamp(access_time).strftime("%d-%m-%Y :: %H:%M:%S") if access_time else 'Not opened Yet'
                email_uuid = int(email_uuid)
                item = Item(str(email_uuid), recipient, sent_time, access_time)
                entry.append(item)
        return ItemTable(items=entry)

if __name__ == '__main__':
    db = Database('./api/main_data.db')
    db.init_database()
    db.create_schema()
    print(db)
#     uuid_data = uuid.uuid4()
#     db.insert_email_recipient(uuid_data, 'testemail@gmail.com')
#     db.update_user_time(uuid_data)
    print(db.get_user_details().__html__())

        
