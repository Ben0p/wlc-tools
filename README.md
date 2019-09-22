# link-test
Cisco aironet automatic wireless link test

## Instructions

1. Enter settings in "settings.txt"
2. Enter Access Point hostnames in "aps.txt"
3. Run "run.py" (or use PyInstaller to convert to .exe)
4. Enter Password for your Cisco Wireless Lan Controller
5. Sit back and relax

## How it works

1. Establishes a connection with the Cisco Wireless Lan Controller via SSH
2. For each access point in the aps.txt list:
    1. show mesh path {ap}
    2. Extracts next AP in upstream hop
    3. Runs command:
        1. config mesh linktest {child} {parent} {data_rate} {packets_per_second} {packet_size} {duration}
        2. eg: config mesh linktest AP-HOSTNAME-01 AP-HOSTNAME-02 18 20 100 15
    4. Logs to .csv file with timestamp
3. That's about it
