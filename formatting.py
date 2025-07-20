import streamlit as st

def hide_menu():
    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    </style> """, unsafe_allow_html=True)
    st.markdown("""
        <style>

            div[data-testid="collapsedControl"]{
                display: none;
            }
            div[data-testid="InputInstructions"]{
                display: none;
            }
            div[data-testid="stToolbar"]{
                display: none;
            }
        </style>
        """, unsafe_allow_html=True)