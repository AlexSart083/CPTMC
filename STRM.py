import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

class CantierSimulatorWeb:
    def __init__(self):
        # Profili asset predefiniti
        self.asset_profiles = {
            "Conservativo": [
                {"name": "Stocks", "return": 7.0, "volatility": 15.0, "allocation": 30.0, "min_return": -37.0, "max_return": 32.0},
                {"name": "Bond", "return": 3.0, "volatility": 5.0, "allocation": 50.0, "min_return": -17.0, "max_return": 12.0},
                {"name": "Gold", "return": 5.5, "volatility": 20.0, "allocation": 0.0, "min_return": -29.0, "max_return": 30.0},
                {"name": "REIT", "return": 4.5, "volatility": 15.0, "allocation": 0.0, "min_return": -17.0, "max_return": 15.0},
                {"name": "Commodities", "return": 2.8, "volatility": 25.0, "allocation": 0.0, "min_return": -35.0, "max_return": 37.0},  
                {"name": "Cash", "return": 1.0, "volatility": 0.5, "allocation": 20.0, "min_return": 0.0, "max_return": 4.0}                                 
            ],
            "Moderato": [
                {"name": "Stocks", "return": 7.0, "volatility": 15.0, "allocation": 60.0, "min_return": -37.0, "max_return": 32.0},
                {"name": "Bond", "return": 3.0, "volatility": 5.0, "allocation": 30.0, "min_return": -17.0, "max_return": 12.0},
                {"name": "Gold", "return": 5.5, "volatility": 20.0, "allocation": 0.0, "min_return": -29.0, "max_return": 30.0},
                {"name": "REIT", "return": 4.5, "volatility": 15.0, "allocation": 0.0, "min_return": -17.0, "max_return": 15.0},
                {"name": "Commodities", "return": 2.8, "volatility": 25.0, "allocation": 0.0, "min_return": -35.0, "max_return": 37.0},  
                {"name": "Cash", "return": 1.0, "volatility": 0.5, "allocation": 10.0, "min_return": 0.0, "max_return": 4.0}                    
            ],
            "Dinamico": [
                {"name": "Stocks", "return": 7.0, "volatility": 15.0, "allocation": 70.0, "min_return": -37.0, "max_return": 32.0},
                {"name": "Bond", "return": 3.0, "volatility": 5.0, "allocation": 10.0, "min_return": -17.0, "max_return": 12.0},
                {"name": "Gold", "return": 5.5, "volatility": 20.0, "allocation": 15.0, "min_return": -29.0, "max_return": 30.0},
                {"name": "REIT", "return": 4.5, "volatility": 15.0, "allocation": 0.0, "min_return": -17.0, "max_return": 15.0},
                {"name": "Commodities", "return": 2.8, "volatility": 25.0, "allocation": 0.0, "min_return": -35.0, "max_return": 37.0},   
                {"name": "Cash", "return": 1.0, "volatility": 0.5, "allocation": 5.0, "min_return": 0.0, "max_return": 4.0}     
            ],
            "Stock_Gold": [
                {"name": "Stocks", "return": 7.0, "volatility": 15.0, "allocation": 70.0, "min_return": -37.0, "max_return": 32.0},
                {"name": "Bond", "return": 3.0, "volatility": 5.0, "allocation": 0.0, "min_return": -17.0, "max_return": 12.0},
                {"name": "Gold", "return": 5.5, "volatility": 20.0, "allocation": 30.0, "min_return": -29.0, "max_return": 30.0},
                {"name": "REIT", "return": 4.5, "volatility": 15.0, "allocation": 0.0, "min_return": -17.0, "max_return": 15.0},
                {"name": "Commodities", "return": 2.8, "volatility": 25.0, "allocation": 0.0, "min_return": -35.0, "max_return": 37.0},   
                {"name": "Cash", "return": 1.0, "volatility": 0.5, "allocation": 0.0, "min_return": 0.0, "max_return": 4.0}     
            ],
            "Diversificato": [
                {"name": "Stocks", "return": 7.0, "volatility": 15.0, "allocation": 25.0, "min_return": -37.0, "max_return": 32.0},
                {"name": "Bond", "return": 3.0, "volatility": 5.0, "allocation": 25.0, "min_return": -17.0, "max_return": 12.0},
                {"name": "Gold", "return": 5.5, "volatility": 20.0, "allocation": 15.0, "min_return": -29.0, "max_return": 30.0},
                {"name": "REIT", "return": 4.5, "volatility": 15.0, "allocation": 15.0, "min_return": -17.0, "max_return": 15.0},
                {"name": "Commodities", "return": 2.8, "volatility": 25.0, "allocation": 10.0, "min_return": -35.0, "max_return": 37.0},  
                {"name": "Cash", "return": 1.0, "volatility": 0.5, "allocation": 10.0, "min_return": 0.0, "max_return": 4.0}     
            ]
        }

def main():
    st.set_page_config(
        page_title="Simulatore Monte Carlo Cantieri",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    simulator = CantierSimulatorWeb()
    
    # Header principale
    st.title("🏗️ Calcolo del Potenziale Temporale di Monitoraggio Cantieri")
    st.markdown("**Simulazione Monte Carlo per la pianificazione del retirement**")
    
    # Sidebar per parametri
    with st.sidebar:
        st.header("⚙️ Parametri di Simulazione")
        
        # Parametri generali
        st.subheader("📊 Parametri Generali")
        initial_amount = st.number_input("Cifra iniziale (€)", value=0.0, min_value=0.0, step=1.0)  # int
        years_to_retirement = st.number_input("Anni prima del pensionamento", value=25.0, min_value=1.0, max_value=50.0, step=1.0)  # int
        years_retired = st.number_input("Anni in pensione", value=25.0, min_value=1.0, max_value=50.0, step=1.0)  # int
        annual_contribution = st.number_input("Versamento annuo (€)", value=6000.0, min_value=0.0, step=500.0)  # int
        inflation = st.number_input("Inflazione annua (%)", value=2.5, min_value=0.0, max_value=10.0, step=0.1, format="%.2f")  # float
        withdrawal = st.number_input("Prelievo annuo in pensione (€)", value=12000.0, min_value=0.0, step=500.0)  # int
        n_simulations = st.selectbox("Numero di simulazioni", [1000, 5000, 10000], index=2)  # int
        
        # Profilo di rischio
        st.subheader("🎯 Profilo di Investimento")
        selected_profile = st.selectbox("Seleziona profilo:", list(simulator.asset_profiles.keys()), index=1)
    
    # Area principale divisa in colonne
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💼 Configurazione Portafoglio")
        
        # Carica profilo selezionato
        if st.button("🔄 Carica Profilo Selezionato"):
            st.session_state.current_assets = simulator.asset_profiles[selected_profile].copy()
        
        # Inizializza asset se non esistono
        if 'current_assets' not in st.session_state:
            st.session_state.current_assets = simulator.asset_profiles[selected_profile].copy()
        
        assets_data = []
        
        for i, asset in enumerate(st.session_state.current_assets):
            with st.expander(f"📈 {asset['name']}", expanded=False):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    name = st.text_input(f"Nome", value=asset['name'], key=f"name_{i}")
                    ret = st.number_input(f"Rendimento (%)", value=asset['return'], key=f"return_{i}", step=0.1, format="%.2f")
                    vol = st.number_input(f"Volatilità (%)", value=asset['volatility'], key=f"vol_{i}", step=0.1, format="%.2f")
                
                with col_b:
                    alloc = st.number_input(f"Allocazione (%)", value=asset['allocation'], key=f"alloc_{i}", step=1.0, format="%.2f")
                    min_ret = st.number_input(f"Rend. Min (%)", value=asset['min_return'], key=f"min_{i}", step=1.0, format="%.2f")
                    max_ret = st.number_input(f"Rend. Max (%)", value=asset['max_return'], key=f"max_{i}", step=1.0, format="%.2f")
                
                assets_data.append({
                    'name': name,
                    'return': ret,
                    'volatility': vol,
                    'allocation': alloc,
                    'min_return': min_ret,
                    'max_return': max_ret
                })
        
        total_allocation = sum(asset['allocation'] for asset in assets_data)
        if abs(total_allocation - 100.0) > 0.01:
            st.error(f"⚠️ Allocazione totale: {total_allocation:.1f}% (deve essere 100%)")
        else:
            st.success(f"✅ Allocazione corretta: {total_allocation:.1f}%")
        
        if st.button("⚖️ Resetta Allocazioni"):
          # equal_alloc = 100.0 / len(assets_data)
            equal_alloc = 0
            for i in range(len(assets_data)):
                assets_data[i]['allocation'] = equal_alloc
    
    with col2:
        st.subheader("📈 Grafico Allocazioni")
        if abs(total_allocation - 100.0) <= 0.01:
            df_alloc = pd.DataFrame([
                {'Asset': asset['name'], 'Allocazione': asset['allocation']}
                for asset in assets_data
            ])
            fig_pie = px.pie(df_alloc, values='Allocazione', names='Asset', title="Distribuzione del Portafoglio")
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.subheader("📋 Riassunto Asset")
        df_summary = pd.DataFrame(assets_data)
        st.dataframe(df_summary, use_container_width=True)
    
    st.markdown("---")
    
    if st.button("🚀 **ESEGUI SIMULAZIONE**", type="primary"):
        if abs(total_allocation - 100.0) > 0.01:
            st.error("❌ Correggi prima le allocazioni!")
            return
        
        total_deposited = initial_amount + (annual_contribution * years_to_retirement)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("🔄 Simulazione in corso..."):
            results = run_monte_carlo_simulation(
                assets_data, initial_amount, years_to_retirement, years_retired,
                annual_contribution, inflation / 100, withdrawal, n_simulations,
                progress_bar, status_text
            )
        
        show_results(results, total_deposited, n_simulations)

def run_monte_carlo_simulation(assets_data, initial_amount, years_to_retirement, 
                              years_retired, annual_contribution, inflation, 
                              withdrawal, n_simulations, progress_bar, status_text):
    
    mean_returns = [asset['return'] / 100 for asset in assets_data]
    volatilities = [asset['volatility'] / 100 for asset in assets_data]
    allocations = [asset['allocation'] / 100 for asset in assets_data]
    min_returns = [asset['min_return'] / 100 for asset in assets_data]
    max_returns = [asset['max_return'] / 100 for asset in assets_data]
    
    accumulation_balances = []
    final_results = []
    
    for sim in range(n_simulations):
        if sim % 100 == 0:
            progress_bar.progress((sim + 1) / n_simulations)
            status_text.text(f"Simulazione {sim + 1} di {n_simulations}")
        
        balance = initial_amount
        
        for year in range(int(years_to_retirement)):
            annual_returns = [np.random.normal(mean_returns[i], volatilities[i]) for i in range(len(mean_returns))]
            capped_returns = [max(min(annual_returns[i], max_returns[i]), min_returns[i]) for i in range(len(mean_returns))]
            annual_return = sum(capped_returns[i] * allocations[i] for i in range(len(mean_returns)))
            balance *= (1 + annual_return)
            balance += annual_contribution
            balance /= (1 + inflation)
        
        accumulation_balances.append(balance)
        
        for year in range(int(years_retired)):
            annual_returns = [np.random.normal(mean_returns[i], volatilities[i]) for i in range(len(mean_returns))]
            capped_returns = [max(min(annual_returns[i], max_returns[i]), min_returns[i]) for i in range(len(mean_returns))]
            annual_return = sum(capped_returns[i] * allocations[i] for i in range(len(mean_returns)))
            balance *= (1 + annual_return)
            balance /= (1 + inflation)
            balance -= withdrawal
            if balance < 0:
                balance = 0
                break
        
        final_results.append(balance)
    
    progress_bar.progress(1.0)
    status_text.text("✅ Simulazione completata!")
    
    return {'accumulation': accumulation_balances, 'final': final_results}


def show_results(results, total_deposited, n_simulations):
    st.markdown("---")
    st.header("🎯 Risultati della Simulazione")
    
    accumulation_balances = results['accumulation']
    final_results = results['final']
    
    avg_accumulation = np.mean(accumulation_balances)
    acc_25th = np.percentile(accumulation_balances, 25)
    acc_75th = np.percentile(accumulation_balances, 75)
    
    avg_final = np.mean(final_results)
    final_25th = np.percentile(final_results, 25)
    final_75th = np.percentile(final_results, 75)
    success_rate = sum(r > 0 for r in final_results) / n_simulations * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Totale Depositato", f"€{total_deposited:,.0f}")
    with col2:
        st.metric("📈 Valore Medio Accumulo", f"€{avg_accumulation:,.0f}")
    with col3:
        st.metric("✨ Valore Medio Finale", f"€{avg_final:,.0f}")
    with col4:
        st.metric("✅ Tasso di Successo", f"{success_rate:.1f}%")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Fase di Accumulo")
        acc_data = {
            'Percentile': ['25°', 'Medio', '75°'],
            'Valore (€)': [f"{acc_25th:,.0f}", f"{avg_accumulation:,.0f}", f"{acc_75th:,.0f}"]
        }
        st.table(pd.DataFrame(acc_data))
    
    with col2:
        st.subheader("🏁 Valori Finali")
        final_data = {
            'Percentile': ['25°', 'Medio', '75°'],
            'Valore (€)': [f"{final_25th:,.0f}", f"{avg_final:,.0f}", f"{final_75th:,.0f}"]
        }
        st.table(pd.DataFrame(final_data))
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_acc = px.histogram(x=accumulation_balances, nbins=50, title="Distribuzione Valori Fine Accumulo")
        fig_acc.update_xaxes(title="Valore (€)")
        fig_acc.update_yaxes(title="Frequenza")
        st.plotly_chart(fig_acc, use_container_width=True)
    
    with col2:
        fig_final = px.histogram(x=final_results, nbins=50, title="Distribuzione Valori Finali")
        fig_final.update_xaxes(title="Valore (€)")
        fig_final.update_yaxes(title="Frequenza")
        st.plotly_chart(fig_final, use_container_width=True)

    if success_rate >= 80:
        st.success(f"🎉 Ottimo! Con il {success_rate:.1f}% di probabilità di successo, ora si guarda i cantieri da Monte-Carlo")
    elif success_rate >= 60:
        st.warning(f"⚠️ Discreto. Con il {success_rate:.1f}% di successo, potresti dover considerare il tonno in scatola.")
    else:
        st.error(f"❌ Attenzione! Solo il {success_rate:.1f}% di probabilità di successo. La caritas ti aspetta.")

if __name__ == "__main__":
    main()

