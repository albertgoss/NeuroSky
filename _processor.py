from . import Connector
import threading
from numpy import amin, amax, fft, absolute, real, array


class Processor(object):
    def __init__(self):  # type: Processor
        self.data_resolution = 250

        self._raw_data_batch = []
        self.blink_threshold = 150
        self.fft_data = []
        self.is_available = False

    @staticmethod
    def _init_thread(target, args=()):
        threading.Thread(target=target, args=args).start()

    def append_data(self, raw_data):  # type: (Processor, int) -> None
        self._raw_data_batch.append(raw_data)
        if len(self._raw_data_batch) >= self.data_resolution:
            self._init_thread(target=self._fft)

    def _fft(self):  # type: (Processor) -> None
        tmp = self._raw_data_batch.copy()
        self._raw_data_batch = []
        batch_size = len(tmp)
        fs = 512
        if batch_size is not 0 and (self.blink_threshold > amax(tmp) or -self.blink_threshold < amin(tmp)):
            x_fft = fft.rfftfreq(batch_size, 2 * (1 / fs))[2:50]
            y_fft = absolute(real(fft.rfft(tmp)))[2:50]
            self.fft_data = array([x_fft, y_fft])
            self.is_available = True


if __name__ == '__main__':
    connector = Connector(debug=True, verbose=False)
    processor = Processor()
    while not connector.is_open:
        processor.append_data(connector.raw_data)
        print(processor.fft_data)