import streamlit as st
from pages.charts import *
from pages.fonds import *

# --- Helper functions ---
def show_growth(df):
    if len(df) >= 2:
        first = df["actual_value"].iloc[0]
        last = df["actual_value"].iloc[-1]
        percent_change = ((last - first) / first) * 100 if first > 0 else 0
        delta = f"{percent_change:.2f}%"
        st.metric("📈 Wachstum", f"{last:.2f} €", delta=delta, label_visibility="hidden")
    else:
        st.info("Nicht genügend Daten zur Berechnung des Wachstums.")

def show_fund_chart(df, fund_name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['last_updated'], y=df['actual_value'],
        mode='lines+markers', name='Aktueller Wert'
    ))
    fig.add_trace(go.Scatter(
        x=df['last_updated'], y=df['fixed_amount'],
        mode='lines+markers', name='Festbetrag'
    ))
    fig.update_layout(
        title=f"Verlauf: {fund_name}",
        yaxis_title="Betrag (€)",
        xaxis=dict(tickformat="%b %Y"),
        template="plotly_white",
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_all_funds(conn):
    names = get_all_fund_names(conn)
    if not names:
        st.info("Noch keine Fonds vorhanden.")
        return

    fig = go.Figure()
    colors = px.colors.qualitative.Set2
    today = pd.Timestamp.today().date()

    for idx, name in enumerate(names):
        df = get_fund_history(conn, name)
        df["last_updated"] = pd.to_datetime(df["last_updated"]).dt.date
        df = df.dropna(subset=["actual_value"])  # NaN filtern

        if not df.empty:
            fig.add_trace(go.Scatter(
                x=df["last_updated"],
                y=df["actual_value"],
                mode="lines+markers",
                name=f"{name} ({df['actual_value'].iloc[-1]:.2f} €)",
                line=dict(color=colors[idx % len(colors)], width=3),
                marker=dict(symbol="circle", size=6),
                hovertemplate=f"{name}<br>%{{x}}: €%{{y:.2f}}"
            ))
        else:
            # Dummylinie für leere Fonds
            fig.add_trace(go.Scatter(
                x=[today],
                y=[0],
                mode="lines",
                name=f"{name} (keine Daten)",
                line=dict(dash="dot", color="gray"),
                showlegend=True,
                hoverinfo="skip"
            ))

    fig.update_layout(
        title="📈 Entwicklung aller Fonds",
        yaxis_title="Betrag (€)",
        xaxis_title="Datum",
        template="plotly_white",
        xaxis=dict(tickformat="%b %Y"),
        legend_title="Fonds",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Dashboard App ---

def financial_dashboard():

    conn = get_connection()
    expenses_df = get_expenses(conn)
    fixed_costs_df = get_fixed_costs(conn)
    income_dict = {"fixed": 1800, "variable": 150}  # Replace with real logic

    df_month, df_year = financial_summary_export(expenses_df, fixed_costs_df, income_dict)

    # --- KPIs ---

    total_income = income_dict.get("fixed", 0) + income_dict.get("variable", 0)
    total_fixed = fixed_costs_df["amount"].sum()
    total_variable = df_month["amount"].sum()
    total_funds = 0
    for name in get_all_fund_names(conn):
        hist = get_fund_history(conn, name)
        if not hist.empty:
            total_funds += hist["actual_value"].iloc[-1]
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Monatliches Einkommen", f"{total_income:.2f} €")
    col2.metric("💸 Monatliche Ausgaben (Fix + Variabel)", f"{(total_fixed + total_variable):.2f} €")
    col3.metric("💰 Fondsvermögen (aktuell)", f"{total_funds:.2f} €")

    st.divider()

    # --- Charts ---
    st.markdown("## 🔍 Ausgabenanalyse")
    spending_charts_tabs(df_month, df_year)

    st.divider()

    # --- Fondsanalyse ---
    st.markdown("## 📈 Fondsentwicklung")
    all_funds = get_all_fund_names(conn)
    if all_funds:
        selected_fund = st.selectbox("Fonds auswählen", all_funds)
        df_fund = get_fund_history(conn, selected_fund)
        df_fund["last_updated"] = pd.to_datetime(df_fund["last_updated"])

        show_growth(df_fund)
        show_fund_chart(df_fund, selected_fund)

        plot_all_funds(conn)

    else:
        st.info("Noch keine Fondsdaten vorhanden.")

if __name__ == "__main__":
    financial_dashboard()
# Plot: combine fixed_costs, variable expenses, fund investments over months
