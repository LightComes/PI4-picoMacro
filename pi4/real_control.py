import serial
import time

# UART 설정
ser = serial.Serial('/dev/serial0', 9600)

# HID 키코드 맵 (자주 쓰는 것만 정의)
HID_CODES = {
    'a': 4, 'b': 5, 'c': 6, 'd': 7, 'e': 8, 'f': 9, 'g': 10, 'h': 11,
    'i': 12, 'j': 13, 'k': 14, 'l': 15, 'm': 16, 'n': 17, 'o': 18,
    'p': 19, 'q': 20, 'r': 21, 's': 22, 't': 23, 'u': 24, 'v': 25,
    'w': 26, 'x': 27, 'y': 28, 'z': 29,
    '1': 30, '2': 31, '3': 32, '4': 33, '5': 34,
    'enter': 40, 'esc': 41, 'backspace': 42, 'tab': 43, 'space': 44,
    'ctrl': 224, 'shift': 225, 'alt': 226, 'win': 227
}

def send_key(action, key_name):
    """
    action: 1 (누름), 0 (뗌)
    key_name: 'a', 'space', 'ctrl' 등
    """
    if key_name not in HID_CODES:
        print(f"알 수 없는 키: {key_name}")
        return

    keycode = HID_CODES[key_name]
    command = f"{action},{keycode}\n"
    ser.write(command.encode())
    print(f">> 전송: {command.strip()} ({'누름' if action==1 else '뗌'} - {key_name})")

try:
    print("=== 리얼 키보드 테스트 ===")
    
    # [시나리오 1] 'a'를 3초간 꾹 누르기 (게임 이동처럼)
    print("1. 'a' 키를 3초간 꾹 누릅니다...")
    send_key(1, 'a')  # 누름 상태 시작
    time.sleep(3)     # 3초 유지 (이때 메모장에 aaaaa... 찍힘)
    send_key(0, 'a')  # 뗌
    print("-> 끝\n")
    time.sleep(1)

    # [시나리오 2] 복사 단축키 (Ctrl 누른채로 + c)
    print("2. Ctrl + A (전체선택) 시도...")
    send_key(1, 'ctrl') # Ctrl 누름 (유지)
    time.sleep(0.1)
    send_key(1, 'a')    # A 누름 (Ctrl+A 상태)
    time.sleep(0.1)
    send_key(0, 'a')    # A 뗌
    send_key(0, 'ctrl') # Ctrl 뗌
    print("-> 끝\n")
    
    # [시나리오 3] 3개 키 동시 입력 (예: Ctrl + Shift + ESC)
    print("3. Ctrl + Shift + ESC (작업관리자)...")
    send_key(1, 'ctrl')
    send_key(1, 'shift')
    send_key(1, 'esc')
    time.sleep(0.2)
    # 뗄 때는 순서 상관 없지만 안전하게 역순으로
    send_key(0, 'esc')
    send_key(0, 'shift')
    send_key(0, 'ctrl')
    print("-> 끝")

except KeyboardInterrupt:
    # 종료 시 혹시 눌려있는 키가 있다면 모두 해제
    ser.write(b"9,0\n") 
    ser.close()
