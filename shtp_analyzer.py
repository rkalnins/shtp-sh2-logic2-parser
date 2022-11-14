# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting

class Packet:
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
        self.length = 0xFFFF
        self.header_idx = 0
        self.sequence_number = 0xFF
        self.channel = 0xFF
        self.start_time = start_time
        self.data = bytearray()

class SHTPHla(HighLevelAnalyzer):
    result_types = {
        'packet': {
            'format': 'CH: {{data.channel}} SEQ: {{data.sequence}} DAT[{{data.length}}]: {{data.contents}}'
        }
    }

    def fill_header(self, d):
        if self.packet.header_idx == 0:
            self.packet.length_lsb = d[0]
        elif self.packet.header_idx == 1:
            self.packet.length_msb = d[0]
            length = self.packet.length_lsb | (self.packet.length_msb << 8)
            length = length & 0x7FFF

            print("len: ", length)
            print("lsb: ", self.packet.length_lsb)
            print("msb: ", self.packet.length_msb)


            self.packet.length = length
        elif self.packet.header_idx == 2:
            self.packet.channel = d[0]
        elif self.packet.header_idx == 3:
            self.packet.sequence_number = d[0]

        self.packet.header_idx += 1

    def __init__(self):
        self.packet = None

        pass

    def decode(self, frame: AnalyzerFrame):
        type = frame.type

        if type == 'start' and self.packet is None:
            self.packet = Packet(frame.start_time)
        elif (type == 'stop' or type == 'data') and self.packet is not None:
            if self.packet.length == len(self.packet.data):
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

                self.packet = None

                return f
        elif type != 'data':
            print("not enough length")


        if self.packet is not None:
            if type == 'data':
                d = frame.data['data']

                if self.packet.header_idx < 4:
                    self.fill_header(d)
                else:
                    # print(d)
                    self.packet.data.extend(d)

                    print(len(self.packet.data), d)

                
                

