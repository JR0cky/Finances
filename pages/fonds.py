import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from db import *

#TODO darstellung mit aufsummierung von eingezahltem betrag 

def show_growth(df):
    if len(df) < 2:
        st.info("Nicht genügend Daten zur Berechnung des Wachstums.")
        return

    df_sorted = df.sort_values("last_updated")
    first = df_sorted["actual_value"].iloc[0]
    last = df_sorted["actual_value"].iloc[-1]

    if first == 0:
        st.metric("📈 Wachstum", f"{last:.2f} €", delta="∞%" if last > 0 else "0%")
        return

    percent_change = ((last - first) / first) * 100
    delta = f"{percent_change:.2f}%"
    st.metric("📈 Wachstum", f"{last:.2f} €", delta=delta)



def show_fund_chart(df, fund_name, key_suffix=""):
    df = df.copy()
    df["last_updated"] = pd.to_datetime(df["last_updated"])
    df["cumulative_fixed"] = df["fixed_amount"].cumsum()

    # 📊 Rendite berechnen (Gewinn/Verlust gegenüber Einzahlungen)
    invested_total = df["cumulative_fixed"].iloc[-1]
    current_value = df["actual_value"].iloc[-1]
    profit = current_value - invested_total
    percent_return = (profit / invested_total) * 100 if invested_total > 0 else 0

    st.metric("📊 Gewinn / Verlust", f"{profit:.2f} €", delta=f"{percent_return:.2f}%")

    # 📈 Diagramm anzeigen
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['last_updated'],
        y=df['actual_value'],
        mode='lines+markers',
        name='📈 Aktueller Wert'
    ))

    fig.add_trace(go.Scatter(
        x=df['last_updated'],
        y=df['cumulative_fixed'],
        mode='lines+markers',
        name='💶 Eingezahlter Gesamtbetrag'
    ))

    fig.update_layout(
        title=f"Verlauf: {fund_name}",
        yaxis_title="Betrag (€)",
        xaxis=dict(tickformat="%b %Y"),
        template="plotly_white",
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True, key=f"chart_{fund_name}_{key_suffix}")



def fund_analysis(conn):
    st.subheader("📊 Fondsanalyse")

    fund_names = get_all_fund_names(conn)
    if not fund_names:
        st.info("Keine Fondsdaten vorhanden.")
        return

    selected_fund = st.selectbox("📌 Fonds auswählen", fund_names, key="fond_select")
    df = get_fund_history(conn, selected_fund)
    df["last_updated"] = pd.to_datetime(df["last_updated"]).dt.date
    today = pd.Timestamp.today().date() 

    if df.empty:
        st.warning("Keine Daten vorhanden.")
        return

    # --- Tabs für Zeiträume ---
    time_tabs = st.tabs(["🔁 Letzte 6 Monate", "🕛 Letzte 12 Monate", "📅 Letzte 24 Monate", "📖 Alle"])

    ranges = {
    "6": today - pd.DateOffset(months=6),
    "12": today - pd.DateOffset(months=12),
    "24": today - pd.DateOffset(months=24)
    }

    views = {
    0: df[df["last_updated"] >= ranges["6"].date()],
    1: df[df["last_updated"] >= ranges["12"].date()],
    2: df[df["last_updated"] >= ranges["24"].date()],
    3: df
    }

    for i, tab in enumerate(time_tabs):
        with tab:
            filtered_df = views[i]

            if filtered_df.empty:
                st.info("Keine Daten für diesen Zeitraum.")
                continue

            # Use a unique key suffix for each view
            key_suffix = f"{i}_months"

            # Pass key_suffix to ensure unique chart key
            show_fund_chart(filtered_df, selected_fund, key_suffix=key_suffix)
            show_growth(filtered_df)

            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 CSV herunterladen",
                data=csv,
                file_name=f"{selected_fund}_funds_{key_suffix}.csv",
                mime="text/csv",
                key=f"download_{selected_fund}_{key_suffix}"  # 🔑 unique key
            )

def reset_button(selected):
    st.session_state["delete_confirm"] = False
    delete_fund(conn, selected)
    time.sleep(2)
    st.success(f"✅ Fonds '{selected}' wurde gelöscht.")

def fund_tracker(conn):
    st.title("💼 Fondsverwaltung & Analyse")

    tab1, tab2 = st.tabs(["🔧 Verwaltung", "📊 Analyse"])

    # --- TAB 1: VERWALTUNG ---
    with tab1:
        st.subheader("📌 Fonds hinzufügen oder aktualisieren")

        action = st.radio("Aktion wählen", [
                "Neuen Fond hinzufügen",
                "Existierenden Fond aktualisieren",
                "Fonds löschen"  # Neue Option
            ])


        if action == "Neuen Fond hinzufügen":
            with st.form("add_fund"):
                name = st.text_input("📌 Fondsname")
                fixed_amount = st.number_input("💶 Monatlicher Festbetrag (€)", min_value=0.0, step=0.01)
                actual_value = st.number_input("📈 Aktueller Wert (€)", min_value=0.0, step=0.01)
                custom_date = st.date_input("📅 Datum wählen", value=pd.Timestamp.today().replace(day=1))

                submitted = st.form_submit_button("➕ Hinzufügen")
                if submitted and name:
                    insert_fund_entry(conn, name, fixed_amount, actual_value, timestamp=custom_date)
                    st.success(f"✅ Fonds '{name}' wurde hinzugefügt.")
        elif action == "Fonds löschen":
            fund_names = get_all_fund_names(conn)

            if not fund_names:
                st.info("ℹ️ Es sind keine Fonds zum Löschen vorhanden.")
                return

            if len(fund_names) <= 1:
                st.warning("⚠️ Der letzte verbleibende Fonds kann nicht gelöscht werden.")
                return


            # --- Select fond to delete ---
            selected_to_delete = st.selectbox("📌 Fonds zum Löschen auswählen", fund_names, key="fond_select_del")

            # --- Confirmation checkbox ---
            confirm = st.checkbox("Ich bin sicher, dass ich diesen Fonds löschen möchte", key="delete_confirm")

            # --- Delete button ---
            if confirm:
                st.button(f"🗑️ Fonds '{selected_to_delete}' löschen", key="delete_button", on_click=reset_button, args=(selected_to_delete,))
                    
        else:
            fund_names = get_all_fund_names(conn)
            if not fund_names:
                st.warning("⚠️ Keine Fonds vorhanden. Bitte zuerst einen hinzufügen.")
                return

            selected_fund = st.selectbox("📌 Fonds auswählen", fund_names)
            latest_fixed = get_latest_fixed_amount(conn, selected_fund)

            with st.form("update_fund"):
                new_fixed = st.number_input("💶 Monatlicher Festbetrag (€)", min_value=0.0, value=latest_fixed, step=0.01)
                actual_value = st.number_input("📈 Aktueller Wert (€)", min_value=0.0, step=0.01)
                custom_date = st.date_input("📅 Datum wählen", value=pd.Timestamp.today().replace(day=1))

                submitted = st.form_submit_button("🔄 Aktualisieren")
                if submitted:
                    insert_fund_entry(conn, selected_fund, new_fixed, actual_value, timestamp=custom_date)
                    st.success(f"✅ Fonds '{selected_fund}' wurde aktualisiert.")


    # --- TAB 2: ANALYSE ---
    with tab2:
        fund_analysis(conn)



# --- APP ENTRYPOINT ---
conn = get_connection()

# Optional: Nur einmal Dummy-Daten hinzufügen (z.B. in einem Button oder Setup-Skript)
# #clear_fund_data(conn)
# if "dummy_added" not in st.session_state:
#     populate_dummy_fund_data(conn)
#     st.session_state["dummy_added"] = True

fund_tracker(conn)