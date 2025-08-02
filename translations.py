"""
Translations for the Monte Carlo Investment Simulator
"""

TRANSLATIONS = {
    'en': {
        # Header and title
        'page_title': 'Monte Carlo Investment Simulator',
        'main_title': '🏗️ Monte Carlo Simulation for Retirement Planning',
        'language_selector': 'Language',
        
        # Disclaimers
        'disclaimers_header': 'ℹ️ **Important Information & Disclaimers**',
        'educational_disclaimer': '**Educational Purpose Disclaimer:**',
        'educational_text': 'This application is for educational purposes only and simulates purely theoretical scenarios based on simplified assumptions. Results should not be interpreted as real predictions nor as investment recommendations. No information provided constitutes financial, wealth or tax advice.',
        'app_explanation': (
            "🔍 **What does this application do?**\n"
            "This application uses the Monte Carlo method to generate thousands of possible market scenarios, "
            "simulating whether the selected portfolio may or may not be suitable for the retirement plan "
            "chosen, based on the parameters entered by the user. The app estimates the probability of success "
            "of the plan and provides an overview of possible outcomes accounting for inflation, based on the "
            "simulation of assets selected."
        ),
        'data_info': '**Data Information:**',
        'data_text': 'The returns are based on global and european market data from the last 30 years. Data may be inaccurate or outdated and should be used for educational purposes only.',        
        # Sidebar parameters
        'simulation_parameters': '⚙️ Simulation Parameters',
        'general_parameters': '📊 General Parameters',
        'initial_amount': 'Initial amount (€)',
        'years_to_retirement': 'Years to retirement',
        'years_retired': 'Years in retirement',
        'annual_contribution': 'Annual contribution (€)',
        'inflation': 'Annual inflation (%)',
        'withdrawal': 'Annual withdrawal in retirement (€)',
        'n_simulations': 'Number of simulations',
        # Portfolio configuration
        'portfolio_config': '💼 Portfolio Configuration',
        'investment_profile': '🎯 Investment Profile',
        'select_profile': 'Select profile:',
        'load_profile': '🔄 Load Selected Profile',
        'allocation_percent': 'Allocation (%)',
        'ter_percent': 'TER (%)',
        'edit_parameters': '✏️ Edit Parameters',
        'advanced_parameters': '**Advanced Parameters:**',
        'return_percent': 'Return (%)',
        'volatility_percent': 'Volatility (%)',
        'min_return_percent': 'Min Return (%)',
        'max_return_percent': 'Max Return (%)',
        'return_label': '**Return:**',
        'volatility_label': '**Volatility:**',
        'min_return_label': '**Min Return:**',
        'max_return_label': '**Max Return:**',
        'reset_allocations': '🔄 Reset Allocations',
        'balance_allocations': '⚖️ Balance Allocations',
        'total_allocation_error': '⚠️ Total allocation: {:.1f}% (must be 100%)',
        'correct_allocation': '✅ Correct allocation: {:.1f}%',
        
        # Charts and tables
        'allocation_chart': '📈 Allocation Chart',
        'portfolio_distribution': 'Portfolio Distribution',
        'no_asset_selected': 'No asset selected',
        'asset_summary': '📋 Asset Summary',
        'no_active_assets': 'No active assets',
        
        # Simulation
        'run_simulation': '🚀 **RUN SIMULATION**',
        'select_assets_error': '❌ Select at least one asset with allocation > 0!',
        'fix_allocations_error': '❌ Fix allocations first!',
        'simulation_progress': '🔄 Simulation in progress...',
        'simulation_step': 'Simulation {} of {}',
        'simulation_completed': '✅ Simulation completed!',
        
        # Results
        'simulation_results': '🎯 Simulation Results',
        'total_deposited': '💰 Total Deposited',
        'median_accumulation': '📈 Median Accumulation Value',
        'median_final': '✨ Median Final Value',
        'success_rate': '✅ Success Rate',
        'accumulation_phase': '📊 Accumulation Phase (With Inflation)',
        'accumulation_phase_real': '📊 Accumulation Phase (With Inflation)',
        'accumulation_phase_nominal': '💰 Accumulation Phase (Without Inflation)',
        'final_values': '🏁 Final Values (With Inflation)',
        'final_values_info': 'Final values are calculated considering inflation during the retirement phase',
        'percentile': 'Percentile',
        'value_euro': 'Value (€)',
        'median': 'Median',
        'average': 'Average',
        'distribution_accumulation': 'Distribution of End-of-Accumulation Values (With Inflation)',
        'distribution_accumulation_real': 'Distribution of End-of-Accumulation Values (With Inflation)',
        'distribution_accumulation_nominal': 'Distribution of End-of-Accumulation Values (Without Inflation)',
        'distribution_final': 'Distribution of Final Values (With Inflation)',
        'frequency': 'Frequency',
        
        # Success messages
        'excellent_success': '🎉 Excellent! With {:.1f}% probability of success, you can now watch the construction sites from Monte Carlo',
        'fair_success': '⚠️ Fair. With {:.1f}% success rate, you might need to consider canned tuna.',
        'warning_success': '❌ Warning! Only {:.1f}% probability of success. Charity awaits you.',
        
        # Footer
        'footer': 'Created by AS with the supervision of KIM',
        
        # Config errors
        'config_not_found': '❌ Configuration file \'{}\' not found!',
        'config_load_error': '❌ Error loading configuration file: {}',
        'asset_characteristics_error': '❌ Error loading asset characteristics: {}',
    },
    
    'it': {
        # Header and title
        'page_title': 'Simulatore Monte Carlo per Investimenti',
        'main_title': '🏗️ Simulazione Monte Carlo per la Pianificazione Pensionistica',
        'language_selector': 'Lingua',

        # Disclaimers
        'disclaimers_header': 'ℹ️ **Informazioni Importanti e Disclaimer**',
        'educational_disclaimer': '**Disclaimer Scopo Educativo:**',
        'educational_text': 'Questa applicazione è solo a scopo educativo e simula scenari puramente teorici basati su assunzioni semplificate. I risultati non devono essere interpretati come previsioni reali né come raccomandazioni di investimento. Nessuna informazione fornita costituisce consulenza finanziaria, patrimoniale o fiscale.',
        'app_explanation': (
            "**Cosa fa questa applicazione?**\n"
            "Questa applicazione utilizza il metodo Monte Carlo per generare migliaia di scenari di mercato possibili, "
            "simulando la possibilità che il portafoglio selezionato possa o meno essere adatto al piano pensionistico "
            "scelto in base ai parametri inseriti dall’utente. L’app restituisce una stima della probabilità "
            "di successo del piano stesso e fornisce una panoramica dei possibili risultati (outcome) tenendo conto "
            "dell'inflazione in base alle simulazioni sugli asset selezionati."
        ),
        'data_info': '**Informazioni sui Dati:**',
        'data_text': 'I rendimenti sono basati su dati di mercato globali ed europei degli ultimi 30 anni. I dati potrebbero essere imprecisi o obsoleti e dovrebbero essere utilizzati solo a scopo educativo.',

        # Sidebar parameters
        'simulation_parameters': '⚙️ Parametri di Simulazione',
        'general_parameters': '📊 Parametri Generali',
        'initial_amount': 'Importo iniziale (€)',
        'years_to_retirement': 'Anni alla pensione',
        'years_retired': 'Anni in pensione',
        'annual_contribution': 'Contributo annuale (€)',
        'inflation': 'Inflazione annuale (%)',
        'withdrawal': 'Prelievo annuale in pensione (€)',
        'n_simulations': 'Numero di simulazioni',
        # Portfolio configuration
        'portfolio_config': '💼 Configurazione Portafoglio',
        'investment_profile': '🎯 Profilo di Investimento',
        'select_profile': 'Seleziona profilo:',
        'load_profile': '🔄 Carica Profilo Selezionato',
        'allocation_percent': 'Allocazione (%)',
        'ter_percent': 'TER (%)',
        'edit_parameters': '✏️ Modifica Parametri',
        'advanced_parameters': '**Parametri Avanzati:**',
        'return_percent': 'Rendimento (%)',
        'volatility_percent': 'Volatilità (%)',
        'min_return_percent': 'Rendimento Min (%)',
        'max_return_percent': 'Rendimento Max (%)',
        'return_label': '**Rendimento:**',
        'volatility_label': '**Volatilità:**',
        'min_return_label': '**Rendimento Min:**',
        'max_return_label': '**Rendimento Max:**',
        'reset_allocations': '🔄 Azzera Allocazioni',
        'balance_allocations': '⚖️ Bilancia Allocazioni',
        'total_allocation_error': '⚠️ Allocazione totale: {:.1f}% (deve essere 100%)',
        'correct_allocation': '✅ Allocazione corretta: {:.1f}%',
        
        # Charts and tables
        'allocation_chart': '📈 Grafico Allocazione',
        'portfolio_distribution': 'Distribuzione Portafoglio',
        'no_asset_selected': 'Nessun asset selezionato',
        'asset_summary': '📋 Riepilogo Asset',
        'no_active_assets': 'Nessun asset attivo',
        
        # Simulation
        'run_simulation': '🚀 **AVVIA SIMULAZIONE**',
        'select_assets_error': '❌ Seleziona almeno un asset con allocazione > 0!',
        'fix_allocations_error': '❌ Correggi prima le allocazioni!',
        'simulation_progress': '🔄 Simulazione in corso...',
        'simulation_step': 'Simulazione {} di {}',
        'simulation_completed': '✅ Simulazione completata!',
        
        # Results
        'simulation_results': '🎯 Risultati Simulazione',
        'total_deposited': '💰 Totale Depositato',
        'median_accumulation': '📈 Valore Mediano Accumulo',
        'median_final': '✨ Valore Mediano Finale',
        'success_rate': '✅ Tasso di Successo',
        'accumulation_phase': '📊 Fase di Accumulo (Con Inflazione)',
        'accumulation_phase_real': '📊 Fase di Accumulo (Con Inflazione)',
        'accumulation_phase_nominal': '💰 Fase di Accumulo (Senza Inflazione)',
        'final_values': '🏁 Valori Finali (Con Inflazione)',
        'final_values_info': 'I valori finali sono calcolati considerando l\'inflazione durante la fase di pensionamento',
        'percentile': 'Percentile',
        'value_euro': 'Valore (€)',
        'median': 'Mediana',
        'average': 'Media',
        'distribution_accumulation': 'Distribuzione dei Valori di Fine Accumulo (Con Inflazione)',
        'distribution_accumulation_real': 'Distribuzione dei Valori di Fine Accumulo (Con Inflazione)',
        'distribution_accumulation_nominal': 'Distribuzione dei Valori di Fine Accumulo (Senza Inflazione)',
        'distribution_final': 'Distribuzione dei Valori Finali (Con Inflazione)',
        'frequency': 'Frequenza',
        
        # Success messages
        'excellent_success': '🎉 Eccellente! Con {:.1f}% di probabilità di successo, ora puoi guardare i cantieri da Monte Carlo',
        'fair_success': '⚠️ Discreto. Con {:.1f}% di tasso di successo, potresti dover considerare il tonno in scatola.',
        'warning_success': '❌ Attenzione! Solo {:.1f}% di probabilità di successo. La carità ti aspetta.',
        
        # Footer
        'footer': 'Creato da AS con la supervisione di KIM',
        
        # Config errors
        'config_not_found': '❌ File di configurazione \'{}\' non trovato!',
        'config_load_error': '❌ Errore nel caricamento del file di configurazione: {}',
        'asset_characteristics_error': '❌ Errore nel caricamento delle caratteristiche degli asset: {}',
    }
}

def get_text(key, lang='en', **kwargs):
    """
    Get translated text for the given key and language.
    Supports string formatting with kwargs.
    """
    try:
        text = TRANSLATIONS[lang][key]
        if kwargs:
            return text.format(**kwargs)
        return text
    except KeyError:
        # Fallback to English if translation not found
        try:
            text = TRANSLATIONS['en'][key]
            if kwargs:
                return text.format(**kwargs)
            return text
        except KeyError:
            return f"[MISSING: {key}]"

def get_profile_names(lang='en'):
    """Get translated profile names"""
    profiles = {
        'en': {
            'Conservative': 'Conservative',
            'Moderate': 'Moderate', 
            'Dynamic': 'Dynamic',
            'StrategicEquityGold': 'Strategic Equity-Gold',
            'Diversified': 'Diversified',
            'NoAllocation': 'No Allocation'
        },
        'it': {
            'Conservative': 'Conservativo',
            'Moderate': 'Moderato',
            'Dynamic': 'Dinamico', 
            'StrategicEquityGold': 'Strategico Equity-Oro',
            'Diversified': 'Diversificato',
            'NoAllocation': 'Nessuna Allocazione'
        }
    }
    return profiles.get(lang, profiles['en'])

def get_asset_names(lang='en'):
    """Get translated asset names"""
    assets = {
        'en': {
            'Stocks': 'Stocks',
            'Bond': 'Bonds',
            'Gold': 'Gold',
            'REIT': 'REIT',
            'Commodities': 'Commodities',
            'Cash': 'Cash',
            'UserAsset1': 'User Custom 1',
            'UserAsset2': 'User Custom 2'
        },
        'it': {
            'Stocks': 'Azioni',
            'Bond': 'Obbligazioni', 
            'Gold': 'Oro',
            'REIT': 'Immobiliare',
            'Commodities': 'Materie Prime',
            'Cash': 'Liquidità',
            'UserAsset1': 'Asset Custom 1',
            'UserAsset2': 'Asset Custom 2'
        }
    }
    return assets.get(lang, assets['en'])


