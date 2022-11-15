
from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting

from common import Packet, SHTPParser


class SH2Hla(HighLevelAnalyzer):
    result_types = {
        'accel': {
            'format': '[x,y,z] = [{{data.x}} {{data.y}} {{data.z}}]',
        },
        'gyro': {
            'format': '[x,y,z] = [{{data.x}} {{data.y}} {{data.z}}]',
        },
        'rotv': {
            'format': '[r,p,y,a] = [{{data.x}} {{data.y}} {{data.z}} {{data.accuracy}}]',
        },
    }

    def __init__(self):
        self.shtp_parser = SHTPParser()
        self.packet = None
        self.reports = None

    def decode(self, frame: AnalyzerFrame):
        return self.shtp_parser.decode(frame)

