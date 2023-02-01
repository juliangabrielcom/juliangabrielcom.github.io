import plotly.graph_objects as go
from plots import *
from calculations import *
from state_functions import *

st.set_page_config(layout="wide")
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("Acoustic Attenuation Version 0.3")

boot_values = {
    "init_temp": 21.0,
    "init_hum": 60,
    "init_pres": 1013,
    "init_dist": 15.0,
    "init_gain": 0.0,
    "init_q": 0.7,
    "cur_temp": 21.0,
    "cur_hum": 60,
    "cur_pres": 1013,
    "cur_dist": 15.0,
    "cur_gain": 0.0,
    "cur_q": 0.7
}

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

for key in boot_values.keys():
    if key not in st.session_state:
        st.session_state[key] = boot_values[key]


init_disp = calc_dissipation(f_analog, st.session_state.init_temp, st.session_state.init_hum,
                                 st.session_state.init_dist, st.session_state.init_pres)

init_gain = calc_dissipation(f_up, st.session_state.init_temp, st.session_state.init_hum,
                             st.session_state.init_dist, st.session_state.init_pres)

st.session_state['init_gain'] = init_gain

init_q = optimize_high_shelf_q_factor(f_digital, init_gain, f_analog_2_digital(f_up, f_s), init_disp)

st.session_state['init_q'] = init_q

abs_plot.add_trace(go.Scatter(x=f_analog, y=init_disp, mode='lines', line=dict(color='red'), name='Attenuation'))
abs_plot.add_trace(
    go.Scatter(x=f_analog, y=calc_high_shelf(f_digital, st.session_state.init_gain, f_analog_2_digital(f_up, f_s),
                                             init_q), mode='lines', line=dict(color='green'), name='Optimized Filter'))

cur_disp = calc_dissipation(f_analog, st.session_state.cur_temp, st.session_state.cur_hum,
                            st.session_state.cur_dist, st.session_state.cur_pres)
cur_gain = calc_dissipation(f_up, st.session_state.cur_temp, st.session_state.cur_hum, st.session_state.cur_dist,
                            st.session_state.cur_pres) - init_gain

st.session_state['cur_gain'] = init_gain

cur_q = optimize_high_shelf_q_factor(f_digital, st.session_state.cur_gain, f_analog_2_digital(f_up, f_s), cur_disp)

st.session_state['cur_q'] = cur_q

rel_plot.add_trace(go.Scatter(x=f_analog, y=cur_disp - init_disp, mode='lines', line=dict(color='red'),
                              name='Relative Attenuation'))
rel_plot.add_trace(
    go.Scatter(x=f_analog, y=calc_high_shelf(f_digital, cur_gain, f_analog_2_digital(f_up, f_s),
                                             cur_q), mode='lines', line=dict(color='green'), name='Optimized Filter'))


def set_init_temp():
    st.session_state.init_temp = st.session_state.init_temp_n


plot_container = st.container()
with plot_container:
    abs_half, rel_half = st.columns(2, gap="large")
    with abs_half:
        st.plotly_chart(abs_plot)
    with rel_half:
        st.plotly_chart(rel_plot)

value_container = st.container()
with value_container:
    c1, c2, c3, c4, c5, c6 = st.columns(6, gap="large")

    with c1:
        init_temp = st.number_input('Initial Temperature in °C', value=boot_values['init_temp'],
                                    step=0.1, min_value=-40.0, max_value=60.0, format="%.1f",
                                    on_change=set_init_temp, key='init_temp_n')
        init_hum = st.number_input('Initial Humidity in %', value=boot_values['init_hum'], step=1, min_value=1,
                                   max_value=100, on_change=set_init_hum, key='init_hum_n')
        init_pres = st.number_input('Initial Pressure in Pa', value=boot_values['init_pres'], step=1,
                                    min_value=850, max_value=1100, on_change=set_init_pres, key='init_pres_n')
        init_dist = st.number_input('Initial Distance in m', value=boot_values['init_dist'], step=0.1, min_value=0.0,
                                    max_value=1000.0, format="%.2f", on_change=set_init_dist, key='init_dist_n')
    with c2:
        st.text('Frequency:')
        st.text('Gain:')
        st.text('Q-Factor:')
        st.text('Band-Width:')

    with c3:
        st.text(str("{:.1f}".format(f_up/1000) + ' kHz'))
        st.text(str("{:.1f}".format(st.session_state.init_gain) + ' dB'))
        st.text(str("{:.2f}".format(st.session_state.init_q)))
        st.text(str("{:.2f}".format(q_to_bw(st.session_state.init_q))))

    with c4:
        cur_temp = st.number_input('Current Temperature in °C', value=boot_values['cur_temp'],
                                   step=0.1, min_value=-40.0, max_value=60.0, format="%.1f",
                                   on_change=set_cur_temp, key='cur_temp_n')
        cur_hum = st.number_input('Current Humidity in %', value=boot_values['cur_hum'],
                                  step=1, min_value=1, max_value=100, on_change=set_cur_hum, key='cur_hum_n')
        cur_pres = st.number_input('Current Pressure in Pa', value=boot_values['cur_pres'],
                                   step=1, min_value=850, max_value=1100,
                                   on_change=set_cur_pres, key='cur_pres_n')
        cur_dist = st.number_input('Current Distance in m', value=boot_values['cur_dist'],
                                   step=0.1, min_value=0.0, max_value=1000.0, format="%.2f",
                                   on_change=set_cur_dist, key='cur_dist_n')

    with c5:
        st.text('Frequency:')
        st.text('Gain:')
        st.text('Q-Factor:')
        st.text('Band-Width:')

    with c6:
        st.text(str("{:.1f}".format(f_up/1000) + ' kHz'))
        st.text(str("{:.1f}".format(st.session_state.cur_gain) + ' dB'))
        st.text(str("{:.2f}".format(st.session_state.cur_q)))
        st.text(str("{:.2f}".format(q_to_bw(st.session_state.cur_q))))

