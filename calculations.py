import numpy as np


def calc_dissipation(f_analog, theta, hr, dist, p):
    pr = 1013.25
    t = 273.15 + theta
    to1 = 273.16
    to = 293.15

    p_sat = pr * 10 ** ((-6.8346 * (to1 / t) ** 1.261) + 4.6151)
    h = hr * (p_sat / p)
    fr_n = (p / pr) * (t / to) ** (-1 / 2) * (9 + 280 * h * np.exp(-4.170 * ((t / to) ** (-1 / 3) - 1)))
    fr_o = (p / pr) * (24 + 4.04 * 10 ** 4 * h * ((0.02 + h) / (0.391 + h)))
    z = 0.1068 * np.exp(-3352 / t) * (fr_n + np.square(f_analog) / fr_n) ** (-1)
    y = (t / to) ** (-5 / 2) * (0.01275 * np.exp(-2239.1 / t) * (fr_o + np.square(f_analog) / fr_o) ** (-1) + z)
    a = 8.686 * np.square(f_analog) * ((1.84 * 10 ** (-11) * (p / pr) ** (-1) * (t / to) ** (1 / 2)) + y)

    return a * dist


def calc_high_shelf(f_z, gain, f0_z, q_factor):
    z = np.exp(1j * f_z)
    alpha = np.sin(f0_z / (2 * q_factor))
    amp = 10 ** (2 * gain / 40)

    b0 = amp * (amp + 1 + (amp - 1) * np.cos(f0_z) + 2 * np.sqrt(amp) * alpha)
    b1 = -2 * amp * (amp - 1 + (amp + 1) * np.cos(f0_z))
    b2 = amp * (amp + 1 + (amp - 1) * np.cos(f0_z) - 2 * np.sqrt(amp) * alpha)

    a0 = amp + 1 - (amp - 1) * np.cos(f0_z) + 2 * np.sqrt(amp) * alpha
    a1 = 2 * (amp - 1 - (amp + 1) * np.cos(f0_z))
    a2 = amp + 1 - (amp - 1) * np.cos(f0_z) - 2 * np.sqrt(amp) * alpha

    h_mag_db = 20 * np.log10(np.absolute(
        np.divide(b0 + b1 * np.power(z, -1) + b2 * np.power(z, -2),
                  a0 + a1 * np.power(z, -1) + a2 * np.power(z, -2))))

    return h_mag_db


def optimize_high_shelf_q_factor(f_z, gain, f0_z, dissipation):
    q_factor = 0.707
    h_mag_db = calc_high_shelf(f_z, gain, f0_z, q_factor)
    e_old = np.sum(np.square(h_mag_db - dissipation))

    while True:
        q_factor = q_factor - 0.005
        h_mag_db = calc_high_shelf(f_z, gain, f0_z, q_factor)
        e_new = np.sum(np.square(h_mag_db - dissipation))

        if e_new > e_old:
            break
        else:
            e_old = e_new

    return q_factor


def create_f_analog(f_start_analog, f_end_analog, n):
    return np.logspace(np.log10(f_start_analog), np.log10(f_end_analog), num=int(n))


def create_f_digital(f_end_analog, fs, n):
    return np.logspace(np.log10(2 * np.pi * 20 / fs), np.log10(2 * np.pi * f_end_analog / fs), num=n)


def f_analog_2_digital(f_analog, fs):
    return 2 * np.pi * f_analog / fs