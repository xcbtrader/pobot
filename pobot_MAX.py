__author__ = 'xcbtrader'
# -*- coding: utf-8 -*-

from json import loads as _loads
from hmac import new as _new
from hashlib import sha512 as _sha512
from requests.exceptions import RequestException
from requests import post as _post
from requests import get as _get
import time
import sys
from datetime import datetime, timedelta
import calendar
from threading import Timer

# python 2
try:
    from urllib import urlencode as _urlencode
    str = unicode
# python 3
except:
    from urllib.parse import urlencode as _urlencode

class RepeatedTimer(object):
	def __init__(self, interval, function):
		self._timer     = None
		self.function   = function
		self.interval   = interval
		self.is_running = False
		self.start()

	def _run(self):
		self.is_running = False
		self.start()
		self.function()

	def start(self):
		if not self.is_running:
			self._timer = Timer(self.interval, self._run)
			self._timer.start()
			self.is_running = True

	def stop(self):
		self._timer.cancel()
		self.is_running = False


def private_order(command, args={}):
	global API_key, Secret

	err = True
	while err:
		try:	
			args['command'] = command
			args['nonce'] = nonce()
			postData = _urlencode(args)
	
			sign = _new(Secret.encode('utf-8'),postData.encode('utf-8'),_sha512)

			ret = _post('https://poloniex.com/tradingApi',data=args,headers={'Sign': sign.hexdigest(), 'Key': API_key})
	
			return  _loads(ret.text, parse_float=str)
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL EJECUTAR PRIVATE ORDER ' + command + ' ###')
			print('### ESPERANDO 10 SEGUNDOS ###')
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			time.sleep(10)	
	
def public_order(command, args={}):

	err = True
	while err:
		try:	
			args['command'] = command
			ret = _get('https://poloniex.com/public?' + _urlencode(args))
			return  _loads(ret.text, parse_float=str)
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL EJECUTAR PUBLIC ORDER ' + command + ' ###')
			print('### ESPERANDO 10 SEGUNDOS ###')
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			time.sleep(10)
			
def nonce():
	global _nonce
	_nonce += 42
	return _nonce

def leer_ticker_full():
	err = True
	while err:
		try:		
			ticker = public_order('returnTicker')
			return ticker
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER TICKER ###')
			print('### ESPERANDO 10 SEGUNDOS ###')
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			time.sleep(10)
			
def leer_balance(c):
	err = True
	while err:
		try:
			cc = c.split('_')
			balance = private_order('returnBalances')
			if len(cc) == 1:
				return float(balance[cc[0]])
			else:
				return float(balance[cc[1]])
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER BALANCE ' + c + ' ###')
			print('### ESPERANDO 10 SEGUNDOS ###')
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			time.sleep(10)
			
def leer_balance_full():
	err = True
	while err:
		try:
			balance = private_order('returnBalances')
			return balance
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER BALANCE ' + c + ' ###')
			print('### ESPERANDO 10 SEGUNDOS ###')
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			time.sleep(10)
			
def actualizar_ticker():
	global l_ticker, coins_trader, ticker_actualizado, funcionamiento
	
	try:
		l_ticker = leer_ticker_full()
		ticker_actualizado = True
		print('-----------------------------------------------------------------------------------------------------------------')
		print('>>> FECHA TICKER: ' + time.strftime("%d/%m/%y") + ' ' + time.strftime("%H:%M:%S"))
		p = 0
		for c in coins_trader:
			t = l_ticker[c.n_alt]
			c.high24hr = float(t['high24hr'])
			c.low24hr = float(t['low24hr'])
			c.percentChange = float(t['percentChange'])
			c.baseVolume = float(t['baseVolume'])
			c.lowestAsk = float(t['lowestAsk'])
			c.highestBid = float(t['highestBid'])
			c.last = float(t['last'])
			if funcionamiento == 6:
				if c.tipo_operacion == 'COMPRA':
					print(c.n_alt + ' - (Max 24H: ' + str(c.high24hr) + ' , Min 24H: ' + str(c.low24hr) + ' , ' + str(round(100 * c.percentChange,3)) + ' %) -- (Compra: ' + str(c.lowestAsk) + ' , Last: ' + str(c.last) + ' , Venta: ' + str(c.highestBid) + ' - PRECIO COMPRA: ' + str(c.last_compra) + ')')
				elif c.tipo_operacion == 'VENTA':
					print(c.n_alt + ' - (Max 24H: ' + str(c.high24hr) + ' , Min 24H: ' + str(c.low24hr) + ' , ' + str(round(100 * c.percentChange,3)) + ' %) -- (Compra: ' + str(c.lowestAsk) + ' , Last: ' + str(c.last) + ' , Venta: ' + str(c.highestBid) + ' - PRECIO VENTA: ' + str(c.last_venta) + ')')
				else:
					print(c.n_alt + ' - (Max 24H: ' + str(c.high24hr) + ' , Min 24H: ' + str(c.low24hr) + ' , ' + str(round(100 * c.percentChange,3)) + ' %) -- (Compra: ' + str(c.lowestAsk) + ' , Last: ' + str(c.last) + ' , Venta: ' + str(c.highestBid) +  ')')
			else:
				if c.tipo_operacion == 'COMPRA':
					print(c.n_alt  + ' - Ciclo: ' + str(c.ciclo) +  ' - (Max 24H: ' + str(c.high24hr) + ' , Min 24H: ' + str(c.low24hr) + ' , ' + str(round(100 * c.percentChange,3)) + ' %) -- (Compra: ' + str(c.lowestAsk) + ' , Last: ' + str(c.last) + ' , Venta: ' + str(c.highestBid) + ' - PRECIO COMPRA: ' + str(c.last_compra) + ')')
				elif c.tipo_operacion == 'VENTA':
					print(c.n_alt  + ' - Ciclo: ' + str(c.ciclo) +  ' - (Max 24H: ' + str(c.high24hr) + ' , Min 24H: ' + str(c.low24hr) + ' , ' + str(round(100 * c.percentChange,3)) + ' %) -- (Compra: ' + str(c.lowestAsk) + ' , Last: ' + str(c.last) + ' , Venta: ' + str(c.highestBid) + ' - PRECIO VENTA: ' + str(c.last_venta) + ')')
				else:
					print(c.n_alt  + ' - Ciclo: ' + str(c.ciclo) +  ' - (Max 24H: ' + str(c.high24hr) + ' , Min 24H: ' + str(c.low24hr) + ' , ' + str(round(100 * c.percentChange,3)) + ' %) -- (Compra: ' + str(c.lowestAsk) + ' , Last: ' + str(c.last) + ' , Venta: ' + str(c.highestBid) +  ')')
			
			p += 1
		print('-----------------------------------------------------------------------------------------------------------------')
			
	except KeyboardInterrupt:
		exit()	
	except Exception:
		print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
		ticker_actualizado = False
		print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
		print('### ESPERANDO 10 SEGUNDOS ###')
		time.sleep(10)
		print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
		
def actualizar_hist():
	global trade_hist, hist_actualizado
	
	err = True
	while err:
		try:
			final = datetime.utcnow()
			inicio = final - timedelta(days=30)
			unixtime1 = calendar.timegm(inicio.utctimetuple())
			unixtime2 = calendar.timegm(final.utctimetuple())
			trade_hist = private_order('returnTradeHistory', {'currencyPair': 'all', 'start': str(unixtime1)})
			hist_actualizado = True
			err = False
			print('-----------------------------------------------------------------------------------------------------------------')
			print('>>> ' + time.strftime("%d/%m/%y") + ' ' + time.strftime("%H:%M:%S") + ' HISTORIAL DE ORDENES FINALIZADAS, ACTUALIZADO CORRECTAMENTE ')
			print('-----------------------------------------------------------------------------------------------------------------')
		except KeyboardInterrupt:
			exit()	
		except Exception:
			hist_actualizado = False
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER HISTORIAL DE ORDENES ###')
			print('### ESPERANDO 10 SEGUNDOS ###')
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			time.sleep(10)

def buscar_historial(c, n_order):
	global trade_hist, hist_actualizado

	if hist_actualizado:
		if c in trade_hist:
			t1 = trade_hist[c]
	
			for t in t1:
				if t['orderNumber'] == n_order:
					return True
	else:
		print('### ESPERANDO A QUE SE ACTUALICE EL HISTORIAL ###')
		
	return False
	
def realizar_compra(c, lowestAsk, saldo_inv):
	
	precio_compra = lowestAsk
	
	try:
		make_order_buy = private_order('buy', {'currencyPair':c, 'rate': str(precio_compra), 'amount': str(saldo_inv/precio_compra), 'postOnly': 1})
		print('**********************************************************************************************************************************')
		print('*** ' + c + ' CREADA ORDEN DE COMPRA NUM ' + make_order_buy['orderNumber'] + ' - PRECIO: ' + str(precio_compra) + ' - INVERSION: ' + str(saldo_inv) + ' ***')
		print('**********************************************************************************************************************************')
		guardar_historial(c + ';CREADA ORDEN DE COMPRA NUM ' + make_order_buy['orderNumber'] + ';PRECIO: ' + str(precio_compra) + ';INVERSION: ' + str(saldo_inv))
		return make_order_buy['orderNumber'], precio_compra
	except KeyboardInterrupt:
		exit()	
	except Exception:
		if make_order_buy['error'] == 'Unable to place post-only order at this price.':
			print('**********************************************************************************************************************************')
			print('### INTENTANDO PONER ORDEN DE COMPRA PARA ' + c + ' ###')
			print('**********************************************************************************************************************************')
			guardar_historial('INTENTANDO PONER ORDEN DE COMPRA PARA ' + c)
		else:
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL CREAR ORDEN DE COMPRA ' + c + ' ###')
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			guardar_historial('ERROR AL CREAR ORDEN DE COMPRA ' + c + ';' + sys.exc_info()[1])
		return '-1', 0.0

def realizar_venta(c, precio_venta, saldo_inv):

	try:	
		make_order_sell = private_order('sell', {'currencyPair':c, 'rate': str(precio_venta), 'amount': str(saldo_inv), 'postOnly': 1})
		print('**********************************************************************************************************************************')
		print('*** ' + c + ' CREADA ORDEN DE VENTA NUM ' + make_order_sell['orderNumber'] + ' - PRECIO: ' + str(precio_venta) + ' - IVERSION: ' + str(saldo_inv) + ' ***')
		print('**********************************************************************************************************************************')
		guardar_historial(c + ';CREADA ORDEN DE VENTA NUM ' + make_order_sell['orderNumber'] + ';PRECIO: ' + str(precio_venta) + ';IVERSION: ' + str(saldo_inv))
		return make_order_sell['orderNumber']
	except KeyboardInterrupt:
		exit()	
	except Exception:
		if make_order_sell['error'] == 'Unable to place post-only order at this price.':
			print('**********************************************************************************************************************************')
			print('### INTENTANDO PONER ORDEN DE VENTA PARA ' + c + ' ###')
			print('**********************************************************************************************************************************')
			guardar_historial('INTENTANDO PONER ORDEN DE VENTA PARA ' + c)
		else:
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL CREAR ORDEN DE VENTA ' + c + ' ###')
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			guardar_historial('ERROR AL CREAR ORDEN DE VENTA ' + c + ';' + sys.exc_info()[1])
		return '-1'	

def mover_orden(num_orden_cerrar, lowestAsk, tipo):	
	try:	
		mov_orden = private_order('moveOrder', {'orderNumber': str(num_orden_cerrar), 'rate': str(lowestAsk), 'postOnly': 1})
		print('**********************************************************************************************************************************')
		print('### MOVIDA ORDEN DE ' + tipo + ': ' + str(num_orden_cerrar) +  ' AL NUEVO PRECIO: ' + str(lowestAsk) + ' CORRECTAMENTE')
		print('**********************************************************************************************************************************')
		guardar_historial('MOVIDA ORDEN DE ' + tipo + ';NUM ORDER: ' + str(num_orden_cerrar) +  ';AL NUEVO PRECIO: ' + str(lowestAsk))
		return str(mov_orden['orderNumber'])
	except KeyboardInterrupt:
		exit()	
	except Exception:
		if mov_orden['error'] == 'Unable to place post-only order at this price.':
			print('**********************************************************************************************************************************')
			print('### INTENTANDO PONER ORDEN DE ' + tipo + ' A NUEVO PRECIO ###')
			print('**********************************************************************************************************************************')
			guardar_historial('INTENTANDO PONER ORDEN DE ' + tipo)
		else:
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL MOVER ORDEN DE ' + tipo + ' ###')
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			guardar_historial('ERROR AL MOVER ORDEN DE ' + tipo + ';' + sys.exc_info()[1])
		return '-1'	

def esperando_ticker():
	global ticker_actualizado
	
	prime = True
	while not ticker_actualizado:
		if prime:
			print('### ESPERANDO A TENER VALOR ACTUAL DEL TICKER ###')
			prime = False
		time.sleep(10)

def ordenes_abiertas(c, num_last_orden):
	err = True
	while err:
		try:
			open_orders = private_order('returnOpenOrders', {'currencyPair':c,})
			err = False
			if len(open_orders) == 0:
				return False
			else:
				for op in open_orders:
					if op['orderNumber'] == num_last_orden:
						return True
				return False
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER LAS ORDENES ABIERTAS ###')
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
			
def menu_funcionamiento():
	funcionamiento = 0
	while funcionamiento < 1 or funcionamiento > 6:	
		print('')
		print('Escoge el modo como operara Pobot_MAX')
		print('    1-> Segun Margen de Incremento 24h (Con todas las Alts)')
		print('    2-> Segun Margen de Incremento 24h (Escogiendo Manualmente las Alts)')
		print('    3-> Version Antigua - Pone ordenes instantaneas (Con todas las Alts)')
		print('    4-> Version Antigua - Pone ordenes instantaneas (Escogiendo Manualmente las Alts)')
		print('    5-> Vamos a por el PUMP (Una sola Alt entrada Manualmente)')
		print('    6-> Automatico. Escoge las mejores Alts para tradear en cada momento')
		print('')
		funcionamiento = int(input('Opcion: ? '))
	return funcionamiento
	
def menu_alt():
	alt = 0
	while alt < 1 or alt > 4:
		balance = leer_balance_full()
		print('')
		print('Escoge la divisa con la que operara Pobot_MAX')
		print('    1-> USDT (' + balance['USDT'] + ' usdt)')
		print('    2-> BTC (' + balance['BTC'] + ' btc)')
		print('    3-> ETH (' + balance['ETH'] + ' eth)')
		print('    4-> XMR (' + balance['XMR'] + ' xmr)')
		print('')
		alt = int(input('Opcion: ? '))
	return alt
	
class info_alt_ok:
	def __init__(self):
		self.n_alt = ''
		self.percentChange = 0.0
		self.high24hr = 0.0
		self.low24hr = 0.0
		self.last = 0.0
		
def escoger_alts(num_max_alts_trader, working_alts, altstr, margen_incremento_24h, margen_incrememto_act):
	alts_ok = []
	alts_ok_def = []
	ticker = leer_ticker_full()

	for cn in working_alts:
		t = ticker[altstr + '_' + cn]
		if float(t['percentChange']) >= margen_incremento_24h and float(t['lowestAsk']) <= float(t['low24hr']) + (float(t['high24hr']) - float(t['low24hr'])) * margen_incrememto_act:
			in_alt_ok = info_alt_ok()
			in_alt_ok.n_alt = cn
			in_alt_ok.percentChange = float(t['percentChange'])
			in_alt_ok.high24hr = float(t['high24hr'])
			in_alt_ok.low24hr = float(t['low24hr'])
			in_alt_ok.last = float(t['last'])				
			alts_ok.append(in_alt_ok)
	
	if len(alts_ok) == 0:
		print('-----------------------------------------------------------------------------------------------------------------')
		print('### NINGUNA NUEVA ALT CUMPLE CON LOS CRITERIOS DE TRADER ###')
		print('-----------------------------------------------------------------------------------------------------------------')
	else:
		print('-----------------------------------------------------------------------------------------------------------------')
		alts_ok = sorted(alts_ok, key=lambda objeto: objeto.percentChange, reverse = True)
		n_tr = 1
		for cn in alts_ok:
			if n_tr <= num_max_alts_trader:
				print(altstr + '_' + cn.n_alt + ' -- Max 24H: ' + str(cn.high24hr) + ' - Min 24H: ' + str(cn.low24hr) + ' - Inc: ' + str(round(cn.percentChange * 100, 3)) + ' % - Last: ' + str(cn.last))
				alts_ok_def.append(cn.n_alt)
				n_tr +=1
		print('-----------------------------------------------------------------------------------------------------------------')
				
	return alts_ok_def
	
def coincidencia(coins_trader, c):
	encontrado = False
	for co in coins_trader:
		if c == co.n_alt:
			encontrado = True
			
	return encontrado
	
def encontrada_opcion(mat, busqueda):
	n = 0
	for m in mat:
		if m == busqueda:
			return n
		else:
			n += 1
	return -1
	
def imprimir_help():
	print('')
	print('###############################################################')
	print('#                                                             #')
	print('# OPCIONES DE LA LINEA DE COMANDOS PARA pobot_MAX.py          #')
	print('#                                                             #')
	print('# -h Help -- Ver las opciones                                 #')
	print('# -f Fichero de configuracion  (Ej. best_alts.cfg)            #')
	print('# -a Alt escogida para tradear (Valores de 1 a 4)             #')
	print('# -s Saldo Alt escogida a invertir en el total de las Alts    #')
	print('# -o Opcion escogida  (Valores de 1 a 6)                      #')
	print('# -m Margen de Incremento de la Alt 24h                       #')
	print('# -n Margen de Incremento Actual de la Alt                    #')
	print('# -b Margen de Beneficio para todas las ALts                  #')
	print('# -l Stop Loss (Solo en la opcion 6)                          #')
	print('# -t Numero Maximo de Alts para Tradear (Solo Opcion 6)       #')
	print('# -p Alt a Pumpear (Solo Opcion 5) (Ej. LTC)                  #')
	print('# -e Valor Entrada del Pump (Solo Opcion 5)                   #') 
	print('# -c Numero de Ciclos del Bot                                 #')          
	print('#                                                             #')
	print('###############################################################')
	print('')
	exit()

def guardar_historial(txt):
	global file_log
	
	f = open(file_log, 'a')
	f.write(time.strftime("%d/%m/%y") + ' ' + time.strftime("%H:%M:%S") + ';' + txt + '\n')
	f.close()
	
class info_alt:
	def __init__(self):
		self.posicion = 0
		self.n_alt = ''
		self.high24hr = 0.0
		self.low24hr = 0.0
		self.last = 0.0
		self.lowestAsk = 0.0
		self.highestBid = 0.0
		self.percentChange = 0.0
		self.baseVolume = 0.0
		self.last_compra = 0.0
		self.inv_last_compra = 0.0
		self.last_venta = 0.0
		self.inv_last_venta = 0.0
		self.tipo_operacion = 'SIN ORDEN'  # Valores: 'Sin Orden', 'Compra', 'Venta'
		self.margen = 0.0
		self.ciclo = 1
		self.num_last_orden = ''
		self.beneficio_total = 0.0

# PROGRAMA PRINCIPAL ##########################################################

global EMA1, EMA2, _nonce, altstr, coins, API_key, Secret, inicio_bot, l_ticker, coins_trader, ticker_actualizado, hist_actualizado, trade_hist, n_ticker, n_hist, file_log

pos = encontrada_opcion(sys.argv, '-h')
file_log = time.strftime("%y%m%d") + '_' + time.strftime("%H%M%S") + '.log'
if  pos > 0:
	imprimir_help()

print('')
print('     **************************************************************************************')
print('     **************************************************************************************')
print('     **                                                                                  **')
print('    ***  ######   ######   ####    ######   ######           #     #   ######  #     #   ***')     
print('    ***  #    #   #    #   #   #   #    #     ##             # # # #   #    #    # #     ***')
print('    ***  ######   #    #   ####    #    #     ##             #  #  #   ######     #      ***')
print('    ***  #        #    #   #   #   #    #     ##             #     #   #    #    #  #    ***')
print('    ***  #        ######   #####   ######     ##   ######    #     #   #    #  #      #  ***')
print('     **                                                                                  **')
print('     **************************************************************************************')
print('     **************************************************************************************')
print('')
print('')
print('')

_nonce = int("{:.6f}".format(time.time()).replace('.', ''))

pos = encontrada_opcion(sys.argv, '-f')
if  pos > 0:
	fichero = sys.argv[pos+1]
	print('### CARGANDO FICHERO ' + fichero + ' CON LA CONFIGURACION PERSONALIZADA ###')
else:
	fichero = 'pobot_MAX.cfg'
	print('### CARGANDO FICHERO ' + fichero + ' CON LA CONFIGURACION ESTANDAR ###')

guardar_historial(fichero)

try:
	configuracion = open(fichero, 'r')
	config = configuracion.readlines()
	t = config[0].split(';')
	API_key = t[1].strip()
	t = config[1].split(';')
	Secret = t[1].strip()
	a_c = config[2].strip()
	b_c = config[3].strip()
	c_c = config[4].strip()
	d_c = config[5].strip()
	a_coins = a_c.split(';')
	b_coins = b_c.split(';')
	c_coins = c_c.split(';')
	d_coins = d_c.split(';')
	
except KeyboardInterrupt:
	exit()	
except Exception:
	print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
	print('### ERROR AL ABRIR FICHERO DE CONFIGURACION : ' + fichero)
	print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
	time.sleep(10)
	exit()

saldo_inv = 0.0
margen_incrememto_act = 0.0

pos = encontrada_opcion(sys.argv, '-a')
if pos > 0:
	alt = int(sys.argv[pos+1])
else:
	alt = menu_alt()
	
working_alts = []

print('')

if alt == 1:
	altstr = 'USDT'
	working_alts = a_coins
	
	pos = encontrada_opcion(sys.argv, '-s')
	if pos > 0:
		saldo_inv = float(sys.argv[pos+1])
	else:
		saldoUSDT = leer_balance(altstr)
		while saldo_inv <= 0.0 or saldo_inv > saldoUSDT:
			print('Entra saldo Maximo USDT a invertir. Maximo Disponible: ' + str(saldoUSDT) + ' ' + altstr)
			saldo_inv = float(input('Inversion:? '))
elif alt == 2:
	altstr = 'BTC'
	working_alts = b_coins
	
	pos = encontrada_opcion(sys.argv, '-s')
	if pos > 0:
		saldo_inv = float(sys.argv[pos+1])
	else:
		saldoUSDT = leer_balance(altstr)
		while saldo_inv <= 0.0 or saldo_inv > saldoUSDT:
			print('Entra saldo Maximo BTC a invertir: ' + str(saldoUSDT) + ' ' + altstr)
			saldo_inv = float(input('Inversion:? '))
elif alt == 3:
	altstr = 'ETH'
	working_alts = c_coins
	
	pos = encontrada_opcion(sys.argv, '-s')
	if pos > 0:
		saldo_inv = float(sys.argv[pos+1])
	else:
		saldoUSDT = leer_balance(altstr)
		while saldo_inv <= 0.0 or saldo_inv > saldoUSDT:
			print('Entra saldo Maximo ETH a invertir: ' + str(saldoUSDT) + ' ' + altstr)
			saldo_inv = float(input('Inversion:? '))
else:
	altstr = 'XMR'
	working_alts = d_coins
	
	pos = encontrada_opcion(sys.argv, '-s')
	if pos > 0:
		saldo_inv = float(sys.argv[pos+1])
	else:
		saldoUSDT = leer_balance(altstr)
		while saldo_inv <= 0.0 or saldo_inv > saldoUSDT:
			print('Entra saldo Maximo XMR a invertir: ' + str(saldoUSDT) + ' ' + altstr)
			saldo_inv = float(input('Inversion:? '))
			
guardar_historial('Alt escogida: ' + altstr)
guardar_historial('Saldo Invertido: ' + str(saldo_inv))

pos = encontrada_opcion(sys.argv, '-o')
if pos > 0:
	funcionamiento = int(sys.argv[pos+1])
else:	
	funcionamiento = menu_funcionamiento()

guardar_historial('Opcion Escogida: ' + str(funcionamiento))
ticker = leer_ticker_full()

if funcionamiento != 5:
	print('')
	print('-----------------------------------------------------------------------------------------------------------------')

	for c in working_alts:
		t = ticker[altstr + '_' + c]
		print(altstr + '_' + c + ' -- Max 24H: ' + t['high24hr'] + ' - Min 24H: ' + t['low24hr'] + ' - Inc: ' + str(round(float(t['percentChange']) * 100, 3)) + ' % - Last: ' + t['last'])
	print('-----------------------------------------------------------------------------------------------------------------')		

print('')

coins = []
a_margen = []

if funcionamiento == 1:
	pos = encontrada_opcion(sys.argv, '-m')
	if pos > 0:
		margen_incremento_24h = float(sys.argv[pos+1])
	else:	
		print('')
		margen_incremento_24h = float(input('Entra el margen de incremento de las ultimas 24h para entrar a invertir:? '))
		
	margen_incremento_24h = margen_incremento_24h/100
	
	pos = encontrada_opcion(sys.argv, '-n')
	if pos > 0:
		margen_incrememto_act = float(sys.argv[pos+1])
	else:	
		print('')
		margen_incrememto_act = float(input('Entra el margen de incremento actual de la Alt para entrar a invertir (0% -> 100%):? '))
		
	margen_incrememto_act = margen_incrememto_act/100

	pos = encontrada_opcion(sys.argv, '-b')
	if pos > 0:
		margen = float(sys.argv[pos+1])
	else:		
		print('')
		margen = 0.0
		while margen <= 0.5:
			margen2 = str(input('Entra el margen de beneficio para todas las Alts: ? ')) 
			margen = float(margen2.replace(',','.'))
		
	for cn in working_alts:
		coins.append(cn)
		a_margen.append(margen/100)
		
	guardar_historial('Margen Incremento 24h: ' + str(margen_incremento_24h) + ';Margen de Incremento Actual: ' + str(margen_incrememto_act) + ';Margen de Beneficio: ' + str(margen))
elif funcionamiento == 2:
	pos = encontrada_opcion(sys.argv, '-m')
	if pos > 0:
		margen_incremento_24h = float(sys.argv[pos+1])
	else:	
		print('')
		margen_incremento_24h = float(input('Entra el margen de incremento de las ultimas 24h para entrar a invertir:? '))

	margen_incremento_24h = margen_incremento_24h/100
	
	pos = encontrada_opcion(sys.argv, '-n')
	if pos > 0:
		margen_incrememto_act = float(sys.argv[pos+1])
	else:	
		print('')
		margen_incrememto_act = float(input('Entra el margen de incremento actual de la Alt para entrar a invertir (0% -> 100%):? '))
		
	margen_incrememto_act = margen_incrememto_act/100
	
	print('')
	print('Entra los margenes para cada Alt. Si ponemos 0 esa Alt no se utiliza en el bot')
	print('')
	
	t = ''
	for cn in working_alts:
		print('Margen para ' + cn + ' >=0.5 o 0 para No Altcoin : ? ')
		m1 = str(input())
		m = float(m1.replace(',','.'))
		if m >= 0.5:
			coins.append(cn)
			a_margen.append(m/100)
			t = t + ';Margen para ' + cn + ': ' + str(m)
			
	guardar_historial('Margen Incremento 24h: ' + str(margen_incremento_24h) + ';Margen de Incremento Actual: ' + str(margen_incrememto_act) + t)
elif funcionamiento == 3:
	margen_incremento_24h = 0.0
	
	pos = encontrada_opcion(sys.argv, '-b')
	if pos > 0:
		margen = float(sys.argv[pos+1])
	else:		
		print('')
		margen = 0.0
		while margen <= 0.5:
			margen2 = str(input('Entra el margen de beneficio para todas las Alts: ? ')) 
			margen = float(margen2.replace(',','.'))
		
	for cn in working_alts:
		coins.append(cn)
		a_margen.append(margen/100)
elif funcionamiento == 4:
	margen_incremento_24h = 0.0
	print('')
	print('Entra los margenes para cada Alt. Si ponemos 0 esa Alt no se utiliza en el bot')
	print('')
	
	for cn in working_alts:
		print('Margen para ' + cn + ' >=0.5 o 0 para No Altcoin : ? ')
		m1 = str(input())
		m = float(m1.replace(',','.'))
		if m >= 0.5:
			coins.append(cn)
			a_margen.append(m/100)	
elif funcionamiento == 5:
	margen_incremento_24h = 0.0
	valor_entrada = 0.0
	
	pos = encontrada_opcion(sys.argv, '-p')
	if pos > 0:
		al = str(sys.argv[pos+1])
	else:	
		print('')
		al = input ('Entra la Alt para hacer PUMP: ')
	al = al.upper()
	alt = al.split('_')
	if len(alt) == 1:
		coins.append(alt[0])
	else:
		coins.append(alt[1])
	
	pos = encontrada_opcion(sys.argv, '-b')
	if pos > 0:
		margen = float(sys.argv[pos+1])
	else:		
		print('')
		margen = 0.0
		while margen <= 0.5:
			margen2 = str(input('Entra el margen de beneficio para la Alt: ? ')) 
			margen = float(margen2.replace(',','.'))
			
	a_margen.append(margen/100)
	
	pos = encontrada_opcion(sys.argv, '-e')
	if pos > 0:
		valor_entrada = float(sys.argv[pos+1])
	else:
		valor_entrada = float(input('Entra el valor de Entrada para el PUMP (0 No se utiliza): ? '))
		
	guardar_historial('Alt para PUMP: ' + al + ';Margen de Beneficio: ' + str(margen) + ';Valor entrada PUMP: ' + str(valor_entrada))
		
elif funcionamiento == 6:
	pos = encontrada_opcion(sys.argv, '-m')
	if pos > 0:
		margen_incremento_24h = float(sys.argv[pos+1])
	else:	
		print('')
		margen_incremento_24h = float(input('Entra el margen de incremento de las ultimas 24h para entrar a invertir:? '))
		
	margen_incremento_24h = margen_incremento_24h/100
	
	pos = encontrada_opcion(sys.argv, '-n')
	if pos > 0:
		margen_incrememto_act = float(sys.argv[pos+1])
	else:	
		print('')
		margen_incrememto_act = float(input('Entra el margen de incremento actual de la Alt para entrar a invertir (0% -> 100%):? '))
	
	margen_incrememto_act = margen_incrememto_act/100

	pos = encontrada_opcion(sys.argv, '-l')
	if pos > 0:
		stop_loss = float(sys.argv[pos+1])
	else:	
		print('')
		stop_loss = float(input('Entra el margen de perdidas aceptado (0 no se utiliza):? '))
		
	stop_loss = stop_loss/100

	pos = encontrada_opcion(sys.argv, '-t')
	if pos > 0:
		num_max_alts_trader = int(sys.argv[pos+1])
	else:		
		print('')
		num_max_alts_trader = 0
		while num_max_alts_trader < 1 or num_max_alts_trader > len(working_alts):
			num_max_alts_trader = int(input('Entra el Num. Max de Alts a tradear: ? '))

	saldo_inv = saldo_inv / num_max_alts_trader
	
	pos = encontrada_opcion(sys.argv, '-b')
	if pos > 0:
		margen = float(sys.argv[pos+1])
	else:		
		print('')
		margen = 0.0
		while margen <= 0.5:
			margen2 = str(input('Entra el margen de beneficio para todas las Alts: ? ')) 
			margen = float(margen2.replace(',','.'))
			
	guardar_historial('Margen Incremento 24h: ' + str(margen_incremento_24h) + ';Margen de Incremento Actual: ' + str(margen_incrememto_act) + ';Maren de Perdidas: ' + str(stop_loss) + ';Num Max Alts Tradear; ' + str(num_max_alts_trader) + ';Margen de Beneficio: ' + str(margen))

	margen = margen/100

pos = encontrada_opcion(sys.argv, '-c')
if pos > 0:
	ciclos = int(sys.argv[pos+1])
else:	
	print('')
	ciclos = 0
	while ciclos < 1:
		if funcionamiento == 6:
			ciclos = int(input('Numero de ciclos total entre todas las Alts para la Inversion:? '))
		else:
			ciclos = int(input('Numero de ciclos de la Inversion:? '))

guardar_historial('Total de Ciclos: ' + str(ciclos))		
coins_trader = []

if funcionamiento < 6:
	p = 0
	for c in coins:
		fit_coin = info_alt()
		fit_coin.posicion = p
		fit_coin.n_alt = altstr + '_' + c
		fit_coin.margen = a_margen[p]
		coins_trader.append(fit_coin)

	p += 1
	saldo_inv = saldo_inv / len(coins_trader)
	
print('')
print('### INICIANDO POBOT_MAX ###')
print('')

ticker_actualizado = False
hist_actualizado = False

act_tick = RepeatedTimer(30, actualizar_ticker)
time.sleep(2)
act_hist = RepeatedTimer(30, actualizar_hist)

print('### ESPERANDO 60 seg PARA PRIMERA RECOGIDA DE DATOS DE POLONIEX ###')
time.sleep(60)
pausa = 10

if funcionamiento == 6:
	ciclos_global = 1

	total_beneficio = 0.0
	n_ciclos_bene = 0
	n_ciclos_perd = 0
	alts_beneficio = []
	alts_perdidas = []
	primera = True
	while ciclos_global <= ciclos:

		if len(coins_trader) < num_max_alts_trader and (len(coins_trader) + ciclos_global) <= ciclos:
			coins = escoger_alts(num_max_alts_trader, working_alts, altstr, margen_incremento_24h, margen_incrememto_act)

			p = len(coins_trader)
			for c in coins:
				if p <= num_max_alts_trader and not coincidencia(coins_trader,altstr + '_' + c):
					fit_coin = info_alt()
					fit_coin.posicion = p
					fit_coin.n_alt = altstr + '_' + c
					fit_coin.margen = margen
					coins_trader.append(fit_coin)
					print('-----------------------------------------------------------------------------------------------------------------')
					print('### (' + str(len(coins_trader)) + ') INCORPORADA LA SIGUIENTE ALT: ' + altstr + '_' + c + ' PARA TRADER ###')
					print('-----------------------------------------------------------------------------------------------------------------')
					p += 1
		if primera:
			ticker_actualizado = False
			esperando_ticker()
			primera = False
	
		alts_borrar = []
		alts_no_cumplen = []
		print('')
		print('-----------------------------------------------------------------------------------------------------------------')
		print('>>> CICLOS: ' + str(ciclos_global) + '/' + str(ciclos) + ' -- Tot. Ciclos Benef: ' + str(n_ciclos_bene) + ' - Tot. Ciclos Perd: ' + str(n_ciclos_perd) + ' -- Beneficio: ' + str(total_beneficio))
		for c in coins_trader:
			if c.tipo_operacion == 'SIN ORDEN':
				if c.lowestAsk == 0.0:
					ticker_actualizado = False
					esperando_ticker()
				if c.percentChange >= margen_incremento_24h and  c.lowestAsk <= c.low24hr + ((c.high24hr - c.low24hr) * margen_incrememto_act):
					num_last_orden2, last_compra2 = realizar_compra(c.n_alt, c.lowestAsk, saldo_inv)
					if num_last_orden2 != '-1':
						c.num_last_orden = num_last_orden2
						c.last_compra = last_compra2
						c.tipo_operacion = 'COMPRA'
						c.inv_last_compra = saldo_inv
						time.sleep(pausa)			
				else:
					alts_no_cumplen.append(c)
				
			elif c.tipo_operacion == 'COMPRA':
				if buscar_historial(c.n_alt, c.num_last_orden) and not ordenes_abiertas(c.n_alt, c.num_last_orden):
					print('-----------------------------------------------------------------------------------------------------------------')
					print('### ORDEN DE COMPRA NUM: ' + c.num_last_orden + ' PARA ' + c.n_alt + ' FINALIZADA CORRECTAMENTE ###')
					print('-----------------------------------------------------------------------------------------------------------------')
					esperando_ticker()
					precio_venta = c.last_compra + (c.last_compra * c.margen)
					if precio_venta < c.highestBid:
						precio_venta = c.highestBid
					saldo_inv_alt = leer_balance(c.n_alt)
					if saldo_inv_alt > 0:
						num_last_orden2 = realizar_venta(c.n_alt, precio_venta, saldo_inv_alt)
						if num_last_orden2 != '-1':
							c.num_last_orden = num_last_orden2
							c.last_venta = precio_venta
							c.tipo_operacion = 'VENTA'
							c.inv_last_venta = saldo_inv_alt
							time.sleep(pausa)						
					else:
						print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
						print('### ERROR. SALDO INSUFICIENTE EN ' + c.n_alt + ' PARA REALIZAR LA VENTA ###')
						print('### ESPERANDO NUEVO SALDO ###')
						print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
				else:
					if c.lowestAsk > (c.last_compra + (c.last_compra * 0.01)):
						mv_num_orden = mover_orden(c.num_last_orden, c.lowestAsk, c.tipo_operacion)
						if mv_num_orden != '-1':
							c.last_compra = c.lowestAsk
							c.num_last_orden = mv_num_orden
							time.sleep(pausa)
					else:
						print('-----------------------------------------------------------------------------------------------------------------')
						print('### ESPERANDO QUE SE CIERRE LA ORDEN ' + c.num_last_orden + ' DE ' + c.tipo_operacion + ' PARA ' + c.n_alt + ' ###')
						print('-----------------------------------------------------------------------------------------------------------------')
			else:
				if buscar_historial(c.n_alt, c.num_last_orden) and not ordenes_abiertas(c.n_alt, c.num_last_orden):
					print('-----------------------------------------------------------------------------------------------------------------')
					print('### ORDEN DE VENTA NUM: ' + c.num_last_orden + ' PARA ' + c.n_alt + ' FINALIZADA CORRECTAMENTE ###')
					print('-----------------------------------------------------------------------------------------------------------------')
					
					if c.last_venta - c.last_compra > 0:
						n_ciclos_bene +=1
						alts_beneficio.append(c.n_alt)
					else:
						n_ciclos_perd +=1
						alts_perdidas.append(c.n_alt)
						
					total_beneficio += (c.last_venta * c.inv_last_venta) - c.inv_last_compra
	
					alts_borrar.append(c)
					ciclos_global +=1
				else:
					if stop_loss > 0.0:
						if c.highestBid <= c.last_compra - (c.last_compra * stop_loss):
							mv_num_orden = mover_orden(c.num_last_orden, c.highestBid, c.tipo_operacion)
							if mv_num_orden != '-1':
								c.last_venta = c.highestBid
								c.num_last_orden = mv_num_orden
								time.sleep(pausa)
						else:
							print('-----------------------------------------------------------------------------------------------------------------')
							print('### ESPERANDO QUE SE CIERRE LA ORDEN ' + c.num_last_orden + ' DE ' + c.tipo_operacion + ' PARA ' + c.n_alt + ' ###')
							print('-----------------------------------------------------------------------------------------------------------------')
					else:
						print('-----------------------------------------------------------------------------------------------------------------')
						print('### ESPERANDO QUE SE CIERRE LA ORDEN ' + c.num_last_orden + ' DE ' + c.tipo_operacion + ' PARA ' + c.n_alt + ' ###')
						print('-----------------------------------------------------------------------------------------------------------------')
	
		if len(alts_borrar) > 0:
			print('-----------------------------------------------------------------------------------------------------------------')
			for al in alts_borrar:
				print('### QUITANDO '+ al.n_alt + ' - PROCESO DE TRADER COMPLETADO CON EXITO ###')
				coins_trader.remove(al)
			print('-----------------------------------------------------------------------------------------------------------------')

		if len(alts_no_cumplen) > 0:
			print('-----------------------------------------------------------------------------------------------------------------')
			for al in alts_no_cumplen:
				print('### QUITANDO '+ al.n_alt + ' POR NO CUMPLIR CON LOS PARAMETROS DE TRADER ###')
				coins_trader.remove(al)
			print('-----------------------------------------------------------------------------------------------------------------')
	
		time.sleep(pausa)

				
	act_tick.stop()
	act_hist.stop()

	print('')
	print('###############################################################')
	print('#########  POBOT_MAX  FINALIZADO   CORRECTAMENTE    ###########')
	print('###############################################################')
	print('')
	print('')
	print(' TOTAL BENEFICIO: ' + str(total_beneficio))
	print('')
	if len(alts_beneficio) > 0:
		print('### ALTS CON BENEFICIO --------------------------------------')
		copia_alts_beneficio = []
		for a in alts_beneficio:
			if a not in copia_alts_beneficio:
				print('(' + str(alts_beneficio.count(a)) + ') ' + a)
				copia_alts_beneficio.append(a)
	print('')
	if len(alts_perdidas) > 0:
		print('### ALTS CON PERDIDAS --------------------------------------')
		copia_alts_perdidas = []
		for a in alts_perdidas:
			if a not in copia_alts_perdidas:
				print('(' + str(alts_perdidas.count(a)) + ') ' + a)
				copia_alts_perdidas.append(a)	
	
else:
	finalizar_bot = False
	while not finalizar_bot:
		for c in coins_trader:
			if c.ciclo > ciclos:
				print('### CICLO PARA ' + c.n_alt + ' FINALIZADO CORRECTAMENTE ###')
			else:
				if c.tipo_operacion == 'SIN ORDEN':
					if (c.percentChange >= margen_incremento_24h and c.lowestAsk <= (c.high24hr + c.low24hr) * margen_incrememto_act) or margen_incremento_24h == 0.0:
						esperando_ticker()
						if funcionamiento == 5 and valor_entrada > 0:
							if c.lowestAsk <= valor_entrada:
								num_last_orden2, last_compra2 = realizar_compra(c.n_alt, c.lowestAsk, saldo_inv)
								if num_last_orden2 != '-1':
									c.num_last_orden = num_last_orden2
									c.last_compra = last_compra2
									c.tipo_operacion = 'COMPRA'
									c.inv_last_compra = saldo_inv
									time.sleep(pausa)
						else:
							num_last_orden2, last_compra2 = realizar_compra(c.n_alt, c.lowestAsk, saldo_inv)
							if num_last_orden2 != '-1':
								c.num_last_orden = num_last_orden2
								c.last_compra = last_compra2
								c.tipo_operacion = 'COMPRA'
								c.inv_last_compra = saldo_inv
								time.sleep(pausa)			
					else:
						print('-----------------------------------------------------------------------------------------------------------------')
						print('### ' + c.n_alt + ' ESPERANDO QUE SE DEN LAS CONDICIONES PARA NUEVA ORDEN DE COMPRA ###')
						print('-----------------------------------------------------------------------------------------------------------------')
				
				elif c.tipo_operacion == 'COMPRA':
					if buscar_historial(c.n_alt, c.num_last_orden) and not ordenes_abiertas(c.n_alt, c.num_last_orden):
						print('-----------------------------------------------------------------------------------------------------------------')
						print('### ORDEN DE COMPRA NUM: ' + c.num_last_orden + ' PARA ' + c.n_alt + ' FINALIZADA CORRECTAMENTE ###')
						print('-----------------------------------------------------------------------------------------------------------------')
						esperando_ticker()
						precio_venta = c.last_compra + (c.last_compra * c.margen)
						if precio_venta < c.highestBid:
							precio_venta = c.highestBid
						saldo_inv_alt = leer_balance(c.n_alt)
						if saldo_inv_alt > 0:
							num_last_orden2 = realizar_venta(c.n_alt, precio_venta, saldo_inv_alt)
							if num_last_orden2 != '-1':
								c.num_last_orden = num_last_orden2
								c.last_venta = precio_venta
								c.tipo_operacion = 'VENTA'
								c.inv_last_venta = saldo_inv_alt
								time.sleep(pausa)						
						else:
							print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
							print('### ERROR. SALDO INSUFICIENTE EN ' + c.n_alt + ' PARA REALIZAR LA VENTA ###')
							print('### ESPERANDO NUEVO SALDO ###')
							print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
					else:
						if c.lowestAsk > (c.last_compra + (c.last_compra * 0.01)):
							mv_num_orden = mover_orden(c.num_last_orden, c.lowestAsk)
							if mv_num_orden != '-1':
								c.last_compra = c.lowestAsk
								c.num_last_orden = mv_num_orden
								time.sleep(pausa)
						else:
							print('-----------------------------------------------------------------------------------------------------------------')
							print('### ESPERANDO QUE SE CIERRE LA ORDEN DE ' + c.tipo_operacion + ' PARA ' + c.n_alt + ' ###')
							print('-----------------------------------------------------------------------------------------------------------------')
				else:
					if buscar_historial(c.n_alt, c.num_last_orden) and not ordenes_abiertas(c.n_alt, c.num_last_orden):
						print('-----------------------------------------------------------------------------------------------------------------')
						print('### ORDEN DE VENTA NUM: ' + c.num_last_orden + ' PARA ' + c.n_alt + ' FINALIZADA CORRECTAMENTE ###')
						print('-----------------------------------------------------------------------------------------------------------------')
						print('-----------------------------------------------------------------------------------------------------------------')
						print('### FINALIZADO CICLO: ' + str(c.ciclo) + ' - BENEFICIO: ' + str((c.last_venta * c.inv_last_venta) - c.inv_last_compra) + ' ' + str(((c.last_venta * c.inv_last_venta * 100)/c.inv_last_compra)-100) + '% ###')
						print('-----------------------------------------------------------------------------------------------------------------')
						c.tipo_operacion = 'SIN ORDEN'
						c.beneficio_total += (c.last_venta * c.inv_last_venta) - c.inv_last_compra
						c.num_last_orden = ''
						c.ciclo +=1
					else:
						print('-----------------------------------------------------------------------------------------------------------------')
						print('### ESPERANDO QUE SE CIERRE LA ORDEN DE ' + c.tipo_operacion + ' PARA ' + c.n_alt + ' ###')
						print('-----------------------------------------------------------------------------------------------------------------')
				
		time.sleep(pausa)

		f = 0
		for c in coins_trader:
			if c.ciclo > ciclos:
				f +=1
		if f == len(coins_trader):
			finalizar_bot = True
		
		
	act_tick.stop()
	act_hist.stop()

	print('')
	print('###############################################################')
	print('#########  POBOT_MAX  FINALIZADO   CORRECTAMENTE    ###########')
	print('###############################################################')
	print('')
	print('Ejecutados ' + str(ciclos) + ' ciclos para ' + altstr)
	print('Para las siguientes AltCoins:')
	for c in coins_trader:
		print(c.n_alt + ' -- Beneficio Total: ' + str(c.beneficio_total))
	print('###############################################################')
