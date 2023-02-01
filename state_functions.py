import streamlit as st


def set_init_hum():
    st.session_state.init_hum = st.session_state.init_hum_n


def set_init_pres():
    st.session_state.init_pres = st.session_state.init_pres_n


def set_init_dist():
    st.session_state.init_dist = st.session_state.init_dist_n


def set_cur_temp():
    st.session_state.cur_temp = st.session_state.cur_temp_n


def set_cur_hum():
    st.session_state.cur_hum = st.session_state.cur_hum_n


def set_cur_pres():
    st.session_state.cur_pres = st.session_state.cur_pres_n


def set_cur_dist():
    st.session_state.cur_dist = st.session_state.cur_dist_n
