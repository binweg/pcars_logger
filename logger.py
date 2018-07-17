import socket
import struct
import csv
from collections import namedtuple

ParticipantInfo = namedtuple('ParticipantInfo',
    ['current_lap_distance', 'current_lap'])

SessionState = namedtuple('SessionState',
    ['current_lap', 'current_lap_time', 'current_lap_invalid'])

def current_lap_is_invalid(race_state):
    return bool(race_state & 8)

def unpack_float(buffer):
    return struct.unpack('f', buffer)[0]

def unpack_participant_info(buffer):
    p_info = ParticipantInfo(
        current_lap_distance=int.from_bytes(buffer[6:8], byteorder='little'),
        current_lap=buffer[10],
    )
    return p_info

def is_new_lap(old_session_state, session_state):
    return (old_session_state.current_lap_time == -1.0 and session_state.current_lap_time > 0 \
        or session_state.current_lap == old_session_state.current_lap + 1)

def int_from_bytes(buffer):
    return int.from_bytes(buffer, byteorder='little')

pc_port = 5606

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(10)
sock.bind(('', pc_port))

data = b''
old_session_state = SessionState(current_lap=1, current_lap_time=-1, current_lap_invalid=True)
track_data_rows = []

with open('trackdata.csv', 'w', newline='') as track_file:
    writer = csv.writer(track_file)
    writer.writerow(['lap', 'pos', 'speed', 'throttle', 'brake', 'steering', 'gear'])
    while True:
        data = sock.recv(2048)
        if len(data) == 1367: #Telemetry
            game_state = data[3]
            race_state = data[10]
            current_lap_invalid = current_lap_is_invalid(race_state)
            current_lap_time = unpack_float(data[20:24])
            last_lap_time = unpack_float(data[16:20])
            participant_info = unpack_participant_info(data[464:464+16])
            brake = data[112]
            throttle = data[113]
            steering = data[115]
            if steering > 127:
                steering -= 256
            speed = unpack_float(data[120:124])
            rpm = int.from_bytes(data[124:126], byteorder='little')
            max_rpm = int.from_bytes(data[126:128], byteorder='little')
            gear = data[128] & 0x0f
            if gear > 8:
                gear -= 16

            session_state = SessionState(
                participant_info.current_lap,
                current_lap_time,
                current_lap_invalid)

            if is_new_lap(old_session_state, session_state):
                if not old_session_state.current_lap_invalid:
                    writer.writerows(track_data_rows)
                track_data_rows = []

            old_session_state = session_state

            if not current_lap_invalid:
                track_data_rows.append((
                    participant_info.current_lap,
                    participant_info.current_lap_distance,
                    speed,
                    throttle,
                    brake,
                    steering,
                    gear,
                ))
        if len(data) == 1347:
            pass
