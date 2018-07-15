import socket
import struct
from collections import namedtuple

ParticipantInfo = namedtuple('ParticipantInfo',
    ['current_lap_distance', 'current_lap'])

def current_lap_is_invalid(race_state_flags):
    return bool(race_state_flags & 8)

def unpack_float(buffer):
    return struct.unpack('f', buffer)

def unpack_participant_info(buffer):
    p_info = ParticipantInfo(
        current_lap_distance=int.from_bytes(buffer[6:8], byteorder='little'),
        current_lap=buffer[10],
    )
    return p_info


def int_from_bytes(byte_string):
    return int.from_bytes(byte_string, byteorder='little')

pc_port = 5606

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.settimeout(5)
sock.bind(('', pc_port))

data = b''
while True:
    data = sock.recv(2048)
    if len(data) == 1367: #Telemetry
        game_state = data[3]
        race_state_flags = data[10]
        lap_invalidated = current_lap_is_invalid(race_state_flags)
        current_lap_time = unpack_float(data[20:24])
        last_lap_time = unpack_float(data[16:20])
        participant_info = unpack_participant_info(data[464:464+16])
        brake = data[112]
        throttle = data[113]
        steering = data[115]
        speed = unpack_float(data[120:124])
        rpm = int.from_bytes(data[124:126], byteorder='little')
        max_rpm = int.from_bytes(data[126:128], byteorder='little')
        gear = data[128] & 0x0f

        print(lap_invalidated,
            participant_info.current_lap,
            participant_info.current_lap_distance,
            gear,
            rpm,
            steering,
            throttle,
            brake)
    if len(data) == 1347:
        pass

# int.from_bytes(data[470:472], byteorder='little')
# currentGameState.SessionData.IsNewLap = previousGameState == null || currentGameState.SessionData.CompletedLaps == previousGameState.SessionData.CompletedLaps + 1