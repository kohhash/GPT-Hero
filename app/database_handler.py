import sqlite3
import bcrypt
from password_encrypt import password_encrypt, password_decrypt
from datetime import datetime
from load_resources import ResourceValues


class Database:
    user_details_table_name = "user_details"
    user_history_table_name = "rephrased_essay_records"

    def __init__(self, file_name):
        self.connection = sqlite3.connect(file_name, detect_types=sqlite3.PARSE_DECLTYPES |
                                                                  sqlite3.PARSE_COLNAMES)
        self.cursor = self.connection.cursor()
        self.table_exists_or_create(self.user_details_table_name, self.create_user_table)
        self.table_exists_or_create(self.user_history_table_name, self.create_user_history_table)

    def table_exists_or_create(self, table_name, create_func):
        self.cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' and name='{table_name}'")
        listOfTables = self.cursor.fetchall()
        print("listOfTables", listOfTables)
        if len(listOfTables) == 0:
            create_func()

    def get_user_field(self, username, field, table_name):
        if self.username_exists(username):
            self.cursor.execute(f"SELECT {field} FROM {table_name} WHERE username=?", (username,))
            row = self.cursor.fetchone()
            if row[0] is None:
                return None

            return row[0]
        else:
            raise Exception(ResourceValues.username_does_not_exist_error)


    def create_user_history_table(self):
        self.cursor.execute(f"""create table {self.user_history_table_name}  
        (
            original_essay           VARCHAR(64000) not null,
            rephrased_essay          VARCHAR(64000),
            timestamp        TIMESTAMP,
            byuser           VARCHAR(16),
            FOREIGN KEY (byuser) REFERENCES user_details(username)
        );""")
        self.connection.commit()

    def create_user_table(self):
        self.cursor.execute(f"""
        CREATE TABLE {self.user_details_table_name}(
        username VARCHAR(16) PRIMARY KEY,
        password VARCHAR(120) NOT NULL ,
        openaiapi_key VARCHAR(255),
        prowritingaidapi_key VARCHAR(255),
        salt VARCHAR(120) NOT NULL ,
        admin BOOLEAN NOT NULL DEFAULT FALSE,
        special_user BOOLEAN NOT NULL DEFAULT FALSE,
        subscribed BOOLEAN NOT NULL DEFAULT FALSE,
        subscription_id VARCHAR(255),
        usage INTEGER      
        )
        """)
        self.connection.commit()

    def insert_essay(self, prompt, answer1, byuser=None):
        if prompt and answer1:  # answer2 can be null
            data = (prompt, answer1, datetime.now().timestamp(), byuser)
            self.cursor.execute(
                f"INSERT INTO {self.user_history_table_name} (original_essay, rephrased_essay, timestamp, byuser) VALUES (?, ?, ?, ?)",
                data)
            self.connection.commit()

        else:
            print(
                f"Could not insert row ({prompt}, {answer1}) into SQL.")


    def get_all(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        data = []
        for row in self.cursor.fetchall():
            data.append(row)
        return data



    def get_query_history(self, username):
        table_name = self.user_history_table_name
        self.cursor.execute(f'SELECT original_essay, rephrased_essay, datetime({table_name}.timestamp, "unixepoch") FROM {table_name} WHERE byuser=?', (username, ))
        data = []
        for row in self.cursor.fetchall():
            data.append(row)
        return data

    def get_all_query_history(self):
        table_name = self.user_history_table_name
        self.cursor.execute(f'SELECT original_essay, rephrased_essay, datetime({table_name}.timestamp, "unixepoch"), byuser FROM {table_name};')
        data = []
        for row in self.cursor.fetchall():
            data.append(row)
        return data

    def list_admin(self):
        table_name = self.user_details_table_name
        self.cursor.execute(f"SELECT username FROM {table_name} WHERE admin=TRUE")
        data = []
        for row in self.cursor.fetchall():
            data.append(row[0])
        return data

    def list_usernames(self):
        table_name = self.user_details_table_name
        self.cursor.execute(f"SELECT username FROM {table_name};")
        data = []
        for row in self.cursor.fetchall():
            data.append(row[0])
        return data
    
    def list_special_users(self):
        table_name = self.user_details_table_name
        self.cursor.execute(f"SELECT username FROM {table_name} WHERE special_user=TRUE")
        data = []
        for row in self.cursor.fetchall():
            data.append(row[0])
        return data

    def username_exists(self, username):
        print(f"Checking if {username} exists.")
        self.cursor.execute(f"SELECT username FROM {self.user_details_table_name} WHERE username=?", (username,))
        data = self.cursor.fetchone()
        if data is not None:
            return True
        else:
            return False


    def get_username_salt(self, username): # Return salt if user exists or Nonr
        if self.username_exists(username):
            self.cursor.execute(f"SELECT salt FROM {self.user_details_table_name} WHERE username=?", (username,))
            salt = self.cursor.fetchone()[0]
            return salt

    def verify_password(self, username, password):
        salt = self.get_username_salt(username)
        if salt is None or not self.username_exists(username):
            return None
        # hashed_pwd = bcrypt.hashpw(password, bytes.fromhex(salt)).hex()
        hashed_pwd, _ = self.salt_password(password, bytes.fromhex(salt))
        self.cursor.execute(f"SELECT password FROM {self.user_details_table_name} WHERE username=?", (username,))
        stored_pwd = self.cursor.fetchone()[0]
        if stored_pwd == hashed_pwd:
            return True
        else:
            return False


    def salt_password(self, password, salt=None): # Return salt, hashed password
        if salt is None:
            salt = bcrypt.gensalt()
        hashed_pwd = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_pwd.hex(), salt.hex()

    def create_user(self, username, password):
        hash_pwd, salt = self.salt_password(password)
        self.cursor.execute(f"INSERT INTO {self.user_details_table_name}(username, password, salt, admin) VALUES (?, ?, ?, FALSE)", (username, hash_pwd, salt))
        self.connection.commit()
        return True

    def is_admin(self, username):
        if self.username_exists(username):
            self.cursor.execute(f"SELECT username FROM {self.user_details_table_name} WHERE username=? AND admin=TRUE", (username,))
            row = self.cursor.fetchone()
            if row is None:
                return None
            elif row[0] == username:
                return True

    def update_field(self, field, value, username, table_name=None):
        if table_name is None:
            table_name = self.user_details_table_name # Default update field is user details table

        self.cursor.execute(f"UPDATE {table_name} SET {field}=? WHERE username=?", (value, username))
        self.connection.commit()

    def set_openai_key(self, username: str, password: str, key: str):
        print("set openai key called")
        print(self.username_exists(username))
        print(self.verify_password(username, password))
        if key is None:
            self.update_field("openaiapi_key", None, username)
            return
        if self.username_exists(username) and self.verify_password(username, password):
            openaiapikey_encrypted = password_encrypt(key.encode("utf-8"), password)
            print("Setting openaiapi key",openaiapikey_encrypted, username)
            self.update_field("openaiapi_key", openaiapikey_encrypted, username)

    def get_openai_key(self, username, password):
        if self.username_exists(username) and self.verify_password(username, password):
            self.cursor.execute(f"SELECT openaiapi_key FROM {self.user_details_table_name} WHERE username=?", (username,))
            row = self.cursor.fetchone()
            if row[0] is None:
                return None
            print("token:", row[0])
            openai_key = password_decrypt(row[0], password).decode()
            return openai_key

    def set_prowritingaidapi_key(self, username: str, password: str, key: str):
        print("Set prowritingaid called, ", username, password, key)

        if key is None:
            self.update_field("prowritingaidapi_key", None, username)
            return
        if self.username_exists(username) and self.verify_password(username, password):
            openaiapikey_encrypted = password_encrypt(key.encode("utf-8"), password)
            self.update_field("prowritingaidapi_key", openaiapikey_encrypted, username)

    def get_prowritingaidapi_key(self, username, password):
        if self.username_exists(username) and self.verify_password(username, password):
            self.cursor.execute(f"SELECT prowritingaidapi_key FROM {self.user_details_table_name} WHERE username=?", (username,))
            row = self.cursor.fetchone()
            if row[0] is None:
                return None

            prowritingaidapi_key = password_decrypt(row[0], password).decode()
            return prowritingaidapi_key

    def set_admin(self, admin_username, admin_status):
        table_name = self.user_details_table_name
        if self.username_exists(admin_username):
            self.cursor.execute(f"UPDATE {table_name} SET admin=? WHERE username=?", (admin_status, admin_username))
            self.connection.commit()

    def set_special_user(self, username, status):
        table_name = self.user_details_table_name
        if self.username_exists(username):
            self.cursor.execute(f"UPDATE {table_name} SET special_user =? WHERE username=?", (status, username))
            self.connection.commit()

    def is_special_user(self, username):
        table_name = self.user_details_table_name
        if self.username_exists(username):
            self.cursor.execute(f"SELECT special_user FROM {table_name} WHERE username=?", (username,))
            row = self.cursor.fetchone()
            if row is None:
                return False
            else:
                return row[0]


    def get_usage(self, username):
        table_name = self.user_details_table_name
        if self.username_exists(username):
            self.cursor.execute(f"SELECT usage FROM  {table_name} WHERE username = ?", (username,))
            row = self.cursor.fetchone()
            if row is None or row[0] is None:
                return 0
            else:
                return int(row[0]) # Return usage in integers
        else:
            raise Exception(ResourceValues.username_does_not_exist_error)


    def set_usage(self, username, usage):
        table_name = self.user_details_table_name
        if self.username_exists(username):
            self.update_field("usage", usage, username)  # Set usage
        else:
            raise Exception(ResourceValues.username_does_not_exist_error)

    def add_usage(self, username, usage):
        new_usage = self.get_usage(username) + usage
        self.set_usage(username, new_usage)

    def is_subscribed(self, username):
        subscribed = self.get_user_field(username, "subscribed", self.user_details_table_name)
        return subscribed

    def subscribe_user(self, username):
        self.update_field("subscribed", True, username, self.user_details_table_name)

    def unsubscribe_user(self, username):
        self.update_field("subscribed", False, username, self.user_details_table_name)

    def get_subscription_id(self, username):
        return self.get_user_field(username, "subscription_id", self.user_details_table_name)

    def get_user_from_subscription(self, subscription_id):
        self.cursor.execute(f"SELECT username FROM {self.user_details_table_name} WHERE subscription_id=?", (subscription_id,))
        row = self.cursor.fetchone()
        if row is None:
            return row

        return row[0]

    def set_subscription_id(self, username, subscription_id):
        self.update_field("subscription_id", subscription_id, username, self.user_details_table_name)