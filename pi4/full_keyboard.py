import sys
import serial
import evdev
from evdev import ecodes
# gpio 버튼
from gpiozero import Button
from signal import pause

#환경 변수
button = Button(17, bounce_time=0.1)

# 이벤트 핸들러 등록
def on_press():
    print(">>> 스위치 ON (눌러짐!)")

def on_release():
    print(">>> 스위치 OFF (떼어짐)")

button.when_pressed = on_press
button.when_released = on_release



# === 1. UART 연결 설정 ===
try:
    ser = serial.Serial('/dev/serial0', 9600)
    print("✅ UART 포트 연결 성공")
except Exception as e:
    print(f"❌ UART 에러: {e}")
    sys.exit(1)

# === 2. 진짜 키보드 자동 찾기 ===
def pick_keyboard():
    print("\n🔍 키보드 장치 검색 중...")
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    
    real_keyboards = []
    for dev in devices:
        # 키 기능이 있고, 'A'키나 'ENTER'키를 가진 놈만 진짜로 인정
        cap = dev.capabilities()
        if ecodes.EV_KEY in cap:
            supported_keys = cap[ecodes.EV_KEY]
            if ecodes.KEY_A in supported_keys or ecodes.KEY_ENTER in supported_keys:
                print(f"  - [후보] {dev.name} ({dev.path})")
                real_keyboards.append(dev)

    if not real_keyboards:
        print("❌ 키보드를 찾을 수 없습니다!")
        return None
    
    # 후보 중 첫 번째 장치 선택
    target = real_keyboards[2]
    print(f"🎯 [최종 선택] {target.name} ({target.path})")
    return target

dev = pick_keyboard()
if not dev:
    sys.exit(1)

# === 3. 전체 키 매핑 (Linux Code -> HID Code) ===
KEY_MAPPING = {
    # --- 알파벳 ---
    ecodes.KEY_A: 4, ecodes.KEY_B: 5, ecodes.KEY_C: 6, ecodes.KEY_D: 7,
    ecodes.KEY_E: 8, ecodes.KEY_F: 9, ecodes.KEY_G: 10, ecodes.KEY_H: 11,
    ecodes.KEY_I: 12, ecodes.KEY_J: 13, ecodes.KEY_K: 14, ecodes.KEY_L: 15,
    ecodes.KEY_M: 16, ecodes.KEY_N: 17, ecodes.KEY_O: 18, ecodes.KEY_P: 19,
    ecodes.KEY_Q: 20, ecodes.KEY_R: 21, ecodes.KEY_S: 22, ecodes.KEY_T: 23,
    ecodes.KEY_U: 24, ecodes.KEY_V: 25, ecodes.KEY_W: 26, ecodes.KEY_X: 27,
    ecodes.KEY_Y: 28, ecodes.KEY_Z: 29,

    # --- 숫자 ---
    ecodes.KEY_1: 30, ecodes.KEY_2: 31, ecodes.KEY_3: 32, ecodes.KEY_4: 33,
    ecodes.KEY_5: 34, ecodes.KEY_6: 35, ecodes.KEY_7: 36, ecodes.KEY_8: 37,
    ecodes.KEY_9: 38, ecodes.KEY_0: 39,

    # --- 기능키 ---
    ecodes.KEY_F1: 58, ecodes.KEY_F2: 59, ecodes.KEY_F3: 60, ecodes.KEY_F4: 61,
    ecodes.KEY_F5: 62, ecodes.KEY_F6: 63, ecodes.KEY_F7: 64, ecodes.KEY_F8: 65,
    ecodes.KEY_F9: 66, ecodes.KEY_F10: 67, ecodes.KEY_F11: 68, ecodes.KEY_F12: 69,

    # --- 특수키 & 편집키 ---
    ecodes.KEY_ENTER: 40, ecodes.KEY_ESC: 41, ecodes.KEY_BACKSPACE: 42,
    ecodes.KEY_TAB: 43, ecodes.KEY_SPACE: 44, ecodes.KEY_MINUS: 45,
    ecodes.KEY_EQUAL: 46, ecodes.KEY_LEFTBRACE: 47, ecodes.KEY_RIGHTBRACE: 48,
    ecodes.KEY_BACKSLASH: 49, ecodes.KEY_SEMICOLON: 51, ecodes.KEY_APOSTROPHE: 52,
    ecodes.KEY_GRAVE: 53, ecodes.KEY_COMMA: 54, ecodes.KEY_DOT: 55, ecodes.KEY_SLASH: 56,
    ecodes.KEY_CAPSLOCK: 57,

    ecodes.KEY_SYSRQ: 70, ecodes.KEY_SCROLLLOCK: 71, ecodes.KEY_PAUSE: 72,
    ecodes.KEY_INSERT: 73, ecodes.KEY_HOME: 74, ecodes.KEY_PAGEUP: 75,
    ecodes.KEY_DELETE: 76, ecodes.KEY_END: 77, ecodes.KEY_PAGEDOWN: 78,
    ecodes.KEY_RIGHT: 79, ecodes.KEY_LEFT: 80, ecodes.KEY_DOWN: 81, ecodes.KEY_UP: 82,

    # --- 텐키 (NumPad) ---
    ecodes.KEY_NUMLOCK: 83, ecodes.KEY_KPSLASH: 84, ecodes.KEY_KPASTERISK: 85,
    ecodes.KEY_KPMINUS: 86, ecodes.KEY_KPPLUS: 87, ecodes.KEY_KPENTER: 88,
    ecodes.KEY_KP1: 89, ecodes.KEY_KP2: 90, ecodes.KEY_KP3: 91,
    ecodes.KEY_KP4: 92, ecodes.KEY_KP5: 93, ecodes.KEY_KP6: 94,
    ecodes.KEY_KP7: 95, ecodes.KEY_KP8: 96, ecodes.KEY_KP9: 97,
    ecodes.KEY_KP0: 98, ecodes.KEY_KPDOT: 99,

    # --- 수정자 (Modifiers) ---
    ecodes.KEY_LEFTCTRL: 224, ecodes.KEY_LEFTSHIFT: 225, ecodes.KEY_LEFTALT: 226,
    ecodes.KEY_LEFTMETA: 227, 
    ecodes.KEY_RIGHTCTRL: 228, ecodes.KEY_RIGHTSHIFT: 229, ecodes.KEY_RIGHTALT: 230,
    ecodes.KEY_RIGHTMETA: 231,

    # --- [수정됨] 한국 키보드 전용 키 (숫자로 직접 지정) ---
    # 한영키(122) -> 오른쪽 Alt(230)
    122: 230,
    # 한자키(123) -> 오른쪽 Ctrl(228)
    123: 228,
    # 일본어/기타 키 (에러 방지용 숫자 처리)
    124: 137, # YEN
    89: 135,  # RO
    90: 136,  # KATAKANA
    92: 138,  # HENKAN
    94: 139,  # MUHENKAN
}

print("🚀 전체 키 입력 전송 시작... (종료: Ctrl+C)")

# === 4. 이벤트 루프 ===
try:
    # dev.grab() # 필요 시 주석 해제 (RPi4 자체 입력을 막음)
    
    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            # 0(뗌), 1(누름) 상태만 전송 (2는 반복 입력이라 무시)
            if event.value in [0, 1]: 
                if event.code in KEY_MAPPING:
                    hid_code = KEY_MAPPING[event.code]
                    msg = f"{event.value},{hid_code}\n"
                    ser.write(msg.encode())
                else:
                    # 매핑 안 된 키가 있으면 알려줌 (추가 필요 시 확인용)
                    print(f"⚠️ 매핑 없음: {event.code}")

except OSError:
    print("\n❌ 장치 연결이 끊어졌습니다.")
except KeyboardInterrupt:
    print("\n👋 종료합니다.")
    ser.write(b"9,0\n") # 종료 시 키 떼기
    ser.close()
