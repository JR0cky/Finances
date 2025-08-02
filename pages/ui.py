import time
import streamlit as st
import pandas as pd
from db import *
from datetime import date

def handle_fixed_cost_submit(conn):
    name = st.session_state["fixed_cost_name"]
    amount = st.session_state["fixed_cost_amount"]

    if name:
        upsert_fixed_cost(conn, name, amount)
        st.session_state["fixed_cost_saved"] = True

    # Reset values
    st.session_state["fixed_cost_name"] = ""
    st.session_state["fixed_cost_amount"] = 0.0

    # Force rerun to clear UI and show success message
    st.rerun()


def sidebar_fixed_costs(conn):
    st.sidebar.header("🧱 Fixposten")
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.subheader("💳 Feste Ausgaben")

    if "fixed_cost_saved" not in st.session_state:
        st.session_state["fixed_cost_saved"] = False

    with st.sidebar.form("fixed_costs_form"):
        st.text_input("Name", key="fixed_cost_name")
        st.number_input("Betrag (€)", min_value=0.0, format="%.2f", key="fixed_cost_amount")
        st.form_submit_button("Ausgabe hinzufügen", on_click=handle_fixed_cost_submit, args=[conn])

    if st.session_state["fixed_cost_saved"]:
        st.sidebar.success("Fixposten gespeichert.")
        time.sleep(1)
        st.session_state["fixed_cost_saved"] = False
        st.rerun()



def handle_fixed_income_submit(conn):
    name = st.session_state["fixed_income_name"]
    amount = st.session_state["fixed_income_amount"]

    if name:
        upsert_fixed_income(conn, name, amount)
        st.session_state["fixed_income_saved"] = True

    # Reset input fields
    st.session_state["fixed_income_name"] = ""
    st.session_state["fixed_income_amount"] = 0.0

    st.rerun()


def sidebar_income(conn):
    st.sidebar.markdown("----", unsafe_allow_html=True)
    st.sidebar.subheader("💰 Fixes Einkommen")

    if "fixed_income_saved" not in st.session_state:
        st.session_state["fixed_income_saved"] = False

    with st.sidebar.form("fixed_income_form"):
        st.text_input("Einnahmequelle", key="fixed_income_name")
        st.number_input("Betrag (€)", min_value=0.0, format="%.2f", key="fixed_income_amount")
        st.form_submit_button("Einkommen hinzufügen", on_click=handle_fixed_income_submit, args=[conn])

    if st.session_state["fixed_income_saved"]:
        st.sidebar.success("Fixes Einkommen gespeichert.")
        time.sleep(1)
        st.session_state["fixed_income_saved"] = False
        st.rerun()

def edit_fixed_cost_ui(conn):
    st.subheader("✏️ Fixposten bearbeiten oder löschen")

    costs_df = get_fixed_costs(conn)
    if not costs_df.empty:
        display_options = [
            f"{row['name']} – {row['amount']:.2f} €"
            for _, row in costs_df.iterrows()
        ]
        display_to_name = {
            display: row['name'] for display, (_, row) in zip(display_options, costs_df.iterrows())
        }

        selected_display = st.selectbox("Fixposten auswählen", display_options, key="selected_fixed_cost_display")
        selected_name = display_to_name[selected_display]
        row = costs_df[costs_df["name"] == selected_name].iloc[0]

        with st.form("edit_fixed_cost_form"):
            new_name = st.text_input("Name", value=row["name"])
            new_amount = st.number_input("Betrag (€)", min_value=0.0, value=row["amount"], format="%.2f")

            col1, col2 = st.columns(2)
            if col1.form_submit_button("Aktualisieren"):
                upsert_fixed_cost(conn, new_name, new_amount)
                st.success("Fixposten aktualisiert!")
                st.rerun()
            if col2.form_submit_button("Löschen"):
                delete_fixed_cost(conn, row["name"])
                st.success("Fixposten gelöscht!")
                st.rerun()

def edit_fixed_income_ui(conn):
    st.subheader("✏️ Fixes Einkommen bearbeiten oder löschen")

    income_df = get_fixed_incomes(conn)
    if not income_df.empty:
        display_options = [
            f"{row['name']} – {row['amount']:.2f} €"
            for _, row in income_df.iterrows()
        ]
        display_to_name = {
            display: row['name'] for display, (_, row) in zip(display_options, income_df.iterrows())
        }

        selected_display = st.selectbox("Fixes Einkommen auswählen", display_options, key="selected_fixed_income_display")
        selected_name = display_to_name[selected_display]
        row = income_df[income_df["name"] == selected_name].iloc[0]

        with st.form("edit_fixed_income_form"):
            new_name = st.text_input("Einnahmequelle", value=row["name"])
            new_amount = st.number_input("Betrag (€)", min_value=0.0, value=row["amount"], format="%.2f")

            col1, col2 = st.columns(2)
            if col1.form_submit_button("Aktualisieren"):
                upsert_fixed_income(conn, new_name, new_amount)
                st.success("Einkommen aktualisiert!")
                st.rerun()
            if col2.form_submit_button("Löschen"):
                delete_fixed_income(conn, row["name"])
                st.success("Einkommen gelöscht!")
                st.rerun()




def add_expense_ui(conn):
    st.title("Mit Finanzen schlau, wird’s Leben genau 🧐")

    with st.form("entry_form"):
        entry_date = st.date_input("Datum", value=date.today(), key="")
        description = st.text_input("Beschreibung")
        category = st.selectbox(
            "Kategorie",
            ["Lebensmittel", "Utensilien", "Mobilität", "Freizeit", "Hund", "Wolle", "Familie", "Sonstiges"],
        )
        amount = st.number_input("Betrag (€)", format="%.2f")
        if st.form_submit_button("Eintrag hinzufügen"):
            insert_expense(conn, entry_date.isoformat(), description, category, amount)
            st.success("Eintrag hinzugefügt!")
            time.sleep(1)
            st.rerun()

# Function to edit expense
def edit_expense_ui(conn, df):

    if not df.empty:
        expenses = [row for _, row in df.iterrows() if row["date"] == date.today()]
        # Create display strings: "Beschreibung – Kategorie – Betrag €"
        # display_options = [
        #     f"{row['description']} – {row['category']} – {row['amount']:.2f} €"
        #     for _, row in df.iterrows()
        # ]
        display_options = expenses
        st.write(display_options)
        if len(display_options) > 0:


            # Map display string back to id
            display_to_id = {
                display: row['id'] for display, (_, row) in zip(display_options, df.iterrows())
            }
            st.subheader("✏️ Eintrag bearbeiten oder löschen")
            # Get previously selected display option or default to first
            selected_display = st.selectbox(
                "Eintrag auswählen",
                display_options,
                key="selected_expense_display"
            )

            # Get the corresponding ID from selection
            edit_id = display_to_id[selected_display]

            # Get row by ID
            row = df[df["id"] == edit_id].iloc[0]

            with st.form("edit_form"):
                new_date = st.date_input("Datum", value=pd.to_datetime(row["date"]))
                new_desc = st.text_input("Beschreibung", value=row["description"])
                new_cat = st.selectbox(
                    "Kategorie",
                    ["Lebensmittel", "Rent", "Utilities", "Mobilität", "Freizeit", "Sonstiges"],
                    index=["Lebensmittel", "Rent", "Utilities", "Mobilität", "Freizeit", "Sonstiges"].index(row["category"]),
                )
                new_amt = st.number_input("Betrag (€)", min_value=0.0, value=row["amount"], format="%.2f")

                col1, col2 = st.columns(2)

                if col1.form_submit_button("Aktualisieren"):
                    update_expense(conn, edit_id, new_date.isoformat(), new_desc, new_cat, new_amt)
                    st.success("Eintrag aktualisiert!")
                    st.rerun()

                if col2.form_submit_button("Löschen"):
                    delete_expense(conn, edit_id)
                    st.success("Eintrag gelöscht!")
                    st.rerun()





def hide_menu():
    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    </style> """, unsafe_allow_html=True)
    
    
    st.markdown("""
        <style>

            div[data-testid="collapsedControl"]{
                display: none;
            }
            div[data-testid="stHeadingWithAnchor"] a {
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
    