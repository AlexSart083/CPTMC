import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import json
import os

class CantierSimulatorWeb:
    def __init__(self):
        self.asset_profiles = self.load_asset_profiles()
    
    def load_asset_profiles(self):
        """Carica i profili asset dal file di configurazione"""
        config_file = 'config.json'
        
        if not os.path.exists(config_file):
            st.error(f"❌ File di configurazione '{config_file}' non trovato!")
            st.stop()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config['asset_profiles']
        except Exception as e:
            st.error(f"❌ Errore nel caricamento del file di configurazione: {str(e)}")
            st.stop()

def main():
    st.set_page_config(
        page_title="Simulatore Monte Carlo Investimenti",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    simulator = CantierSimulatorWeb()
    
    # Header principale
    st.title("🏗️ Simulazione Monte Carlo per la pianificazione del retirement")
    st.markdown("Questa applicazione ha scopo esclusivamente didattico e simula scenari puramente teorici basati su ipotesi semplificate. I risultati non devono essere interpretati come previsioni reali né come raccomandazioni di investimento. Nessuna informazione fornita costituisce consulenza finanziaria, patrimoniale o fiscale.")    
    
    # Sidebar per parametri
    with st.sidebar:
        st.header("⚙️ Parametri di Simulazione")
        
        # Parametri generali
        st.subheader("📊 Parametri Generali")
        initial_amount = st.number_input("Cifra iniziale (€)", value=0.0, min_value=0.0, step=500.0)
        years_to_retirement = st.number_input("Anni prima del pensionamento", value=40.0, min_value=0.0, max_value=99.0, step=1.0)
        years_retired = st.number_input("Anni in pensione", value=25.0, min_value=0.0, max_value=99.0, step=1.0)
        annual_contribution = st.number_input("Versamento annuo (€)", value=6000.0, min_value=0.0, step=500.0)
        inflation = st.number_input("Inflazione annua (%)", value=2.5, min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
        withdrawal = st.number_input("Prelievo annuo in pensione (€)", value=12000.0, min_value=0.0, step=500.0)
        n_simulations = st.selectbox("Numero di simulazioni", [1000, 5000, 10000], index=2)
        
        # Profilo di rischio
        st.subheader("🎯 Profilo di Investimento")
        selected_profile = st.selectbox("Seleziona profilo:", list(simulator.asset_profiles.keys()), index=1)
    
    # Area principale divisa in colonne
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💼 Configurazione Portafoglio")
        
        # Carica profilo selezionato
        if st.button("🔄 Carica Profilo Selezionato"):
            st.session_state.current_assets = [asset.copy() for asset in simulator.asset_profiles[selected_profile]]
        
        # Inizializza asset se non esistono
        if 'current_assets' not in st.session_state:
            st.session_state.current_assets = [asset.copy() for asset in simulator.asset_profiles[selected_profile]]
        
        assets_data = []
        
        for i, asset in enumerate(st.session_state.current_assets):
            with st.expander(f"📈 {asset['name']}", expanded=False):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Informazioni di sola lettura
                    st.text_input(f"Nome", value=asset['name'], key=f"name_{i}", disabled=True)
                    st.number_input(f"Rendimento (%)", value=asset['return'], key=f"return_{i}", step=0.1, format="%.2f", disabled=True)
                    st.number_input(f"Volatilità (%)", value=asset['volatility'], key=f"vol_{i}", step=0.1, format="%.2f", disabled=True)
                
                with col_b:
                    # Solo l'allocazione è modificabile
                    alloc = st.number_input(f"Allocazione (%)", value=asset['allocation'], key=f"alloc_{i}", step=1.0, format="%.2f", min_value=0.0, max_value=100.0)
                    st.number_input(f"Rend. Min (%)", value=asset['min_return'], key=f"min_{i}", step=1.0, format="%.2f", disabled=True)
                    st.number_input(f"Rend. Max (%)", value=asset['max_return'], key=f"max_{i}", step=1.0, format="%.2f", disabled=True)
                
                # Aggiorna l'allocazione nell'asset
                asset['allocation'] = alloc
                
                assets_data.append({
                    'name': asset['name'],
                    'return': asset['return'],
                    'volatility': asset['volatility'],
                    'allocation': alloc,
                    'min_return': asset['min_return'],
                    'max_return': asset['max_return']
                })
        
        total_allocation = sum(asset['allocation'] for asset in assets_data)
        
        # Pulsante per bilanciare le allocazioni
        col_reset, col_balance = st.columns(2)
        
        with col_reset:
            if st.button("🔄 Reset Allocazioni"):
                for asset in st.session_state.current_assets:
                    asset['allocation'] = 0.0
                st.rerun()
        
        with col_balance:
            if st.button("⚖️ Bilancia Allocazioni"):
                # Distribuisce equamente tra gli asset con allocazione > 0
                active_assets = [asset for asset in st.session_state.current_assets if asset['allocation'] > 0]
                if active_assets:
                    equal_alloc = 100.0 / len(active_assets)
                    for asset in st.session_state.current_assets:
                        if asset['allocation'] > 0:
                            asset['allocation'] = equal_alloc
                        else:
                            asset['allocation'] = 0.0
                    st.rerun()
        
        # Mostra stato allocazione
        if abs(total_allocation - 100.0) > 0.01:
            st.error(f"⚠️ Allocazione totale: {total_allocation:.1f}% (deve essere 100%)")
        else:
            st.success(f"✅ Allocazione corretta: {total_allocation:.1f}%")
    
    with col2:
        st.subheader("📈 Grafico Allocazioni")
        if abs(total_allocation - 100.0) <= 0.01:
            # Filtra solo gli asset con allocazione > 0 per il grafico
            active_assets = [asset for asset in assets_data if asset['allocation'] > 0]
            if active_assets:
                df_alloc = pd.DataFrame([
                    {'Asset': asset['name'], 'Allocazione': asset['allocation']}
                    for asset in active_assets
                ])
                fig_pie = px.pie(df_alloc, values='Allocazione', names='Asset', title="Distribuzione del Portafoglio")
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Nessun asset selezionato")
        
        st.subheader("📋 Riassunto Asset")
        # Mostra solo asset con allocazione > 0 nella tabella riassuntiva
        active_assets_df = pd.DataFrame([asset for asset in assets_data if asset['allocation'] > 0])
        if not active_assets_df.empty:
            st.dataframe(active_assets_df, use_container_width=True)
        else:
            st.info("Nessun asset attivo")
    
    st.markdown("---")
    
    if st.button("🚀 **ESEGUI SIMULAZIONE**", type="primary"):
        # Filtra solo asset con allocazione > 0
        active_assets = [asset for asset in assets_data if asset['allocation'] > 0]
        
        if not active_assets:
            st.error("❌ Seleziona almeno un asset con allocazione > 0!")
            return
        
        active_total = sum(asset['allocation'] for asset in active_assets)
        if abs(active_total - 100.0) > 0.01:
            st.error("❌ Correggi prima le allocazioni!")
            return
        
        total_deposited = initial_amount + (annual_contribution * years_to_retirement)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("🔄 Simulazione in corso..."):
            results = run_monte_carlo_simulation(
                active_assets, initial_amount, years_to_retirement, years_retired,
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
    
    # Calcolo statistiche per la fase di accumulo
    avg_accumulation = np.mean(accumulation_balances)
    acc_25th = np.percentile(accumulation_balances, 25)
    acc_50th = np.percentile(accumulation_balances, 50)  # Mediana
    acc_75th = np.percentile(accumulation_balances, 75)
    
    # Calcolo statistiche per i risultati finali
    avg_final = np.mean(final_results)
    final_25th = np.percentile(final_results, 25)
    final_50th = np.percentile(final_results, 50)  # Mediana
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
            'Statistica': ['Media', '25° percentile', '50° percentile', '75° percentile'],
            'Valore (€)': [f"{avg_accumulation:,.0f}", f"{acc_25th:,.0f}", f"{acc_50th:,.0f}", f"{acc_75th:,.0f}"]
        }
        st.table(pd.DataFrame(acc_data))
    
    with col2:
        st.subheader("🏁 Valori Finali")
        final_data = {
            'Statistica': ['Media', '25° percentile', '50° percentile', '75° percentile'],
            'Valore (€)': [f"{avg_final:,.0f}", f"{final_25th:,.0f}", f"{final_50th:,.0f}", f"{final_75th:,.0f}"]
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
