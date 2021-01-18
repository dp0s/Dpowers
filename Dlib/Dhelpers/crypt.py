from cryptography.fernet import Fernet
from .container import container

fernet = Fernet(Fernet.generate_key())

def generate_key(name):
    key = fernet.encrypt(Fernet.generate_key())
    container.set_temp_store_key(name, key, 60*120)

def get_coder(name):
    f = Fernet(fernet.decrypt(container.store[name]))
    return lambda by: f.decrypt(by).decode(), lambda str: f.encrypt(
            str.encode())