from cryptography.fernet import Fernet

def get_password(encryptionPwd,refKey,logger,logHandler):
    """This function will take encryptedpassword and reference key and return the password"""
    try:
        # read encrypted pwd and convert into byte
        encpwdbyt = bytes(encryptionPwd, 'utf-8')
        # read key and convert into byte
        refKeybyt = bytes(refKey, 'utf-8')
        # use the key and encrypt pwd
        keytouse = Fernet(refKeybyt)
        myPass = (keytouse.decrypt(encpwdbyt))
        # print("my password - ",myPass)
        str_password = myPass.decode('UTF-8')  
    except Exception as msg:
        logger.error("Unable to decrypt the password")
        logger.removeHandler(logHandler)
    return str_password

# print(get_password(refKey="s37fblfC7vitV4xkfVxkUnSR3aTBBgYWNgONiKsarGM=",encryptionPwd="gAAAAABg-D-i1QO0phG0gh_tc5eE-Qf_6GbJCix3dMqC3mB6LPS819BysBcpUM6l69n7Dw3rJgQ53RicjTQZrQaGQpbnsyewIg=="))