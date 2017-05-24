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

# python 2
try:
    from urllib import urlencode as _urlencode
    str = unicode
# python 3
except:
    from urllib.parse import urlencode as _urlencode


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



def leer_ticker(c):
	global altstr
	
	err = True
	while err:
		try:		
			ticker = public_order('returnTicker')
			c = altstr + '_' + c
			t = ticker[c]
			last = float(t['last'])
			return last
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER PRECIO ' + c + ' ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)		

def leer_balance(c):
	err = True
	while err:
		try:
			balance = private_order('returnBalances')
			return float(balance[c])
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print(balance)
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER BALANCE ' + c + ' ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)
			
def realizar_compra(c, last, margen, saldo_inv):
	global altstr
	
	precio_compra = last
	c1 = c
	c = altstr + '_' + c

	err = True
	while err:	
		try:
			make_order_buy = private_order('buy', {'currencyPair':c, 'rate': str(precio_compra), 'amount': str(saldo_inv/precio_compra), 'postOnly': 1})
			print('**********************************************************************************************************************************')
			print('*** ' + c + ' CREADA ORDEN DE COMPRA NUM ' + make_order_buy['orderNumber'] + ' - PRECIO: ' + str(precio_compra) + ' $ - INVERSION: ' + str(saldo_inv) + ' $ ***')
			print('**********************************************************************************************************************************')
			err = False
			return make_order_buy['orderNumber'], precio_compra
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print(make_order_buy)
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL CREAR ORDEN DE COMPRA ' + c + ' ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)
			precio_compra = leer_ticker(c1)
	
def realizar_venta(c, precio_venta, margen, saldo_inv):
	global altstr
	
	c = altstr + '_' + c
	
	err = True
	while err:	
		try:
			make_order_sell = private_order('sell', {'currencyPair':c, 'rate': str(precio_venta), 'amount': str(saldo_inv), 'postOnly': 1})
			print('**********************************************************************************************************************************')
			print('*** ' + c + ' CREADA ORDEN DE VENTA NUM ' + make_order_sell['orderNumber'] + ' - PRECIO: ' + str(precio_venta) + ' $ - IVERSION: ' + str(saldo_inv) +  ' ' + c + ' ***')
			print('**********************************************************************************************************************************')
			err = False
			return make_order_sell['orderNumber']
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print(make_order_sell)
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL CREAR ORDEN DE VENTA ' + c + ' ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)

def guardar_historial(a_ciclo, a_saldo, a_order, a_last, a_lecturas, a_ultimo_precio_compra):
	
	f_historial = open('pobot.his', 'a')
	
	texto = ''
	for o in a_ciclo:
		texto = texto + str(o) + ';'
	
	texto = texto[0 :-1]
	f_historial.write(texto + '\n')

	texto = ''
	for o in a_saldo:
		texto = texto + str(o) + ';'
	
	texto = texto[0 :-1]
	f_historial.write(texto + '\n')
	
	texto = ''
	for o in a_order:
		texto = texto + str(o) + ';'
	
	texto = texto[0 :-1]
	f_historial.write(texto + '\n')
	
	texto = ''
	for o in a_last:
		texto = texto + str(o) + ';'
	
	texto = texto[0 :-1]
	f_historial.write(texto + '\n')	

	texto = ''
	for o in a_lecturas:
		texto = texto + str(o) + ';'
	
	texto = texto[0 :-1]
	f_historial.write(texto + '\n')
	
	texto = ''
	for o in a_ultimo_precio_compra:
		texto = texto + str(o) + ';'
	
	texto = texto[0 :-1]
	f_historial.write(texto + '\n')
	
	f_historial.close()
	
def leer_historial():
	
	f_historial = open('pobot.his', 'r')
	orde = f_historial.readlines()
	f_historial.close()
	
	t = orde[-6].strip()
	t = t.split(';')
	a_ciclo = []
	for tt in t:
		a_ciclo.append(int(tt))
		
	
	t = orde[-5].strip()
	t = t.split(';')
	a_saldo = []
	for tt in t:
		a_saldo.append(float(tt))
		
	
	t = orde[-4].strip()
	t = t.split(';')
	a_order = []
	for tt in t:
		a_order.append(tt)
		
	
	t = orde[-3].strip()
	t = t.split(';')
	a_last = []
	for tt in t:
		a_last.append(float(tt))
		
	
	t = orde[-2].strip()
	t = t.split(';')
	a_lecturas = []
	for tt in t:
		a_lecturas.append(int(tt))
		
	t = orde[-1].strip()
	t = t.split(';')
	a_ultimo_precio_compra = []
	for tt in t:
		a_ultimo_precio_compra.append(float(tt))
						
	
	
	return a_ciclo, a_saldo, a_order, a_last, a_lecturas, a_ultimo_precio_compra

def cancelar_orden(num_orden_cerrar):
	global polo

	try:	
		canc_orden = private_order('cancelOrder', {'orderNumber': str(num_orden_cerrar), 'orderType': 'postOnly'})
		print('### CANCELADA ORDEN: ' + str(num_orden_cerrar) + ' CORRECTAMENTE')
		time.sleep(60)
	except KeyboardInterrupt:
		exit()	
	except Exception:
		print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
		print('### ERROR AL CANCELAR ORDEN ###')
		print('### ESPERANDO 30 SEGUNDOS ###')
		time.sleep(30)
		
def mover_orden(num_orden_cerrar, last):
	err = True
	while err:	
		try:	
			mov_orden = private_order('moveOrder', {'orderNumber': str(num_orden_cerrar), 'postOnly': 1})
			print('### MOVIDA ORDEN: ' + str(num_orden_cerrar) +  ' AL NUEVO PRECIO: ' + str(last) + ' $ CORRECTAMENTE')
			err = False
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print(mov_orden)
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL MOVER ORDEN ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)
		

def historial_trades(c, n_order):
	global altstr
	
	c = altstr + '_' + c
	err = True
	while err:
		try:
			final = datetime.utcnow()
			inicio = final - timedelta(days=30)
			unixtime1 = calendar.timegm(inicio.utctimetuple())
			unixtime2 = calendar.timegm(final.utctimetuple())
			trade_hist = private_order('returnTradeHistory', {'currencyPair': c, 'start': str(unixtime1)})
			for t in trade_hist:
				if t['orderNumber'] == n_order:
					return True, t['type']
			return False, ''
		except KeyboardInterrupt:
			exit()	
		except Exception:
			print(trade_hist)
			print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
			print('### ERROR AL LEER HISTORIAL DE ORDENES ###')
			print('### ESPERANDO 30 SEGUNDOS ###')
			time.sleep(30)

		
# PROGRAMA PRINCIPAL #####################################################################

global coins, API_key, Secret, _nonce, altstr

print('')
print('     ****************************************************************')
print('     ****************************************************************')
print('     **                                                            **')
print('    ***  ######   ######   ####    ######   ######         ######  ***')     
print('    ***  #    #   #    #   #   #   #    #     ##                #  ***')
print('    ***  ######   #    #   ####    #    #     ##     ##    ######  ***')
print('    ***  #        #    #   #   #   #    #     ##           #       ***')
print('    ***  #        ######   #####   ######     ##           ######  ***')
print('     **                                                            **')
print('     ****************************************************************')
print('     ****************************************************************')
print('')
print('')
print('')

_nonce = int("{:.6f}".format(time.time()).replace('.', ''))

try:
	configuracion = open('pobot.cfg', 'r')
	config = configuracion.readlines()
	t = config[0].split(';')
	API_key = t[1].strip()
	t = config[1].split(';')
	Secret = t[1].strip()
	a_c = config[2].strip()
	b_c = config[3].strip()
	a_coins = a_c.split(';')
	b_coins = b_c.split(';')
	
except KeyboardInterrupt:
	exit()	
except Exception:
	print("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
	exit()

resumir = input('Continuar sesion guardada (s/n): ? ')

if resumir == 's' or resumir == 'S':
	f_historial = open('pobot.his', 'a')
	f_historial.close()
	f_historial = open('pobot.his', 'r')
	historial = f_historial.readline()
	
	if historial == '':
		print('### ERROR NO EXISTE NINGUNA SESION GUARDADA ###')
		print('### CERRANDO BOT ###')
		exit()
	else:
		f_historial.close()
		f_historial = open('pobot.his', 'r')
		historial = f_historial.readlines()
		
		altstr = historial[0].strip()
		saldo_inv_usdt = float(historial[1].strip())
		m = historial[2].split(';')
		a_margen = []
		coins = []
		n = 0
		for mm in m:
			if float(mm.strip()) > 0:
				a_margen.append(float(mm.strip()))
				if altstr == 'USDT':
					coins.append(a_coins[n])
				else:
					coins.append(b_coins[n])
			n +=1
		saldo_inv_usdt = saldo_inv_usdt/len(coins)
		n_ciclos = int(historial[3].strip())
		
		f_historial.close()
		
		a_ciclo, a_saldo, a_order, a_last, a_lecturas, a_ultimo_precio_compra = leer_historial()
		
else:
	f_historial = open('pobot.his', 'w')
	
	saldo_inv_usdt = 0.0
	alt = int(input('Divisa para operar: 1-> BTC, 2-> USDT ?? '))
	if alt == 1:
		altstr = 'BTC'
		saldoUSDT = leer_balance(altstr)
		while saldo_inv_usdt <= 0.0005 or saldo_inv_usdt > saldoUSDT:
			print('Entra saldo BTC a invertir. Maximo: ' + str(saldoUSDT) + ' ' + altstr)
			saldo_inv_usdt = float(input('Inversion:? '))
	else:
		altstr = 'USDT'
		saldoUSDT = leer_balance(altstr)
		while saldo_inv_usdt <= 20 or saldo_inv_usdt > saldoUSDT:
			print('Entra saldo USDT a invertir. Maximo: ' + str(saldoUSDT) + ' ' + altstr)
			saldo_inv_usdt = float(input('Inversion:? '))
				
	f_historial.write(altstr + '\n')
	f_historial.write(str(saldo_inv_usdt) + '\n')
	
	print('ENTRA LOS MARGENES PARA CADA ALTCOIN. SI PONEMOS 0 ESA ALTCOIN NO SE UTILIZA EN EL BOT')

	coins = []
	a_margen = []
	c_margen = ''
	
	if altstr == 'USDT':
		for cn in a_coins:
			print('Margen para ' + cn + ' >=0.5 o 0 para No Altcoin : ? ')
			m1 = str(input())
			m = float(m1.replace(',','.'))
			if m >= 0.5:
				coins.append(cn)
				a_margen.append(m/100)
			c_margen = c_margen + str(m/100) + ';'

	else:
		for cn in b_coins:
			print('Margen para ' + cn + ' >=0.5 o 0 para No Altcoin : ? ')
			m1 = str(input())
			m = float(m1.replace(',','.'))
			if m >= 0.5:
				coins.append(cn)
				a_margen.append(m/100)
			c_margen = c_margen + str(m/100) + ';'
			
	c_margen = c_margen[0 :-1]
	f_historial.write(c_margen + '\n')
	
	saldo_inv_usdt = saldo_inv_usdt/len(coins)
		
	n_ciclos = int(input('Entra el numero de ciclos que durara la inversion: ? '))
	f_historial.write(str(n_ciclos) + '\n')
	
	a_ciclo = []
	a_saldo = []
	a_order = []
	a_last = []
	a_lecturas = []
	a_ultimo_precio_compra = []

	for nc in coins:
		a_ciclo.append(1)
		a_saldo.append(0.0)
		a_order.append('')
		a_last.append(0.0)
		a_lecturas.append(1)
		a_ultimo_precio_compra.append(0.0)
	
# PRIMERA COMPRA ###################################################
	print('')
	print('### INICIANDO PRIMERA COMPRA ###')

	j = 0
	for nc in coins:
		a_last[j] = leer_ticker(nc)
		a_order[j], a_ultimo_precio_compra[j] = realizar_compra(nc, a_last[j], a_margen[j], saldo_inv_usdt)
		print('### ESPERANDO 30 SEGUNDOS ###')
		guardar_historial(a_ciclo, a_saldo, a_order, a_last, a_lecturas, a_ultimo_precio_compra)
		time.sleep(30)	
		j +=1
	
print('')

finalizar_bot = False
while not finalizar_bot:
	j = 0
	for nc in coins:
		if a_ciclo[j] > n_ciclos:
			print('******** CICLOS PARA ' + nc + ' FINALIZADOS CORRECTAMENTE ********')
			print('### ESPERANDO 30 SEGUNDOS ### ')
			time.sleep(30)
		else:
			fin, tipo = historial_trades(nc, a_order[j])
			if fin:
				if tipo == 'buy':
					print('### ORDEN DE COMPRA NUM: ' + a_order[j] + ' FINALIZADA CORRECTAMENTE ###')
					print('### ESPERANDO 30 SEGUNDOS PARA GENERAR ORDEN DE VENTA ###')
					time.sleep(30)
					a_last[j] = leer_ticker(nc)
					precio_venta = a_ultimo_precio_compra[j] + (a_ultimo_precio_compra[j] * a_margen[j])

					if a_last[j] > precio_venta:
						precio_venta = a_last[j]					
				
					saldo_ALT_nuevo = leer_balance(nc)
					if saldo_ALT_nuevo > 0:
#						saldo_inv_alt = saldo_ALT_nuevo * 0.995
						saldo_inv_alt = saldo_ALT_nuevo
						a_order[j] = realizar_venta(nc, precio_venta, a_margen[j], saldo_inv_alt)
						guardar_historial(a_ciclo, a_saldo, a_order, a_last, a_lecturas, a_ultimo_precio_compra)
						print('### ESPERANDO 30 SEGUNDOS ###')
						time.sleep(30)
					else:
						print('### SALDO INSUFICIENTE EN ' + nc + ' PARA REALIZAR LA VENTA ###')
					
				elif tipo == 'sell':
					print('### ORDEN DE VENTA NUM: ' + a_order[j] + ' FINALIZADA CORRECTAMENTE ###')
					a_ciclo[j] +=1
					if a_ciclo[j] > n_ciclos:
						print('### CICLOS PARA ' + nc + ' FINALIZADOS CORRECTAMENTE ###')
					else:
						print('### ESPERANDO 30 SEGUNDOS PARA GENERAR ORDEN DE COMPRA ###')
						time.sleep(30)
						a_last[j] = leer_ticker(nc)				
						saldoUSDT = leer_balance(altstr)
						if saldoUSDT > saldo_inv_usdt:
							a_order[j], a_ultimo_precio_compra[j] = realizar_compra(nc, a_last[j], a_margen[j], saldo_inv_usdt)
							guardar_historial(a_ciclo, a_saldo, a_order, a_last, a_lecturas, a_ultimo_precio_compra)					
							a_ultimo_precio_compra[j] = a_last[j]
							print('### ESPERANDO 30 SEGUNDOS ###')
							time.sleep(30)
						else:
							print('### ' + str(saldoUSDT) + ' SALDO INSUFICIENTE PARA REALIZAR LA COMPRA ###')
		
			else:
				a_last[j] = leer_ticker(nc)
				if a_last[j] > a_ultimo_precio_compra[j] + (a_ultimo_precio_compra[j] * 0.01):
					mover_orden(a_order[j],a_last[j])
					a_ultimo_precio_compra[j] = a_last[j]
					print('### ESPERANDO 30 SEGUNDOS ###')
					time.sleep(30)
				else:
					if altstr == 'BTC':
						print('### ' + altstr + '_' + nc + ' - CICLO: ' + str(a_ciclo[j]) + '/' + str(n_ciclos) + ' - NUM. LECTURAS: ' + str(a_lecturas[j]) + ' - LAST: ' + str(100000000 * a_last[j]) + 'Sat (' + str(100000000 * a_ultimo_precio_compra[j]) + ') ###') 
					else:
						print('### ' + altstr + '_' + nc + ' - CICLO: ' + str(a_ciclo[j]) + '/' + str(n_ciclos) + ' - NUM. LECTURAS: ' + str(a_lecturas[j]) + ' - LAST: ' + str(a_last[j]) + '$ (' + str(a_ultimo_precio_compra[j]) + ') ###') 						
					print('### ESPERANDO 30 SEGUNDOS A QUE SE CIERRE LA ORDEN ###')
					time.sleep(30)
				
		a_lecturas[j] += 1	
		j +=1

	fc = 0
	ff = 0
	for nc2 in coins:
		if a_ciclo[fc] > n_ciclos:
			ff +=1
		fc +=1
	if ff == fc:
		finalizar_bot = True
		
print('#########################################################')
print('#########  BOT  FINALIZADO   CORRECTAMENTE    ###########')
print('#########################################################')
print('')
print('Ejecutados ' + str(n_ciclos) + ' ciclos para ' + altstr)
print('Para las siguientes AltCoins:')
for nc in coins:
	print(nc)
print('#########################################################')
