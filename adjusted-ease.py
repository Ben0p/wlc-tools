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




def adjustedEase(_map):
    print(f"Checking adjusted ease for {_map}...")

    ease = []
    checked_ap = False
    checked_ae = False   

    try:
        output = connection.recv(9999).decode(encoding='utf-8')
    except:
        pass

    connection.send(f'show mesh neigh detail {_map}\r')
    time.sleep(1)
    output = connection.recv(9999).decode(encoding='utf-8')
    lines = output.splitlines()

    for line in lines:
        if line.startswith('AP MAC'):
            ap = line.split('AP Name: ')
            if len(ap) == 2:
                ap = ap[1]
            else:
                ap = 'Unknown'
            checked_ap = True

        if line.startswith('adjustedEase'):
            try:
                ae = line.split(',')[0]
                ae = ae.split()[1]
            except:
                ae = ''
            checked_ae = True
        
        if checked_ap and checked_ae:
            checked_ap = False
            checked_ae = False        
            ease.append(
                {
                    'best': ap,
                    'ease': ae
                }
            )
    
    if ease:
        best_ease = max(ease, key=lambda x:x['ease'])
        best_ease['map'] = _map
    else:
        print(f'{_map} offline')
        best_ease={}
        best_ease['best'] = ''
        best_ease['ease'] = ''
        best_ease['map'] = _map
    
    return(best_ease)
        
def showMeshPath(ap):

    print(f"Checking mesh path for {ap}...")

    meshPath = {}
    hops = []

    # Clear out the cache
    try:
        output = connection.recv(9999).decode(encoding='utf-8')
    except:
        pass


    connection.send(f'show mesh path {ap}\r')
    time.sleep(0.5)
    output = connection.recv(9999).decode(encoding='utf-8')
    lines = output.splitlines()

    meshPath['ap'] = ap
    try:
        if lines[2] == 'Cisco AP name is invalid.':
            meshPath['online'] = False
            return(meshPath)

        else:
            meshPath['online'] = True
            meshPath['root'] = root_ap = lines[-2].split()[0]
            del lines[0:5]
            del lines[-2:]
            for idx, ap in enumerate(lines):
                
                ap = ap.split()
                stats = {

                    'ap' : ap[0],
                    'channel' : ap[1],
                    'rate' : ap[2],
                    'snr' : ap[3],
                    'hop' : idx+1
                }
                hops.append(stats)
            
            meshPath['hops'] = hops

            return(meshPath)
    except IndexError:
        meshPath['online'] = False
        print("Failed, skipping...")
        return(meshPath)


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

    settings['password'] = getpass.getpass()
    

    return(settings)

def counter(sec):
    interval = sec/100
    
    for i in range(101):       # for 0 to 100
        s = str(i) + '%'       # string for output
        print(s, end='')       # just print and flush
        print('\r', end='')    # back to the beginning of line    
        time.sleep(interval)   # sleep for 200ms


if __name__ == '__main__':

    while True:
        settings = getSettings()
        connection = login(settings['wlc_ip'], settings['wlc_username'], settings['password'])
        if connection:
            break


    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    out_file_name = f'{timestamp} - Adjusted Ease.csv'

    with open(settings['maps_file'], 'r') as maps:
        with open(out_file_name, 'w', 5) as tests:
            tests.write('time,map,best,ease,current,is best\n')
            for line in maps:
                if line[0] == '#':
                    continue
                _map = line.strip()
                testtime = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                result = adjustedEase(_map)
                mesh_path = showMeshPath(_map)
                if mesh_path['online']:
                    current = mesh_path['hops'][0]['ap']

                    if result['best'] == current:
                        is_best = True
                    else:
                        is_best = False
                else:
                    current = ''
                    is_best = ''

                time.sleep(0.5)
                tests.write(f"{testtime},{result['map']},{result['best']},{result['ease']},{current},{is_best}\n")

                tests.flush()

            tests.close()
        maps.close()
