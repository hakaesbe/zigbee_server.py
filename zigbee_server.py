#!/usr/bin/env python
import serial
import requests
import sys
import time
import os
import shutil
import urlparse
import eventlet
import ConfigParser
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# Config
config = ConfigParser.ConfigParser()
config.read('config.cfg')
USB_PATH = config.get('ZIGBEE', 'USB_PATH')
SERVER_ZIGBEE_IP = config.get('ZIGBEE', 'ip')
SERVER_ZIGBEE_PORT = config.get('ZIGBEE', 'port')
ZIGBEE_DEVICES_PATH = config.get('ZIGBEE', 'devices_path')
ZIGBEE_TMP_PATH = config.get('ZIGBEE', 'tmp_path')
SERVER_DOMOTICZ_PROTOCOL = config.get('DOMOTICZ', 'protocol')
SERVER_DOMOTICZ_IP = config.get('DOMOTICZ', 'ip')
SERVER_DOMOTICZ_PORT = config.get('DOMOTICZ', 'port')
SERVER_DOMOTICZ_GETTER = config.get('DOMOTICZ', 'getter')

# Commands
INIT = 'INIT'
INFO = 'INFO'
RESET = 'RESET'
JOIN = 'JOIN'
NETINFO = 'NETINFO'
DISCOVER = 'DISCOVER'
ENDPOINT = 'ENDPOINT'
IDENTIFY = 'IDENTIFY'
MOVEUP = 'MOVEUP'
MOVEDOWN = 'MOVEDOWN'
MOVETO = 'MOVETO'
STATUS = 'STATUS'
DIRECT = 'DIRECT'

# Params
ALL = 'ALL'
OK = 'OK'
LEVEL = 'LEVEL'

# Errors
errors = ConfigParser.ConfigParser()
errors.read('errors.cfg')

# Other
TIME_TO_SLEEP = 0.2

line = ""
eui_dongle = ""
device = list()
eventlet.monkey_patch()
ser = serial.Serial(USB_PATH, 19200, timeout=1)


def delai():
    time.sleep(TIME_TO_SLEEP)


def send_order(order):
    global line
    global eui_dongle
    ser.write(order)
    line = ""
    while OK not in line:
        delai()
        line = ser.readline()
        print_line(line)
        if "Telegesis" in line:
            delai()
            line = ser.readline()
            delai()
            line = ser.readline()
            eui_dongle = line
            eui_dongle = eui_dongle.replace("\r", "")
            eui_dongle = eui_dongle.replace("\n", "")
    line = ""
    print '------------------------------------------'


def print_line(output):
    output = output.replace("\r", "")
    output = output.replace("\n", "")
    output = output.strip()
    if output != '':
        if 'ERROR:' not in output:
            print output
        else:
            print_red(output + " - " + errors.get('ERRORS', output.split(':')[1]))


def print_red(prt):
    print("\033[91m{}\033[00m".format(prt))


def format_level(level):
    a = -0.0084
    b = 3.04
    c = 35
    level = level * level * a + level * b + c
    level = int(level)
    return format(level, '02X')


class ZigbeeServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        path = self.path
        tmp = urlparse.urlparse(path).query
        qs = urlparse.parse_qs(tmp)

        if INIT in qs:
            print("Processing command [" + INIT + "]")
            send_order("AT+PANSCAN\r")

        elif INFO in qs:
            print("Processing command [" + INFO + "]")
            send_order("ATI\r")

        elif RESET in qs:
            print("Processing command [" + RESET + "]")
            send_order("ATZ\r")

        elif JOIN in qs:
            print("Processing command [" + JOIN + "]")
            send_order("AT+JN\r")

        elif NETINFO in qs:
            print("Processing command [" + NETINFO + "]")
            send_order("AT+N\r")

        elif DISCOVER in qs:
            print("Processing command [" + DISCOVER + "]")
            device_file = open(ZIGBEE_DEVICES_PATH, 'w')
            nbr_device = qs.get('DISCOVER')[0]
            i = 1
            index = 0
            ident = "FF"
            index_ident = 0
            while len(list(set(device))) < int(nbr_device):
                while i == 1:
                    ser.write("AT+NTABLE:0" + str(index) + "," + ident + "\r")
                    time.sleep(1)
                    cont = 0
                    i = 0
                    sousindex = 0
                    dline = ""
                    while "ACK" not in dline:
                        dline = ser.readline()
                        time.sleep(1)
                        print dline
                        if cont == 1 and "|" in dline and "RFD" not in dline and eui_dongle not in dline:
                            id = dline.split(' | ')[3]
                            print id
                            device.append(id)
                            sousindex += 1

                        if "EUI" in dline:
                            cont = 1
                        if "2." in dline or "5." in dline or "8." in dline:
                            i = 1
                            print "detection 2 5 8"
                    index += 3
                print "Changement de device: " + str(index_ident)
                ident = device[index_ident]
                index_ident += 1
                i = 1
                index = 0
            for i in list(set(device)):
                print i
                device_file.write(i + "\n")
            device_file.close()

        elif ENDPOINT in qs:
            print("Processing command [" + ENDPOINT + "]")
            send_order("ATI\r")
            oldfile = open(ZIGBEE_DEVICES_PATH, 'r+')
            newfile = open(ZIGBEE_TMP_PATH, 'w')
            for dligne in oldfile:
                dligne = dligne.replace("\r", "")
                dligne = dligne.replace("\n", "")
                ser.write("AT+ACTEPDESC:" + dligne + "," + dligne + "\r")
                time.sleep(1)
                dligne = ""
                while "ACK" not in dligne:
                    dligne = ser.readline()
                    print dligne
                    time.sleep(1)
                    if "ActEpDesc" in dligne:
                        ep = dligne.split(',')[2]
                        ep = ep.replace("\r", "")
                        ep = ep.replace("\n", "")
                        newfile.write(dligne.replace(dligne, dligne + "|" + ep + "\n"))
                        dligne = ""
            oldfile.close()
            newfile.close()
            os.remove(ZIGBEE_DEVICES_PATH)
            shutil.move(ZIGBEE_TMP_PATH, ZIGBEE_DEVICES_PATH)

        elif IDENTIFY in qs:
            print("Processing command [" + IDENTIFY + "]")
            send_order("ATI\r")
            oldfile = open(ZIGBEE_DEVICES_PATH, 'r+')
            newfile = open(ZIGBEE_TMP_PATH, 'w')
            for ligne in oldfile:
                ligne = ligne.replace("\r", "")
                ligne = ligne.replace("\n", "")
                input_var = raw_input("delai() d'attente pour volet " + ligne.split('|')[0] + " en secondes? ")
                time.sleep(int(input_var))
                ser.write("AT+IDENTIFY:" + ligne.split('|')[0] + "," + ligne.split('|')[1] + ",0,000A\r")
                time.sleep(1)
                dline = ""
                while OK not in dline:
                    dline = ser.readline()
                    print dline
                    time.sleep(1)
                input_var = raw_input("Nom pour ce volet: ")
                newfile.write(ligne.replace(ligne, ligne + "|" + input_var + "\n"))
            oldfile.close()
            newfile.close()

        elif MOVEUP in qs:
            print("Processing command [" + MOVEUP + "]")
            if qs.get('MOVEUP')[0] != ALL:
                device_text = qs.get('MOVEUP')[0]
                with open(ZIGBEE_DEVICES_PATH) as devices:
                    for dline in devices:
                        dline = dline.rstrip()
                        if device_text == dline.split('|')[2]:
                            ser.write("AT+LCMV:" + dline.split('|')[0] + "," + dline.split('|')[1] + ",0,1,00,FF\r")
                            receive = ""
                            delai()
                            while "DFTREP" not in receive:
                                receive = ser.readline()
                                print receive
                                delai()
                            receive = receive.rstrip()
                            if receive.split(',')[4] != "00":
                                print "Transmit KO to " + dline.split('|')[2] + "\n"
                            else:
                                print "Transmit OK to " + dline.split('|')[2] + "\n"

            else:
                with open(ZIGBEE_DEVICES_PATH) as devices:
                    for dline in devices:
                        dline = dline.rstrip()
                        ser.write("AT+LCMV:" + dline.split('|')[0] + "," + dline.split('|')[1] + ",0,1,00,FF\r")
                        receive = ""
                        delai()
                        while "DFTREP" not in receive:
                            receive = ser.readline()
                            print receive
                            delai()
                        receive = receive.rstrip()
                        if receive.split(',')[4] != "00":
                            print "Transmit KO to " + dline.split('|')[2] + "\n"
                        else:
                            print "Transmit OK to " + dline.split('|')[2] + "\n"

        elif MOVEDOWN in qs:
            print("Processing command [" + MOVEDOWN + "]")
            if qs.get('MOVEDOWN')[0] != ALL:
                device_text = qs.get(MOVEDOWN)[0]
                with open(ZIGBEE_DEVICES_PATH) as devices:
                    for dline in devices:
                        dline = dline.rstrip()
                        if device_text == dline.split('|')[2]:
                            ser.write("AT+LCMV:" + dline.split('|')[0] + "," + dline.split('|')[1] + ",0,1,01,FF\r")
                            receive = ""
                            delai()
                            while "DFTREP" not in receive:
                                receive = ser.readline()
                                print receive
                                delai()
                            receive = receive.rstrip()
                            if receive.split(',')[4] != "00":
                                print "Transmit KO to " + dline.split('|')[2] + "\n"
                            else:
                                print "Transmit OK to " + dline.split('|')[2] + "\n"

            else:
                with open(ZIGBEE_DEVICES_PATH) as devices:
                    for dline in devices:
                        dline = dline.rstrip()
                        ser.write("AT+RONOFF:" + dline.split('|')[0] + "," + dline.split('|')[1] + ",0,0\r")
                        ser.write("AT+LCMV:" + dline.split('|')[0] + "," + dline.split('|')[1] + ",0,1,01,FF\r")
                        receive = ""
                        delai()
                        while "DFTREP" not in receive:
                            receive = ser.readline()
                            print receive
                            delai()
                        receive = receive.rstrip()
                        if receive.split(',')[4] != "00":
                            print "Transmit KO to " + dline.split('|')[2] + "\n"
                        else:
                            print "Transmit OK to " + dline.split('|')[2] + "\n"

        elif MOVETO in qs:
            print("Processing command [" + MOVETO + "]")
            if qs.get(MOVETO)[0] != ALL:
                level = format_level(int(qs.get(LEVEL)[0]))
                device_text = qs.get(MOVETO)[0]
                with open(ZIGBEE_DEVICES_PATH) as devices:
                    for dline in devices:
                        dline = dline.rstrip()
                        if device_text == dline.split('|')[2]:
                            ser.write("AT+LCMVTOLEV:" + dline.split('|')[0] + "," + dline.split('|')[
                                1] + ",0,0," + level + ",000F\r")
                            receive = ""
                            delai()
                            while "DFTREP" not in receive:
                                receive = ser.readline()
                                print receive
                                delai()
                            receive = receive.rstrip()
                            if receive.split(',')[4] != "00":
                                print "Transmit KO to " + dline.split('|')[2] + "\n"
                            else:
                                print "Transmit OK to " + dline.split('|')[2] + "\n"

            else:
                level = format_level(int(qs.get(LEVEL)[0]))

                with open(ZIGBEE_DEVICES_PATH) as devices:
                    for dline in devices:
                        dline = dline.rstrip()
                        ser.write("AT+LCMVTOLEV:" + dline.split('|')[0] + "," + dline.split('|')[
                            1] + ",0,0," + level + ",000F\r")
                        receive = ""
                        while "DFTREP" not in receive:
                            receive = ser.readline()
                            print receive
                            delai()
                        receive = receive.rstrip()
                        if receive.split(',')[4] != "00":
                            print "Transmit KO to " + dline.split('|')[2] + "\n"
                        else:
                            print "Transmit OK to " + dline.split('|')[2] + "\n"

        elif STATUS in qs:
            print("Processing command [" + STATUS + "]")
            a = 0.00081872
            b = 0.2171167
            c = -8.60201639
            if qs.get(STATUS)[0] == ALL:
                with open(ZIGBEE_DEVICES_PATH) as devices:
                    for dline in devices:
                        with eventlet.Timeout(10, False):
                            dline = dline.rstrip()
                            delai()
                            print dline
                            ser.write(
                                "AT+READATR:" + dline.split('|')[0] + "," + dline.split('|')[1] + ",0,0008,0000\r")
                            receive = ""
                            print "1 " + dline.split('|')[2]
                            while OK not in receive:
                                receive = ser.readline()
                                print receive
                                delai()

                            while ("RESPATTR" and dline.split('|')[0]) not in receive:
                                receive = ser.readline()
                                print receive
                                delai()
                            print "2 " + receive
                            receive = receive.rstrip()
                            level = int(receive.split(',')[5], 16)
                            print level
                            level = int(level * level * a + level * b + c)
                            if level < 0:
                                level = 0
                            print dline.split('|')[2] + " est au niveau " + str(level) + " \n"
                            level = int(level * 32 / 100)

                            url = SERVER_DOMOTICZ_PROTOCOL + "://" + SERVER_DOMOTICZ_IP + ":" + SERVER_DOMOTICZ_PORT + SERVER_DOMOTICZ_GETTER
                            idx = dline.split('|')[3]

                            if level == 0:
                                request = url + "&idx=" + idx + "&nvalue=1"
                            elif level > 31:
                                request = url + "&idx=" + idx + "&nvalue=0"
                            else:
                                request = url + "&idx=" + idx + "&nvalue=16&svalue=" + str(level)
                            print request
                            requests.get(request)
                            print "Suivant\n"
            else:
                print "Un seul Status\n"
                device_text = qs.get(STATUS)[0]
                with open(ZIGBEE_DEVICES_PATH) as devices:
                    for dline in devices:
                        dline = dline.rstrip()
                        if device_text == dline.split('|')[2]:
                            ser.write(
                                "AT+READATR:" + dline.split('|')[0] + "," + dline.split('|')[1] + ",0,0006,0000\r")
                            receive = ""
                            while "RESPATTR" not in receive:
                                receive = ser.readline()
                                print receive
                                delai()
                            receive = receive.rstrip()
                            if receive.split(',')[5] != "00":
                                print dline.split('|')[2] + " est ouvert. Niveau: "
                            else:
                                print dline.split('|')[2] + " est ferme. Niveau: "
                            ser.write(
                                "AT+READATR:" + dline.split('|')[0] + "," + dline.split('|')[1] + ",0,0008,0000\r")
                            receive = ""
                            delai()
                            while "RESPATTR" not in receive:
                                receive = ser.readline()
                                print receive
                                delai()
                            receive = receive.rstrip()
                            level = int(receive.split(',')[5], 16)
                            level = int(level * level * a + level * b + c)
                            print str(level) + " \n"
                            if level < 0:
                                level = 0
                            level = int(level * 32 / 100)
                            level = 32 - level

        elif DIRECT in qs:
            print("Processing command [DIRECT]")
            send_order("ATI\r")
            ser.write(qs.get(DIRECT)[0] + "\r")
            time.sleep(1)
            while 1:
                dline = ser.readline()
                print dline

        else:
            print("Unrecognized command")
            print '------------------------------------------'

        return


if __name__ == "__main__":
    try:
        server = HTTPServer((SERVER_ZIGBEE_IP, int(SERVER_ZIGBEE_PORT)), ZigbeeServer)
        print("Started Zigbee HTTP server - " + time.asctime())
        server.serve_forever()
    except KeyboardInterrupt:
        print('Shutting down Zigbee HTTP server')
        print("Shutting down Zigbee HTTP server - " + time.asctime())
        server.socket.close()
        ser.close()
        sys.exit()
