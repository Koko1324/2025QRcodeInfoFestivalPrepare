import cv2
import json
from pyzbar.pyzbar import decode

# JSON 파일 경로
JSON_FILE = "attendance.json"

# JSON 파일 초기화 (없으면 새로 생성)
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"scanned_ids": []}

# 웹캠 시작
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # QR코드 인식
    decoded_objects = decode(frame)
    for obj in decoded_objects:
        qr_data = obj.data.decode("utf-8")

        # 중복 방지
        if qr_data not in data["scanned_ids"]:
            data["scanned_ids"].append(qr_data)

            # JSON 파일 실시간 저장
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            # 현재 인원수 출력
            print(f"새로운 QR 코드 감지됨: {qr_data}")
            print(f"현재 인원수: {len(data['scanned_ids'])}명")

    # 화면에 현재 인원수 표시
    cv2.putText(frame,
                f"Total: {len(data['scanned_ids'])} people",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2)

    cv2.imshow("QR Scanner", frame)

    # ESC키 누르면 종료
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
