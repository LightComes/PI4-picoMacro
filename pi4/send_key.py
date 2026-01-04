import serial
import time

# RPi4의 기본 시리얼 포트 열기
# (Pico 코드의 baudrate인 9600과 맞춰야 함)
ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.flush()

print("명령을 보냅니다...")

try:
    while True:
        cmd = input("명령 입력 (c:복사, v:붙여넣기): ")
        
        if cmd == 'c':
            ser.write(b'c') # 바이트 형태로 전송
            print("-> 'c' 전송 완료")
            
        elif cmd == 'v':
            ser.write(b'v')
            print("-> 'v' 전송 완료")
            
except KeyboardInterrupt:
    ser.close()
