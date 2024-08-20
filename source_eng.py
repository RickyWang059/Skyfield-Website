#!pip install skyfield
#!pip install timezonefinder
#!pip install geopy


from datetime import datetime
from geopy import Nominatim
from timezonefinder import TimezoneFinder
from pytz import timezone, utc
from skyfield.api import Star, load, wgs84
from skyfield.data import hipparcos, stellarium
from skyfield.projections import build_stereographic_projection
from matplotlib.collections import LineCollection
import numpy as np
import matplotlib.pyplot as plt


plt.rcParams['font.family'] = 'Microsoft JhengHei'
plt.rcParams['font.size'] = 15
plt.rcParams['axes.unicode_minus'] = False

constellation_names = {
    'And': 'Andromeda',
    'Ant': 'Antlia',
    'Aps': 'Apus',
    'Aql': 'Aquila',
    'Aqr': 'Aquarius',
    'Ara': 'Ara',
    'Ari': 'Aries',
    'Aur': 'Auriga',
    'Boo': 'Boötes',
    'CMa': 'Canis Major',
    'CMi': 'Canis Minor',
    'CVn': 'Canes Venatici',
    'Cae': 'Caelum',
    'Cam': 'Camelopardalis',
    'Cap': 'Capricornus',
    'Car': 'Carina',
    'Cas': 'Cassiopeia',
    'Cen': 'Centaurus',
    'Cep': 'Cepheus',
    'Cet': 'Cetus',
    'Cha': 'Chamaeleon',
    'Cir': 'Circinus',
    'Cnc': 'Cancer',
    'Col': 'Columba',
    'Com': 'Coma Berenices',
    'CrA': 'Corona Australis',
    'CrB': 'Corona Borealis',
    'Crt': 'Crater',
    'Cru': 'Crux',
    'Crv': 'Corvus',
    'Cyg': 'Cygnus',
    'Del': 'Delphinus',
    'Dor': 'Dorado',
    'Dra': 'Draco',
    'Equ': 'Equuleus',
    'Eri': 'Eridanus',
    'For': 'Fornax',
    'Gem': 'Gemini',
    'Gru': 'Grus',
    'Her': 'Hercules',
    'Hor': 'Horologium',
    'Hya': 'Hydra',
    'Hyi': 'Hydrus',
    'Ind': 'Indus',
    'LMi': 'Leo Minor',
    'Lac': 'Lacerta',
    'Leo': 'Leo',
    'Lep': 'Lepus',
    'Lib': 'Libra',
    'Lup': 'Lupus',
    'Lyn': 'Lynx',
    'Lyr': 'Lyra',
    'Men': 'Mensa',
    'Mic': 'Microscopium',
    'Mon': 'Monoceros',
    'Mus': 'Musca',
    'Nor': 'Norma',
    'Oct': 'Octans',
    'Oph': 'Ophiuchus',
    'Ori': 'Orion',
    'Pav': 'Pavo',
    'Peg': 'Pegasus',
    'Per': 'Perseus',
    'Phe': 'Phoenix',
    'Pic': 'Pictor',
    'PsA': 'Piscis Austrinus',
    'Psc': 'Pisces',
    'Pup': 'Puppis',
    'Pyx': 'Pyxis',
    'Ret': 'Reticulum',
    'Scl': 'Sculptor',
    'Sco': 'Scorpius',
    'Sct': 'Scutum',
    'Ser': 'Serpens',
    'Sex': 'Sextans',
    'Sge': 'Sagitta',
    'Sgr': 'Sagittarius',
    'Tau': 'Taurus',
    'Tel': 'Telescopium',
    'TrA': 'Triangulum Australe',
    'Tri': 'Triangulum',
    'Tuc': 'Tucana',
    'UMa': 'Ursa Major',
    'UMi': 'Ursa Minor',
    'Vel': 'Vela',
    'Vir': 'Virgo',
    'Vol': 'Volans',
    'Vul': 'Vulpecula'
}

def load_data4():
    eph = load('de440.bsp')
    with load.open(hipparcos.URL) as f:
        stars = hipparcos.load_dataframe(f)
    url = 'https://raw.githubusercontent.com/Stellarium/stellarium/master/skycultures/modern_st/constellationship.fab'
    with load.open(url) as f:
        constellations = stellarium.parse_constellations(f)
    return eph, stars, constellations

def collect_celestial_data4(location, when, altitude, azimuth, eph, stars, constellations):
    locator = Nominatim(user_agent='StarChartApp', timeout=10)
    location = locator.geocode(location)
    lat, long = location.latitude, location.longitude
    dt = datetime.strptime(when, '%Y-%m-%d %H:%M')
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=long, lat=lat)
    local = timezone(timezone_str)
    utc_dt = local.localize(dt, is_dst=None).astimezone(utc)
    t = load.timescale().from_datetime(utc_dt)
    observer = wgs84.latlon(latitude_degrees=lat, longitude_degrees=long).at(t)
    sun = eph['sun']
    earth = eph['earth']
    edges = [edge for name, edges in constellations for edge in edges]
    edges_star1 = [star1 for star1, star2 in edges]
    edges_star2 = [star2 for star1, star2 in edges]
    position = observer.from_altaz(alt_degrees=altitude, az_degrees=azimuth)
    ra, dec, distance = position.radec()
    center_object = Star(ra=ra, dec=dec)
    center = earth.at(t).observe(center_object)
    projection = build_stereographic_projection(center)
    star_positions = earth.at(t).observe(Star.from_dataframe(stars))
    stars['x'], stars['y'] = projection(star_positions)

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

def create_star_chart4(location, when, altitude, azimuth, eph, stars, constellations, filename, draw_lines, draw_constellation_names):
    stars, edges_star1, edges_star2, constellations_at_location = collect_celestial_data4(location, when, altitude, azimuth, eph, stars, constellations)
    limiting_magnitude = 10
    bright_stars = (stars.magnitude <= limiting_magnitude)
    magnitude = stars['magnitude'][bright_stars]
    max_star_size = 200
    marker_size = max_star_size * 10 ** (magnitude / -2.5)
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
    plt.subplots_adjust(left=0, right=1, top=0.98, bottom=0)
    if draw_lines:
        xy1 = stars[['x', 'y']].loc[edges_star1].values
        xy2 = stars[['x', 'y']].loc[edges_star2].values
        lines_xy = np.rollaxis(np.array([xy1, xy2]), 1)
        ax.add_collection(LineCollection(lines_xy, colors='#ffff', linewidths=0.15))
    ax.scatter(stars['x'][bright_stars], stars['y'][bright_stars], s=marker_size, color='white', marker='.', linewidths=0, zorder=2)
    if draw_constellation_names:
        for constellation_name, constellation_stars in constellations_at_location.items():
            name = constellation_names.get(constellation_name, constellation_name)
            constellation_x = np.mean(stars.loc[list(constellation_stars)]['x'])
            constellation_y = np.mean(stars.loc[list(constellation_stars)]['y'])
            ax.text(constellation_x, constellation_y, name, color='yellow', fontsize=8, ha='center', va='center')

    ax.set_aspect('equal')
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    plt.axis('off')
    when_datetime = datetime.strptime(when, '%Y-%m-%d %H:%M')
    ax.set_title(f"{location}, {when_datetime.strftime('%Y-%m-%d %H:%M')}", loc='right',
             color='white', fontsize=10)
    plt.savefig(filename, facecolor='black', dpi=500)
    plt.close()