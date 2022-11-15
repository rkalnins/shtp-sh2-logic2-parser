
from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting

from common import Packet, SHTPParser


GYRO_REPORT_ID = 0x02
GYRO_REPORT_LEN = 10

LIN_ACCEL_REPORT_ID = 0x04
LIN_ACCEL_REPORT_LEN = 10

ROTV_REPORT_ID = 0x05
ROTV_REPORT_LEN = 14

TIMEBASE_REPORT_ID = 0xFB
TIMEBASE_REPORT_LEN = 5

class Report:
    report_type: str
    start_time: float
    end_time: float
    report_id: int
    sequence: int
    status: int
    delay: int
    length: int

    byte_data: bytearray

    def __init__(self):
        self.byte_data = bytearray()

    def done(self):
        # convert to floats
        # get quaternions
        # etc.
        pass

class FixedInt16Data:
    lsb: int
    msb: int
    full: int
    q: int

    def __init__(self, q):
        self.q = q

    def getFloating(self):
        return 0.0

class GyroReport(Report):
    report_id = GYRO_REPORT_ID
    length = GYRO_REPORT_LEN
    report_type = 'gyro'

    x: FixedInt16Data
    y: FixedInt16Data
    z: FixedInt16Data

    def __init__(self):
        super().__init__()
        self.x = FixedInt16Data(9)
        self.y = FixedInt16Data(9)
        self.z = FixedInt16Data(9)

class LinAccelReport(Report):
    report_id = LIN_ACCEL_REPORT_ID
    length = GYRO_REPORT_LEN
    report_type = 'accel'

    x: FixedInt16Data
    y: FixedInt16Data
    z: FixedInt16Data
    
    def __init__(self):
        super().__init__()
        self.x = FixedInt16Data(8)
        self.y = FixedInt16Data(8)
        self.z = FixedInt16Data(8)

class RotVReport(Report):
    report_id = ROTV_REPORT_ID
    length = GYRO_REPORT_LEN
    report_type = 'rotv'
    
    i: FixedInt16Data
    j: FixedInt16Data
    k: FixedInt16Data
    real: FixedInt16Data
    accuracy: FixedInt16Data

    roll: float
    pitch: float
    yaw: float

    def __init__(self):
        super().__init__()
        self.i = FixedInt16Data(14)
        self.j = FixedInt16Data(14)
        self.k = FixedInt16Data(14)
        self.real = FixedInt16Data(14)
        self.accuracy = FixedInt16Data(12)

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

class TimebaseReport(Report):
    report_id = TIMEBASE_REPORT_ID
    length = TIMEBASE_REPORT_LEN
    report_type = 'tbase'

    delta: int

    def __init__(self):
        self.delta = 0
        super().__init__()


class SH2Hla(HighLevelAnalyzer):
    result_types = {
        'packet': {
            'format': 'CH: {{data.channel}} SEQ: {{data.sequence}} DAT[{{data.length}}]: {{data.contents}}'
        },
        'tbase': {
            'format': 'delta = {{data.delta}}',
        },
        'accel': {
            'format': '[x,y,z] = [{{data.x}} {{data.y}} {{data.z}}]',
        },
        'gyro': {
            'format': '[x,y,z] = [{{data.x}} {{data.y}} {{data.z}}]',
        },
        'rotv': {
            'format': '[r,p,y,a] = [{{data.roll}} {{data.pitch}} {{data.yaw}} {{data.accuracy}}]',
        },
    }

    def __init__(self):
        self.shtp_parser = SHTPParser()
        self.current_report = None

    def execute_parser_step(self, new_data, start_time, end_time):
        if self.current_report is None:
            if new_data == GYRO_REPORT_ID:
                self.current_report = GyroReport()
            elif new_data == LIN_ACCEL_REPORT_ID:
                self.current_report = LinAccelReport()
            elif new_data == ROTV_REPORT_ID:
                self.current_report = RotVReport()
            elif new_data == TIMEBASE_REPORT_ID:
                self.current_report = TimebaseReport()
            else:
                return False

            self.current_report.start_time = start_time
            return False
        else:
            self.current_report.byte_data.extend(new_data.to_bytes(1, 'big'))

            if self.current_report.length - 1 == len(self.current_report.byte_data):
                self.current_report.end_time = end_time
                print('done', self.current_report.report_type, self.current_report.byte_data)
                return True
            else:
                return False

    def parse_sh2(self, frame: AnalyzerFrame, p):
        frames = []

        for i in range(len(p.data)):
            is_done = self.execute_parser_step(p.data[i], p.start_times[i], p.end_times[i])

            if is_done:
                data = dict()
                if self.current_report.report_type == 'gyro' or self.current_report.report_type == 'accel':

                    data['x'] = self.current_report.x.getFloating() 
                    data['y'] = self.current_report.x.getFloating() 
                    data['z'] = self.current_report.x.getFloating() 
                elif self.current_report.report_type == 'rotv':
                    data['roll'] = self.current_report.roll
                    data['pitch'] = self.current_report.pitch
                    data['yaw'] = self.current_report.yaw
                elif self.current_report.report_type == 'tbase':
                    data['delta'] = self.current_report.delta

                f = AnalyzerFrame(
                        self.current_report.report_type,
                        self.current_report.start_time,
                        self.current_report.end_time,
                        data
                )

                self.current_report = None
                        
                frames.append(f)


        return None

    def decode(self, frame: AnalyzerFrame):
        fp = self.shtp_parser.decode(frame)
        print(fp)

        if fp is not None:
            return self.parse_sh2(fp[0], fp[1])

        return fp


