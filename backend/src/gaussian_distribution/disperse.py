import math
import numpy as np

# Константы
g = 9.80616  # Ускорение свободного падения

def sigma_y(c, d):
    def inner(x):
        theta = 0.017453293 * (c - d * math.log(x))
        return 465.11628 * x * math.tan(theta)
    return inner

SigmaY = {
    "A": sigma_y(24.1670, 2.5334),
    "B": sigma_y(18.3330, 1.8096),
    "C": sigma_y(12.5000, 1.0857),
    "D": sigma_y(8.3330, 0.72382),
    "E": sigma_y(6.2500, 0.54287),
    "F": sigma_y(4.1667, 0.36191),
}

def sigma_z(a, b, x):
    return a * (x ** b)

def sigma_za(x):
    if x <= 0.10:
        sz = sigma_z(122.800, 0.94470, x)
    elif x <= 0.15:
        sz = sigma_z(158.080, 1.05420, x)
    elif x <= 0.20:
        sz = sigma_z(170.220, 1.09320, x)
    elif x <= 0.25:
        sz = sigma_z(179.520, 1.12620, x)
    elif x <= 0.30:
        sz = sigma_z(217.410, 1.26440, x)
    elif x <= 0.40:
        sz = sigma_z(258.890, 1.40940, x)
    elif x <= 0.50:
        sz = sigma_z(346.750, 1.72830, x)
    elif x <= 3.11:
        sz = sigma_z(453.850, 2.11660, x)
    else:
        sz = 5000

    return min(sz, 5000)

def sigma_zb(x):
    if x <= 0.20:
        sz = sigma_z(90.673, 0.93198, x)
    elif x <= 0.40:
        sz = sigma_z(98.483, 0.98332, x)
    else:
        sz = sigma_z(109.300, 1.09710, x)

    return min(sz, 5000)

def sigma_zc(x):
    sz = sigma_z(61.141, 0.91465, x)
    return min(sz, 5000)

def sigma_zd(x):
    if x <= 0.30:
        sz = sigma_z(34.459, 0.86974, x)
    elif x <= 1.00:
        sz = sigma_z(32.093, 0.81066, x)
    elif x <= 3.00:
        sz = sigma_z(32.093, 0.64403, x)
    elif x <= 10.00:
        sz = sigma_z(33.504, 0.60486, x)
    elif x <= 30.00:
        sz = sigma_z(36.650, 0.56589, x)
    else:
        sz = sigma_z(44.053, 0.51179, x)

    return sz

def sigma_ze(x):
    if x <= 0.10:
        sz = sigma_z(24.260, 0.83660, x)
    elif x <= 0.30:
        sz = sigma_z(23.331, 0.81956, x)
    elif x <= 1.00:
        sz = sigma_z(21.628, 0.75660, x)
    elif x <= 2.00:
        sz = sigma_z(21.628, 0.63077, x)
    elif x <= 4.00:
        sz = sigma_z(22.534, 0.57154, x)
    elif x <= 10.00:
        sz = sigma_z(24.703, 0.50527, x)
    elif x <= 20.00:
        sz = sigma_z(26.970, 0.46713, x)
    elif x <= 40.00:
        sz = sigma_z(35.420, 0.37615, x)
    else:
        sz = sigma_z(47.618, 0.29592, x)

    return sz

def sigma_zf(x):
    if x <= 0.20:
        sz = sigma_z(15.209, 0.81558, x)
    elif x <= 0.70:
        sz = sigma_z(14.457, 0.78407, x)
    elif x <= 1.00:
        sz = sigma_z(13.953, 0.68465, x)
    elif x <= 2: 
        sz = sigma_z(13.953, .63227,x)
    elif x<=3: 
        sz=sigma_z(14.823, .54503,x)
    elif x<=7: 
        sz=sigma_z (16.187, .46490,x)
    elif x<=15: 
        sz=sigma_z (17.836, .41507,x)
    elif x<=30: 
        sz=sigma_z (22.651, .32681,x)
    elif x<=60: 
        sz=sigma_z (27.074, .27436,x)
    else: 
        sz=sigma_z (34.219, .21716,x)

    return sz

SigmaZ = {
	"A": sigma_za,
	"B": sigma_zb,
	"C": sigma_zc,
	"D": sigma_zd,
	"E": sigma_ze,
	"F": sigma_zf,
};


wind_profile = {
    "urban": {
        "A": .15,
        "B": .15,
        "C": .20,
        "D": .25,
        "E": .30,
        "F": .30,
    },
    "rural": {
        "A": .07,
        "B": .07,
        "C": .10,
        "D": .15,
        "E": .35,
        "F": .55,
    },
 }

def calc_uz(uzref: float, z: float, zref: float, pgcat: str, profile_type: str) -> float :
    p = wind_profile[profile_type][pgcat]
    uz = uzref * (z / zref) ** p
    return uz


# Calculate concentration at distance x along plume, at perpendicular offset y and height z

# inputs:
# x		[km]	receptor distance downwind along plume centreline
# y		[m]		receptor perpendicular offset from plume centreline
# z		[m]		receptor height
# Uz		[m/s]	wind speed at stack exit
# Q		[g/s]	pollutant mass emission rate
# H		[m]		effective stack height (includes plume rise)
# sigY	[f(m)]	y plume sigma formula (function of distance in m)
# sigZ	[f(m)]	z plume sigma formula (function of distance in m)

# returns:
# conc	[g/m3]	calculated receptor concentration

def C(x, y, z, Uz, Q, H, sigY, sigZ):
    # Ранний возврат, если координата вверх по потоку, так как концентрация всегда равна нулю
    if x <= 0:
        return 0

    Sz = sigZ(x)
    Sy = sigY(x)

    Sz2 = 2 * Sz * Sz
    Sy2 = 2 * Sy * Sy

    c1 = Q / (2 * np.pi * Uz * Sy * Sz)
    c2 = np.exp(-1 * (z - H) ** 2 / Sz2)
    c3 = np.exp(-1 * (z + H) ** 2 / Sz2)
    c4 = np.exp(-1 * y ** 2 / Sy2)

    conc = c1 * (c2 + c3) * c4  # г/м3
    if not np.isfinite(conc):
        conc = 0
    return conc



# Calculates the plume rise (dH) and a downwind plume offset (Xf), using Briggs model.

# inputs:
# us		[m/s]	wind velocity at stack tip
# vs		[m/s]	stack exit velocity
# ds		[m]		stack tip diameter
# Ts		[K]		stack tip temperature
# Ta		[K]		ambient temperature
# pgcat	[]		Pasquill-Gifford stability category

# returns:
# dH		[m]		plume rise
# Xf		[m]		plume rise offset
def plumeRise(us, vs, ds, Ts, Ta, pgcat):
    # Вычисление потока подъемной силы
    Fb = g * vs * ds ** 2 * (Ts - Ta) / (4 * Ts)
    # Вычисление импульсного потока
    Fm = vs ** 2 * ds ** 2 * Ta / (4 * Ts)

    Xf = 0
    dH = 0

    # Стабильные категории PG
    if pgcat in ["E", "F"]:
        eta = 0.020 if pgcat == "E" else 0.035
        s = g * eta / Ta
        dT = 0.019582 * Ts * vs * np.sqrt(s)

        # Подъемная сила доминирует
        if (Ts - Ta) >= dT:
            Xf = 2.0715 * us / np.sqrt(s)
            dH = 2.6 * (Fb / (us * s)) ** (1/3)
        else:
            Xf = 0
            prUN = 3.0 * ds * vs / us
            prS = 1.5 * (Fm / (us * np.sqrt(s))) ** (1/3)
            dH = min(prUN, prS)

    else:
        # Нестабильные или нейтральные категории PG
        if Fb < 55.0:
            dT = 0.0297 * Ts * vs ** (1/3) / ds ** (2/3)
            if (Ts - Ta) >= dT:
                Xf = 49.0 * Fb ** (5/8)
                dH = 21.425 * Fb ** (3/4) / us
            else:
                Xf = 0
                dH = 3.0 * ds * vs / us
        else:
            dT = 0.00575 * Ts * vs ** (2/3) / ds ** (1/3)
            if (Ts - Ta) >= dT:
                Xf = 119.0 * Fb ** (0.4)
                dH = 38.71 * Fb ** (0.6) / us
            else:
                Xf = 0
                dH = 3.0 * ds * vs / us

    return dH, Xf


# Iterate though each met hour and calculate concentrations across plan and slice grids.

# Uses a single source located at the origin, at a user specified height.

def iter_disp(rsdm, met, ambient_temp):
    # Смещения массива PNG
    yc = len(rsdm.rGrid) - 1
    zc = rsdm.hCoords.ymax / rsdm.hCoords.ygap

    for metline in met:
        # Вычисление эффективной скорости ветра на выходе из трубы 
        Uz = calc_uz(metline.u, rsdm.source.elevation, 10, metline.pgcat, rsdm.roughness)

        # Вычисление подъема дымовой трубы с использованием уравнений Бриггса
        Ts = rsdm.source.temp + 273.15
        dH, Xf = plumeRise(Uz, rsdm.source.velocity, rsdm.source.diameter, Ts, ambient_temp, metline.pgcat)
        H = rsdm.source.elevation + dH
        Q = rsdm.source.emission

        sinPHI = np.sin(metline.phi)
        cosPHI = np.cos(metline.phi)
        sigY = SigmaY[metline.pgcat]
        sigZ = SigmaZ[metline.pgcat]

        # Вычисление концентраций для плоской сетки (фиксированная высота сетки равна 0 м)
        x_index = 0
        for Xr in range(rsdm.rCoords.xmin, rsdm.rCoords.xmax + rsdm.rCoords.xgap, rsdm.rCoords.xgap):
            y_index = 0
            for Yr in range(rsdm.rCoords.ymin, rsdm.rCoords.ymax + rsdm.rCoords.ygap, rsdm.rCoords.ygap):
                if Uz > 0.5:
                    xx, yy = rsdm.source.wind_components(Xr, Yr, sinPHI, cosPHI)
                    xx -= (Xf / 1000)  # Коррекция подъема дымовой трубы
                    rsdm.rGrid[yc - y_index][x_index] += C(xx, yy, 0, Uz, Q, H, sigY, sigZ) / metline.hours
                y_index += 1
            x_index += 1

        # Вычисление концентраций для двумерного среза вдоль профиля высоты дымовой трубы
        z_index = 0
        offset = (rsdm.hCoords.xmax - rsdm.hCoords.xmin) / (2 * rsdm.hCoords.xgap)
        
        for Zh in range(0, int(rsdm.hCoords.ymax) + int(rsdm.hCoords.ygap), int(rsdm.hCoords.ygap)):
            x_index = 0
            if Uz > 0.5:
                for Xh in range(0, int(rsdm.hCoords.xmax) + int(rsdm.hCoords.xgap), int(rsdm.hCoords.xgap)):
                    xx = (Xh - Xf) / 1000  # Включает коррекцию подъема дымовой трубы
                    rsdm.hGrid[int(zc - z_index)][int(offset + x_index)] += C(xx, 0.0, Zh, Uz, Q, H, sigY, sigZ) / metline.hours
                    x_index += 1
            z_index += 1
