import cv2
from pyzbar import pyzbar

recognized_ids = set()  # 인식된 고유 번호 저장 (중복 방지)

# 카메라 열기 (0번 카메라)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # QR 코드 탐지
    barcodes = pyzbar.decode(frame)
    for barcode in barcodes:
        data = barcode.data.decode("utf-8")  # QR코드 안에 있는 데이터 (숫자)
        if data.isdigit():  # 숫자인 경우만
            recognized_ids.add(int(data))

        # QR코드 영역 표시
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"ID: {data}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 현재 인원수 표시
    cv2.putText(frame, f"Count: {len(recognized_ids)}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("QR Scanner", frame)

    # q 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# 최종 결과 출력
print("인식된 고유 번호 목록:", recognized_ids)
print("총 인원 수:", len(recognized_ids))
