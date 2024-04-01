import pandas
import bcrypt


def read_data(path = "accounts/data/gpthero_data.csv"):
    return pandas.read_csv(path)

def username_exists(username): # Return True if user exists or False
    data = read_data()
    if username in data['username'].values:
        return True
    else:
        return False

def get_username_salt(username): # Return salt if user exists or Nonr
    if username_exists(username):
        data = read_data()
        return data[data['username'] == username]['salt'].values[0]
        return salt
    else:
        return None

def salt_password(password, salt=None): # Return salt, hashed password
    if salt is None:
        salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_pwd.hex(), salt.hex()


def verify_password( username, password):
    salt = get_username_salt(username)
    data = read_data()
    if salt is None or not username_exists(username):
        return False
    # hashed_pwd = bcrypt.hashpw(password, bytes.fromhex(salt)).hex()
    hashed_pwd, _ = salt_password(password, bytes.fromhex(salt))
    print(hashed_pwd)
    stored_pwd = data[data['username'] == username]['password'].values[0]
    print(stored_pwd)
    if stored_pwd == hashed_pwd:
        return True
    else:
        return False