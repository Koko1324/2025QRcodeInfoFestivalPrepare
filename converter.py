import pandas as pd

# 1. CSV 파일 읽기
# 파일 이름은 실제 파일명과 동일해야 합니다.
try:
    df = pd.read_csv('색상표_확정1500.csv')
except FileNotFoundError:
    print("오류: '색상표_확정1500.xlsx - RGB 1500 Palette.csv' 파일을 찾을 수 없습니다.")
    print("스크립트와 CSV 파일이 같은 폴더에 있는지 확인하세요.")
    exit()

# 2. JavaScript 객체 문자열 생성 시작
# f-string을 사용하여 문자열을 효율적으로 조합합니다.
js_object_lines = ["const colorPalette = {"]

# 3. DataFrame의 각 행을 순회하며 변환
for index, row in df.iterrows():
    # 각 행에서 ID, R, G, B 값을 가져옵니다.
    color_id = int(row['ID'])
    r = int(row['R'])
    g = int(row['G'])
    b = int(row['B'])
    
    # 'ID: "rgb(R,G,B)",' 형태의 문자열을 만듭니다.
    line = f'    {color_id}: "rgb({r},{g},{b})",'
    js_object_lines.append(line)

# 마지막 라인의 쉼표(,)를 제거합니다.
if len(js_object_lines) > 1:
    js_object_lines[-1] = js_object_lines[-1].rstrip(',')

# 4. JavaScript 객체 문자열 마무리
js_object_lines.append("};")

# 5. 최종 결과 출력
# join을 사용하여 리스트의 모든 라인을 하나의 문자열로 합칩니다.
final_output = "\n".join(js_object_lines)
print(final_output)

# (선택 사항) 결과를 파일로 저장하고 싶을 경우
with open('color_palette.js', 'w', encoding='utf-8') as f:
    f.write(final_output)
    print("\n'color_palette.js' 파일로 저장되었습니다.")