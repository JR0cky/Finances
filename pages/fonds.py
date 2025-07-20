import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from db import *

# TODO Monat/Datum selber auswählen festbetrag eintragen (vorher letzten anzeigen) und aktueller wert + ansicht graph monatlicher verlauf, skala nach möglichekit anpasspar




def fund_tracker(conn):
    st.header("📊 Fonds-Entwicklung verwalten")

    action = st.radio("Aktion wählen", ["Neuen Fond hinzufügen", "Existierenden Fond aktualisieren"])

    if action == "Neuen Fond hinzufügen":
        with st.form("add_fund"):
            name = st.text_input("Name")
            fixed_amount = st.number_input("Monatlicher Festbetrag (€)", min_value=0.0, step=0.01, value=None, value=None)
            actual_value = st.number_input("Aktueller Wert (€)", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Hinzufügen")

            if submitted:
                insert_fund_entry(conn, name, fixed_amount, actual_value)
                st.success(f"Fonds '{name}' wurde hinzugefügt.")

    else:  # Update existing
        fund_names = get_all_fund_names(conn)
        selected_fund = st.selectbox("Fond auswählen", fund_names)
        latest_fixed = get_latest_fixed_amount(conn, selected_fund)

        with st.form("update_fund"):
            new_fixed = st.number_input("Monatlicher Festbetrag (€)", min_value=0.0, value=latest_fixed, step=0.01)
            actual_value = st.number_input("Aktueller Wert (€)", min_value=0.0, step=0.01, value=None)
            submitted = st.form_submit_button("Aktualisieren")

            if submitted:
                insert_fund_entry(conn, selected_fund, new_fixed, actual_value)
                st.success(f"Fond '{selected_fund}' wurde aktualisiert.")

    # Optional: show development plot
    st.markdown("---")
    st.subheader("📈 Entwicklung anzeigen")
    selected_plot_fund = st.selectbox("Fonds wählen", get_all_fund_names(conn), key="plot_select")
    history_df = get_fund_history(conn, selected_plot_fund)
    history_df['last_updated'] = pd.to_datetime(history_df['last_updated'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df['last_updated'],
        y=history_df['actual_value'],
        mode='lines+markers',
        name='Aktueller Wert'
    ))
    fig.add_trace(go.Scatter(
        x=history_df['last_updated'],
        y=history_df['fixed_amount'],
        mode='lines+markers',
        name='Festbetrag'
    ))
    fig.update_layout(
        title=f"Entwicklung von '{selected_plot_fund}'",
        yaxis_title="Betrag (€)",
        xaxis=dict(tickformat="%b %Y"),
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)



conn = get_connection()
fund_tracker(conn)