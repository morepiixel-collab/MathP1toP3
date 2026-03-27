import streamlit as st
import streamlit.components.v1 as components
import random
import math
import zipfile
import io
import time

# ==========================================
# ⚙️ ตรวจสอบไลบรารี pdfkit
# ==========================================
try:
    import pdfkit
    HAS_PDFKIT = True
except ImportError:
    HAS_PDFKIT = False

# ==========================================
# ตั้งค่าหน้าเพจ Web App & Professional CSS
# ==========================================
st.set_page_config(page_title="Math Generator - Primary 1-3", page_icon="🧸", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }
    div[data-testid="stSidebar"] div.stButton > button { background-color: #27ae60; color: white; border-radius: 8px; height: 3.5rem; font-size: 18px; font-weight: bold; border: none; box-shadow: 0 4px 6px rgba(39,174,96,0.3); }
    div[data-testid="stSidebar"] div.stButton > button:hover { background-color: #219653; box-shadow: 0 6px 12px rgba(39,174,96,0.4); }
    .main-header { background: linear-gradient(135deg, #f39c12, #d35400); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; box-shadow: 0 10px 20px rgba(0,0,0,0.15); }
    .main-header h1 { margin: 0; font-size: 2.8rem; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); }
    .main-header p { margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🧸 Math Worksheet Pro <span style="font-size: 20px; background: #2c3e50; color: #fff; padding: 5px 15px; border-radius: 20px; vertical-align: middle;">ประถมต้น ป.1 - ป.3</span></h1>
    <p>ระบบสร้างสื่อการสอนคณิตศาสตร์พื้นฐาน พร้อมภาพประกอบและเฉลยละเอียด</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 1. คลังคำศัพท์และฟังก์ชันตัวช่วย
# ==========================================
NAMES = ["อคิณ", "นาวิน", "ภูผา", "สายฟ้า", "ข้าวหอม", "ใบบัว", "มะลิ", "น้ำใส", "ไออุ่น"]
PLACE_EMOJIS = {"บ้าน": "🏠", "โรงเรียน": "🏫", "ตลาด": "🛒", "สวนสาธารณะ": "🌳", "โรงพยาบาล": "🏥"}
FRUIT_EMOJIS = {"แอปเปิล": "🍎", "ส้ม": "🍊", "สตรอว์เบอร์รี": "🍓", "กล้วย": "🍌", "มะม่วง": "🥭"}
ROOMS = ["ห้องนอน", "ห้องนั่งเล่น", "ห้องเรียน", "ห้องสมุด"]
FURNITURE = ["ตู้เสื้อผ้า", "โต๊ะทำงาน", "เตียงนอน", "ชั้นวางหนังสือ"]

def f_html(n, d, c="#2c3e50", b=True):
    w = "bold" if b else "normal"
    return f"<span style='display:inline-flex; flex-direction:column; vertical-align:middle; text-align:center; line-height:1.4; margin:0 4px;'><span style='border-bottom:2px solid {c}; padding:0 4px; font-weight:{w}; color:{c};'>{n}</span><span style='padding:0 4px; font-weight:{w}; color:{c};'>{d}</span></span>"

def generate_vertical_table_html(a, b, op, result="", is_key=False):
    a_str, b_str = f"{a:,}", f"{b:,}"
    res_str = f"{result:,}" if result != "" else ""
    ans_val = res_str if is_key else ""
    border_ans = "border-bottom: 4px double #000;" if is_key else ""
    return f"""<div style='margin-left: 60px; display: block; font-family: "Sarabun", sans-serif; font-size: 26px; margin-top: 15px; margin-bottom: 15px;'>
        <table style='border-collapse: collapse; text-align: right;'>
            <tr><td style='padding: 0 10px 0 0; border: none;'>{a_str}</td><td rowspan='2' style='vertical-align: middle; text-align: left; padding: 0 0 0 15px; font-size: 28px; font-weight: bold; border: none;'>{op}</td></tr>
            <tr><td style='padding: 5px 10px 5px 0; border: none; border-bottom: 2px solid #000;'>{b_str}</td></tr>
            <tr><td style='padding: 5px 10px 0 0; border: none; {border_ans} height: 35px;'>{ans_val}</td><td style='border: none;'></td></tr>
        </table></div>"""

def generate_unit_math_html(u_maj, u_min, v1_maj, v1_min, v2_maj, v2_min, op, multiplier):
    if op == "+":
        raw_min, raw_maj = v1_min + v2_min, v1_maj + v2_maj
        carry, fin_min = raw_min // multiplier, raw_min % multiplier
        fin_maj = raw_maj + carry
        html = f"<div style='margin-left: 40px;'><table style='text-align: center; border-collapse: collapse; font-size: 22px; font-family: Sarabun; margin: 10px 0;'>"
        html += f"<tr style='border-bottom: 2px solid #333; font-weight: bold; color: #2c3e50;'><td style='padding: 5px 25px;'>{u_maj}</td><td style='padding: 5px 25px;'>{u_min}</td><td></td></tr>"
        html += f"<tr><td style='padding: 5px;'>{v1_maj:,}</td><td>{v1_min:,}</td><td></td></tr>"
        html += f"<tr><td style='padding: 5px; border-bottom: 2px solid #333;'>{v2_maj:,}</td><td style='border-bottom: 2px solid #333;'>{v2_min:,}</td><td style='font-weight:bold; font-size:26px; padding-left:15px;'>{op}</td></tr>"
        if carry > 0:
            html += f"<tr><td style='padding: 5px;'>{raw_maj:,}</td><td>{raw_min:,}</td><td></td></tr>"
            html += f"<tr style='font-weight: bold; color: #c0392b;'><td style='padding: 5px; border-bottom: 4px double #333;'>{fin_maj:,}</td><td style='border-bottom: 4px double #333;'>{fin_min:,}</td><td style='font-size: 16px; text-align: left; padding-left: 10px;'>(ทด {carry} {u_maj})</td></tr>"
        else:
            html += f"<tr style='font-weight: bold; color: #c0392b;'><td style='padding: 5px; border-bottom: 4px double #333;'>{fin_maj:,}</td><td style='border-bottom: 4px double #333;'>{fin_min:,}</td><td></td></tr>"
        html += "</table></div>"
        ans_str = f"{fin_maj:,} {u_maj} {fin_min:,} {u_min}" if fin_min > 0 else f"{fin_maj:,} {u_maj}"
        return html, ans_str
    else: 
        is_borrow = v1_min < v2_min
        c_v1_maj, c_v1_min = (v1_maj - 1, v1_min + multiplier) if is_borrow else (v1_maj, v1_min)
        fin_maj, fin_min = c_v1_maj - v2_maj, c_v1_min - v2_min
        html = f"<div style='margin-left: 40px;'><table style='text-align: center; border-collapse: collapse; font-size: 22px; font-family: Sarabun; margin: 10px 0;'>"
        html += f"<tr style='border-bottom: 2px solid #333; font-weight: bold; color: #2c3e50;'><td style='padding: 5px 25px;'>{u_maj}</td><td style='padding: 5px 25px;'>{u_min}</td><td></td></tr>"
        if is_borrow:
            html += f"<tr style='color: #e74c3c; font-size: 18px; font-weight: bold;'><td>{c_v1_maj:,}</td><td>{c_v1_min:,}</td><td></td></tr>"
            html += f"<tr><td style='padding: 5px; text-decoration: line-through;'>{v1_maj:,}</td><td style='text-decoration: line-through;'>{v1_min:,}</td><td></td></tr>"
        else:
            html += f"<tr><td style='padding: 5px;'>{v1_maj:,}</td><td>{v1_min:,}</td><td></td></tr>"
        html += f"<tr><td style='padding: 5px; border-bottom: 2px solid #333;'>{v2_maj:,}</td><td style='border-bottom: 2px solid #333;'>{v2_min:,}</td><td style='font-weight:bold; font-size:26px; padding-left:15px;'>{op}</td></tr>"
        html += f"<tr style='font-weight: bold; color: #c0392b;'><td style='padding: 5px; border-bottom: 4px double #333;'>{fin_maj:,}</td><td style='border-bottom: 4px double #333;'>{fin_min:,}</td><td></td></tr>"
        html += "</table></div>"
        ans_str = f"{fin_maj:,} {u_maj} {fin_min:,} {u_min}" if fin_min > 0 else f"{fin_maj:,} {u_maj}"
        if fin_maj <= 0: ans_str = f"{fin_min:,} {u_min}"
        return html, ans_str

def generate_long_division_step_by_step_html(divisor, dividend, equation_html, is_key=False):
    div_str = str(dividend)
    div_len = len(div_str)
    if not is_key:
        ans_tds_list = [f'<td style="width: 35px; height: 45px;"></td>' for _ in div_str] + ['<td style="width: 35px;"></td>']
        div_tds_list = []
        for i, c in enumerate(div_str):
            left_border = "border-left: 3px solid #000;" if i == 0 else ""
            div_tds_list.append(f'<td style="width: 35px; text-align: center; border-top: 3px solid #000; {left_border} font-size: 38px; height: 50px; vertical-align: bottom;">{c}</td>')
        div_tds_list.append('<td style="width: 35px;"></td>')
        empty_rows = ""
        for _ in range(div_len + 1): 
            empty_rows += f"<tr><td style='border: none;'></td>"
            for _ in range(div_len + 1): empty_rows += f"<td style='width: 35px; height: 45px;'></td>"
            empty_rows += "</tr>"
        return f"{equation_html}<div style=\"display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;\"><div style=\"display: inline-block; font-family: 'Sarabun', sans-serif; line-height: 1.2;\"><table style=\"border-collapse: collapse;\"><tr><td style=\"border: none;\"></td>{''.join(ans_tds_list)}</tr><tr><td style=\"border: none; text-align: right; padding-right: 12px; vertical-align: bottom; font-size: 38px;\">{divisor}</td>{''.join(div_tds_list)}</tr>{empty_rows}</table></div></div>"
    
    steps, current_val_str, ans_str, has_started = [], "", "", False
    for i, digit in enumerate(div_str):
        current_val_str += digit
        current_val = int(current_val_str)
        q = current_val // divisor
        mul_res = q * divisor
        rem = current_val - mul_res
        if not has_started and q == 0 and i < len(div_str) - 1:
             current_val_str = str(rem) if rem != 0 else ""
             continue
        has_started = True
        ans_str += str(q)
        steps.append({'mul_res': mul_res, 'rem': rem, 'col_index': i})
        current_val_str = str(rem) if rem != 0 else ""
        
    ans_padded = ans_str.rjust(div_len, " ")
    ans_tds_list = [f'<td style="width: 35px; text-align: center; color: red; font-weight: bold; font-size: 38px;">{c.strip()}</td>' for c in ans_padded] + ['<td style="width: 35px;"></td>']
    div_tds_list = [f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; border-top: 3px solid #000; {"border-left: 3px solid #000;" if i == 0 else ""} font-size: 38px;">{c}</td>' for i, c in enumerate(div_str)] + ['<td style="width: 35px;"></td>']
    
    html = f"{equation_html}<div style=\"display: block; margin-left: 60px; margin-top: 15px; margin-bottom: 15px;\"><div style=\"display: inline-block; font-family: 'Sarabun', sans-serif; line-height: 1.2;\"><table style=\"border-collapse: collapse;\"><tr><td style=\"border: none;\"></td>{''.join(ans_tds_list)}</tr><tr><td style=\"border: none; text-align: right; padding-right: 12px; vertical-align: bottom; font-size: 38px;\">{divisor}</td>{''.join(div_tds_list)}</tr>"
    
    for idx, step in enumerate(steps):
        mul_res_str = str(step['mul_res'])
        pad_len = step['col_index'] + 1 - len(mul_res_str)
        mul_tds = ""
        for i in range(div_len + 1):
            if i >= pad_len and i <= step['col_index']:
                border_b = "border-bottom: 2px solid #000;" if i <= step['col_index'] else ""
                mul_tds += f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; font-size: 38px; {border_b}">{mul_res_str[i - pad_len]}</td>'
            elif i == step['col_index'] + 1: mul_tds += '<td style="width: 35px; text-align: center; font-size: 38px; color: #333; position: relative; top: -24px;">-</td>'
            else: mul_tds += '<td style="width: 35px;"></td>'
        html += f"<tr><td style='border: none;'></td>{mul_tds}</tr>"
        
        is_last_step = (idx == len(steps) - 1)
        display_str = str(step['rem']) if str(step['rem']) != "0" or is_last_step else ""
        next_digit = div_str[step['col_index'] + 1] if not is_last_step else ""
        if not is_last_step and display_str != "": display_str += next_digit
        elif display_str == "": display_str = next_digit
        
        pad_len_rem = step['col_index'] + 1 - len(display_str) + (1 if not is_last_step else 0)
        rem_tds = ""
        for i in range(div_len + 1):
            if i >= pad_len_rem and i <= step['col_index'] + (1 if not is_last_step else 0):
                border_b2 = "border-bottom: 6px double #000;" if is_last_step else ""
                rem_tds += f'<td style="width: 35px; height: 50px; vertical-align: bottom; text-align: center; font-size: 38px; {border_b2}">{display_str[i - pad_len_rem]}</td>'
            else: rem_tds += '<td style="width: 35px;"></td>'
        html += f"<tr><td style='border: none;'></td>{rem_tds}</tr>"
    html += "</table></div></div>"
    return html

def generate_thai_number_text(num_str):
    thai_nums = ["ศูนย์", "หนึ่ง", "สอง", "สาม", "สี่", "ห้า", "หก", "เจ็ด", "แปด", "เก้า"]
    positions = ["", "สิบ", "ร้อย", "พัน", "หมื่น", "แสน", "ล้าน"]
    def read_int(s):
        if s == "0" or s == "": return "ศูนย์"
        res, length = "", len(s)
        for i, digit in enumerate(s):
            d = int(digit)
            if d == 0: continue
            pos = length - i - 1
            if pos == 1 and d == 2: res += "ยี่สิบ"
            elif pos == 1 and d == 1: res += "สิบ"
            elif pos == 0 and d == 1 and length > 1: res += "เอ็ด"
            else: res += thai_nums[d] + positions[pos]
        return res
    return read_int(str(num_str))

def cm_to_m_cm_mm(cm_float):
    total_mm = int(round(cm_float * 10))
    m, cm, mm = total_mm // 1000, (total_mm % 1000) // 10, total_mm % 10
    parts = []
    if m > 0: parts.append(f"{m} เมตร")
    if cm > 0: parts.append(f"{cm} เซนติเมตร")
    if mm > 0: parts.append(f"{mm} มิลลิเมตร")
    return " ".join(parts) if parts else "0 เซนติเมตร"

def get_prefix(grade): return "<b style='color: #2c3e50; margin-right: 5px;'>ประโยคสัญลักษณ์:</b> "

# ================== SVG Drawing Functions ==================
def draw_distance_route_svg(p_names, p_emojis, dist_texts):
    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="500" height="120">'
    svg += f'<line x1="50" y1="60" x2="250" y2="60" stroke="#34495e" stroke-width="4" stroke-dasharray="10,5"/>'
    if len(p_names) == 3: svg += f'<line x1="250" y1="60" x2="450" y2="60" stroke="#34495e" stroke-width="4" stroke-dasharray="10,5"/>'
    svg += f'<text x="150" y="45" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{dist_texts[0]}</text>'
    if len(p_names) == 3: svg += f'<text x="350" y="45" font-family="Sarabun" font-size="16" font-weight="bold" fill="#c0392b" text-anchor="middle">{dist_texts[1]}</text>'
    xs = [50, 250, 450]
    for i, name in enumerate(p_names):
        svg += f'<circle cx="{xs[i]}" cy="60" r="28" fill="#ecf0f1" stroke="#2c3e50" stroke-width="3"/><text x="{xs[i]}" y="68" font-size="28" text-anchor="middle">{p_emojis[i]}</text><text x="{xs[i]}" y="110" font-family="Sarabun" font-size="16" font-weight="bold" fill="#2c3e50" text-anchor="middle">{name}</text>'
    return svg + '</svg></div>'

def draw_beakers_svg(v1_l, v1_ml, v2_l, v2_ml):
    def single_beaker(l, ml, name, color):
        tot, d_max = l * 1000 + ml, max(1000, math.ceil((l * 1000 + ml)/1000)*1000)
        fill_h = (tot / d_max) * 100
        svg = f'<g><rect x="0" y="{120-fill_h}" width="60" height="{fill_h}" fill="{color}" opacity="0.7"/><path d="M0,20 L0,120 Q0,125 5,125 L55,125 Q60,125 60,120 L60,20" fill="none" stroke="#34495e" stroke-width="3"/>'
        for i in range(1, 4): svg += f'<line x1="0" y1="{120 - (i*25)}" x2="10" y2="{120 - (i*25)}" stroke="#34495e" stroke-width="2"/>'
        lbl = f"{l} ลิตร {ml} มล." if l > 0 and ml > 0 else (f"{l} ลิตร" if l > 0 else f"{ml} มล.")
        svg += f'<text x="30" y="145" font-family="Sarabun" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">{name}</text><text x="30" y="165" font-family="Sarabun" font-size="14" fill="#e74c3c" font-weight="bold" text-anchor="middle">{lbl}</text></g>'
        return svg
    return f'<div style="text-align:center; margin: 20px 0;"><svg width="300" height="200"><g transform="translate(50, 0)">{single_beaker(v1_l, v1_ml, "ถัง A", "#3498db")}</g><g transform="translate(190, 0)">{single_beaker(v2_l, v2_ml, "ถัง B", "#1abc9c")}</g></svg></div>'

def draw_vol_number_line(val_ml, max_l=3):
    max_ml, width, height = max_l * 1000, 550, 120
    svg = f'<div style="text-align:center; margin:15px 0;"><svg width="{width}" height="{height}"><line x1="40" y1="60" x2="510" y2="60" stroke="#34495e" stroke-width="4"/>'
    total_ticks, tick_spacing = max_l * 10, 460 / (max_l * 10)
    for i in range(total_ticks + 1):
        x = 40 + i * tick_spacing
        tick_len, sw = (15, 3) if i % 10 == 0 else ((10, 2) if i % 5 == 0 else (6, 1))
        svg += f'<line x1="{x}" y1="{60-tick_len}" x2="{x}" y2="{60+tick_len}" stroke="#34495e" stroke-width="{sw}"/>'
        if i % 10 == 0: svg += f'<text x="{x}" y="95" font-family="sans-serif" font-size="16" font-weight="bold" fill="#333" text-anchor="middle">{i//10}L</text>'
    val_x = 40 + (val_ml / max_ml) * 460
    svg += f'<circle cx="{val_x}" cy="60" r="6" fill="#e74c3c"/><polygon points="{val_x-8},40 {val_x+8},40 {val_x},54" fill="#e74c3c"/></svg></div>'
    return svg

def draw_clock_svg(h_24, m):
    cx, cy, r = 150, 150, 110
    h_12, m_angle, h_angle = h_24 % 12, math.radians(m * 6 - 90), math.radians((h_24%12) * 30 + (m * 0.5) - 90)
    hx, hy, mx, my = cx + 60 * math.cos(h_angle), cy + 60 * math.sin(h_angle), cx + 90 * math.cos(m_angle), cy + 90 * math.sin(m_angle)
    svg = f'<div style="text-align:center;"><svg width="300" height="300"><circle cx="{cx}" cy="{cy}" r="{r}" fill="white" stroke="#333" stroke-width="4"/>'
    for i in range(60):
        angle = math.radians(i * 6 - 90)
        is_hour = i % 5 == 0
        tick_len, sw = (10, 3) if is_hour else (5, 1)
        svg += f'<line x1="{cx + (r - tick_len) * math.cos(angle)}" y1="{cy + (r - tick_len) * math.sin(angle)}" x2="{cx + r * math.cos(angle)}" y2="{cy + r * math.sin(angle)}" stroke="#333" stroke-width="{sw}"/>'
        if is_hour: svg += f'<text x="{cx + (r - 28) * math.cos(angle)}" y="{cy + (r - 28) * math.sin(angle)}" font-family="sans-serif" font-size="20" font-weight="bold" fill="#333" text-anchor="middle" dominant-baseline="central">{12 if i//5 == 0 else i//5}</text>'
    svg += f'<line x1="{cx}" y1="{cy}" x2="{hx}" y2="{hy}" stroke="#e74c3c" stroke-width="6" stroke-linecap="round"/>'
    svg += f'<line x1="{cx}" y1="{cy}" x2="{mx}" y2="{my}" stroke="#3498db" stroke-width="4" stroke-linecap="round"/>'
    svg += f'<circle cx="{cx}" cy="{cy}" r="6" fill="#333"/></svg></div>'
    return svg

def draw_scale_svg(kg, kheed, max_kg=5):
    cx, cy, r = 150, 150, 120
    angle = math.radians((kg * 10 + kheed) * 7.2 - 90)
    nx, ny = cx + 100 * math.cos(angle), cy + 100 * math.sin(angle) 
    svg = f'<div style="text-align:center;"><svg width="300" height="300"><circle cx="{cx}" cy="{cy}" r="{r}" fill="#fdfefe" stroke="#2c3e50" stroke-width="6"/><circle cx="{cx}" cy="{cy}" r="{r-25}" fill="none" stroke="#bdc3c7" stroke-width="1"/><text x="{cx}" y="{cy+45}" font-family="sans-serif" font-size="20" font-weight="bold" fill="#7f8c8d" text-anchor="middle">kg</text>'
    for i in range(max_kg * 10):
        tick_angle = math.radians(i * 7.2 - 90)
        is_kg = i % 10 == 0
        tick_len, sw = (25, 4) if is_kg else ((15, 3) if i % 5 == 0 else (10, 2))
        svg += f'<line x1="{cx + (r - tick_len) * math.cos(tick_angle)}" y1="{cy + (r - tick_len) * math.sin(tick_angle)}" x2="{cx + r * math.cos(tick_angle)}" y2="{cy + r * math.sin(tick_angle)}" stroke="#2c3e50" stroke-width="{sw}"/>'
        if is_kg: svg += f'<text x="{cx + (r - 40) * math.cos(tick_angle)}" y="{cy + (r - 40) * math.sin(tick_angle)}" font-family="sans-serif" font-size="26" font-weight="bold" fill="#2c3e50" text-anchor="middle" dominant-baseline="central">{i // 10}</text>'
    svg += f'<line x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" stroke="#c0392b" stroke-width="4" stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="10" fill="#c0392b"/></svg></div>'
    return svg

def draw_long_ruler_svg(length_cm, color="#f1c40f", name=""):
    scale, base_cm, max_cm_display = 40, max(0, int(length_cm) - 2), 6 
    width, height = max_cm_display * scale + 60, 140
    svg = f'<div style="text-align:center; margin: 15px 0;"><svg width="{width}" height="{height}"><rect x="20" y="70" width="{max_cm_display*scale + 20}" height="50" fill="#ecf0f1" stroke="#bdc3c7" stroke-width="2" rx="5"/>'
    obj_end_x = 30 + (length_cm - base_cm) * scale
    tip_len = min(20, obj_end_x - 10)
    svg += f'<rect x="0" y="20" width="{obj_end_x - tip_len}" height="24" fill="{color}" stroke="#333" stroke-width="2"/><polygon points="{obj_end_x - tip_len},20 {obj_end_x - tip_len},44 {obj_end_x},32" fill="#34495e"/><text x="10" y="15" font-family="Sarabun" font-size="14" font-weight="bold" fill="#e74c3c">← {name} (เริ่มจาก 0)</text><line x1="{obj_end_x}" y1="32" x2="{obj_end_x}" y2="70" stroke="#e74c3c" stroke-width="2" stroke-dasharray="4,4"/>'
    for i in range(max_cm_display * 10 + 1):
        x = 30 + i * (scale / 10)
        if i % 10 == 0:
            svg += f'<line x1="{x}" y1="70" x2="{x}" y2="90" stroke="#2c3e50" stroke-width="3"/><text x="{x}" y="110" font-family="sans-serif" font-size="16" font-weight="bold" fill="#2c3e50" text-anchor="middle">{base_cm + i//10}</text>'
        elif i % 5 == 0: svg += f'<line x1="{x}" y1="70" x2="{x}" y2="85" stroke="#2c3e50" stroke-width="2"/>'
        else: svg += f'<line x1="{x}" y1="70" x2="{x}" y2="80" stroke="#7f8c8d" stroke-width="1"/>'
    return svg + '</svg></div>'

def draw_complex_pictogram_html(item, emoji, pic_val):
    days = random.sample(["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์"], 3)
    counts = [random.randint(2, 6) for _ in range(3)]
    html = f'<div style="border: 2px solid #34495e; border-radius: 10px; width: 80%; margin: 15px auto; background-color: #fff; font-family: \'Sarabun\', sans-serif;"><div style="text-align: center; background-color: #ecf0f1; padding: 10px; font-weight: bold; border-bottom: 2px solid #34495e; font-size: 20px;">จำนวน{item}ที่ขายได้</div><table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 24px;">'
    for d, c in zip(days, counts):
        icons = "".join([f"<span style='margin: 0 4px;'>{emoji}</span>"] * c)
        html += f'<tr><td style="padding: 10px; border-bottom: 1px solid #eee; width: 30%; border-right: 2px solid #34495e; text-align: center;"><b>วัน{d}</b></td><td style="padding: 10px; border-bottom: 1px solid #eee; text-align: left; padding-left: 20px;">{icons}</td></tr>'
    html += f'</table><div style="background-color: #fdf2e9; padding: 10px; text-align: center; font-size: 18px; color: #d35400; font-weight: bold; border-top: 2px solid #34495e;">กำหนดให้ {emoji} 1 รูป แทนจำนวน {pic_val} ผล</div></div>'
    return html, days, counts

# ==========================================
# 2. ฐานข้อมูลหลักสูตร (Master Database P.1 - P.3)
# ==========================================
curriculum_db = {
    "ป.1": {
        "จำนวนนับ 1 ถึง 100 และ 0": ["การนับทีละ 1 และ 10", "การอ่านและการเขียนตัวเลข", "หลัก ค่าของเลขโดด และการเรียงลำดับ"],
        "การบวก การลบ": ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)"],
        "แผนภูมิรูปภาพ": ["การอ่านแผนภูมิรูปภาพ"]
    },
    "ป.2": {
        "จำนวนนับไม่เกิน 1,000 และ 0": ["การนับทีละ 2 ทีละ 5 ทีละ 10", "การอ่านและการเขียนตัวเลข", "หลัก ค่าของเลขโดด และการเรียงลำดับ"],
        "เวลาและการวัด": ["การบอกเวลาเป็นนาฬิกาและนาที", "การอ่านน้ำหนักจากเครื่องชั่งสปริง", "การอ่านความยาวจากไม้บรรทัด"],
        "การบวก ลบ คูณ หาร": ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)", "การคูณ (แบบตั้งหลัก)", "การหารพื้นฐาน"],
        "แผนภูมิรูปภาพ": ["การอ่านแผนภูมิรูปภาพ"]
    },
    "ป.3": {
        "จำนวนนับและเศษส่วน": ["การอ่านและการเขียนตัวเลข", "หลัก ค่าของเลขโดด และการเรียงลำดับ", "การอ่านและเขียนเศษส่วน", "การบวกลบเศษส่วน (ตัวส่วนเท่ากัน)"],
        "เวลา เงิน และการวัด": [
            "การบอกเวลาเป็นนาฬิกาและนาที", "การบอกจำนวนเงินทั้งหมด", "การอ่านน้ำหนักจากเครื่องชั่งสปริง", "การอ่านความยาวจากไม้บรรทัด", 
            "ระยะทาง (กิโลเมตรและเมตร)", "โจทย์ปัญหาความยาว (คูณและหาร)", "การเปรียบเทียบหน่วยการวัด และการแปลงหน่วย (มิลลิเมตร เซนติเมตร เมตร)",
            "การเปรียบเทียบหน่วยระยะทาง และการแปลงหน่วย (เมตร กิโลเมตร)", "การเปรียบเทียบหน่วยน้ำหนัก และการแปลงหน่วย (กรัม กิโลกรัม ตัน)", "ปริมาตรและความจุ (มิลลิลิตร ลิตร)"
        ],
        "การบวก ลบ คูณ หาร": ["การบวก (แบบตั้งหลัก)", "การลบ (แบบตั้งหลัก)", "การคูณ (แบบตั้งหลัก)", "การหารยาว"],
        "แผนภูมิรูปภาพ": ["การอ่านแผนภูมิรูปภาพ"]
    }
}

# ==========================================
# 3. Logic & Dynamic Difficulty Scaling (P.1-P.3)
# ==========================================
def generate_questions_logic(grade, main_t, sub_t, num_q, is_challenge=False):
    questions, seen = [], set()
    limit_map = {"ป.1": 100, "ป.2": 1000, "ป.3": 100000}
    base_limit = limit_map.get(grade, 100)
    
    for _ in range(num_q):
        q, sol, attempts = "", "", 0
        
        while attempts < 300:
            actual_sub_t = sub_t
            if sub_t == "แบบทดสอบรวมปลายภาค":
                rand_main = random.choice(list(curriculum_db[grade].keys()))
                actual_sub_t = random.choice(curriculum_db[grade][rand_main])

            prefix = get_prefix(grade)

            # ================= หมวดการวัด ปริมาตร ระยะทาง (ป.3) =================
            if actual_sub_t == "ปริมาตรและความจุ (มิลลิลิตร ลิตร)":
                q_cat = random.choice(["number_line", "add_sub", "divide"])
                u_major, u_minor, multiplier = "ลิตร", "มิลลิลิตร", 1000
                
                if q_cat == "number_line": 
                    max_l = random.randint(3, 6) if is_challenge else random.randint(1, 2)
                    val_ml = random.randint(5, (max_l * 1000 // 50) - 5) * 50 if is_challenge else random.randint(1, (max_l * 10) - 1) * 100
                    ans_l, ans_ml = val_ml // 1000, val_ml % 1000
                    ans_str = f"{ans_l} ลิตร {ans_ml} มิลลิลิตร" if ans_l > 0 and ans_ml > 0 else (f"{ans_l} ลิตร" if ans_ml == 0 else f"{ans_ml} มิลลิลิตร")
                    svg = draw_vol_number_line(val_ml, max_l)
                    q = f"จากเส้นจำนวนด้านล่าง ลูกศรชี้ที่ปริมาตรความจุเท่าใด?<br>{svg}"
                    sol = f"<span style='color: #2c3e50;'><b>วิธีทำ:</b> นับจากสเกลจะได้ {val_ml:,} มล. หรือ {ans_str}</span>"
                elif q_cat == "add_sub":
                    op = random.choice(["+", "-"])
                    v1_maj, v1_min = random.randint(3, 10), random.randint(100, 900)
                    v2_maj = random.randint(1, v1_maj-1) if op == "-" else random.randint(1, 10)
                    v2_min = random.randint(100, 900)
                    if op == "-" and v1_min >= v2_min:
                        v1_min, v2_min = v2_min, v1_min + 50
                        if v2_min >= 1000: v2_min = 950
                    svg = draw_beakers_svg(v1_maj, v1_min, v2_maj, v2_min)
                    q = f"{svg}ถ้านำน้ำจากทั้งสองถังมา<b>{'รวมกัน' if op=='+' else 'หาความต่าง'}</b> จะได้เท่าไร?"
                    table_html, ans_str = generate_unit_math_html(u_major, u_minor, v1_maj, v1_min, v2_maj, v2_min, op, multiplier)
                    sol = f"<span style='color: #2c3e50;'><b>วิธีทำ:</b><br>{table_html}<b>ตอบ: {ans_str}</b></span>"
                else: 
                    item, container = random.choice(["น้ำผลไม้", "นมสด"]), random.choice(["ขวด", "แก้ว"])
                    N = random.randint(3, 9)
                    ans_maj, ans_min = random.randint(0, 2), random.randint(15, 85) * 10
                    if ans_maj == 0 and ans_min < 200: ans_min += 300
                    total_min = (ans_maj * multiplier + ans_min) * N
                    tot_maj, tot_rem_min = total_min // multiplier, total_min % multiplier
                    str_tot = f"{tot_maj} ลิตร {tot_rem_min} มล." if tot_rem_min > 0 else f"{tot_maj} ลิตร"
                    str_ans = f"{ans_maj} ลิตร {ans_min} มล." if ans_maj > 0 else f"{ans_min} มล."
                    q = f"มี{item}อยู่ <b>{str_tot}</b> แบ่งใส่{container} <b>{N} {container}</b> เท่าๆกัน จะได้{container}ละเท่าไร?"
                    sol = f"<span style='color: #2c3e50;'><b>ตอบ: {str_ans}</b></span>"

            elif actual_sub_t == "การเปรียบเทียบหน่วยการวัด และการแปลงหน่วย (มิลลิเมตร เซนติเมตร เมตร)":
                selected_type = random.choice(["cm_mm", "m_cm"])
                u_major, u_minor, multiplier = ("เซนติเมตร", "มิลลิเมตร", 10) if selected_type == "cm_mm" else ("เมตร", "เซนติเมตร", 100)
                val_major = random.randint(5, 50) if is_challenge else random.randint(2, 20)
                val_minor = random.randint(1, multiplier-1)
                total_minor_1 = (val_major * multiplier) + val_minor
                case = random.choice(["greater", "less", "equal"])
                total_minor_2 = total_minor_1 if case == "equal" else (total_minor_1 - random.randint(1, multiplier-1) if case == "greater" else total_minor_1 + random.randint(1, multiplier-1))
                str_val_1, str_val_2 = f"{val_major} {u_major} {val_minor} {u_minor}", f"{total_minor_2:,} {u_minor}"
                item_A, item_B = (str_val_1, str_val_2) if random.choice([True, False]) else (str_val_2, str_val_1)
                val_A, val_B = (total_minor_1, total_minor_2) if item_A == str_val_1 else (total_minor_2, total_minor_1)
                final_ans = "ยาวเท่ากัน" if val_A == val_B else ("ยาวกว่า" if val_A > val_B else "สั้นกว่า")
                q = f"จงเติมคำว่า <b>ยาวกว่า, สั้นกว่า</b> หรือ <b>เท่ากับ</b><br><span style='font-size:22px;'>{item_A} &nbsp; ______ &nbsp; {item_B}</span>"
                sol = f"<span style='color: #2c3e50;'><b>ตอบ: {final_ans}</b></span>"

            elif actual_sub_t == "การเปรียบเทียบหน่วยระยะทาง และการแปลงหน่วย (เมตร กิโลเมตร)":
                u_major, u_minor, multiplier = "กิโลเมตร", "เมตร", 1000
                val_major = random.randint(2, 20) if is_challenge else random.randint(1, 9)
                val_minor = random.randint(50, 950)
                total_minor_1 = (val_major * multiplier) + val_minor
                case = random.choice(["greater", "less", "equal"])
                total_minor_2 = total_minor_1 if case == "equal" else (total_minor_1 - random.randint(1, multiplier-1) if case == "greater" else total_minor_1 + random.randint(1, multiplier-1))
                str_val_1, str_val_2 = f"{val_major} {u_major} {val_minor} {u_minor}", f"{total_minor_2:,} {u_minor}"
                item_A, item_B = (str_val_1, str_val_2) if random.choice([True, False]) else (str_val_2, str_val_1)
                val_A, val_B = (total_minor_1, total_minor_2) if item_A == str_val_1 else (total_minor_2, total_minor_1)
                final_ans = "ไกลเท่ากัน" if val_A == val_B else ("ไกลกว่า" if val_A > val_B else "ใกล้กว่า")
                q = f"จงเติมคำว่า <b>ไกลกว่า, ใกล้กว่า</b> หรือ <b>เท่ากับ</b><br><span style='font-size:22px;'>{item_A} &nbsp; ______ &nbsp; {item_B}</span>"
                sol = f"<span style='color: #2c3e50;'><b>ตอบ: {final_ans}</b></span>"

            elif actual_sub_t == "การเปรียบเทียบหน่วยน้ำหนัก และการแปลงหน่วย (กรัม กิโลกรัม ตัน)":
                selected_type = random.choice(["kg_g", "ton_kg"])
                u_major, u_minor = ("กิโลกรัม", "กรัม") if selected_type == "kg_g" else ("ตัน", "กิโลกรัม")
                multiplier = 1000
                val_major = random.randint(5, 50) if is_challenge else random.randint(1, 15)
                val_minor = random.randint(50, 950)
                total_minor_1 = (val_major * multiplier) + val_minor
                case = random.choice(["greater", "less", "equal"])
                total_minor_2 = total_minor_1 if case == "equal" else (total_minor_1 - random.randint(1, multiplier-1) if case == "greater" else total_minor_1 + random.randint(1, multiplier-1))
                str_val_1, str_val_2 = f"{val_major} {u_major} {val_minor} {u_minor}", f"{total_minor_2:,} {u_minor}"
                item_A, item_B = (str_val_1, str_val_2) if random.choice([True, False]) else (str_val_2, str_val_1)
                val_A, val_B = (total_minor_1, total_minor_2) if item_A == str_val_1 else (total_minor_2, total_minor_1)
                final_ans = "หนักเท่ากัน" if val_A == val_B else ("หนักกว่า" if val_A > val_B else "เบากว่า")
                q = f"จงเติมคำว่า <b>หนักกว่า, เบากว่า</b> หรือ <b>เท่ากับ</b><br><span style='font-size:22px;'>{item_A} &nbsp; ______ &nbsp; {item_B}</span>"
                sol = f"<span style='color: #2c3e50;'><b>ตอบ: {final_ans}</b></span>"

            elif actual_sub_t == "โจทย์ปัญหาความยาว (คูณและหาร)":
                room, furn = random.choice(ROOMS), random.choice(FURNITURE)
                r_m, r_cm = random.randint(3, 8), random.choice([0, 20, 50, 80])
                f_m, f_cm = random.randint(0, 1), random.choice([50, 60, 80, 100])
                if f_m == 0 and f_cm < 40: f_cm = 50 
                if f_m == 1 and f_cm == 100: f_m, f_cm = 2, 0
                room_total_cm = r_m * 100 + r_cm
                furn_total_cm = f_m * 100 + f_cm
                count, rem_cm = room_total_cm // furn_total_cm, room_total_cm % furn_total_cm
                room_str = f"{r_m} เมตร {r_cm} เซนติเมตร" if r_cm > 0 else f"{r_m} เมตร"
                furn_str = f"{f_m} เมตร {f_cm} เซนติเมตร" if f_m > 0 and f_cm > 0 else (f"{f_m} เมตร" if f_cm == 0 else f"{f_cm} เซนติเมตร")
                q = f"<b>{room}</b> มีความกว้าง {room_str} <br>นำ <b>{furn}</b> ที่กว้าง {furn_str} มาวางเรียงติดกัน จะได้มากที่สุดกี่ตัว และเหลือพื้นที่ว่างกี่ซม.?"
                sol = f"<span style='color: #2c3e50;'><b>ตอบ: วางได้ {count} ตัว และเหลือพื้นที่ว่าง {rem_cm} ซม.</b></span>"

            elif actual_sub_t == "ระยะทาง (กิโลเมตรและเมตร)":
                p_names = random.sample(list(PLACE_EMOJIS.keys()), 3)
                p_emojis = [PLACE_EMOJIS[n] for n in p_names]
                q_type = random.choice(["convert_to_km", "convert_to_m"])
                if q_type == "convert_to_km":
                    dist_m = random.randint(1100, 9800)
                    km, m = dist_m // 1000, dist_m % 1000
                    svg = draw_distance_route_svg([p_names[0], p_names[1]], [p_emojis[0], p_emojis[1]], [f"{dist_m:,} ม."])
                    q = svg + f"<br>ระยะทางจาก <b>{p_names[0]}</b> ไป <b>{p_names[1]}</b> คือ {dist_m:,} เมตร<br>คิดเป็นกี่กิโลเมตร กี่เมตร?"
                    sol = f"<span style='color: #2c3e50;'><b>ตอบ: {km} กิโลเมตร {m} เมตร</b></span>"
                elif q_type == "convert_to_m":
                    km, m = random.randint(1, 9), random.randint(50, 950)
                    svg = draw_distance_route_svg([p_names[0], p_names[1]], [p_emojis[0], p_emojis[1]], [f"{km} กม. {m} ม."])
                    q = svg + f"<br>ระยะทางจาก <b>{p_names[0]}</b> ไป <b>{p_names[1]}</b> คือ {km} กม. {m} ม.<br>คิดเป็นระยะทางกี่เมตร?"
                    sol = f"<span style='color: #2c3e50;'><b>ตอบ: {(km * 1000) + m:,} เมตร</b></span>"

# ================= หมวดพื้นฐาน ป.1 - ป.3 (เวลา, น้ำหนัก, ความยาว, รูปภาพ) =================
            elif actual_sub_t == "การบอกเวลาเป็นนาฬิกาและนาที":
                h_24, m = random.randint(0, 23), random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
                period = "เวลากลางวัน" if 6 <= h_24 <= 17 else "เวลากลางคืน"
                q = draw_clock_svg(h_24, m) + f"<br>จากรูปนาฬิกาด้านบน (กำหนดเป็น<b>{period}</b>) อ่านเวลาได้ว่าอย่างไร?"
                sol = f"<span style='color: #2c3e50;'><b>ตอบ: {h_24:02d}:{m:02d} น. หรือ {h_24} นาฬิกา {m} นาที</b></span>"

            elif actual_sub_t == "การอ่านน้ำหนักจากเครื่องชั่งสปริง":
                kg, kheed = random.randint(0, 4), random.randint(1, 9)
                q = draw_scale_svg(kg, kheed) + "<br>จากรูป เครื่องชั่งสปริงแสดงน้ำหนักเท่าไร? (ตอบเป็นกิโลกรัมและกรัม)"
                sol = f"<span style='color: #2c3e50;'><b>ตอบ: {kg} กิโลกรัม {kheed*100} กรัม</b></span>"

            elif actual_sub_t == "การอ่านความยาวจากไม้บรรทัด":
                len_a = round(random.uniform(110.0, 350.0), 1)
                svg = draw_long_ruler_svg(len_a, "#f1c40f", "สิ่งของ (เริ่มวัดจาก 0)")
                q = f"จากรูป สายวัดแสดงตำแหน่งส่วนปลายของสิ่งของ (เริ่มวัดจาก 0 เสมอ)<br>{svg}จงหาว่าสิ่งของนี้ยาวเท่าไร? (ตอบในหน่วย เมตร เซนติเมตร มิลลิเมตร)"
                sol = f"<span style='color: #2c3e50;'><b>ตอบ: {cm_to_m_cm_mm(len_a)}</b></span>"

            elif actual_sub_t == "การอ่านแผนภูมิรูปภาพ":
                item = random.choice(list(FRUIT_EMOJIS.keys()))
                emoji = FRUIT_EMOJIS[item]
                pic_val = random.choice([2, 5]) if grade == "ป.2" else (random.choice([5, 10]) if grade == "ป.3" else 1)
                q_type = random.choice(["single", "total", "diff"])
                pic_html, days, counts = draw_complex_pictogram_html(item, emoji, pic_val)
                
                if q_type == "single":
                    ask_idx = random.randint(0, 2)
                    ans = counts[ask_idx] * pic_val
                    q = pic_html + f"<br>จากแผนภูมิรูปภาพ ใน<b>วัน{days[ask_idx]}</b> ขาย{item}ได้กี่ผล?"
                elif q_type == "total":
                    ans = sum(counts) * pic_val
                    q = pic_html + f"<br>จากแผนภูมิรูปภาพ รวมทั้ง 3 วัน ขาย{item}ได้ทั้งหมดกี่ผล?"
                else:
                    d1, d2 = random.sample([0, 1, 2], 2)
                    if counts[d1] < counts[d2]: d1, d2 = d2, d1 
                    ans = (counts[d1] - counts[d2]) * pic_val
                    q = pic_html + f"<br>จากแผนภูมิรูปภาพ วัน{days[d1]} ขาย{item}ได้<b>มากกว่า</b>วัน{days[d2]} กี่ผล?"
                sol = f"<span style='color: #2c3e50;'><b>ตอบ: {ans} ผล</b></span>"

            # ================= หมวดจำนวน การบวก ลบ คูณ หาร (ป.1 - ป.3) =================
            elif actual_sub_t in ["การนับทีละ 1 และ 10", "การนับทีละ 2 ทีละ 5 ทีละ 10"]:
                step = random.choice([1, 10]) if grade == "ป.1" else random.choice([2, 5, 10])
                start = random.randint(10, 50) if grade == "ป.1" else random.randint(100, 500)
                seq = [start + (i * step) for i in range(4)]
                q = f"แบบรูปของจำนวนเพิ่มขึ้นทีละ {step} จงหาจำนวนถัดไป:<br><span style='font-size:24px; color:#2980b9;'>{seq[0]}, {seq[1]}, {seq[2]}, ...</span>"
                sol = f"<span style='color: #2c3e50;'><b>ตอบ: {seq[3]}</b></span>"

            elif actual_sub_t in ["การอ่านและการเขียนตัวเลข", "การอ่าน การเขียนตัวเลข"]:
                num = random.randint(10, 100) if grade == "ป.1" else (random.randint(100, 1000) if grade == "ป.2" else random.randint(1000, 100000))
                thai_text = generate_thai_number_text(str(num))
                mode = random.choice(["to_text", "to_num"])
                if mode == "to_text":
                    q = f"จงเขียนตัวเลข <b>{num:,}</b> เป็นตัวหนังสือภาษาไทย"
                    sol = f"<span style='color:#2c3e50;'><b>ตอบ: {thai_text}</b></span>"
                else:
                    q = f"จงเขียนคำอ่าน <b>\"{thai_text}\"</b> เป็นตัวเลขฮินดูอารบิก"
                    sol = f"<span style='color:#2c3e50;'><b>ตอบ: {num:,}</b></span>"

            elif actual_sub_t in ["หลัก ค่าของเลขโดดในแต่ละหลัก และรูปกระจาย", "หลัก ค่าของเลขโดด และรูปกระจาย", "หลัก ค่าของเลขโดด และการเรียงลำดับ"]:
                mode = random.choice(["expanded", "compare"])
                if mode == "expanded":
                    num = random.randint(20, 99) if grade == "ป.1" else (random.randint(100, 999) if grade == "ป.2" else random.randint(1000, 99999))
                    num_str = str(num)
                    q = f"จงเขียนจำนวน <b>{num:,}</b> ให้อยู่ในรูปกระจาย"
                    expanded = " + ".join([f"{int(d) * (10**(len(num_str)-i-1))}" for i, d in enumerate(num_str) if d != '0'])
                    sol = f"<span style='color:#2c3e50;'><b>ตอบ: {expanded}</b></span>"
                else:
                    count = 3 if grade == "ป.1" else 4
                    limit = 100 if grade == "ป.1" else (1000 if grade == "ป.2" else 100000)
                    nums = random.sample(range(10, limit), count)
                    order = random.choice(["น้อยไปมาก", "มากไปน้อย"])
                    nums_str = ", ".join([f"{n:,}" for n in nums])
                    sorted_nums = sorted(nums) if order == "น้อยไปมาก" else sorted(nums, reverse=True)
                    sorted_str = ", ".join([f"{n:,}" for n in sorted_nums])
                    q = f"จงเรียงลำดับจำนวนต่อไปนี้จาก<b>{order}</b>:<br><div style='font-size:22px; margin: 10px 0; color:#2980b9;'>{nums_str}</div>"
                    sol = f"<span style='color:#2c3e50;'><b>ตอบ: {sorted_str}</b></span>"

            elif actual_sub_t == "การบอกจำนวนเงินทั้งหมด":
                c10, c5, b20, b50, b100 = random.randint(1, 5), random.randint(1, 5), random.randint(0, 3), random.randint(0, 2), random.randint(0, 2)
                total = (c10*10) + (c5*5) + (b20*20) + (b50*50) + (b100*100)
                items = []
                if b100 > 0: items.append(f"ธนบัตร 100 บาท {b100} ฉบับ")
                if b50 > 0: items.append(f"ธนบัตร 50 บาท {b50} ฉบับ")
                if b20 > 0: items.append(f"ธนบัตร 20 บาท {b20} ฉบับ")
                if c10 > 0: items.append(f"เหรียญ 10 บาท {c10} เหรียญ")
                if c5 > 0: items.append(f"เหรียญ 5 บาท {c5} เหรียญ")
                q = f"น้องมีเงินดังนี้:<br>- " + "<br>- ".join(items) + "<br>น้องมีเงินรวมทั้งหมดกี่บาท?"
                sol = f"<span style='color:#2c3e50;'><b>ตอบ: {total:,} บาท</b></span>"

            elif actual_sub_t == "การบวก (แบบตั้งหลัก)":
                limit = 100 if grade == "ป.1" else (1000 if grade == "ป.2" else 100000)
                a, b = random.randint(10, limit // 2), random.randint(10, limit // 2)
                ans = a + b
                q = f"จงหาผลบวกของ <b>{a:,} + {b:,}</b><br>{generate_vertical_table_html(a, b, '+', result=ans, is_key=False)}"
                sol = f"<span style='color:#2c3e50;'>{generate_vertical_table_html(a, b, '+', result=ans, is_key=True)}</span>"

            elif actual_sub_t == "การลบ (แบบตั้งหลัก)":
                limit = 100 if grade == "ป.1" else (1000 if grade == "ป.2" else 100000)
                a = random.randint(20, limit)
                b = random.randint(10, a - 5)
                ans = a - b
                q = f"จงหาผลลบของ <b>{a:,} - {b:,}</b><br>{generate_vertical_table_html(a, b, '-', result=ans, is_key=False)}"
                sol = f"<span style='color:#2c3e50;'>{generate_vertical_table_html(a, b, '-', result=ans, is_key=True)}</span>"

            elif actual_sub_t == "การคูณ (แบบตั้งหลัก)":
                if grade == "ป.2": a, b = random.randint(10, 99), random.randint(2, 9)
                else: a, b = random.randint(100, 999), random.randint(2, 99)
                ans = a * b
                q = f"จงหาผลคูณของ <b>{a:,} × {b:,}</b><br>{generate_vertical_table_html(a, b, '×', result=ans, is_key=False)}"
                sol = f"<span style='color:#2c3e50;'>{generate_vertical_table_html(a, b, '×', result=ans, is_key=True)}</span>"

            elif actual_sub_t in ["การหารพื้นฐาน", "การหารยาว"]:
                divisor = random.randint(2, 9)
                quotient = random.randint(5, 12) if actual_sub_t == "การหารพื้นฐาน" else random.randint(20, 999)
                dividend = divisor * quotient
                
                eq_html = f"<div style='font-size: 24px; margin-bottom: 10px;'><b>{dividend:,} ÷ {divisor} = ?</b></div>"
                table_html = generate_long_division_step_by_step_html(divisor, dividend, eq_html, is_key=False)
                table_key = generate_long_division_step_by_step_html(divisor, dividend, eq_html, is_key=True)
                
                if actual_sub_t == "การหารยาว":
                    q = f"จงหาผลหารโดยวิธีหารยาว<br>{table_html}"
                else:
                    q = f"จงหาผลหารต่อไปนี้ พร้อมทั้งแสดงวิธีทำแบบตั้งหารยาว<br>{table_html}"
                    
                sol = f"<span style='color:#2c3e50;'>{table_key}<br><b>ตอบ: {quotient:,}</b></span>"

            else:
                # ป้องกัน Error กรณีสุ่มโดนหัวข้อที่ไม่ได้ระบุเจาะจง
                q = f"📝 แบบฝึกหัดทบทวน: <b>{actual_sub_t}</b><br><span style='color:#7f8c8d;'>(ส่วนนี้เป็นพื้นที่สำหรับให้นักเรียนได้แสดงวิธีทำตามที่เรียนมาในห้องเรียน)</span>"
                sol = f"<span style='color:#2c3e50;'><i>ขึ้นอยู่กับดุลยพินิจและวิธีการสอนของคุณครู</i></span>"

            # ==================================================
            # ระบบเช็คโจทย์ซ้ำ (ยันต์กันค้าง)
            # ==================================================
            if q not in seen: 
                seen.add(q)
                questions.append({"question": f"{prefix} {q}", "solution": sol})
                break 
            elif attempts >= 299:
                questions.append({"question": f"{prefix} {q}", "solution": sol})
                break
                
            attempts += 1  
            
    return questions

# ==========================================
# 4. UI Rendering & Streamlit Main (P.1-P.3)
# ==========================================
def extract_body(html_str):
    try: return html_str.split('<body>')[1].split('</body>')[0]
    except IndexError: return html_str

def create_page(grade, sub_t, questions, is_key=False, q_margin="20px", ws_height="180px", brand_name=""):
    title = "🔑 เฉลยแบบฝึกหัด (Answer Key)" if is_key else "📄 แบบฝึกหัดคณิตศาสตร์"
    student_info = """
        <table style="width: 100%; margin-bottom: 10px; font-size: 18px; border-collapse: collapse;">
            <tr>
                <td style="width: 1%; white-space: nowrap; padding-right: 5px;"><b>ชื่อ-สกุล</b></td>
                <td style="border-bottom: 2px dotted #999; width: 60%;"></td>
                <td style="width: 1%; white-space: nowrap; padding-left: 20px; padding-right: 5px;"><b>ชั้น</b></td>
                <td style="border-bottom: 2px dotted #999; width: 15%;"></td>
                <td style="width: 1%; white-space: nowrap; padding-left: 20px; padding-right: 5px;"><b>เลขที่</b></td>
                <td style="border-bottom: 2px dotted #999; width: 15%;"></td>
            </tr>
        </table>
        """ if not is_key else ""
        
    html = f"""<!DOCTYPE html><html lang="th"><head><meta charset="utf-8">
    <style>
        @page {{ size: A4; margin: 15mm; }}
        body {{ font-family: 'Sarabun', sans-serif; padding: 20px; line-height: 1.6; color: #333; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }}
        .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.6; }}
        .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }}
        .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }}
        .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f1f8ff; border-left: 4px solid #3498db; border-radius: 4px; line-height: 1.6; }}
        .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
    </style></head><body>
    <div class="header"><h2>{title} - {grade}</h2><p><b>หมวดหมู่:</b> {sub_t}</p></div>
    {student_info}"""
    
    for i, item in enumerate(questions, 1):
        html += f'<div class="q-box"><b>ข้อที่ {i}.</b> '
        if is_key:
            if "(แบบตั้งหลัก)" in sub_t or "หารยาว" in sub_t: 
                html += f'{item["solution"]}'
            else: 
                html += f'{item["question"]}<div class="sol-text">{item["solution"]}</div>'
        else:
            html += f'{item["question"]}<div class="workspace">พื้นที่สำหรับทดเลขและแสดงวิธีทำ...</div><div class="ans-line">ตอบ: </div>'
        html += '</div>'
        
    if brand_name: 
        html += f'<div class="page-footer">&copy; 2026 {brand_name} | สงวนลิขสิทธิ์</div>'
        
    return html + "</body></html>"


# ==========================================
# เมนูด้านข้าง Streamlit (Sidebar)
# ==========================================
st.sidebar.markdown("## ⚙️ พารามิเตอร์การสร้าง")

# ล็อกเฉพาะ ป.1 - ป.3
selected_grade = st.sidebar.selectbox("📚 เลือกระดับชั้น:", ["ป.1", "ป.2", "ป.3"])
main_topics_list = list(curriculum_db[selected_grade].keys())
main_topics_list.append("🌟 โหมดพิเศษ (สุ่มทุกเรื่อง)")

selected_main = st.sidebar.selectbox("📂 เลือกหัวข้อหลัก:", main_topics_list)

if selected_main == "🌟 โหมดพิเศษ (สุ่มทุกเรื่อง)":
    selected_sub = "แบบทดสอบรวมปลายภาค"
    st.sidebar.info("💡 โหมดนี้จะสุ่มดึงโจทย์จากทุกเรื่องในชั้นเรียนนี้มายำรวมกัน")
else:
    selected_sub = st.sidebar.selectbox("📝 เลือกหัวข้อย่อย:", curriculum_db[selected_grade][selected_main])

num_input = st.sidebar.number_input("🔢 จำนวนข้อ:", min_value=1, max_value=100, value=10)

st.sidebar.markdown("---")
is_challenge = st.sidebar.toggle("🔥 โหมดชาเลนจ์ (ท้าทาย)", value=False)
if is_challenge:
    st.sidebar.warning("เปิดโหมดชาเลนจ์แล้ว! ตัวเลขจะยากขึ้นและโจทย์จะท้าทายกว่าเดิม")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📏 ตั้งค่าหน้ากระดาษ")
spacing_level = st.sidebar.select_slider(
    "↕️ ความสูงของพื้นที่ทดเลข:", 
    options=["แคบ", "ปานกลาง", "กว้าง", "กว้างพิเศษ"], 
    value="ปานกลาง"
)

if spacing_level == "แคบ": q_margin, ws_height = "15px", "100px"
elif spacing_level == "ปานกลาง": q_margin, ws_height = "20px", "150px"
elif spacing_level == "กว้าง": q_margin, ws_height = "30px", "250px"
else: q_margin, ws_height = "40px", "350px"

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 ตั้งค่าแบรนด์")
brand_name = st.sidebar.text_input("🏷️ ชื่อแบรนด์ / ผู้สอน:", value="บ้านทีเด็ด")

# ==========================================
# ระบบปุ่มกดและการ Export ไฟล์
# ==========================================
if st.sidebar.button("🚀 สั่งสร้างใบงาน ป.1-ป.3", type="primary", use_container_width=True):
    with st.spinner("กำลังออกแบบรูปภาพและสร้างโจทย์คณิตศาสตร์..."):
        
        qs = generate_questions_logic(selected_grade, selected_main, selected_sub, num_input, is_challenge)
        
        html_w = create_page(selected_grade, selected_sub, qs, is_key=False, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        html_k = create_page(selected_grade, selected_sub, qs, is_key=True, q_margin=q_margin, ws_height=ws_height, brand_name=brand_name)
        
        st.session_state['worksheet_html'] = html_w
        st.session_state['answerkey_html'] = html_k
        
        ebook_body = f'\n<div class="a4-wrapper">{extract_body(html_w)}</div>\n<div class="a4-wrapper">{extract_body(html_k)}</div>\n'
        
        full_ebook_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap" rel="stylesheet"><style>@page {{ size: A4; margin: 15mm; }} @media screen {{ body {{ font-family: 'Sarabun', sans-serif; background-color: #525659; display: flex; flex-direction: column; align-items: center; padding: 40px 0; margin: 0; }} .a4-wrapper {{ width: 210mm; min-height: 297mm; background: white; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.3); padding: 15mm; box-sizing: border-box; }} }} @media print {{ body {{ font-family: 'Sarabun', sans-serif; background: transparent; padding: 0; display: block; margin: 0; }} .a4-wrapper {{ width: 100%; min-height: auto; margin: 0; padding: 0; box-shadow: none; page-break-after: always; }} }} .header {{ text-align: center; border-bottom: 2px solid #333; margin-bottom: 10px; padding-bottom: 10px; }} .q-box {{ margin-bottom: {q_margin}; padding: 10px 15px; page-break-inside: avoid; font-size: 20px; line-height: 1.6; }} .workspace {{ height: {ws_height}; border: 2px dashed #bdc3c7; border-radius: 8px; margin: 15px 0; padding: 10px; color: #95a5a6; font-size: 16px; background-color: #fafbfc; }} .ans-line {{ margin-top: 10px; border-bottom: 1px dotted #999; width: 80%; height: 30px; font-weight: bold; font-size: 20px; display: flex; align-items: flex-end; padding-bottom: 5px; }} .sol-text {{ color: #333; font-size: 18px; display: block; margin-top: 15px; padding: 15px; background-color: #f1f8ff; border-left: 4px solid #3498db; border-radius: 4px; line-height: 1.6; }} .page-footer {{ text-align: right; font-size: 14px; color: #95a5a6; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }} </style></head><body>{ebook_body}</body></html>"""

        filename_base = f"BaanTded_P1_P3_{selected_grade}_{int(time.time())}"
        st.session_state['ebook_html'] = full_ebook_html
        st.session_state['filename_base'] = filename_base
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(f"{filename_base}_Full_EBook.html", full_ebook_html.encode('utf-8'))
            zip_file.writestr(f"{filename_base}_Worksheet.html", html_w.encode('utf-8'))
            zip_file.writestr(f"{filename_base}_AnswerKey.html", html_k.encode('utf-8'))
        st.session_state['zip_data'] = zip_buffer.getvalue()

if 'ebook_html' in st.session_state:
    st.success(f"✅ สร้างใบงานสำเร็จ! ลิขสิทธิ์โดย {brand_name}")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📄 โหลดเฉพาะโจทย์", data=st.session_state['worksheet_html'], file_name=f"{st.session_state['filename_base']}_Worksheet.html", mime="text/html", use_container_width=True)
        st.download_button("🔑 โหลดเฉพาะเฉลย", data=st.session_state['answerkey_html'], file_name=f"{st.session_state['filename_base']}_AnswerKey.html", mime="text/html", use_container_width=True)
    with c2:
        st.download_button("📚 โหลดรวมเล่ม E-Book", data=st.session_state['ebook_html'], file_name=f"{st.session_state['filename_base']}_Full_EBook.html", mime="text/html", use_container_width=True)
        st.download_button("🗂️ โหลดแพ็กเกจ (.zip)", data=st.session_state['zip_data'], file_name=f"{st.session_state['filename_base']}.zip", mime="application/zip", use_container_width=True)
    st.markdown("---")
    components.html(st.session_state['ebook_html'], height=800, scrolling=True)
