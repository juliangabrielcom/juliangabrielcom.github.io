import streamlit as st
import numpy as np
import plotly_express as px
import plotly.graph_objects as go
import time

st.set_page_config(layout="wide")

with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


basic_tick = np.arange(2, 10)
minor_ticks = np.concatenate((10*basic_tick[1:], 100*basic_tick, 1e3*basic_tick, 1e4*basic_tick), axis=0)


def get_plot(plot_type='absolute'):
    # plot = px.line(x=x, y=y, labels={'x': 'frequency in Hz', 'y': ''}, log_x=True)
    plot = px.line(labels={'x': 'frequency in Hz', 'y': ''}, log_x=True, range_x=[20, 20e3])
    plot.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor='white',
        minor=dict(tickvals=minor_ticks, showgrid=True, gridwidth=1, gridcolor='#262626'),
        showline=True, mirror=True, linewidth=1, linecolor='white'
    )
    plot.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor='white',
        zeroline=True, zerolinewidth=1, zerolinecolor='white',
        minor=dict(showgrid=True, gridwidth=1, gridcolor='#262626'),
        showline=True, mirror=True, linewidth=1, linecolor='white'
    )
    plot.update_layout(
        xaxis=dict(
            tickvals=[20, 100, 1e3, 10e3, 20e3],
            ticktext=['20', '100', '1k', '10k', '20k'],
            tickfont=dict(size=16),
            titlefont=dict(size=16),
            ticks="outside"
        ),
        yaxis=dict(
            tickfont=dict(size=16),
            ticks="outside"
        ),
        showlegend=False,
        margin=dict(pad=0)
    )
    if plot_type == 'absolute':
        plot.update_yaxes(
            range=[0, 18]
        )
        plot.update_layout(
            yaxis=dict(
                tickvals=[0, 3, 6, 9, 12, 15, 18],
                ticktext=['0dB', '3dB', '6dB', '9dB','12dB', '15dB', '18dB']
            )
        )
    if plot_type == 'relative':
        plot.update_yaxes(
            range=[-6, 6]
        )
        plot.update_layout(
            yaxis=dict(
                tickvals=[-6, -3, 0, 3, 6],
                ticktext=['-6dB', '-3dB', '0dB', '3dB', '6dB']
            )
        )

    return plot


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


st.title("Acoustic Attenuation")

f_s = 48e3
f_analog = create_f_analog(20, 20e3, 1e3)
f_digital = f_analog_2_digital(f_analog, f_s)
f_up = 12e3

abs_plot = get_plot('absolute')
rel_plot = get_plot('relative')

subtitle_container = st.container()
with subtitle_container:
    a1, a2 = st.columns(2, gap="large")

    with a1:
        st.text('Initial Filter Coefficient Estimation')

    with a2:
        st.text('Current Filter Coefficient Estimation')

value_container = st.container()
with value_container:
    c1, c2, c3, c4, c5, c6 = st.columns(6, gap="large")

    with c1:
        init_temp = st.number_input('Initial Temperature in °C', value=21.0, step=0.1, min_value=-40.0, max_value=60.0,
                                    format="%.1f")
        init_hum = st.number_input('Initial Humidity in %', value=60, step=1, min_value=1, max_value=100)
        init_pres = st.number_input('Initial Pressure in Pa', value=1013, step=1, min_value=850, max_value=1100)
        init_dist = st.number_input('Initial Distance in m', value=15.0, step=0.1, min_value=0.0, max_value=1000.0,
                                    format="%.2f")

        init_disp = calc_dissipation(f_analog, init_temp, init_hum, init_dist, init_pres)
        init_gain = calc_dissipation(f_up, init_temp, init_hum, init_dist, init_pres)
        init_Q = optimize_high_shelf_q_factor(f_digital, init_gain, f_analog_2_digital(f_up, f_s), init_disp)
        abs_plot.add_trace(go.Scatter(x=f_analog, y=init_disp, mode='lines', line=dict(color='red')))
        abs_plot.add_trace(go.Scatter(x=f_analog, y=calc_high_shelf(f_digital, init_gain, f_analog_2_digital(f_up, f_s), init_Q)
                                      , mode='lines', line=dict(color='green')))

    with c2:
        st.text('Frquency 1:')
        st.text('Gain 1:')
        st.text('Q-Factor 1:')
        st.text('Band-Width 1:')

    with c3:
        st.text(str("{:.1f}".format(f_up/1000) + ' kHz'))
        st.text(str("{:.1f}".format(init_gain) + ' dB'))
        st.text(str("{:.2f}".format(init_Q)))
        st.text(str("{:.2f}".format(init_Q)))

    with c4:
        cur_temp = st.number_input('Current Temperature in °C', value=21.0, step=0.1, min_value=-40.0, max_value=60.0,
                        format="%.1f")
        cur_hum = st.number_input('Current Humidity in %', value=60, step=1, min_value=1, max_value=100)
        cur_pres = st.number_input('Current Pressure in Pa', value=1013, step=1, min_value=850, max_value=1100)
        cur_dist = st.number_input('Current Distance in m', value=15.0, step=0.1, min_value=0.0, max_value=1000.0, format="%.2f")

        cur_disp = calc_dissipation(f_analog, cur_temp, cur_hum, cur_dist, cur_pres)
        cur_gain = calc_dissipation(f_up, cur_temp, cur_hum, cur_dist, cur_pres)-init_gain
        cur_Q = optimize_high_shelf_q_factor(f_digital, cur_gain, f_analog_2_digital(f_up, f_s), cur_disp)
        rel_plot.add_trace(go.Scatter(x=f_analog, y=cur_disp-init_disp, mode='lines', line=dict(color='red')))
        rel_plot.add_trace(
            go.Scatter(x=f_analog, y=calc_high_shelf(f_digital, cur_gain, f_analog_2_digital(f_up, f_s), cur_Q)
                       , mode='lines', line=dict(color='green')))

    with c5:
        st.text('Frequency 2:')
        st.text('Gain 2:')
        st.text('Q-Factor 2:')
        st.text('Band-Width 2:')

    with c6:
        st.text(str("{:.1f}".format(f_up/1000) + ' kHz'))
        st.text(str("{:.1f}".format(cur_gain) + ' dB'))
        st.text(str("{:.2f}".format(cur_Q)))
        st.text(str("{:.2f}".format(cur_Q)))

plot_container = st.container()
with plot_container:
    abs_half, rel_half = st.columns(2, gap="large")
    with abs_half:
        st.plotly_chart(abs_plot)
    with rel_half:
        st.plotly_chart(rel_plot)

