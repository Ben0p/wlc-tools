import paramiko
import time
from datetime import datetime
import getpass


def login(ip, un, pw):
    print('Logging in to WLC...')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(ip, port=22, username=un, password=pw)
    connection = client.invoke_shell()
    connection.settimeout(1)
    time.sleep(1)
    connection.send(un+'\r')
    time.sleep(1)
    connection.send(pw+'\r')
    time.sleep(1)
    output = connection.recv(9999).decode(encoding='utf-8')

    lastline = output.splitlines()[-1]
    if lastline == "User:":
        print("Login failed, try again...")
        return(False)

    else:
        print('Logged in!')
        return(connection)




def iosVersion(ap):
    print(f"Checking IOS version on {ap}...")

    try:
        output = connection.recv(9999).decode(encoding='utf-8')
    except:
        pass

    connection.send(f'show ap config general {ap}\r')
    time.sleep(1)
    output = connection.recv(9999).decode(encoding='utf-8')
    lines = output.splitlines()

    for line in lines:
        if line.startswith('IOS Version'):
            line = line.split(".... ")
            line = line[1]
            print(line)
            break
    
    return(line)



def getSettings():
    settings ={}

    print("Retrieving settings...")
    try:
        with open('settings.txt', 'r') as f:
            for line in f:
                line = line.strip()
                setting, parameter = line.split('=')
                settings[setting] = parameter
    except:
        input("Failed to open settings.txt")

    settings['wlc_username'] = input("Username: ")
    settings['password'] = getpass.getpass()

    return(settings)
    

if __name__ == '__main__':

    while True:
        settings = getSettings()
        connection = login(settings['wlc_ip'], settings['wlc_username'], settings['password'])
        if connection:
            connection.send(f'config paging disable\r')
            time.sleep(1)
            break
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    out_file_name = f'{timestamp} - IOS Versions.csv'

    with open(settings['maps_file'], 'r') as maps:
        with open(out_file_name, 'w', 5) as tests:
            tests.write('ap,version\n')

            for line in maps:
                if line[0] == '#':
                    continue

                ap = line.strip()

                version = iosVersion(ap)
                tests.write(f'{ap},{version}\n')
                tests.flush()

            tests.close()

        maps.close()
