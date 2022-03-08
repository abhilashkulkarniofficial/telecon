from pydispatch import dispatcher
from time import sleep
import random

SIGNAL = 'my-first-signal'

class RandomDataGen(object):
    def __init__(self, init=50):
        self.data = self.init = init

    def next(self):
        self._recalc_data()
        return self.data

    def _recalc_data(self):
        delta = random.uniform(-0.5, 0.5)
        r = random.random()

        if r > 0.9:
            self.data += delta * 15
        elif r > 0.8:
            delta += (0.5 if self.init > self.data else -0.5)
            self.data += delta
        else:
            self.data += delta


class PubSub(object):
    def __init__(self, signal) -> None:
        super().__init__()
        self.SIGNAL = signal


    def publish(self):
        datagen = RandomDataGen()
        data = datagen.next()
        while True:
            dispatcher.send(signal=self.SIGNAL, data=data)
            data = datagen.next()
            sleep(1)

    def subscribe(self, handler):
        dispatcher.connect(handler, signal=self.SIGNAL, sender=dispatcher.Any)

# def handle_event(data):
#     """Simple event handler"""
#     print(data)

# if __name__ == '__main__':
# # def main():
#     ps = PubSub(SIGNAL)
#     ps.subscribe(handle_event)
#     ps.publish()