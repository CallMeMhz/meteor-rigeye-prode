#!/usr/bin/env python
import sys
import psutil
import platform
import requests
import time

API = 'http://' + sys.argv[1] + '/restful/instance'
TOKEN = ''

def message(text):
	print '[', time.ctime(), '] %s' % text

def load_stat():
    loadavg = {}
    f = open("/proc/loadavg")
    con = f.read().split()
    f.close()
    loadavg['lavg_1']=con[0]
    loadavg['lavg_5']=con[1]
    loadavg['lavg_15']=con[2]
    loadavg['nr']=con[3]
    loadavg['last_pid']=con[4]
    return loadavg

def get_bytes(t, iface='enp4s0'):
    with open('/sys/class/net/' + iface + '/statistics/' + t + '_bytes', 'r') as f:
        data = f.read();
    return int(data)

def monitor():
	global TOKEN
	global tx_prev, rx_prev

	while True:
		tx_speed, rx_speed = (0, 0)
		tx = get_bytes('tx')
		rx = get_bytes('rx')

		if tx_prev > 0:
			tx_speed = tx - tx_prev

		if rx_prev > 0:
			rx_speed = rx - rx_prev

		payload = {
			'token': TOKEN,
			'cpu_percent': psutil.cpu_percent(),
			'iowait': psutil.cpu_times_percent().iowait,
			'lavg1': load_stat()['lavg_1'],
			'lavg15': load_stat()['lavg_5'],
			'lavg15': load_stat()['lavg_15'],
			'net_speed_r': rx_speed,
			'net_speed_t': tx_speed,
			'updatedAt': time.time()
		}

		requests.put(API, data=payload)

		message('Sent JSON...')

		time.sleep(int(sys.argv[2]))

		tx_prev = tx
		rx_prev = rx

def init():
	global TOKEN
	try:
		token_file = open('.token', 'r')
		TOKEN = token_file.readline()
		message('Read token successfully')
	except:
		payload = {
			'node': platform.node(),
			'os': platform.system(),
		}
 		TOKEN = requests.post(API, payload).text
		token_file = open('.token', 'w')
		token_file.write(TOKEN)
		message('Register new token')
	token_file.close()

	message('TOKEN: ' + TOKEN)

if __name__ == '__main__':
	init()
	(tx_prev, rx_prev) = (0, 0)
	monitor()
