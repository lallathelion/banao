import sqlite3
import datetime
import uuid

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
    
    def insert_email_recipient(self, email_uuid:uuid.UUID, email_recipient):
        date = datetime.datetime.now().timestamp()
        uuid_int = email_uuid.int%(1E+20)
        self.cursor.execute(INSERT_RECIPIENT, (uuid_int, email_recipient, date))
        self.database.commit()
    
    def update_user_time(self, email_uuid:uuid.UUID):
        date = datetime.datetime.now().timestamp()
        uuid_int = email_uuid.int%(1E+20)
        self.cursor.execute(OPENED_EMAIL, (uuid_int, date))
        self.database.commit()

if __name__ == '__main__':
    db = Database('new_data')
    db.init_database()
    db.create_schema()
    print(db)
    uuid_data = uuid.uuid4()
    db.insert_email_recipient(uuid_data, 'testemail@gmail.com')
    db.update_user_time(uuid_data)


        
