import os
import sys
import socket
import json

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import TLS_FTPHandler
from pyftpdlib.servers import FTPServer
from OpenSSL import crypto
from datetime import datetime, timedelta

BASE_PATH = os.path.join(os.environ.get("BASE_PATH"))
CONF_PATH = os.path.join(BASE_PATH, "conf")
DATA_PATH = os.path.join(BASE_PATH, "data")
KEY_PATH = os.path.join(CONF_PATH, "key.pem")
CERT_PATH = os.path.join(CONF_PATH, "cert.pem")
JSON_USER_PATH = os.path.join(CONF_PATH, "user.json")

def console_log(message):
    print(message)
    # sys.stdout.write(message"\n")
    # sys.stdout.flush()

def create_self_signed_cert():

    if (os.path.exists(KEY_PATH)):
        os.remove(KEY_PATH)
    if (os.path.exists(CERT_PATH)):
        os.remove(CERT_PATH)
    cert_cn = os.environ.get("CERT_CN")
    if not cert_cn:
        cert_cn = socket.gethostname()
        console_log("The environment variable CERT_CN is not set - new value is (" + cert_cn + ").")

    # Create a key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Create a self-signed certificate
    cert = crypto.X509()
    #cert.get_subject().C = "US"  # Country
    #cert.get_subject().ST = "State"  # State
    #cert.get_subject().L = "City"  # City
    #cert.get_subject().O = "Organization"  # Organization
    #cert.get_subject().OU = "Organizational Unit"  # Organizational Unit
    cert.get_subject().CN = cert_cn  # Common Name (e.g., your domain)
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60 * 10)  # Valid for 10 years
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    # Write the private key to a file
    with open(KEY_PATH, "wb") as key_file:
        key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    # Write the certificate to a file
    with open(CERT_PATH, "wb") as cert_file:
        cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

def check_configuration():
    console_log("Check configuration")
    if (not(os.path.exists(BASE_PATH))):
        console_log("Please define the environment variable BASE_PATH and use a valid path (Current value " + BASE_PATH + ")")
    if (not(os.path.exists(CONF_PATH))):
        os.mkdir(CONF_PATH)
    if (not(os.path.exists(DATA_PATH))):
        os.mkdir(DATA_PATH) 
    if ((not(os.path.exists(CERT_PATH))) or (not(os.path.exists(CERT_PATH)))):
        console_log("Try to create certificate...")
        create_self_signed_cert()
        console_log("Certificate created")

def add_user_from_json(authorizer):
    if (not(os.path.exists(JSON_USER_PATH))):
        console_log("The file " + JSON_USER_PATH + " was not found. The user config file will be skipped")
        return False
    json_file = open(JSON_USER_PATH) 
    user_list_data = json.load(json_file)
    #console_log("User data list: " + json.dumps(user_list_data))
    for user_data in user_list_data:
        #console_log("User data: " + json.dumps(user_data))
        user_name = user_data.get("User")
        user_password = user_data.get("Password")
        sub_folder = user_data.get("Folder")
        path = DATA_PATH
        if not user_name:
            return False
        if not user_password:
            return False
        if not permissions:
            permissions = 'elradfmwMT'
        if sub_folder:
            path = os.path.join(DATA_PATH, sub_folder)
            if (not(os.path.exists(path))):
                os.mkdir(path)
        authorizer.add_user(user_name, user_password, path, perm=permissions)
        console_log("User " + user_name + " added to the user list")        
    return True

def add_user(authorizer):
    if (add_user_from_json(authorizer)):
        return
    user_name = os.environ.get("USER_NAME")
    user_password = os.environ.get("USER_PASSWORD")
    if not user_name:
        user_name = "ftp_user"
        console_log("Please define the environment variable USER_NAME - Default user name is " + user_name)
    if not user_password:
        user_password = "ftp_password"
        console_log("Please define the environment variable USER_PASSWORD - Default user password is " + user_password )
    authorizer.add_user(user_name, user_password, DATA_PATH, perm='elradfmwMT')
    console_log("User " + user_name + " added to the user list")

def start_sftp_server():
    console_log("Add users")
    authorizer = DummyAuthorizer()
    add_user(authorizer)
    console_log("Start server")
    handler = TLS_FTPHandler
    handler.certfile = CERT_PATH
    handler.keyfile = KEY_PATH
    handler.authorizer = authorizer
    handler.tls_control_required = True
    handler.tls_data_required = True
    server = FTPServer(('', 2121), handler)
    server.serve_forever()


def main():
    check_configuration()
    start_sftp_server()

if __name__ == '__main__':
    main()