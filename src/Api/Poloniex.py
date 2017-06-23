import calendar
import hmac
import json
import requests
import time
from datetime import datetime, timedelta
from hashlib import sha512
from urllib.parse import urlencode

from src.Utils import PrintUtils as cPrint


class Poloniex(object):
    def __init__(self, api_key, secret):
        self.nonce = int("{:.6f}".format(time.time()).replace('.', ''))
        self.base_coin = ''
        self.api_key = api_key
        self.secret = secret

    def get_new_nonce(self):
        self.nonce += 42
        return self.nonce

    def private_order(self, command, args={}):
        err = True
        while err:
            try:
                args['command'] = command
                args['nonce'] = self.get_new_nonce()
                post_data = urlencode(args)

                sign = hmac.new(self.secret.encode('utf-8'), post_data.encode('utf-8'), sha512)

                ret = requests.post('https://poloniex.com/tradingApi', data=args,
                                    headers={'Sign': sign.hexdigest(), 'Key': self.api_key})

                return json.loads(ret.text, parse_float=str)
            except KeyboardInterrupt:
                exit()
            except Exception:
                print(ret)
                cPrint.print_error('EJECUTAR PRIVATE ORDER ' + command)

    def public_order(self, command, args={}):
        err = True
        while err:
            try:
                args['command'] = command
                ret = requests.get('https://poloniex.com/public?' + urlencode(args))
                return json.loads(ret.text, parse_float=str)
            except KeyboardInterrupt:
                exit()
            except Exception:
                print(ret)
                cPrint.print_error('EJECUTAR PUBLIC ORDER ' + command)

    def leer_ticker(self, c):
        err = True
        while err:
            try:
                ticker = self.public_order('returnTicker')
                c = self.base_coin + '_' + c
                t = ticker[c]
                last = float(t['last'])
                return last
            except KeyboardInterrupt:
                exit()
            except Exception:
                cPrint.print_error('LEER PRECIO ' + c)

    def leer_balance(self, c):
        err = True
        while err:
            try:
                balance = self.private_order('returnBalances')
                return float(balance[c])
            except KeyboardInterrupt:
                exit()
            except Exception:
                cPrint.print_log(balance)
                cPrint.print_error('LEER BALANCE ' + c)

    def realizar_compra(self, c, last, margen, saldo_inv):
        precio_compra = last
        c1 = c
        c = self.base_coin + '_' + c

        err = True
        while err:
            try:
                make_order_buy = self.private_order('buy', {'currencyPair': c, 'rate': str(precio_compra),
                                                       'amount': str(saldo_inv / precio_compra), 'postOnly': 1})
                cPrint.print_log('**********************************************************************************************************************************')
                cPrint.print_log('*** ' + c + ' CREADA ORDEN DE COMPRA NUM ' + make_order_buy['orderNumber'] + ' - PRECIO: ' + str(
                    precio_compra) + ' $ - INVERSION: ' + str(saldo_inv) + ' $ ***')
                cPrint.print_log('**********************************************************************************************************************************')
                err = False
                return make_order_buy['orderNumber'], precio_compra
            except KeyboardInterrupt:
                exit()
            except Exception:
                cPrint.print_log(make_order_buy)
                cPrint.print_error('CREAR ORDEN DE COMPRA ' + c)
                precio_compra = self.leer_ticker(c1)

    def realizar_venta(self, c, precio_venta, margen, saldo_inv):
        c = self.base_coin + '_' + c

        err = True
        while err:
            try:
                make_order_sell = self.private_order('sell',
                                                {'currencyPair': c, 'rate': str(precio_venta), 'amount': str(saldo_inv),
                                                 'postOnly': 1})
                cPrint.print_log('**********************************************************************************************************************************')
                cPrint.print_log('*** ' + c + ' CREADA ORDEN DE VENTA NUM ' + make_order_sell['orderNumber'] + ' - PRECIO: ' + str(
                    precio_venta) + ' $ - IVERSION: ' + str(saldo_inv) + ' ' + c + ' ***')
                cPrint.print_log('**********************************************************************************************************************************')
                err = False
                return make_order_sell['orderNumber']
            except KeyboardInterrupt:
                exit()
            except Exception:
                cPrint.print_log(make_order_sell)
                cPrint.print_error('CREAR ORDEN DE VENTA ' + c)

    def cancelar_orden(self, num_orden_cerrar):
        global polo

        try:
            canc_orden = self.private_order('cancelOrder', {'orderNumber': str(num_orden_cerrar), 'orderType': 'postOnly'})
            cPrint.print_log('### CANCELADA ORDEN: ' + str(num_orden_cerrar) + ' CORRECTAMENTE')
            time.sleep(60)
        except KeyboardInterrupt:
            exit()
        except Exception:
            cPrint.print_error('CANCELAR ORDEN')

    def mover_orden(self, num_orden_cerrar, last):
        err = True
        while err:
            try:
                mov_orden = self.private_order('moveOrder', {'orderNumber': str(num_orden_cerrar), 'postOnly': 1})
                cPrint.print_log('### MOVIDA ORDEN: ' + str(num_orden_cerrar) + ' AL NUEVO PRECIO: ' + str(last) + ' $ CORRECTAMENTE')
                err = False
            except KeyboardInterrupt:
                exit()
            except Exception:
                cPrint.print_log(mov_orden)
                cPrint.print_error('MOVER ORDEN')

    def historial_trades(self, c, n_order):
        c = self.base_coin + '_' + c
        err = True
        while err:
            try:
                final = datetime.utcnow()
                inicio = final - timedelta(days=30)
                unixtime1 = calendar.timegm(inicio.utctimetuple())
                unixtime2 = calendar.timegm(final.utctimetuple())
                trade_hist = self.private_order('returnTradeHistory', {'currencyPair': c, 'start': str(unixtime1)})
                for t in trade_hist:
                    if t['orderNumber'] == n_order:
                        return True, t['type']
                return False, ''
            except KeyboardInterrupt:
                exit()
            except Exception:
                cPrint.print_log(trade_hist)
                cPrint.print_error('LEER HISTORIAL DE ORDENES')
