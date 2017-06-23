class Transaction(object):
    def __init__(self, cycle, balance, order, last_price, reads, last_buy_price):
        self.cycle = cycle
        self.balance = balance
        self.order = order
        self.last_price = last_price
        self.reads = reads
        self.last_buy_price = last_buy_price
