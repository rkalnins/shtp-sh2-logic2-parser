
from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting

class Packet:
    end_times: list
    start_times: list
    is_continuation_header: bool
    header_idx: int
    start_time: float
    end_time: float
    length_lsb: int
    length_msb: int
    length: int
    channel: int
    sequence_number: int
    data: bytearray

    def __init__(self, start_time) -> None:
        self.end_times = list()
        self.start_times = list()
        self.is_continuation_header = False
        self.length = 0xFFFF
        self.header_idx = 0
        self.sequence_number = 0xFF
        self.channel = 0xFF
        self.start_time = start_time
        self.end_time = 0
        self.data = bytearray()


class SHTPParser:
    def __init__(self):
        self.packet = None

    def fill_header(self, d):
        if self.packet.header_idx == 0:
            self.packet.length_lsb = d[0]
        elif self.packet.header_idx == 1:
            self.packet.length_msb = d[0]
            length = self.packet.length_lsb | (self.packet.length_msb << 8)
            length = length & 0x7FFF

            print("len: ", length)

            self.packet.length = length
        elif self.packet.header_idx == 2:
            self.packet.channel = d[0]
        elif self.packet.header_idx == 3:
            self.packet.sequence_number = d[0]

        self.packet.header_idx += 1


    def decode(self, frame: AnalyzerFrame):
        type = frame.type

        if type == 'start' and self.packet is None:
            self.packet = Packet(frame.start_time)
        elif type == 'start':
            self.packet.is_continuation_header = True
            self.packet.header_idx = 0
        elif (type == 'stop' or type == 'data') and self.packet is not None:
            if self.packet.length - 4 == len(self.packet.data):
                self.packet.end_time = frame.end_time

                f = AnalyzerFrame(
                    'packet',
                    self.packet.start_time,
                    self.packet.end_time,
                    {
                        'contents': self.packet.data,
                        'channel': self.packet.channel,
                        'sequence': self.packet.sequence_number,
                        'length': self.packet.length
                    },
                )
                p = self.packet

                self.packet = None

                return f, p 
        elif type != 'data':
            pass


        if self.packet is not None:
            if type == 'data':
                if self.packet.is_continuation_header:
                    self.packet.header_idx += 1

                    if self.packet.header_idx >= 4:
                        self.packet.is_continuation_header = False
                else:
                    d = frame.data['data']

                    if self.packet.header_idx < 4:
                        self.fill_header(d)
                    else:
                        # print(d)
                        self.packet.data.extend(d)
                        self.packet.start_times.append(frame.start_time)
                        self.packet.end_times.append(frame.end_time)

                
                

