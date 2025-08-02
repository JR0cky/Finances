import time
import streamlit as st
import pandas as pd
from db import *
from datetime import date



def expenses_editor(conn):
    st.title("💸 Ausgabe hinzufügen")

    # --- Input Form ---
    with st.form("add_expense"):
        col1, col2 = st.columns(2)
        with col1:
            expense_date = st.date_input("Datum", value=date.today())
            category = st.selectbox(
                "Kategorie",
                ["Lebensmittel", "Utensilien", "Mobilität", "Freizeit", "Hund", "Wolle", "Familie", "Sonstiges"]
            )
        with col2:
            amount = st.number_input("Betrag (€)", min_value=0.0, step=0.01, format="%.2f", value=None)
            description = st.text_input("Beschreibung")

        submitted = st.form_submit_button("➕ Hinzufügen")
        if submitted:
            if amount > 0:
                insert_expense(conn, expense_date.isoformat(), description, category, amount)
                st.success("Ausgabe hinzugefügt.")
                st.rerun()
            else:
                st.warning("Bitte einen Betrag hinzufügen.")

    # --- Display today's expenses with delete buttons ---
    st.markdown("---")
    st.subheader("📋 Exraausgaben im letzten Monat")

    df = get_expenses(conn)
    df["date"] = pd.to_datetime(df["date"])
    today = pd.to_datetime(date.today())
    df_today = df[df["date"].dt.date == today.date()]

    if df_today.empty:
        st.info("Keine Ausgaben erfasst.")
    else:
        for i, row in df_today.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 3, 1])
            col1.write(row["description"])
            col2.write(f"{row['amount']:.2f} €")
            col3.write(row["category"])
            col4.write(f"📅 {row['date'].date().isoformat()}")
            if col5.button("🗑️", key=f"delete_exp_{row['id']}"):
                delete_expense(conn, row["id"])
                st.success(f"'{row['description']}' gelöscht.")
                st.rerun()


conn = get_connection()
expenses_editor(conn)