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
			print(ret)
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL EJECUTAR PRIVATE ORDER ' + command + ' ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)	
	
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
			print(ret)
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL EJECUTAR PUBLIC ORDER ' + command + ' ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)
			
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
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER TICKER ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)	

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
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER BALANCE ' + c + ' ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)

def leer_balance_full():
	err = True
	while err:
		try:
			balance = private_order('returnBalances')
			return balance
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER BALANCE ' + c + ' ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)

def actualizar_ticker():
	global l_ticker, coins_trader, ticker_actualizado, estadisticas
	
	try:
		l_ticker = leer_ticker_full()
		ticker_actualizado = True
		print('**-----------------------------------------------------------------------------------------------------------------**')
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
			print(c.n_alt + ' - Ciclo: ' + str(c.ciclo) + ' - (Max 24H: ' + str(c.high24hr) + ' , Min 24H: ' + str(c.low24hr) + ' , ' + str(round(100 * c.percentChange,3)) + ' %) -- (Compra: ' + str(c.lowestAsk) + ' , Last: ' + str(c.last) + ' , Venta: ' + str(c.highestBid) + ')')
			
			es = estadisticas[p].last
			es.append(float(t['last']))
			
			p += 1
		print('**-----------------------------------------------------------------------------------------------------------------**')
			
	except KeyboardInterrupt:
		exit()	
	except Exception:
		ticker_actualizado = False
		print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
		print('### ESPERANDO 30 SEGUNDOS ###')
		time.sleep(30)

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
			print('>>>> ' + time.strftime("%d/%m/%y") + ' ' + time.strftime("%H:%M:%S") + ' HISTORIAL DE ORDENES FINALIZADAS, ACTUALIZADO CORRECTAMENTE ')
			print('-----------------------------------------------------------------------------------------------------------------')
		except KeyboardInterrupt:
			exit()	
		except Exception:
			hist_actualizado = False
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER HISTORIAL DE ORDENES ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)						
			
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
		return make_order_buy['orderNumber'], precio_compra
	except KeyboardInterrupt:
		exit()	
	except Exception:
		if make_order_buy['error'] == 'Unable to place post-only order at this price.':
			print('### INTENTANDO PONER ORDEN DE COMPRA PARA ' + c + ' ###')
		else:
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL CREAR ORDEN DE COMPRA ' + c + ' ###')
		return '-1', 0.0
	
def realizar_venta(c, precio_venta, saldo_inv):

	try:	
		make_order_sell = private_order('sell', {'currencyPair':c, 'rate': str(precio_venta), 'amount': str(saldo_inv), 'postOnly': 1})
		print('**********************************************************************************************************************************')
		print('*** ' + c + ' CREADA ORDEN DE VENTA NUM ' + make_order_sell['orderNumber'] + ' - PRECIO: ' + str(precio_venta) + ' - IVERSION: ' + str(saldo_inv) + ' ***')
		print('**********************************************************************************************************************************')
		return make_order_sell['orderNumber']
	except KeyboardInterrupt:
		exit()	
	except Exception:
		if make_order_sell['error'] == 'Unable to place post-only order at this price.':
			print('### INTENTANDO PONER ORDEN DE VENTA PARA ' + c + ' ###')
		else:
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL CREAR ORDEN DE VENTA ' + c + ' ###')
		return '-1'

def mover_orden(num_orden_cerrar, lowestAsk):	
	try:	
		mov_orden = private_order('moveOrder', {'orderNumber': str(num_orden_cerrar), 'rate': str(lowestAsk), 'postOnly': 1})
		print('### MOVIDA ORDEN DE COMPRA: ' + str(num_orden_cerrar) +  ' AL NUEVO PRECIO: ' + str(lowestAsk) + ' CORRECTAMENTE')
		return str(mov_orden['orderNumber'])
	except KeyboardInterrupt:
		exit()	
	except Exception:
		if mov_orden['error'] == 'Unable to place post-only order at this price.':
			print('### INTENTANDO PONER ORDEN DE COMPRA A NUEVO PRECIO ###')
		else:
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL MOVER ORDEN DE COMPRA ###')
		return '-1'

def esperando_ticker():
	prime = True
	while not ticker_actualizado:
		if prime:
			print('### ESPERANDO A TENER VALOR ACTUAL DEL TICKER ###')
			prime = False
		time.sleep(10)

def ordenes_abiertas(c):
	err = True
	while err:
		try:
			open_orders = private_order('returnOpenOrders', {'currencyPair':c,})
			err = False
			if len(open_orders) == 0:
				return False
			else:
				return True
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print(open_orders)
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER LAS ORDENES ABIERTAS ###')
			
def menu_funcionamiento():
	funcionamiento = 0
	while funcionamiento < 1 or funcionamiento > 7:	
		print('')
		print('Escoge el modo como operara Pobot_MAX')
		print('    1-> Segun Margen de Incremento 24h (Con todas las Alts)')
		print('    2-> Segun Margen de Incremento 24h (Escogiendo Manualmente las Alts)')
		print('    3-> Version Antigua - Pone ordenes instantaneas (Con todas las Alts)')
		print('    4-> Version Antigua - Pone ordenes instantaneas (Escogiendo Manualmente las Alts)')
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
	
def escoger_alts(num_max_alts_trader, working_alts, altstr, margen_incremento_24h, margen_incrememto_act):
	alts_ok = []
	err = True
	while err:
		ticker = leer_ticker_full()
		n_tr = 1
		print('')
		print('-----------------------------------------------------------------------------------------------------------------')
		for cn in working_alts:
			if n_tr <= num_max_alts_trader:
				t = ticker[altstr + '_' + cn]
				if (float(t['percentChange']) >= margen_incremento_24h and float(t['lowestAsk']) <= (float(t['high24hr']) + float(t['low24hr'])) * margen_incrememto_act):
					alts_ok.append(cn)
					print('### (' + str(n_tr) + ') AÑADIDO EL SIGUIENTE PAR AL BOT: ' + altstr + '_' + cn + ' ###')
					n_tr += 1
				else:
					print(altstr + '_' + cn +  ' - (Max 24H: ' + t['high24hr'] + ' , Min 24H: ' + t['low24hr'] + ' , ' + str(round(100 * float(t['percentChange']),3)) + ' %) -- (Compra: ' + t['lowestAsk'] + ' , Last: ' + t['last'] + ' , Venta: ' + t['highestBid'] + ')')
	
		if len(alts_ok) == 0:
			print('')
			print('### ESPERANDO A TENER ALTS QUE CUMPLAN LOS CRITERIOS DE TRADER ###')
			print('')
			print('-----------------------------------------------------------------------------------------------------------------')
			time.sleep(30)
		else:
			err = False
	return alts_ok
	
			
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
		self.last_venta = 0.0
		self.tipo_operacion = 'SIN ORDEN'  # Valores: 'Sin Orden', 'Compra', 'Venta'
		self.margen = 0.0
		self.ciclo = 1
		self.num_last_orden = ''
		self.beneficio_total = 0.0
		
class estadist_alt:
	def __init__(self):
		self.n_alt = ''
		self.fecha = ''
		self.last = []
		self.high24hr = []
		self.low24hr = []
		self.EMA1 = []
		self.EMA2 = []
		self.MACD = []
		self.SMA = []
		self.boll_band_max = []
		self.boll_band_min = []
		
		
	def actualizar_valor_ticker(self, n_alt, last):
		pass

# PROGRAMA PRINCIPAL ##########################################################

global EMA1, EMA2, _nonce, altstr, coins, API_key, Secret, inicio_bot, l_ticker, coins_trader, ticker_actualizado, hist_actualizado, trade_hist, n_ticker, n_hist, estadisticas

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

try:
	configuracion = open('pobot_MAX.cfg', 'r')
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
	d_coins = c_c.split(';')
	
except KeyboardInterrupt:
	exit()	
except Exception:
	print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
	exit()

saldo_inv = 0.0
margen_incrememto_act = 0.0
	
alt = menu_alt()
working_alts = []

print('')
	
if alt == 1:
	altstr = 'USDT'
	working_alts = a_coins
	saldoUSDT = leer_balance(altstr)
	while saldo_inv <= 0.0 or saldo_inv > saldoUSDT:
		print('Entra saldo Maximo USDT a invertir. Maximo Disponible: ' + str(saldoUSDT) + ' ' + altstr)
		saldo_inv = float(input('Inversion:? '))
elif alt == 2:
	altstr = 'BTC'
	working_alts = b_coins
	saldoUSDT = leer_balance(altstr)
	while saldo_inv <= 0.0 or saldo_inv > saldoUSDT:
		print('Entra saldo Maximo BTC a invertir: ' + str(saldoUSDT) + ' ' + altstr)
		saldo_inv = float(input('Inversion:? '))
elif alt == 3:
	altstr = 'ETH'
	working_alts = c_coins
	saldoUSDT = leer_balance(altstr)
	while saldo_inv <= 0.0 or saldo_inv > saldoUSDT:
		print('Entra saldo Maximo ETH a invertir: ' + str(saldoUSDT) + ' ' + altstr)
		saldo_inv = float(input('Inversion:? '))
else:
	altstr = 'XMR'
	working_alts = d_coins
	saldoUSDT = leer_balance(altstr)
	while saldo_inv <= 0.0 or saldo_inv > saldoUSDT:
		print('Entra saldo Maximo XMR a invertir: ' + str(saldoUSDT) + ' ' + altstr)
		saldo_inv = float(input('Inversion:? '))
 
funcionamiento = menu_funcionamiento()

ticker = leer_ticker_full()

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
	print('')
	margen_incremento_24h = float(input('Entra el margen de incremento de las ultimas 24h para entrar a invertir:? '))
	margen_incremento_24h = margen_incremento_24h/100
	
	print('')
	margen_incrememto_act = float(input('Entra el margen de incremento actual de la Alt para entrar a invertir:? '))
	margen_incrememto_act = margen_incrememto_act/100
	
	print('')
	margen = 0.0
	while margen <= 0.5:
		margen2 = str(input('Entra el margen de beneficio para todas las Alts: ? ')) 
		margen = float(margen2.replace(',','.'))
		
	for cn in working_alts:
		coins.append(cn)
		a_margen.append(margen/100)

elif funcionamiento == 2:
	print('')
	margen_incremento_24h = float(input('Entra el margen de incremento de las ultimas 24h para entrar a invertir:? '))
	margen_incremento_24h = margen_incremento_24h/100
	
	print('')
	margen_incrememto_act = float(input('Entra el margen de incremento actual de la Alt para entrar a invertir:? '))
	margen_incrememto_act = margen_incrememto_act/100
	
	print('')
	print('ENTRA LOS MARGENES PARA CADA ALTCOIN. SI PONEMOS 0 ESA ALTCOIN NO SE UTILIZA EN EL BOT')
	
	for cn in working_alts:
		print('Margen para ' + cn + ' >=0.5 o 0 para No Altcoin : ? ')
		m1 = str(input())
		m = float(m1.replace(',','.'))
		if m >= 0.5:
			coins.append(cn)
			a_margen.append(m/100)
			
elif funcionamiento == 3:
	margen_incremento_24h = 0.0
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
	print('ENTRA LOS MARGENES PARA CADA ALTCOIN. SI PONEMOS 0 ESA ALTCOIN NO SE UTILIZA EN EL BOT')
	
	for cn in working_alts:
		print('Margen para ' + cn + ' >=0.5 o 0 para No Altcoin : ? ')
		m1 = str(input())
		m = float(m1.replace(',','.'))
		if m >= 0.5:
			coins.append(cn)
			a_margen.append(m/100)	
			
print('')
n_ticker = 0
n_hist = 0

ciclos = 0
while ciclos < 1:
	ciclos = int(input('Numero de ciclos de la Inversion:? '))
		
coins_trader = []
estadisticas = []
p = 0
for c in coins:
	ele_hist = estadist_alt()
	fit_coin = info_alt()
	fit_coin.posicion = p
	fit_coin.n_alt = altstr + '_' + c
	fit_coin.margen = a_margen[p]
	coins_trader.append(fit_coin)
	
	ele_hist.n_alt =  altstr + '_' + c
	ele_hist.fecha = time.strftime("%d/%m/%y") + ' ' + time.strftime("%H:%M:%S")
	estadisticas.append(ele_hist)
	
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

print('### ESPERANDO PRIMERA RECOGIDA DE DATOS DE POLONIEX ###')
time.sleep(60)
finalizar_bot = False
pausa = 10

while not finalizar_bot:
	for c in coins_trader:
		if c.ciclo > ciclos:
			print('### CICLO PARA ' + c.n_alt + ' FINALIZADO CORRECTAMENTE ###')
		else:
			if c.tipo_operacion == 'SIN ORDEN':
				if (c.percentChange >= margen_incremento_24h and c.lowestAsk <= c.low24hr + ((c.high24hr - c.low24hr) * margen_incrememto_act)) or margen_incremento_24h == 0.0:
					esperando_ticker()
					num_last_orden2, last_compra2 = realizar_compra(c.n_alt, c.lowestAsk, saldo_inv)
					if num_last_orden2 != '-1':
						c.num_last_orden = num_last_orden2
						c.last_compra = last_compra2
						c.tipo_operacion = 'COMPRA'
						time.sleep(pausa)			
				else:
					print('-----------------------------------------------------------------------------------------------------------------')
					print('### ' + c.n_alt + ' ESPERANDO QUE SE DEN LAS CONDICIONES PARA NUEVA ORDEN DE COMPRA ###')
					print('-----------------------------------------------------------------------------------------------------------------')
				
			elif c.tipo_operacion == 'COMPRA':
				if buscar_historial(c.n_alt, c.num_last_orden) and not ordenes_abiertas(c.n_alt):
					print('### ORDEN DE COMPRA NUM: ' + c.num_last_orden + ' PARA ' + c.n_alt + ' FINALIZADA CORRECTAMENTE ###')
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
							time.sleep(pausa)						
					else:
						print('### ERROR. SALDO INSUFICIENTE EN ' + c.n_alt + ' PARA REALIZAR LA VENTA ###')
						print('### ESPERANDO NUEVO SALDO ###')
				else:
					if c.lowestAsk > (c.last_compra + (c.last_compra * 0.01)):
						mv_num_orden = mover_orden(c.num_last_orden, c.lowestAsk)
						if mv_num_orden != '-1':
							c.last_compra = c.lowestAsk
							c.num_last_orden = mv_num_orden
							time.sleep(pausa)
					else:
						print('### ESPERANDO QUE SE CIERRE LA ORDEN DE ' + c.tipo_operacion + ' PARA ' + c.n_alt + ' ###')
						
			else:
				if buscar_historial(c.n_alt, c.num_last_orden) and not ordenes_abiertas(c.n_alt):
					print('### ORDEN DE VENTA NUM: ' + c.num_last_orden + ' PARA ' + c.n_alt + ' FINALIZADA CORRECTAMENTE ###')
					print('### FINALIZADO CICLO: ' + str(c.ciclo) + ' - BENEFICIO: ' + str(c.last_venta - c.last_compra) + ' ' + str(((c.last_venta * 100)/c.last_compra)-100) + '% ###')
					c.tipo_operacion = 'SIN ORDEN'
					c.beneficio_total += (c.last_venta - c.last_compra)
					c.num_last_orden = ''
					c.ciclo +=1
				else:
					print('### ESPERANDO QUE SE CIERRE LA ORDEN DE ' + c.tipo_operacion + ' PARA ' + c.n_alt + ' ###')
				
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
