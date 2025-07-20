import time
import streamlit as st
import pandas as pd
from db import *
from datetime import date



def fixed_costs_editor(conn):
    st.subheader("🧱 Feste Ausgaben hinzufügen")

    with st.form("add_fixed_cost"):
        name = st.text_input("Name der Ausgabe")
        amount = st.number_input("Betrag (€)", min_value=0.0, step=0.01, format="%.2f", value=None)
        submitted = st.form_submit_button("➕ Hinzufügen")

        if submitted:
            if name:
                upsert_fixed_cost(conn, name, amount)
                st.success(f"'{name}' wurde gespeichert.")
                st.rerun()
            else:
                st.warning("Bitte gib einen Namen ein.")

    # Show existing fixed costs with delete buttons
    st.markdown("---")
    st.subheader("📋 Vorhandene Fixkosten")

    df = get_fixed_costs(conn)
    if df.empty:
        st.info("Noch keine Fixkosten eingetragen.")
    else:
        for i, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([4, 2, 3, 1])
            col1.write(row["name"])
            col2.write(f"{row['amount']:.2f} €")
            col3.write(f"🕒 {row['last_updated']}")
            if col4.button("🗑️", key=f"delete_{row['name']}"):
                delete_fixed_cost(conn, row["name"])
                st.success(f"'{row['name']}' gelöscht.")
                st.rerun()




def fixed_income_editor(conn):
    st.subheader("💰 Fixes Einkommen hinzufügen")

    with st.form("add_fixed_income"):
        name = st.text_input("Name der Einnahmequelle")
        amount = st.number_input("Betrag (€)", min_value=0.0, step=0.01, format="%.2f", value=None)
        submitted = st.form_submit_button("➕ Hinzufügen")

        if submitted:
            if name:
                upsert_fixed_income(conn, name, amount)
                st.success(f"'{name}' wurde gespeichert.")
                st.rerun()
            else:
                st.warning("Bitte gib einen Namen ein.")

    # Show existing fixed incomes with delete buttons
    st.markdown("---")
    st.subheader("📋 Vorhandene feste Einkommen")

    df = get_fixed_incomes(conn)
    if df.empty:
        st.info("Noch keine festen Einkommen eingetragen.")
    else:
        for i, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([4, 2, 3, 1])
            col1.write(row["name"])
            col2.write(f"{row['amount']:.2f} €")
            col3.write(f"🕒 {row['last_updated']}")
            if col4.button("🗑️", key=f"delete_income_{row['name']}"):
                delete_fixed_income(conn, row["name"])
                st.success(f"'{row['name']}' gelöscht.")
                st.rerun()




conn = get_connection()
fixed_costs_editor(conn)
fixed_income_editor(conn)