# wlc-tools
Cisco Aironet Wireless LAN Controller Tools

## Instructions
### Link Test
Runs a wireless link test between all Mesh Access Points (MAPs) and it's parent Access Point (AP)
1. Enter settings in "settings.txt"
2. Enter Access Point hostnames in "aps.txt"
3. Run "run.py" (or use PyInstaller to convert to .exe)
4. Enter password for your Cisco Wireless Lan Controller
5. Sit back and relax
### Adjusted Ease 
Checks calculated best parent Access Point (AP) for each Mesh Access Point (MAP)
1. Enter settings in "settings.txt"
2. Enter Access Point hostnames in "aps.txt"
3. Run "run.py" (or use PyInstaller to convert to .exe)
4. Enter password for your Cisco Wireless Lan Controller
5. Sit back and relax

## How it works
1. Establishes a connection with the Cisco Wireless Lan Controller via SSH
2. For each access point in the aps.txt list:
    1. show mesh path {ap}
    2. Extracts next AP in upstream hop
    3. Runs relevant command
    4. Logs to .csv file with timestamp
3. That's about it
