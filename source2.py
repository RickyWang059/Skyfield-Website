#pip install starplot

# 匯入日期及時間套件
from datetime import datetime
#匯入地理編碼套件
from geopy import Nominatim
#匯入時區轉換套件
from timezonefinder import TimezoneFinder
from pytz import timezone, utc
# 匯入星空資料套件 
from skyfield.api import load, wgs84
from skyfield.projections import build_stereographic_projection
from skyfield.data import hipparcos, stellarium
#匯入現成的星空圖片生成套件
from starplot import MapPlot, Projection, Star
from starplot.styles import PlotStyle, extensions


# 自訂函數1:取得目標地資訊
def collect_celestial_data2(location, when, altitude, azimuth):
    locator = Nominatim(user_agent='StarChartApp', timeout=10)
    #利用Geopy將目的地名稱轉為經緯度
    location = locator.geocode(location)
    lat, lon = location.latitude, location.longitude
    #取得目標地當地時間，
    #將輸入的時間轉為datetime格式
    dt = datetime.strptime(when, '%Y-%m-%d %H:%M')
    #取得目標地之時區
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    #藉由目標地時區將輸入之時間轉為UTC標準時間
    local = timezone(timezone_str)
    utc_dt = local.localize(dt, is_dst=None).astimezone(utc)
    # 將UTC時間轉為skyfield可以處理的時間格式
    t = load.timescale().from_datetime(utc_dt)
    #利用wgs84建立觀察者經緯度
    observer = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon).at(t)
    #帶入觀察者之仰角及方位角
    position = observer.from_altaz(alt_degrees=altitude, az_degrees=azimuth)
    ra, dec, distance = position.radec()
    return lat, lon, utc_dt, ra, dec

# 自訂函數2:建立星座圖
def create_star_chart2(location, when, altitude, azimuth,filename, constellation_line,
                       constellation_border, ecliptic, celestial_equator, milky_way):
    #取得經緯度、時間、仰角、方位角
    lat, lon, utc_dt, ra, dec = collect_celestial_data2(location, when, altitude, azimuth)
    #利用現成函數畫圖
    p = MapPlot(
        projection=Projection.ZENITH,
        lat=lat,
        lon=lon,
        dt=utc_dt,
        ephemeris= "de440.bsp",
        style=PlotStyle().extend(
            extensions.NORD,
        ),
        resolution=1000,
    )
    #藉由表單勾選項目分別執行
    #星座連線與名稱
    if constellation_line:
        p.constellations()
    p.stars(mag=5.6, where_labels=[Star.magnitude < 2.1])
    p.dsos(mag=9, true_size=True, labels=None)
    #星座界線
    if constellation_border:
        p.constellation_borders()
    #黃道
    if ecliptic:
        p.ecliptic()
    #天球赤道
    if celestial_equator:
        p.celestial_equator()
    #銀河
    if milky_way:
        p.milky_way()
        
    p.marker(
        ra=ra.hours,
        dec=dec.degrees,
        label="Mel 111",
        style={
            "marker": {
                "size": 28,
                "symbol": "circle",
                "fill": "full",
                "color": "#ed7eed",
                "edge_color": "#e0c1e0",
                "alpha": 0.4,
                "zorder": 100,
            },
            "label": {
                "zorder": 200,
                "font_size": 12,
                "font_weight": "bold",
                "font_color": "#ed7eed",
                "font_alpha": 0.8,
            },
        },
    )

    p.export(filename, transparent=True)