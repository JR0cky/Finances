# main.py
import streamlit as st
from streamlit import Page, navigation
from formatting import hide_menu
from db import get_connection, init_db

st.set_page_config("📈 Finanzheini", layout="wide")  # Must be first

def main():
    hide_menu()
    conn = get_connection()
    init_db(conn)

    # Define pages
    intro = Page('pages/app.py', title='Einführung', icon='📖')
    fixed = Page('pages/fixed.py', title='Fixposten', icon='🔨')
    vary = Page('pages/vary.py', title='Variable Posten', icon='⚙️')
    charts = Page('pages/charts.py', title='Grafiken', icon='📊')
    fonds = Page('pages/fonds.py', title='Fond', icon='💹')

    # Run navigation
    nav = navigation([intro, fixed, vary, charts, fonds])
    nav.run()

if __name__ == "__main__":
    main()