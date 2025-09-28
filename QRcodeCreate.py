import os
import qrcode

# QR 코드 저장 폴더
save_dir = "qrcode"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)  # 폴더 생성

for i in range(1, 601):
    url = f"https://koko1324.github.io/2025forQRinfoPage/?id={i}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(os.path.join(save_dir, f"qr_{i}.png"))
    print("QR저장 완")
