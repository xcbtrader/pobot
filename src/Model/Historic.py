import jsonpickle
import copy


class Historic(object):
    HISTORY_FILENAME = 'history.json'

    def __init__(self, base_coin, balance_to_use, min_profit_share, cycles):
        self.base_coin = base_coin
        self.balance_to_use = balance_to_use
        self.min_profit_share = min_profit_share
        self.cycles = cycles
        self.historic = []
        self.global_state = {}

    def add_altcoin_historic(self, coin_name, transaction):
        new_entry = {coin_name: copy.copy(transaction)}
        self.historic.append(new_entry)
        self.global_state[coin_name] = transaction
        self.save()

    def save(self):
        with open(self.HISTORY_FILENAME, "w") as history_filename:
            history_filename.write(jsonpickle.encode(self))

    @staticmethod
    def load():
        with open(Historic.HISTORY_FILENAME, "r") as history_filename:
            return jsonpickle.decode(history_filename.read())
