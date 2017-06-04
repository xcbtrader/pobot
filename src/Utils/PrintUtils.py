from datetime import datetime
import sys
import time


def print_error(message):
    print_log("### ERROR INESPERADO TIPO:", sys.exc_info()[1])
    print_log('### ERROR AL ' + message + ' ###')
    print_log('### ESPERANDO 30 SEGUNDOS ###')
    time.sleep(30)


def print_log(message):
    print("[" + str(datetime.now())+"]" + message)