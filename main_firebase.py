import cv2
from pyzbar.pyzbar import decode
import time
import re
import threading
import firebase_admin
from firebase_admin import credentials, firestore
from PIL import ImageFont, ImageDraw, Image
import numpy as np

# ------------------------------
# Firebase 초기화
# ------------------------------
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

total_ref = db.collection("attendance").document("total")
scanned_ref = db.collection("attendance").document("scanned_ids")

# ------------------------------
# Firestore 헬퍼 함수
# ------------------------------
def get_total_count():
    doc = total_ref.get()
    if doc.exists:
        return doc.to_dict().get("count", 0)
    return 0

def increment_if_new(user_id):
    """Firestore 업데이트 (별도 스레드에서 실행)"""
    def worker():
        scanned_doc = scanned_ref.get()
        scanned_ids = scanned_doc.to_dict() if scanned_doc.exists else {}

        str_id = str(user_id)
        if str_id in scanned_ids:
            print(f"⚠️ 이미 인식된 ID입니다: {str_id}")
            return

        scanned_ref.set({str_id: True}, merge=True)
        total_doc = total_ref.get()
        current_count = total_doc.to_dict().get("count", 0) if total_doc.exists else 0
        new_count = current_count + 1
        total_ref.set({"count": new_count}, merge=True)

        print(f"✅ Firestore 업데이트 완료: 현재 누적 인원 = {new_count}명")

    threading.Thread(target=worker, daemon=True).start()

# ------------------------------
# QR 관련 함수
# ------------------------------
def extract_id_from_url(qr_data):
    match = re.search(r"id=(\d+)", qr_data)
    return int(match.group(1)) if match else None

# ✅ 카메라 초기화 함수 (재시작용)
def open_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 인덱스 0 기본 / 윈도우용 안정화
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print("❌ 카메라 열기 실패. 1초 후 재시도...")
        time.sleep(1)
        return open_camera()
    print("📷 카메라 연결 완료.")
    return cap

def scan_qr():
    global doc_watch
    try:
        doc_watch.unsubscribe()  # 실시간 리스너 일시 해제
    except Exception:
        pass

    cap = open_camera()
    print("QR코드를 카메라에 보여주세요... (종료: q)")

    last_code = None
    last_time = 0
    detected_time = 0
    failure_count = 0

    fontpath = "C:/Windows/Fonts/malgunbd.ttf"
    font = ImageFont.truetype(fontpath, 40)

    while True:
        ret, frame = cap.read()

        if not ret:
            failure_count += 1
            print(f"⚠️ 프레임 읽기 실패 ({failure_count}회)")
            time.sleep(0.3)

            if failure_count >= 10:
                print("🔄 카메라 재연결 중...")
                cap.release()
                time.sleep(1)
                cap = open_camera()
                failure_count = 0
            continue
        else:
            failure_count = 0

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        qr_codes = decode(gray)

        for qr in qr_codes:
            qr_data = qr.data.decode("utf-8")
            if qr_data != last_code or time.time() - last_time > 1:
                print(f"QR 코드 인식: {qr_data}")
                user_id = extract_id_from_url(qr_data)
                if user_id:
                    increment_if_new(user_id)
                    detected_time = time.time()
                else:
                    print("❌ QR 코드에서 ID를 추출할 수 없습니다.")
                last_code = qr_data
                last_time = time.time()

        # ✅ '감지됨!' 표시 (1초 유지)
        if time.time() - detected_time < 1:
            frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(frame_pil)
            draw.text((230, 30), "감지됨!", font=font, fill=(0, 255, 0))
            frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

        cv2.imshow("QR Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    # 스캔이 끝나면 리스너 재등록
    doc_watch = total_ref.on_snapshot(on_snapshot)

# ------------------------------
# Firestore 실시간 동기화
# ------------------------------
def get_attendance():
    total = get_total_count()
    print(f"현재 누적 인원: {total}명")

def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        data = doc.to_dict()
        print(f"🔄 [실시간 갱신] 현재 누적 인원: {data.get('count', 0)}명")

doc_watch = total_ref.on_snapshot(on_snapshot)

# ------------------------------
# 메인 루프
# ------------------------------
if __name__ == "__main__":
    while True:
        cmd = input("명령어 입력 (scan / get / exit): ").strip().lower()
        if cmd == "scan":
            scan_qr()
        elif cmd == "get":
            get_attendance()
        elif cmd == "exit":
            try:
                doc_watch.unsubscribe()
            except Exception:
                pass
            break
        else:
            print("명령어는 scan, get, exit 중 하나를 입력하세요.")
