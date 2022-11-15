from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting

from common import Packet, SHTPParser

class SHTPHla(HighLevelAnalyzer):
    result_types = {
        'packet': {
            'format': 'CH: {{data.channel}} SEQ: {{data.sequence}} DAT[{{data.length}}]: {{data.contents}}'
        }
    }


    def __init__(self):
        self.shtp_parser = SHTPParser()

    def decode(self, frame: AnalyzerFrame):
        f = self.shtp_parser.decode(frame)

        if f is not None:
            return f[0]

