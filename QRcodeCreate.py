import qrcode
import os

# 저장 폴더 생성
output_dir = "qrcodes"
os.makedirs(output_dir, exist_ok=True)

# 1~600까지 고유 숫자 QR코드 생성
for i in range(1, 601):
    qr = qrcode.QRCode(
        version=1,  # QR 코드 크기 (1이 제일 작음, 자동으로 늘어남)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 오류 보정 (높음)
        box_size=10,
        border=4,
    )
    qr.add_data(str(i))  # 고유 숫자 입력
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(os.path.join(output_dir, f"qr_{i}.png"))

print("QR코드 600개 생성 완료!")


import qrcode

for i in range(1, 601):
    # URL은 나중에 안내 페이지로 바꿀 수 있음
    url = f"http://localhost:5000/scan?id={i}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(os.path.join("qrcodes", f"qr_{i}.png"))