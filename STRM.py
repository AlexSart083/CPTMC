import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import json
import os

class CantierSimulatorWeb:
    def __init__(self):
        self.config = self.load_config()
        self.asset_profiles = self.config['asset_profiles']
        self.asset_characteristics = self.config['asset_characteristics']
        self.original_characteristics = self.config['asset_characteristics'].copy()
    
    def load_config(self):
        """Carica i profili asset e le caratteristiche dal file di configurazione"""
        config_file = 'config.json'
        
        if not os.path.exists(config_file):
            st.error(f"❌ File di configurazione '{config_file}' non trovato!")
            st.stop()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
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
        years_to_retirement = st.number_input("Anni prima del pensionamento", value=25.0, min_value=0.0, max_value=99.0, step=1.0)
        years_retired = st.number_input("Anni in pensione", value=25.0, min_value=0.0, max_value=99.0, step=1.0)
        annual_contribution = st.number_input("Versamento annuo (€)", value=6000.0, min_value=0.0, step=500.0)
        inflation = st.number_input("Inflazione annua (%)", value=2.5, min_value=0.0, max_value=10.0, step=0.1, format="%.2f")
        withdrawal = st.number_input("Prelievo annuo in pensione (€)", value=12000.0, min_value=0.0, step=500.0)
        n_simulations = st.selectbox("Numero di simulazioni", [1000, 5000, 10000], index=2)
        
        # Profilo di rischio
        st.subheader("🎯 Profilo di Investimento")
        selected_profile = st.selectbox("Seleziona profilo:", list(simulator.asset_profiles.keys()), index=1)
    
    # Inizializza le caratteristiche asset nel session state se non esistono
    if 'asset_characteristics' not in st.session_state:
        st.session_state.asset_characteristics = simulator.asset_characteristics.copy()
    
    # Tab per organizzare le sezioni - RINOMINATA LA TERZA SCHEDA
    tab1, tab2, tab3 = st.tabs(["💼 Portafoglio", "📊 Caratteristiche Asset", "🎲 Simulazione"])
    
    with tab1:
        st.subheader("💼 Configurazione Portafoglio")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔄 Carica Profilo Selezionato"):
                st.session_state.current_assets = [asset.copy() for asset in simulator.asset_profiles[selected_profile]]
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset Allocazioni"):
                if 'current_assets' in st.session_state:
                    for asset in st.session_state.current_assets:
                        asset['allocation'] = 0.0
                    st.rerun()
        
        with col3:
            if st.button("⚖️ Bilancia Allocazioni"):
                if 'current_assets' in st.session_state:
                    active_assets = [asset for asset in st.session_state.current_assets if asset['allocation'] > 0]
                    if active_assets:
                        equal_alloc = 100.0 / len(active_assets)
                        for asset in st.session_state.current_assets:
                            if asset['allocation'] > 0:
                                asset['allocation'] = equal_alloc
                            else:
                                asset['allocation'] = 0.0
                        st.rerun()
        
        # Inizializza asset se non esistono
        if 'current_assets' not in st.session_state:
            st.session_state.current_assets = [asset.copy() for asset in simulator.asset_profiles[selected_profile]]
        
        # Tabella modificabile per il portafoglio
        st.subheader("📋 Configurazione Asset")
        
        # Crea DataFrame per editing
        portfolio_data = []
        for asset in st.session_state.current_assets:
            portfolio_data.append({
                'Nome Asset': asset['name'],
                'Allocazione (%)': asset['allocation'],
                'TER (%)': asset['ter']
            })
        
        df_portfolio = pd.DataFrame(portfolio_data)
        
        # Editor di tabella
        edited_df = st.data_editor(
            df_portfolio,
            column_config={
                "Nome Asset": st.column_config.TextColumn("Nome Asset", disabled=True),
                "Allocazione (%)": st.column_config.NumberColumn(
                    "Allocazione (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    format="%.2f"
                ),
                "TER (%)": st.column_config.NumberColumn(
                    "TER (%)",
                    min_value=0.0,
                    max_value=5.0,
                    step=0.01,
                    format="%.3f"
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Aggiorna i dati nel session state
        for i, asset in enumerate(st.session_state.current_assets):
            asset['allocation'] = edited_df.iloc[i]['Allocazione (%)']
            asset['ter'] = edited_df.iloc[i]['TER (%)']
        
        # Verifica allocazione
        total_allocation = sum(asset['allocation'] for asset in st.session_state.current_assets)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if abs(total_allocation - 100.0) > 0.01:
                st.error(f"⚠️ Allocazione totale: {total_allocation:.1f}% (deve essere 100%)")
            else:
                st.success(f"✅ Allocazione corretta: {total_allocation:.1f}%")
        
        with col2:
            # Grafico allocazioni
            active_assets = [asset for asset in st.session_state.current_assets if asset['allocation'] > 0]
            if active_assets and abs(total_allocation - 100.0) <= 0.01:
                df_alloc = pd.DataFrame([
                    {'Asset': asset['name'], 'Allocazione': asset['allocation']}
                    for asset in active_assets
                ])
                fig_pie = px.pie(df_alloc, values='Allocazione', names='Asset', 
                               title="Distribuzione del Portafoglio")
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Nessun asset attivo o allocazione non valida")
    
    with tab2:
        st.subheader("📊 Caratteristiche degli Asset")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🔄 Reset a Valori Originali"):
                st.session_state.asset_characteristics = simulator.original_characteristics.copy()
                st.rerun()
        
        # Crea DataFrame per le caratteristiche
        characteristics_data = []
        for asset_name, characteristics in st.session_state.asset_characteristics.items():
            characteristics_data.append({
                'Nome Asset': asset_name,
                'Rendimento (%)': characteristics['return'],
                'Volatilità (%)': characteristics['volatility'],
                'Rendimento Min (%)': characteristics['min_return'],
                'Rendimento Max (%)': characteristics['max_return']
            })
        
        df_characteristics = pd.DataFrame(characteristics_data)
        
        # Editor di tabella per caratteristiche
        edited_characteristics = st.data_editor(
            df_characteristics,
            column_config={
                "Nome Asset": st.column_config.TextColumn("Nome Asset", disabled=True),
                "Rendimento (%)": st.column_config.NumberColumn(
                    "Rendimento (%)",
                    min_value=-50.0,
                    max_value=50.0,
                    step=0.1,
                    format="%.2f"
                ),
                "Volatilità (%)": st.column_config.NumberColumn(
                    "Volatilità (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    format="%.2f"
                ),
                "Rendimento Min (%)": st.column_config.NumberColumn(
                    "Rendimento Min (%)",
                    min_value=-100.0,
                    max_value=100.0,
                    step=0.1,
                    format="%.2f"
                ),
                "Rendimento Max (%)": st.column_config.NumberColumn(
                    "Rendimento Max (%)",
                    min_value=-100.0,
                    max_value=100.0,
                    step=0.1,
                    format="%.2f"
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Aggiorna i dati nel session state
        for i, (asset_name, _) in enumerate(st.session_state.asset_characteristics.items()):
            st.session_state.asset_characteristics[asset_name] = {
                'return': edited_characteristics.iloc[i]['Rendimento (%)'],
                'volatility': edited_characteristics.iloc[i]['Volatilità (%)'],
                'min_return': edited_characteristics.iloc[i]['Rendimento Min (%)'],
                'max_return': edited_characteristics.iloc[i]['Rendimento Max (%)']
            }
    
    with tab3:
        st.subheader("🚀 Esecuzione Simulazione")
        
        if st.button("🚀 **ESEGUI SIMULAZIONE**", type="primary"):
            # Filtra solo asset con allocazione > 0
            active_assets = [asset for asset in st.session_state.current_assets if asset['allocation'] > 0]
            
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
                    active_assets, st.session_state.asset_characteristics,
                    initial_amount, years_to_retirement, years_retired,
                    annual_contribution, inflation / 100, withdrawal, n_simulations,
                    progress_bar, status_text
                )
            
            show_results(results, total_deposited, n_simulations, active_assets)

def run_monte_carlo_simulation(assets_data, asset_characteristics, initial_amount, 
                              years_to_retirement, years_retired, annual_contribution, 
                              inflation, withdrawal, n_simulations, progress_bar, status_text):
    
    accumulation_balances = []
    final_results = []
    
    for sim in range(n_simulations):
        if sim % 100 == 0:
            progress_bar.progress((sim + 1) / n_simulations)
            status_text.text(f"Simulazione {sim + 1} di {n_simulations}")
        
        balance = initial_amount
        
        # Fase di accumulo
        for year in range(int(years_to_retirement)):
            annual_return = 0.0
            
            # Calcola il rendimento del portafoglio
            for asset in assets_data:
                asset_name = asset['name']
                allocation = asset['allocation'] / 100
                ter = asset['ter'] / 100
                
                characteristics = asset_characteristics[asset_name]
                mean_return = characteristics['return'] / 100
                volatility = characteristics['volatility'] / 100
                min_return = characteristics['min_return'] / 100
                max_return = characteristics['max_return'] / 100
                
                # Genera rendimento random per l'asset
                random_return = np.random.normal(mean_return, volatility)
                # Cap il rendimento tra min e max
                capped_return = max(min(random_return, max_return), min_return)
                # Sottrai il TER
                net_return = capped_return - ter
                
                # Contributo al portafoglio
                annual_return += net_return * allocation
            
            balance *= (1 + annual_return)
            balance += annual_contribution
            balance /= (1 + inflation)
        
        accumulation_balances.append(balance)
        
        # Fase di pensionamento
        for year in range(int(years_retired)):
            annual_return = 0.0
            
            # Calcola il rendimento del portafoglio
            for asset in assets_data:
                asset_name = asset['name']
                allocation = asset['allocation'] / 100
                ter = asset['ter'] / 100
                
                characteristics = asset_characteristics[asset_name]
                mean_return = characteristics['return'] / 100
                volatility = characteristics['volatility'] / 100
                min_return = characteristics['min_return'] / 100
                max_return = characteristics['max_return'] / 100
                
                # Genera rendimento random per l'asset
                random_return = np.random.normal(mean_return, volatility)
                # Cap il rendimento tra min e max
                capped_return = max(min(random_return, max_return), min_return)
                # Sottrai il TER
                net_return = capped_return - ter
                
                # Contributo al portafoglio
                annual_return += net_return * allocation
            
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

def show_results(results, total_deposited, n_simulations, active_assets):
    st.markdown("---")
    st.header("🎯 Risultati della Simulazione")
    
    # AGGIUNTA: Tabella riassuntiva Asset Allocation
    st.subheader("📊 Asset Allocation Utilizzata")
    
    allocation_data = []
    for asset in active_assets:
        allocation_data.append({
            'Asset': asset['name'],
            'Allocazione (%)': f"{asset['allocation']:.2f}%",
            'TER (%)': f"{asset['ter']:.3f}%"
        })
    
    df_allocation_summary = pd.DataFrame(allocation_data)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.dataframe(df_allocation_summary, hide_index=True, use_container_width=True)
    
    with col2:
        # Grafico a torta dell'allocazione
        df_alloc_chart = pd.DataFrame([
            {'Asset': asset['name'], 'Allocazione': asset['allocation']}
            for asset in active_assets
        ])
        fig_allocation = px.pie(df_alloc_chart, values='Allocazione', names='Asset', 
                              title="Distribuzione Asset")
        fig_allocation.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_allocation, use_container_width=True)
    
    st.markdown("---")
    
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
