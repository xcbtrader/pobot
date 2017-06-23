import json
import sys
import time
from pathlib import Path
from src.Api import Poloniex
from src.Model import Transaction
from src.Model import Historic
from src.Utils import PrintUtils as cPrint

__author__ = 'xcbtrader'

CONFIG_FILENAME = 'pobot.cfg'


def create_initial_history(usdt_coins, btc_coins):
    global api

    saldo_inv_usdt = 0.0
    alt = int(input('Divisa para operar: 1-> BTC, 2-> USDT ?? '))
    if alt == 1:
        currency = 'BTC'
        saldoUSDT = api.leer_balance(currency)
        while saldo_inv_usdt <= 0.0005 or saldo_inv_usdt > saldoUSDT:
            cPrint.print_log('Entra saldo BTC a invertir. Maximo: ' + str(saldoUSDT) + ' ' + currency)
            saldo_inv_usdt = float(input('Inversion:? '))
    else:
        currency = 'USDT'
        saldoUSDT = api.leer_balance(currency)
        while saldo_inv_usdt <= 20 or saldo_inv_usdt > saldoUSDT:
            cPrint.print_log('Entra saldo USDT a invertir. Maximo: ' + str(saldoUSDT) + ' ' + currency)
            saldo_inv_usdt = float(input('Inversion:? '))

    cPrint.print_log('ENTRA LOS MARGENES PARA CADA ALTCOIN. SI PONEMOS 0 ESA ALTCOIN NO SE UTILIZA EN EL BOT')
    margin = {}

    if currency == 'USDT':
        for cn in usdt_coins:
            cPrint.print_log('Margen para ' + cn + ' >=0.5 o 0 para No Altcoin : ? ')
            m1 = str(input())
            m = float(m1.replace(',', '.'))
            if m >= 0.5:
                margin[cn] = m / 100
    else:
        for cn in btc_coins:
            cPrint.print_log('Margen para ' + cn + ' >=0.5 o 0 para No Altcoin : ? ')
            m1 = str(input())
            m = float(m1.replace(',', '.'))
            if m >= 0.5:
                margin[cn] = m / 100

    saldo_inv_usdt = saldo_inv_usdt / len(margin)
    n_ciclos = int(input('Entra el numero de ciclos que durara la inversion: ? '))

    hmanager = Historic.Historic(currency, saldo_inv_usdt, margin, n_ciclos)
    for nc in margin:
        transaction = Transaction.Transaction(1, 0.0, '', 0.0, 1, 0.0)
        hmanager.add_altcoin_historic(nc, transaction)

    return hmanager


def handle_buy_scenario(nc, global_state, historia):
    global api

    cPrint.print_log('### ORDEN DE COMPRA NUM: ' + global_state.order + ' FINALIZADA CORRECTAMENTE ###')
    cPrint.print_log('### ESPERANDO 30 SEGUNDOS PARA GENERAR ORDEN DE VENTA ###')
    time.sleep(30)
    global_state.last_price = api.leer_ticker(nc)
    precio_venta = global_state.last_buy_price + (global_state.last_buy_price * historia.min_profit_share[nc])

    if global_state.last_price > precio_venta:
        precio_venta = global_state.last_price

    saldo_ALT_nuevo = api.leer_balance(nc)
    if saldo_ALT_nuevo > 0:
        # saldo_inv_alt = saldo_ALT_nuevo * 0.995
        saldo_inv_alt = saldo_ALT_nuevo
        global_state.order = api.realizar_venta(nc, precio_venta, historia.min_profit_share[nc], saldo_inv_alt)
        historia.add_altcoin_historic(nc, global_state)
        cPrint.print_log('### ESPERANDO 30 SEGUNDOS ###')
        time.sleep(30)
    else:
        cPrint.print_log('### SALDO INSUFICIENTE EN ' + nc + ' PARA REALIZAR LA VENTA ###')


def handle_sell_scenario(nc, global_state, historia):
    global api

    cPrint.print_log('### ORDEN DE VENTA NUM: ' + global_state.order + ' FINALIZADA CORRECTAMENTE ###')
    global_state.cycle += 1
    if global_state.cycle > historia.cycles:
        cPrint.print_log('### CICLOS PARA ' + nc + ' FINALIZADOS CORRECTAMENTE ###')
    else:
        cPrint.print_log('### ESPERANDO 30 SEGUNDOS PARA GENERAR ORDEN DE COMPRA ###')
        time.sleep(30)
        global_state.last_price = api.leer_ticker(nc)
        saldoUSDT = api.leer_balance(historia.base_coin)
        saldo_inv_usdt = historia.balance_to_use / len(historia.global_state)
        if saldoUSDT > saldo_inv_usdt:
            global_state.order, global_state.last_buy_price = api.realizar_compra(nc, global_state.last_price, historia.min_profit_share[nc], saldo_inv_usdt)
            historia.add_altcoin_historic(nc, global_state)
            global_state.last_buy_price = global_state.last_price
            cPrint.print_log('### ESPERANDO 30 SEGUNDOS ###')
            time.sleep(30)
        else:
            cPrint.print_log('### ' + str(saldoUSDT) + ' SALDO INSUFICIENTE PARA REALIZAR LA COMPRA ###')


def handle_order_not_closed_yet(nc, global_state, historia):
    global api

    global_state.last_price = api.leer_ticker(nc)
    if global_state.last_price > global_state.last_buy_price + (global_state.last_buy_price * 0.01):
        api.mover_orden(global_state.order, global_state.last_price)
        global_state.last_buy_price = global_state.last_price
        cPrint.print_log('### ESPERANDO 30 SEGUNDOS ###')
        time.sleep(30)
    else:
        if historia.base_coin == 'BTC':
            cPrint.print_log('### ' + historia.base_coin + '_' + nc + ' - CICLO: ' + str(global_state.cycle) + '/' + str(
                historia.cycles) + ' - NUM. LECTURAS: ' + str(global_state.reads) + ' - LAST: ' + str(
                100000000 * global_state.last_price) + 'Sat (' + str(100000000 * global_state.last_buy_price) + ') ###')
        else:
            cPrint.print_log('### ' + historia.base_coin + '_' + nc + ' - CICLO: ' + str(global_state.cycle) + '/' + str(
                historia.cycles) + ' - NUM. LECTURAS: ' + str(global_state.reads) + ' - LAST: ' + str(
                global_state.last_price) + '$ (' + str(global_state.last_buy_price) + ') ###')
        cPrint.print_log('### ESPERANDO 30 SEGUNDOS A QUE SE CIERRE LA ORDEN ###')
        time.sleep(30)


def check_requirements():
    from pkgutil import iter_modules
    modules = set(x[1] for x in iter_modules())
    missing_modules = ""
    required_modules = ['requests', 'jsonpickle']
    for module in required_modules:
        if not module in modules:
            missing_modules += " " + module

    if missing_modules != '':
        cPrint.print_log('[ERROR] Missing Modules Found:\n\t Use "pip install' + missing_modules + '" first.')
        exit(1)


def print_header():
    cPrint.print_log('')
    cPrint.print_log('     ****************************************************************')
    cPrint.print_log('     ****************************************************************')
    cPrint.print_log('     **                                                            **')
    cPrint.print_log('    ***  ######   ######   ####    ######   ######         ######  ***')
    cPrint.print_log('    ***  #    #   #    #   #   #   #    #     ##                #  ***')
    cPrint.print_log('    ***  ######   #    #   ####    #    #     ##     ##    ######  ***')
    cPrint.print_log('    ***  #        #    #   #   #   #    #     ##           #       ***')
    cPrint.print_log('    ***  #        ######   #####   ######     ##           ######  ***')
    cPrint.print_log('     **                                                            **')
    cPrint.print_log('     ****************************************************************')
    cPrint.print_log('     ****************************************************************')
    cPrint.print_log('')
    cPrint.print_log('')
    cPrint.print_log('')


if __name__ == "__main__":
    check_requirements()
    print_header()

    global api

    try:
        config_file = Path(CONFIG_FILENAME)
        if not config_file.is_file():
            cPrint.print_log("Config file missing")
            exit()
        with open(CONFIG_FILENAME, 'r') as config_file:
            data = json.load(config_file)
            API_key = data["API_key"]
            Secret = data["Secret"]
            usdt_coins = data["USDT_Coins"]
            btc_coins = data["BTC_Coins"]
            api = Poloniex.Poloniex(API_key, Secret)

    except KeyboardInterrupt:
        exit()
    except Exception:
        cPrint.print_log("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
        exit()

    reinitialize_history = True
    history_file = Path(Historic.Historic.HISTORY_FILENAME)
    if history_file.is_file():
        resumir = input('Continuar sesion guardada (S/n): ? ')
        if resumir == 's' or resumir == 'S' or resumir == '':
            reinitialize_history = False

    if reinitialize_history:
        historia = create_initial_history(usdt_coins, btc_coins)
        cPrint.print_log('')
        cPrint.print_log('### INICIANDO PRIMERA COMPRA ###')

        for nc, transaction in historia.global_state.items():
            transaction.last_price = api.leer_ticker(nc)
            saldo_inv_usdt = historia.balance_to_use / len(historia.global_state)
            transaction.order, transaction.last_buy_price = api.realizar_compra(nc, transaction.last_price, historia.min_profit_share[nc], saldo_inv_usdt)
            cPrint.print_log('### ESPERANDO 30 SEGUNDOS ###')
            historia.add_altcoin_historic(nc, transaction)
            time.sleep(30)
    else:
        historia = Historic.Historic.load()

    api.base_coin = historia.base_coin
    finalizar_bot = False
    while not finalizar_bot:
        for nc, global_state in historia.global_state.items():
            if global_state.cycle > historia.cycles:
                cPrint.print_log('******** CICLOS PARA ' + nc + ' FINALIZADOS CORRECTAMENTE ********')
                cPrint.print_log('### ESPERANDO 30 SEGUNDOS ### ')
                time.sleep(30)
            else:
                fin, tipo = api.historial_trades(nc, global_state.order)
                if fin:
                    if tipo == 'buy':
                        handle_buy_scenario(nc, global_state, historia)

                    elif tipo == 'sell':
                        handle_sell_scenario(nc, global_state, historia)

                else:
                    handle_order_not_closed_yet(nc, global_state, historia)

            global_state.reads += 1

        ff = 0
        for nc, global_state in historia.global_state.items():
            if global_state.cycle > historia.cycles:
                ff += 1
        if ff == len(historia.global_state):
            finalizar_bot = True

    cPrint.print_log('#########################################################')
    cPrint.print_log('#########  BOT  FINALIZADO   CORRECTAMENTE    ###########')
    cPrint.print_log('#########################################################')
    cPrint.print_log('')
    cPrint.print_log('Ejecutados ' + str(historia.cycles) + ' ciclos para ' + historia.base_coin)
    cPrint.print_log('Para las siguientes AltCoins:')
    for nc in historia.global_state:
        cPrint.print_log(nc)
    cPrint.print_log('#########################################################')
