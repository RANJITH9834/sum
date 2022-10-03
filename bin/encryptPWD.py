# Description: This program will be executed only when we have a new password file.

from cryptography.fernet import Fernet
import os

from configparser import ConfigParser


def encrypt_password(password,properties_file_path):
  """This function will encrypt the password and store it on the given properities file"""
  try:
    key = Fernet.generate_key()
    refKey = Fernet(key)
    mypwdbyt = bytes(password, 'utf-8') # convert into byte
    encryptedPWD = refKey.encrypt(mypwdbyt)
    parser = ConfigParser()
    parser.read(properties_file_path)
    parser.set('job1-configuration','refKey',key.decode('utf-8'))
    parser.set('job1-configuration','encryptedPWD',encryptedPWD.decode('utf-8'))
  except Exception as msg:
    print("unable to encrypt the password")
    raise Exception(msg)
  # Writing our configuration file to properties file
  try:
    with open(properties_file_path, 'w') as configfile:
        parser.write(configfile)
  except Exception as msg:
    print("Unable to write the data into properties file")
    raise Exception(msg)

encrypt_password(password=input("enter password : "),properties_file_path=input("config.properties file path "))