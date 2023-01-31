import streamlit as st
import plotly.graph_objects as go
from plots import *
from calculations import *

st.set_page_config(layout="wide")

with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("Acoustic Attenuation Version 0.3")

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

if 'init_temp' not in st.session_state:
    st.session_state['init_temp'] = 21.0

value_container = st.container()
with value_container:
    c1, c2, c3, c4, c5, c6 = st.columns(6, gap="large")

    with c1:
        st.session_state.init_temp = st.number_input('Initial Temperature in °C', value=21.0, step=0.1, min_value=-40.0, max_value=60.0,
                                    format="%.1f")
        init_hum = st.number_input('Initial Humidity in %', value=60, step=1, min_value=1, max_value=100)
        init_pres = st.number_input('Initial Pressure in Pa', value=1013, step=1, min_value=850, max_value=1100)
        init_dist = st.number_input('Initial Distance in m', value=15.0, step=0.1, min_value=0.0, max_value=1000.0,
                                    format="%.2f")

        init_disp = calc_dissipation(f_analog, st.session_state.init_temp, init_hum, init_dist, init_pres)
        init_gain = calc_dissipation(f_up, st.session_state.init_temp, init_hum, init_dist, init_pres)
        init_Q = optimize_high_shelf_q_factor(f_digital, init_gain, f_analog_2_digital(f_up, f_s), init_disp)
        abs_plot.add_trace(go.Scatter(x=f_analog, y=init_disp, mode='lines', line=dict(color='red')))
        abs_plot.add_trace(go.Scatter(x=f_analog, y=calc_high_shelf(f_digital, init_gain, f_analog_2_digital(f_up, f_s), init_Q)
                                      , mode='lines', line=dict(color='green')))

    with c2:
        st.text('Frequency 1:')
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
        cur_dist = st.number_input('Current Distance in m', value=15.0, step=0.1, min_value=0.0, max_value=1000.0,
                                   format="%.2f")

        cur_disp = calc_dissipation(f_analog, cur_temp, cur_hum, cur_dist, cur_pres)
        cur_gain = calc_dissipation(f_up, cur_temp, cur_hum, cur_dist, cur_pres)-init_gain
        cur_q = optimize_high_shelf_q_factor(f_digital, cur_gain, f_analog_2_digital(f_up, f_s), cur_disp)
        rel_plot.add_trace(go.Scatter(x=f_analog, y=cur_disp-init_disp, mode='lines', line=dict(color='red')))
        rel_plot.add_trace(
            go.Scatter(x=f_analog, y=calc_high_shelf(f_digital, cur_gain, f_analog_2_digital(f_up, f_s), cur_q)
                       , mode='lines', line=dict(color='green')))

    with c5:
        st.text('Frequency 2:')
        st.text('Gain 2:')
        st.text('Q-Factor 2:')
        st.text('Band-Width 2:')

    with c6:
        st.text(str("{:.1f}".format(f_up/1000) + ' kHz'))
        st.text(str("{:.1f}".format(cur_gain) + ' dB'))
        st.text(str("{:.2f}".format(cur_q)))
        st.text(str("{:.2f}".format(cur_q)))

plot_container = st.container()
with plot_container:
    abs_half, rel_half = st.columns(2, gap="large")
    with abs_half:
        st.plotly_chart(abs_plot)
    with rel_half:
        st.plotly_chart(rel_plot)

