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
            st.warning(f"⚠️ File di configurazione '{config_file}' non trovato! Uso configurazione di default.")
            return self.get_default_profiles()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Verifica la presenza delle sezioni necessarie
            if 'asset_profiles' not in config or 'asset_characteristics' not in config:
                st.error("❌ Il file config.json deve contenere 'asset_profiles' e 'asset_characteristics'")
                return self.get_default_profiles()
            
            asset_characteristics = config['asset_characteristics']
            asset_profiles = config['asset_profiles']
            
            # Combina i profili con le caratteristiche
            validated_profiles = {}
            for profile_name, assets in asset_profiles.items():
                validated_assets = []
                for asset in assets:
                    validated_asset = self.merge_asset_data(asset, asset_characteristics)
                    if validated_asset:
                        validated_assets.append(validated_asset)
                
                if validated_assets:
                    validated_profiles[profile_name] = validated_assets
            
            return validated_profiles if validated_profiles else self.get_default_profiles()
            
        except Exception as e:
            st.error(f"❌ Errore nel caricamento del file di configurazione: {str(e)}")
            return self.get_default_profiles()
    
    def merge_asset_data(self, asset_profile, asset_characteristics):
        """Combina i dati del profilo con le caratteristiche dell'asset"""
        asset_name = asset_profile.get('name', '')
        
        if asset_name not in asset_characteristics:
            st.warning(f"⚠️ Caratteristiche per '{asset_name}' non trovate in asset_characteristics")
            return None
        
        characteristics = asset_characteristics[asset_name]
        
        # Combina i dati
        merged_asset = {
            'name': asset_name,
            'allocation': asset_profile.get('allocation', 0.0),
            'ter': asset_profile.get('ter', 0.0),  # Total Expense Ratio
            'return': characteristics.get('return', 5.0),
            'volatility': characteristics.get('volatility', 10.0),
            'min_return': characteristics.get('min_return', -20.0),
            'max_return': characteristics.get('max_return', 30.0)
        }
        
        return merged_asset
    
    def get_default_profiles(self):
        """Restituisce profili asset di default"""
        return {
            'Conservativo': [
                {'name': 'Obbligazioni Gov', 'return': 2.5, 'volatility': 3.0, 'allocation': 70.0, 'min_return': -5.0, 'max_return': 8.0},
                {'name': 'Azioni Div', 'return': 6.0, 'volatility': 12.0, 'allocation': 30.0, 'min_return': -25.0, 'max_return': 25.0}
            ],
            'Moderato': [
                {'name': 'Obbligazioni', 'return': 3.0, 'volatility': 4.0, 'allocation': 40.0, 'min_return': -8.0, 'max_return': 10.0},
                {'name': 'Azioni Globali', 'return': 7.0, 'volatility': 15.0, 'allocation': 50.0, 'min_return': -30.0, 'max_return': 35.0},
                {'name': 'REIT', 'return': 5.5, 'volatility': 18.0, 'allocation': 10.0, 'min_return': -35.0, 'max_return': 40.0}
            ],
            'Aggressivo': [
                {'name': 'Azioni Growth', 'return': 8.5, 'volatility': 20.0, 'allocation': 60.0, 'min_return': -40.0, 'max_return': 50.0},
                {'name': 'Azioni Emergenti', 'return': 9.0, 'volatility': 25.0, 'allocation': 25.0, 'min_return': -50.0, 'max_return': 60.0},
                {'name': 'Small Cap', 'return': 10.0, 'volatility': 22.0, 'allocation': 15.0, 'min_return': -45.0, 'max_return': 55.0}
            ]
        }

def show_asset_popup(asset, asset_index):
    """Mostra un popup modale per modificare un singolo asset"""
    # Verifica che l'asset abbia tutti i campi necessari
    required_fields = ['name', 'return', 'volatility', 'allocation', 'min_return', 'max_return']
    if not all(key in asset for key in required_fields):
        st.error(f"❌ Asset '{asset.get('name', 'Sconosciuto')}' ha una struttura non valida")
        return
    
    with st.popover(f"✏️ Modifica {asset['name']}", use_container_width=True):
        st.markdown(f"### 📊 {asset['name']}")
        
        # Mostra il TER se presente
        if 'ter' in asset:
            st.info(f"💰 TER (Total Expense Ratio): {asset['ter']:.2f}%")
        
        # Crea due colonne per il layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📈 Caratteristiche di Rendimento**")
            new_return = st.number_input(
                "Rendimento medio (%)", 
                value=float(asset['return']), 
                step=0.1, 
                format="%.2f",
                key=f"popup_return_{asset_index}",
                help="Rendimento annuo atteso dell'asset"
            )
            
            new_volatility = st.number_input(
                "Volatilità (%)", 
                value=float(asset['volatility']), 
                step=0.1, 
                format="%.2f",
                key=f"popup_vol_{asset_index}",
                help="Deviazione standard dei rendimenti"
            )
        
        with col2:
            st.markdown("**🎯 Limiti di Rendimento**")
            new_min_return = st.number_input(
                "Rendimento minimo (%)", 
                value=float(asset['min_return']), 
                step=1.0, 
                format="%.2f",
                key=f"popup_min_{asset_index}",
                help="Rendimento minimo possibile (cap inferiore)"
            )
            
            new_max_return = st.number_input(
                "Rendimento massimo (%)", 
                value=float(asset['max_return']), 
                step=1.0, 
                format="%.2f",
                key=f"popup_max_{asset_index}",
                help="Rendimento massimo possibile (cap superiore)"
            )
        
        # Allocazione in una riga separata per darle più spazio
        st.markdown("**💼 Allocazione nel Portafoglio**")
        new_allocation = st.slider(
            "Allocazione (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=float(asset['allocation']), 
            step=1.0,
            key=f"popup_alloc_{asset_index}",
            help="Percentuale di questo asset nel portafoglio"
        )
        
        # Mostra il TER modificabile se presente
        new_ter = asset.get('ter', 0.0)
        if 'ter' in asset:
            new_ter = st.number_input(
                "TER - Total Expense Ratio (%)", 
                value=float(asset['ter']), 
                step=0.01, 
                format="%.3f",
                key=f"popup_ter_{asset_index}",
                help="Costi annuali dell'asset"
            )
        
        # Pulsanti di azione
        col_save, col_cancel = st.columns(2)
        
        with col_save:
            if st.button("💾 Salva Modifiche", key=f"save_{asset_index}", type="primary"):
                # Aggiorna l'asset nella sessione
                update_data = {
                    'return': new_return,
                    'volatility': new_volatility,
                    'min_return': new_min_return,
                    'max_return': new_max_return,
                    'allocation': new_allocation
                }
                
                # Aggiungi TER se presente
                if 'ter' in asset:
                    update_data['ter'] = new_ter
                
                st.session_state.current_assets[asset_index].update(update_data)
                st.success("✅ Modifiche salvate!")
                st.rerun()
        
        with col_cancel:
            if st.button("❌ Annulla", key=f"cancel_{asset_index}"):
                st.info("Modifiche annullate")

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
            st.rerun()
        
        # Inizializza asset se non esistono
        if 'current_assets' not in st.session_state:
            st.session_state.current_assets = [asset.copy() for asset in simulator.asset_profiles[selected_profile]]
        
        # Pulsanti di gestione globale
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
        
        st.markdown("---")
        
        # Lista asset con popup per modifica
        assets_data = []
        
        # Assicurati che current_assets sia inizializzato correttamente
        if not st.session_state.current_assets:
            st.warning("⚠️ Nessun asset caricato. Carica un profilo per iniziare.")
            return
        
        for i, asset in enumerate(st.session_state.current_assets):
            # Verifica che l'asset abbia tutti i campi necessari
            if not all(key in asset for key in ['name', 'return', 'volatility', 'allocation', 'min_return', 'max_return']):
                st.error(f"❌ Asset {i} ha una struttura non valida. Ricarica il profilo.")
                continue
                
            # Container per ogni asset
            with st.container():
                # Header dell'asset con informazioni principali
                col_info, col_edit = st.columns([3, 1])
                
                with col_info:
                    # Mostra info essenziali in formato compatto
                    allocation_color = "🟢" if asset['allocation'] > 0 else "⚪"
                    ter_info = f" | 💰 TER: {asset.get('ter', 0):.2f}%" if 'ter' in asset else ""
                    st.markdown(f"""
                    **{allocation_color} {asset['name']}**  
                    📊 Rend: {asset['return']:.1f}% | 📈 Vol: {asset['volatility']:.1f}% | 💼 Alloc: {asset['allocation']:.1f}%{ter_info}
                    """)
                
                with col_edit:
                    # Popup per modifica
                    show_asset_popup(asset, i)
                
                assets_data.append({
                    'name': asset['name'],
                    'return': asset['return'],
                    'volatility': asset['volatility'],
                    'allocation': asset['allocation'],
                    'min_return': asset['min_return'],
                    'max_return': asset['max_return'],
                    'ter': asset.get('ter', 0.0)
                })
                
                st.markdown("---")
        
        total_allocation = sum(asset['allocation'] for asset in assets_data)
        
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
        
        st.subheader("📋 Riassunto Asset Attivi")
        # Mostra solo asset con allocazione > 0 nella tabella riassuntiva
        active_assets_df = pd.DataFrame([asset for asset in assets_data if asset['allocation'] > 0])
        if not active_assets_df.empty:
            # Formatta i numeri per una migliore leggibilità
            display_df = active_assets_df.copy()
            for col in ['return', 'volatility', 'allocation', 'min_return', 'max_return']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].round(2)
            st.dataframe(display_df, use_container_width=True)
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
