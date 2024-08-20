#!pip install skyfield
#!pip install timezonefinder
#!pip install geopy

# 匯入tkinter及相關套件
import tkinter as tk
from tkinter import ttk
from PIL import Image,ImageTk
# 匯入日期及時間套件
from datetime import datetime
#匯入地理編碼套件
from geopy import Nominatim
#匯入時區轉換套件
from timezonefinder import TimezoneFinder
from pytz import timezone, utc
# 匯入星空資料套件 
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos, stellarium
from skyfield.projections import build_stereographic_projection
from skyfield.constants import GM_SUN_Pitjeva_2005_km3_s2 as GM_SUN
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from functools import partial

#設定中文字
plt.rcParams['font.family']='Microsoft JhengHei'
plt.rcParams['font.size']=15
plt.rcParams['axes.unicode_minus']=False

# 自訂函數1:取得資料集
def load_data():
    # 導入de440.bsp資料集，取得星球的位置及相對距離
    eph = load('de440.bsp')
    # 導入hipparcos資料集，取得星球的位置及星等
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)
    # 導入stellarium資料集，取得星座名稱及範圍
    url = (r'https://raw.githubusercontent.com/Stellarium/stellarium/master/skycultures/modern_st/constellationship.fab')
    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)
    return eph, stars, constellations

# 自訂函數2:取得目標地資訊
def collect_celestial_data(location, when, altitude, azimuth, eph, stars, constellations):
    locator = Nominatim(user_agent='Spyder', timeout=10)
    #利用Geopy將目的地名稱轉為經緯度
    location = locator.geocode(location)
    lat, long = location.latitude, location.longitude
    #取得目標地當地時間，
    #將輸入的時間轉為datetime格式
    dt = datetime.strptime(when, '%Y-%m-%d %H:%M')
    #取得目標地之時區
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=long, lat=lat)
    #藉由目標地時區將輸入之時間轉為UTC標準時間
    local = timezone(timezone_str)
    utc_dt = local.localize(dt, is_dst=None).astimezone(utc)
    # 將UTC時間轉為skyfield可以處理的時間格式
    t = load.timescale().from_datetime(utc_dt)
    #利用wgs84建立觀察者經緯度
    observer = wgs84.latlon(latitude_degrees=lat, longitude_degrees=long).at(t)
    #建立太陽及地球之絕對位置
    sun = eph['sun']
    earth = eph['earth']
    #建立星座之範圍
    edges = [edge for name, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, star2 in edges]
    edges_star2 = [star2 for star1, star2 in edges]
    #帶入觀察者之仰角及方位角
    position = observer.from_altaz(alt_degrees=altitude, az_degrees=azimuth)
    
    '''利用輸入的高度角及方位角，對應到天球上的赤經(Right Ascension)及
    赤緯(Declination)，並假想一顆此赤經赤緯度的星球center_object，
    '''
    ra, dec, distance = position.radec()
    center_object = Star(ra=ra, dec=dec)
    
    '''以地球為中心，將center_object投影到地球上，作為center
    並以center為中心，將周圍其他星體利用stereographic將天球上的天體
    轉換至二維座標'''
    center = earth.at(t).observe(center_object)
    projection = build_stereographic_projection(center)
    # field_of_view_degrees = 180.0
    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    stars['x'], stars['y'] = projection(star_positions)

    #取得星座名稱(英文簡寫版)
    constellations_at_location = {}
    for name, stars_in_constellation in constellations:
        constellation_stars = set()
        for star1, star2 in stars_in_constellation:
            if star1 in stars.index and star2 in stars.index:
                constellation_stars.add(star1)
                constellation_stars.add(star2)
        if constellation_stars:
            constellations_at_location[name] = constellation_stars

    return stars, edges_star1, edges_star2, constellations_at_location

# 自訂函數3:建立星座圖
def create_star_chart(location, when, altitude, azimuth, eph, stars, constellations, filename, draw_lines_var, draw_constellation_names_var):
    stars, edges_star1, edges_star2, constellations_at_location = collect_celestial_data(location, when, altitude, azimuth, eph, stars, constellations)
    #設定最低星等
    limiting_magnitude = 10
    #定義星球選取標準(亮度低於10等星)
    bright_stars = (stars.magnitude <= limiting_magnitude)
    magnitude = stars['magnitude'][bright_stars]
    #設定輸出星球數量
    max_star_size = 200
    #輸出之星球依照視星等做大小變化
    marker_size = max_star_size * 10 ** (magnitude / -2.5)
    #設定畫布
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
    plt.subplots_adjust(left=0, right=1, top=0.98, bottom=0)
    #若是星座連線選項被勾選則執行
    if draw_lines_var.get():
        xy1 = stars[['x', 'y']].loc[edges_star1].values
        xy2 = stars[['x', 'y']].loc[edges_star2].values
        lines_xy = np.rollaxis(np.array([xy1, xy2]), 1)
        ax.add_collection(LineCollection(lines_xy, colors='#ffff', linewidths=0.15))
    #繪製散布圖
    ax.scatter(stars['x'][bright_stars], stars['y'][bright_stars],
               s=marker_size, color='white', marker='.', linewidths=0,
               zorder=2)
    
    #若是星座名稱選項被勾選則執行
    if draw_constellation_names_var.get():
        for constellation_name, constellation_stars in constellations_at_location.items():
            chinese_name = constellation_names_chinese.get(constellation_name, constellation_name)
            constellation_x = np.mean(stars.loc[list(constellation_stars)]['x'])
            constellation_y = np.mean(stars.loc[list(constellation_stars)]['y'])
            ax.text(constellation_x, constellation_y, chinese_name,
                    color='yellow', fontsize=8, ha='center', va='center')


    ax.set_aspect('equal')
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    plt.axis('off')
    when_datetime = datetime.strptime(when, '%Y-%m-%d %H:%M')
    #設定圖片標題
    ax.set_title(f"Observation Location: {location}, Time: {when_datetime.strftime('%Y-%m-%d %H:%M')}", loc='right',
                 color='white', fontsize=10)

    plt.savefig(filename, format='png', dpi=500)
    plt.close()

#建立星座中英文名稱對照表
constellation_names_chinese = {
    'And': '仙女座',
    'Ant': '唧筒座',
    'Aps': '天燕座',
    'Aql': '天鷹座',
    'Aqr': '寶瓶座',
    'Ara': '天壇座',
    'Ari': '白羊座',
    'Aur': '御夫座',
    'Boo': '牧夫座',
    'CMa': '大犬座',
    'CMi': '小犬座',
    'CVn': '獵犬座',
    'Cae': '雕具座',
    'Cam': '鹿豹座',
    'Cap': '魔羯座',
    'Car': '船底座',
    'Cas': '仙后座',
    'Cen': '半人馬座',
    'Cep': '仙王座',
    'Cet': '鯨魚座',
    'Cha': '蝘蜓座',
    'Cir': '圓規座',
    'Cnc': '巨蟹座',
    'Col': '天鴿座',
    'Com': '后髮座',
    'CrA': '南冕座',
    'CrB': '北冕座',
    'Crt': '巨爵座',
    'Cru': '南十字座',
    'Crv': '烏鴉座',
    'Cyg': '天鵝座',
    'Del': '海豚座',
    'Dor': '劍魚座',
    'Dra': '天龍座',
    'Equ': '小馬座',
    'Eri': '波江座',
    'For': '天爐座',
    'Gem': '雙子座',
    'Gru': '天鶴座',
    'Her': '武仙座',
    'Hor': '時鐘座',
    'Hya': '長蛇座',
    'Hyi': '水蛇座',
    'Ind': '印第安座',
    'LMi': '小獅座',
    'Lac': '蠍虎座',
    'Leo': '獅子座',
    'Lep': '天兔座',
    'Lib': '天秤座',
    'Lup': '豺狼座',
    'Lyn': '天貓座',
    'Lyr': '天琴座',
    'Men': '山案座',
    'Mic': '顯微鏡座',
    'Mon': '麒麟座',
    'Mus': '蒼蠅座',
    'Nor': '矩尺座',
    'Oct': '南極座',
    'Oph': '蛇夫座',
    'Ori': '獵戶座',
    'Pav': '孔雀座',
    'Peg': '飛馬座',
    'Per': '英仙座',
    'Phe': '鳳凰座',
    'Pic': '繪架座',
    'PsA': '南魚座',
    'Psc': '雙魚座',
    'Pup': '船尾座',
    'Pyx': '羅盤座',
    'Ret': '網罟座',
    'Scl': '玉夫座',
    'Sco': '天蝎座',
    'Sct': '盾牌座',
    'Ser': '巨蛇座',
    'Sex': '六分儀座',
    'Sge': '天箭座',
    'Sgr': '人馬座',
    'Tau': '金牛座',
    'Tel': '望遠鏡座',
    'TrA': '南三角座',
    'Tri': '三角座',
    'Tuc': '杜鵑座',
    'UMa': '大熊座',
    'UMi': '小熊座',
    'Vel': '船帆座',
    'Vir': '室女座',
    'Vol': '飛魚座',
    'Vul': '狐狸座',
}

#自訂函數4:執行
def on_submit(location_entry, year_entry, month_entry, day_entry, hour_entry, minute_entry, altitude_entry, azimuth_entry, draw_lines_var, draw_constellation_names_var):
    #必須填寫所有欄位才可執行，否則會跳error
    if any([entry.get() == '' for entry in (location_entry, year_entry, month_entry, day_entry, hour_entry, minute_entry, altitude_entry, azimuth_entry)]):
        tk.messagebox.showerror("Error", "請填寫所有輸入欄位")
        return
    location = location_entry.get()
    year = year_entry.get()
    month = month_entry.get()
    day = day_entry.get()
    hour = hour_entry.get()
    minute = minute_entry.get()
    when = f"{year}-{month}-{day} {hour}:{minute}"
    altitude = int(altitude_entry.get())
    azimuth = int(azimuth_entry.get())
    eph, stars, constellations = load_data()
    filename = f"{location}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    #取得兩個勾選項目的回傳值
    if draw_lines_var.get():
        create_star_chart(location, when, altitude, azimuth, eph, stars, constellations, filename, draw_lines_var, draw_constellation_names_var)
    elif draw_constellation_names_var.get():
        create_star_chart(location, when, altitude, azimuth, eph, stars, constellations, filename, draw_lines_var, draw_constellation_names_var)
    else:
        create_star_chart(location, when, altitude, azimuth, eph, stars, constellations, filename, draw_lines_var, draw_constellation_names_var)
    #下載完成時跳出完成視窗
    tk.messagebox.showinfo("Download Complete", f"Star chart saved as {filename}")

#自訂函數5-1:地點填寫除錯測試
def validate_location_entry(event=None):
    location_value = location_entry.get()
    if not location_value.strip():
        tk.messagebox.showerror("Error", "請輸入有效的位置")
        return
    # 使用 geopy 的 Nominatim 來檢查地址是否有效
    locator = Nominatim(user_agent='Spyder', timeout=10)
    try:
        location_data = locator.geocode(location_value)
        if location_data is None:
            tk.messagebox.showerror("Error", "找不到該位置，請輸入有效的位置")
            location_entry.delete(0, tk.END)  # 清空輸入
    except Exception as e:
        tk.messagebox.showerror("Error", "無法檢索位置資訊，請檢查網路連線或稍後再試")
        location_entry.delete(0, tk.END)

#自訂函數5-2:年份填寫除錯測試
def validate_year_entry(event=None):
    year_value = year_entry.get()
    if year_value:
        try:
            year = int(year_value)
            #de440.bsp支援之年份為1550~2650
            if year < 1550 or year > 2650:
                tk.messagebox.showerror("Error", "請輸入有效的年份(1550~2650)")
                year_entry.delete(0, tk.END)  # 清空輸入
        except ValueError:
            tk.messagebox.showerror("Error", "請輸入正確的年份(1550~2650)")
            year_entry.delete(0, tk.END) 
#建立閏年list
leap_year=[]
for year in range(1550,2651):
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        leap_year.append(year)

#自訂函數5-3:月份填寫除錯測試
def validate_month_entry(event=None):
    month_value = month_entry.get()
    if month_value:
        try:
            month = int(month_value)
            if month < 1 or month > 12:
                tk.messagebox.showerror("Error", "請輸入有效的月份(1~12)")
                month_entry.delete(0, tk.END)  # 清空輸入
        except ValueError:
            tk.messagebox.showerror("Error", "請輸入正確的月份(1~12)")
            month_entry.delete(0, tk.END) 

#自訂函數5-4:日期填寫除錯測試
def validate_day_entry(event=None):
    day_value = day_entry.get()
    month_value = month_entry.get()
    year_value = year_entry.get()
    if day_value:
        try:
            year = int(year_value)
            month = int(month_value)
            day = int(day_value)
            if day < 1 or day > 31:
                tk.messagebox.showerror("Error", "請輸入有效的日期(1~31)")
                day_entry.delete(0, tk.END) 
            #除錯無效搭配(如4月沒有30日)
            elif (month == 2 and day > 29) or (month in [4, 6, 9, 11] and day > 30):
                tk.messagebox.showerror("Error", "無效的日期搭配")
                day_entry.delete(0, tk.END) 
            #閏年檢驗
            elif (month == 2 and day==29 and (year not in leap_year)):
                tk.messagebox.showerror("Error", "該年不是閏年，2月沒有29日")
                day_entry.delete(0, tk.END)
        except ValueError:
            tk.messagebox.showerror("Error", "請輸入正確的日期")
            day_entry.delete(0, tk.END) 

#自訂函數5-5:小時填寫除錯測試
def validate_hour_entry(event=None):
    hour_value = hour_entry.get()
    if hour_value:
        try:
            hour = int(hour_value)
            if hour < 0 or hour > 23:
                tk.messagebox.showerror("Error", "請輸入有效的小時(0~23)")
                hour_entry.delete(0, tk.END)  # 清空輸入
        except ValueError:
            tk.messagebox.showerror("Error", "請輸入正確的小時(0~23)")
            hour_entry.delete(0, tk.END)

#自訂函數5-6:分鐘填寫除錯測試
def validate_minute_entry(event=None):
    minute_value = minute_entry.get()
    if minute_value:
        try:
            minute = int(minute_value)
            if minute < 0 or minute > 59:
                tk.messagebox.showerror("Error", "請輸入有效的分鐘(0~59)")
                minute_entry.delete(0, tk.END)  # 清空輸入
        except ValueError:
            tk.messagebox.showerror("Error", "請輸入正確的分鐘(0~59)")
            minute_entry.delete(0, tk.END)

#自訂函數5-7:高度角填寫除錯測試
def validate_altitude_entry(event=None):
    altitude_value = altitude_entry.get()
    if altitude_value:
        try:
            altitude = int(altitude_value)
            if altitude > 90:
                tk.messagebox.showerror("Error", "請輸入有效的仰角(0~90)")
                altitude_entry.delete(0, tk.END)  # 清空輸入
        except ValueError:
            tk.messagebox.showerror("Error", "請輸入正確的仰角(0~90)")
            altitude_entry.delete(0, tk.END)

#自訂函數5-8:方位角填寫除錯測試
def validate_azimuth_entry(event=None):
    azimuth_value = azimuth_entry.get()
    if azimuth_value:
        try:
            azimuth = int(azimuth_value)
            if azimuth > 360:
                tk.messagebox.showerror("Error", "請輸入有效的方位角(0~360)")
                azimuth_entry.delete(0, tk.END)  # 清空輸入
        except ValueError:
            tk.messagebox.showerror("Error", "請輸入正確的方位角(0~360)")
            azimuth_entry.delete(0, tk.END)

#自訂函數6:清空輸入框內容按鍵
def clear_entries():
    # 清空所有輸入框的內容
    location_entry.delete(0, tk.END)
    year_entry.delete(0, tk.END)
    month_entry.delete(0, tk.END)
    day_entry.delete(0, tk.END)
    hour_entry.delete(0, tk.END)
    minute_entry.delete(0, tk.END)
    altitude_entry.delete(0, tk.END)
    azimuth_entry.delete(0, tk.END)

#自訂函數7:tkinter
def main():
    root = tk.Tk()
    root.title("Star Chart Generator")
    #設定視窗大小及起始位置
    root.geometry('700x500+450+100')

    # 將icon之png檔轉為ico檔
    icon = Image.open("static/picture/astrology.png")
    icon.save('static/picture/astrology.ico')
    # 設定視窗icon
    root.iconbitmap('static/picture/astrology.ico')
    # 開啟背景圖片檔案
    bg_image = Image.open("static/picture/sky.jpg")
    # 修改圖片尺寸fit視窗大小
    bg_image_resized = bg_image.resize((700, 500))
    bg_photo = ImageTk.PhotoImage(bg_image_resized)
    #設定標籤、按鈕的格式
    style = ttk.Style()
    # style.configure("TEntry", foreground="white", background="black")
    style.configure("TCheckbutton", foreground="white", background="black")
    # style.configure("TButton", foreground="white", background="black")
    
    #將Entry內容設定為全域變數
    global location_entry, year_entry, month_entry, day_entry, hour_entry, minute_entry, altitude_entry, azimuth_entry
    
    # 設定背景圖片
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    #設定標籤、輸入格、輸入錯誤警告視窗
    ttk.Label(root, text="Location:", foreground="white", background="black").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    location_entry = ttk.Entry(root,style="TEntry")
    location_entry.grid(row=0, column=1, padx=5, pady=5)
    location_entry.bind("<FocusOut>", validate_location_entry)

    ttk.Label(root, text="Year:", foreground="white", background="black").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    year_entry = ttk.Entry(root, style="TEntry")
    year_entry.grid(row=1, column=1, padx=5, pady=5)
    year_entry.bind("<FocusOut>", validate_year_entry)

    ttk.Label(root, text="Month:", foreground="white", background="black").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    month_entry = ttk.Entry(root, style="TEntry")
    month_entry.grid(row=2, column=1, padx=5, pady=5)
    month_entry.bind("<FocusOut>", validate_month_entry)
    
    ttk.Label(root, text="Day:", foreground="white", background="black").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    day_entry = ttk.Entry(root, style="TEntry")
    day_entry.grid(row=3, column=1, padx=5, pady=5)
    day_entry.bind("<FocusOut>", validate_day_entry)

    ttk.Label(root, text="Hour:", foreground="white", background="black").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    hour_entry = ttk.Entry(root, style="TEntry")
    hour_entry.grid(row=4, column=1, padx=5, pady=5)
    hour_entry.bind("<FocusOut>", validate_hour_entry)
    
    ttk.Label(root, text="Minute:", foreground="white", background="black").grid(row=5, column=0, padx=5, pady=5, sticky="w")
    minute_entry = ttk.Entry(root, style="TEntry")
    minute_entry.grid(row=5, column=1, padx=5, pady=5)
    minute_entry.bind("<FocusOut>", validate_minute_entry)
    
    ttk.Label(root, text="Altitude:", foreground="white", background="black").grid(row=6, column=0, padx=5, pady=5, sticky="w")
    altitude_entry = ttk.Entry(root, style="TEntry")
    altitude_entry.grid(row=6, column=1, padx=5, pady=5)
    altitude_entry.bind("<FocusOut>", validate_altitude_entry)

    ttk.Label(root, text="Azimuth:", foreground="white", background="black").grid(row=7, column=0, padx=5, pady=5, sticky="w")
    azimuth_entry = ttk.Entry(root, style="TEntry")
    azimuth_entry.grid(row=7, column=1, padx=5, pady=5)
    azimuth_entry.bind("<FocusOut>", validate_azimuth_entry)

    #設定勾選項目
    draw_lines_var = tk.BooleanVar(root)
    draw_lines_checkbox = ttk.Checkbutton(root, text="Draw Constellation Lines", variable=draw_lines_var, style="TCheckbutton", onvalue=True, offvalue=False)
    draw_lines_checkbox.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    draw_constellation_names_var = tk.BooleanVar(root)
    draw_constellation_names_checkbox = ttk.Checkbutton(root, text="Show Constellation Names", variable=draw_constellation_names_var, style="TCheckbutton", onvalue=True, offvalue=False)
    draw_constellation_names_checkbox.grid(row=9, column=0, columnspan=2, padx=5, pady=5,sticky="w")


    #設定輸出按鈕
    ttk.Button(root, text="Generate Star Chart", command=partial(on_submit, location_entry, year_entry, month_entry, day_entry, hour_entry, minute_entry, altitude_entry, azimuth_entry, draw_lines_var,draw_constellation_names_var), style="TButton").grid(row=10, column=0, columnspan=2, padx=5, pady=5)
    #設定清空輸入格內容按鈕
    ttk.Button(root, text="Clear Entries", command=clear_entries).grid(row=11, column=0, columnspan=2, padx=5, pady=5)

    root.mainloop()
    return [location_entry, year_entry, month_entry, day_entry, hour_entry, minute_entry, altitude_entry, azimuth_entry, draw_lines_var,draw_constellation_names_var]

main()
