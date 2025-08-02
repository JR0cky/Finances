import locale
import calendar
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from db import *

# TODO Monatsbericht anzeigen lassen und optional exportieren + Tägliche ausgaben raus, nur Jahr und Monat und Fixkosten integrieren, dann Legende mit grouped bar chart

# Set locale to get month names in German
try:
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, '')  # fallback to system locale

def financial_summary_export(df, fixed_cost_df, income_dict):
    st.subheader("📊 Finanzübersicht")

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month

    years = sorted(df['year'].unique(), reverse=True)
    selected_year = st.selectbox("📆 Jahr auswählen", years, index=0, key="summary_year_select")

    default_month = datetime.today().month
    months = sorted(df[df['year'] == selected_year]['month'].unique())
    if default_month in months:
        default_index = months.index(default_month)
    else:
        default_index = 0

    selected_month = st.selectbox("📅 Monat auswählen", months, index=default_index,key="summary_month_select")

    df_month = df[(df['year'] == selected_year) & (df['month'] == selected_month)]
    df_year = df[df['year'] == selected_year]

    def build_summary(name, sub_df):
        total_expenses = sub_df["amount"].sum()
        total_fixed = fixed_cost_df["amount"].sum() if not fixed_cost_df.empty else 0
        total_income = income_dict.get("fixed", 0) + income_dict.get("variable", 0)
        balance = total_income - total_fixed - total_expenses

        return pd.DataFrame([{
            "Zeitraum": name,
            "Einkommen (€)": total_income,
            "Fixkosten (€)": total_fixed,
            "Variable Ausgaben (€)": total_expenses,
            "Saldo (€)": balance
        }])

    def export_report(name, sub_df):
        summary = build_summary(name, sub_df)
        spacer = pd.DataFrame({col: [""] for col in summary.columns})
        details = sub_df[["date", "description", "category", "amount"]].rename(columns={
            "date": "Datum", "description": "Beschreibung", "category": "Kategorie", "amount": "Betrag (€)"
        })

        all_rows = pd.concat([summary, spacer, details])
        return all_rows.to_csv(index=False).encode("utf-8")
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if len(df_month) > 0:
            csv_month = export_report(f"{calendar.month_name[selected_month]} {selected_year}", df_month)
            st.download_button(
                label="📥 Monatsbericht exportieren",
                data=csv_month,
                file_name=f"monatsbericht_{selected_year}_{selected_month}.csv",
                mime="text/csv"
            )
        else:
            st.info("Keine Ausgaben im ausgewählten Monat.")

    with col2:
        if len(df_year) > 0:
            csv_year = export_report(str(selected_year), df_year)
            st.download_button(
                label="📥 Jahresbericht exportieren",
                data=csv_year,
                file_name=f"jahresbericht_{selected_year}.csv",
                mime="text/csv"
            )
        else:
            st.info("Keine Ausgaben im ausgewählten Jahr.")

    return df_month, df_year


def bar_chart_grouped_by_month_category(df_year):
    df_year = df_year.copy()
    df_year['month_num'] = df_year['date'].dt.month
    df_year['month_name'] = df_year['month_num'].apply(lambda x: calendar.month_name[x])
    df_year['year'] = df_year['date'].dt.year.astype(str)

    grouped = df_year.groupby(['year', 'month_num', 'month_name', 'category'], as_index=False)['amount'].sum()
    grouped = grouped.sort_values('month_num')

    fig = px.bar(
        grouped,
        x='month_name',
        y='amount',
        color='category',
        barmode='group',  # grouped bars side by side
        title="Ausgaben nach Monat und Kategorie",
        labels={'month_name': '', 'amount': 'Betrag (€)'}
    )

    # Show year as x-axis title only if all data is from one year
    years = grouped['year'].unique()
    if len(years) == 1:
        fig.update_layout(xaxis_title=years[0])
    else:
        fig.update_layout(xaxis_title="Monat")

    fig.update_layout(xaxis_tickangle=-45)
    return fig


def spending_charts_tabs(df_month, df_year):
    tab1, tab2 = st.tabs(["📅 Monat", "📆 Jahr"])

    with tab1:
        if not df_month.empty:
            df_month = df_month.copy()
            df_month["month_label"] = df_month["date"].dt.strftime("%B %Y")
            month_label = df_month["month_label"].iloc[0]

            # Group by category for the single selected month
            grouped_month = df_month.groupby("category")["amount"].sum().reset_index()

            fig_grouped_month = px.bar(
                grouped_month,
                x="category",
                y="amount",
                color="category",
                title=f"Ausgaben pro Kategorie für {month_label}",
                labels={"amount": "Betrag (€)", "category": "Kategorie"},
            )
            fig_grouped_month.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig_grouped_month, use_container_width=True)

            # Line chart by day
            df_month['day'] = df_month['date'].dt.day
            trend_month = df_month.groupby("day")["amount"].sum().reset_index()

            fig_line_month = px.line(
                trend_month,
                x="day",
                y="amount",
                markers=True,
                title="Tägliche Ausgaben im Monat",
                labels={"day": "Tag", "amount": "Betrag (€)"},
            )
            fig_line_month.update_layout(
                xaxis_tickangle=0,
                xaxis=dict(
                    tickmode='linear',
                    dtick=1,
                    tick0=1,
                    title="Tag"
                )
            )
            st.plotly_chart(fig_line_month, use_container_width=True)
        else:
            st.info("Keine Ausgaben im aktuellen Monat.")

    with tab2:
        if not df_year.empty:
            df_year = df_year.copy()
            df_year['month_num'] = df_year['date'].dt.month
            df_year['month_name'] = df_year['month_num'].apply(lambda x: calendar.month_name[x])
            df_year['year'] = df_year['date'].dt.year.astype(str)

            fig_bar = bar_chart_grouped_by_month_category(df_year)
            st.plotly_chart(fig_bar, use_container_width=True)

            # Line chart by month number
            trend_year = df_year.groupby("month_num")["amount"].sum().reset_index()
            fig_line_year = px.line(
                trend_year,
                x="month_num",
                y="amount",
                markers=True,
                title="Monatliche Ausgaben im Jahr",
                labels={"month_num": "Monat", "amount": "Betrag (€)"},
            )
            fig_line_year.update_layout(
                xaxis_tickangle=0,
                xaxis=dict(
                    tickmode='linear',
                    dtick=1,
                    tick0=1,
                    title="Monat"
                )
            )
            st.plotly_chart(fig_line_year, use_container_width=True)
        else:
            st.info("Keine Ausgaben im aktuellen Jahr.")


# Main flow
conn = get_connection()
expenses_df = get_expenses(conn)
fixed_costs_df = get_fixed_costs(conn)
income_dict = {"fixed": 1800, "variable": 150}  # Replace with your actual logic

df_month, df_year = financial_summary_export(expenses_df, fixed_costs_df, income_dict)

st.markdown("---")
st.markdown("<br>", unsafe_allow_html=True)
spending_charts_tabs(df_month, df_year)
