"""
 translations for Monte Carlo Investment Simulator
"""

TRANSLATIONS = {
    'en': {
        # Header and title
        'page_title': 'Monte Carlo Investment Simulator',
        'main_title': 'Monte Carlo Simulation for Retirement Planning',
        'language_selector': 'Language',
        
        # Enhanced disclaimers
        'disclaimers_header': 'Important Information & Disclaimers',
        'educational_disclaimer': 'Educational Purpose Disclaimer',
        'educational_text': 'This application is for educational purposes only and simulates purely theoretical scenarios based on simplified assumptions. Results should not be interpreted as real predictions nor as investment recommendations. No information provided constitutes financial, wealth or tax advice.',
        'app_explanation': (
            "What does this application do?\n"
            "This application uses the Monte Carlo method to generate thousands of possible market scenarios, "
            "simulating whether the selected portfolio may or may not be suitable for the retirement plan "
            "chosen, based on the parameters entered by the user. The app estimates the probability of success "
            "of the plan and delivers an overview of possible outcomes while factoring in inflation, based on the "
            "performance simulations of the selected assets."
        ),
        'long_term_disclaimer': 'Long-Term Investment Focus',
        'long_term_text': 'This simulator is specifically designed for long-term investment planning (15+ years). Investment strategies for shorter time horizons may face different challenges and risks that are not adequately captured by this model. Short-term retirement planning requires different approaches and considerations.',
        'returns_disclaimer': 'Asset Return Assumptions',
        'returns_text': 'The default return parameters are examples based on realistic historical data that the developer considers reasonable. However, these are fully customizable by the user. All return assumptions should be carefully reviewed and adjusted based on your own research and expectations.',
        'correlation_disclaimer': 'Asset Correlation Limitations',
        'correlation_text': 'This simulation does not model correlations between different asset classes. Asset correlations are extremely difficult to parametrize accurately due to their dynamic nature and the numerous variables and unknowns involved. Each asset is simulated independently, which may not reflect real-world portfolio behavior during market stress events.',
        
        # Real withdrawal disclaimer
        'real_withdrawal_disclaimer': 'Real vs Nominal Withdrawal',
        'real_withdrawal_text': 'This app now supports REAL withdrawal amounts that maintain purchasing power by adjusting for inflation annually. If you select a €12,000 real withdrawal, you will maintain €12,000 of today\'s purchasing power throughout retirement. With nominal withdrawals, the purchasing power decreases over time due to inflation.',
        
        'data_info': 'Data Information',
        'data_text': 'The returns are based on global and european market data from the last 30 years. Data may be inaccurate or outdated and should be used for educational purposes only.',        
        
        # Sidebar parameters
        'simulation_parameters': 'Simulation Parameters',
        'general_parameters': 'General Parameters',
        'initial_amount': 'Initial amount (€)',
        'years_to_retirement': 'Years to retirement',
        'years_retired': 'Years in retirement',
        'annual_contribution': 'Annual contribution (€)',
        'adjust_contribution_inflation': 'Adjust contribution for inflation',
        'adjust_contribution_inflation_help': 'If checked, the annual contribution will increase each year by the inflation rate. If unchecked, the contribution remains fixed.',
        'inflation': 'Annual inflation (%)',
        
        # Real withdrawal parameters
        'withdrawal_section_title': 'Retirement Withdrawal Settings',
        'use_real_withdrawal': 'Use REAL withdrawal (recommended)',
        'use_real_withdrawal_help': 'If checked, withdrawal amount maintains constant purchasing power by adjusting for inflation. If unchecked, uses fixed nominal amount that loses purchasing power over time.',
        'real_withdrawal_amount': 'Annual REAL withdrawal (€ in today\'s purchasing power)',
        'real_withdrawal_help': 'This amount represents TODAY\'S purchasing power. At retirement, it will be automatically adjusted for inflation during accumulation, then continue adjusting annually. Example: €12,000 today → €22,235 at retirement (after 25 years at 2.5%) → €22,791 in year 2, etc.',
        'nominal_withdrawal_amount': 'Annual NOMINAL withdrawal (€ fixed amount)',
        'nominal_withdrawal_help': 'This exact amount will be withdrawn every year without inflation adjustment. The purchasing power will decrease over time.',
        'real_withdrawal_explanation': 'Real withdrawal selected: Your purchasing power will remain constant throughout retirement. The amount will first be adjusted for inflation during accumulation, then continue adjusting annually during retirement.',
        'nominal_withdrawal_explanation': 'Nominal withdrawal selected: The euro amount remains fixed, but your purchasing power will decrease over time due to inflation. After 25 years with 2.5% inflation, €12,000 will have the purchasing power of €6,473 today.',
        
        'withdrawal': 'Annual withdrawal in retirement (€)',
        'capital_gains_tax_rate': 'Capital gains tax rate (%)',
        'capital_gains_tax_help': 'Tax rate applied to capital gains portion of withdrawals. The effective withdrawal amount will be reduced based on the capital gains percentage in your portfolio.',
        'n_simulations': 'Number of simulations',
        
        # Portfolio configuration
        'portfolio_config': 'Portfolio Configuration',
        'accumulation_portfolio': 'Accumulation Phase Portfolio',
        'retirement_portfolio': 'Retirement Phase Portfolio',
        'use_same_portfolio': 'Use same portfolio for both phases',
        'use_same_portfolio_help': 'If checked, the same portfolio allocation will be used for both accumulation and retirement phases.',
        
        'investment_profile': 'Investment Profile',
        'accumulation_profile': 'Accumulation Profile',
        'retirement_profile': 'Retirement Profile',
        'select_profile': 'Select profile:',
        'load_profile': 'Load Selected Profile',
        'allocation_percent': 'Allocation (%)',
        'ter_percent': 'TER (%)',
        'edit_parameters': 'Edit Parameters',
        'advanced_parameters': 'Advanced Parameters',
        'return_percent': 'Return (%)',
        'volatility_percent': 'Volatility (%)',
        'min_return_percent': 'Min Return (%)',
        'max_return_percent': 'Max Return (%)',
        'return_label': 'Return',
        'volatility_label': 'Volatility',
        'min_return_label': 'Min Return',
        'max_return_label': 'Max Return',
        'reset_allocations': 'Reset Allocations',
        'balance_allocations': 'Balance Allocations',
        'total_allocation_error': 'Total allocation: {:.1f}% (must be 100%)',
        'correct_allocation': 'Correct allocation: {:.1f}%',
        
        # Charts and tables
        'allocation_chart': 'Allocation Chart',
        'accumulation_chart': 'Accumulation Phase Chart',
        'retirement_chart': 'Retirement Phase Chart',
        'portfolio_distribution': 'Portfolio Distribution',
        'no_asset_selected': 'No asset selected',
        'asset_summary': 'Asset Summary',
        'accumulation_summary': 'Accumulation Assets',
        'retirement_summary': 'Retirement Assets',
        'no_active_assets': 'No active assets',
        
        # Simulation
        'run_simulation': 'RUN SIMULATION',
        'select_assets_error': 'Select at least one asset with allocation > 0!',
        'select_accumulation_assets_error': 'Select at least one asset with allocation > 0 for accumulation phase!',
        'select_retirement_assets_error': 'Select at least one asset with allocation > 0 for retirement phase!',
        'fix_allocations_error': 'Fix allocations first!',
        'fix_accumulation_allocations_error': 'Fix accumulation phase allocations first!',
        'fix_retirement_allocations_error': 'Fix retirement phase allocations first!',
        'simulation_progress': 'Simulation in progress...',
        'simulation_step': 'Simulation {} of {}',
        'simulation_completed': 'Simulation completed!',
        
        # Results
        'simulation_results': 'Simulation Results',
        'total_deposited': 'Total Deposited',
        'median_accumulation': 'Median Accumulation Value',
        'median_final': 'Median Final Value',
        'success_rate': 'Success Rate',
        'real_withdrawal_amount_result': 'Real Withdrawal Amount (After Tax)',
        'accumulation_phase': 'Accumulation Phase (With Inflation)',
        'accumulation_phase_real': 'Accumulation Phase (With Inflation)',
        'accumulation_phase_nominal': 'Accumulation Phase (Without Inflation)',
        'final_values': 'Final Values (With Inflation)',
        'final_values_info': 'Final values are calculated considering inflation during the retirement phase',
        'percentile': 'Percentile',
        'value_euro': 'Value (€)',
        'cagr_percent': 'CAGR (%)',
        'median': 'Median',
        'average': 'Average',
        'distribution_accumulation': 'Distribution of End-of-Accumulation Values (With Inflation)',
        'distribution_accumulation_real': 'Distribution of End-of-Accumulation Values (With Inflation)',
        'distribution_accumulation_nominal': 'Distribution of End-of-Accumulation Values (Without Inflation)',
        'distribution_final': 'Distribution of Final Values (With Inflation)',
        'frequency': 'Frequency',
        
        # Enhanced chart labels
        'distribution_charts_title': 'Distribution and Correlation Charts',
        'distributions_tab': 'Distributions',
        'correlations_tab': 'Correlations (Nominal)',
        'comparison_tab': 'Nominal vs Real Comparison',
        'accumulation_nominal_dist': 'Accumulation Values Distribution (Nominal)',
        'accumulation_real_dist': 'Accumulation Values Distribution (Real)',
        'final_nominal_dist': 'Final Values Distribution (Nominal)',
        'final_real_dist': 'Final Values Distribution (Real)',
        'accumulation_final_correlation': 'Accumulation vs Final Correlation (Nominal)',
        'accumulation_final_heatmap': 'Heat Map: Accumulation → Final (Nominal)',
        'final_values_comparison': 'Final Values Comparison: Nominal vs Real',
        'final_values_correlation': 'Final Values Correlation: Real vs Nominal',
        'correlation_label': 'Correlation',
        'inflation_impact_label': 'Average Inflation Impact',
        'inflation_impact_text': 'Real values are on average {:.1f}% of nominal values',
        'one_to_one_line': '1:1 Line',
        
        # Success messages
        'excellent_success': 'Excellent! With {:.1f}% probability of success, your retirement plan appears well-funded',
        'fair_success': 'Fair. With {:.1f}% success rate, consider reviewing your strategy.',
        'warning_success': 'Warning! Only {:.1f}% probability of success. Strategy adjustment recommended.',
        
        # Footer
        'footer': 'Monte Carlo Investment Simulator - For Educational Purposes Only',
        
        # Config errors
        'config_not_found': 'Configuration file \'{}\' not found!',
        'config_load_error': 'Error loading configuration file: {}',
        'asset_characteristics_error': 'Error loading asset characteristics: {}',
        
        # VaR/CVaR Risk Analysis
        'risk_analysis_title': 'Risk Analysis (VaR & CVaR)',
        'var_explanation_title': 'What are VaR and CVaR?',
        'key_risk_metrics_title': 'Key Risk Metrics (Final Values)',
        'risk_visualizations_title': 'VaR and CVaR Visualizations',
        'distribution_with_var_cvar': 'Distribution with VaR/CVaR',
        'phase_comparison': 'Phase Comparison',
        'var_cvar_table_by_phase': 'VaR and CVaR Table by Phase',
        'loss_probability_analysis': 'Loss Probability Analysis',
        'minimum_value_95_percent': 'Minimum value in 95% of cases',
        'average_value_worst_5_percent': 'Average value in worst 5% of cases',
        'average_value_all_scenarios': 'Average value across all scenarios',
        'difference_mean_cvar': 'Difference between mean and CVaR 5%',
        'high_risk': 'HIGH RISK',
        'moderate_high_risk': 'MODERATE-HIGH RISK',
        'moderate_risk': 'MODERATE RISK',
        'low_risk': 'LOW RISK',
        'significant_probability_lose_all': 'Significant probability of losing all capital',
        'worst_scenarios_very_negative': 'Worst-case scenarios can be very negative',
        'manageable_risk_monitor': 'Manageable risk but worth monitoring',
        'worst_scenarios_contained': 'Worst-case scenarios relatively contained',
        'final_values_distribution_var_cvar': 'Final Values Distribution with VaR and CVaR',
        'var_cvar_comparison_phases': 'VaR and CVaR Comparison Across Phases',
        'total_loss_probability': 'Total Loss Probability',
        'prob_final_less_deposited': 'Probability that final portfolio is less than total deposited',
        'average_value_when_loss': 'Average Value (when loss occurs)',
        'probability_by_threshold': 'Probability by Threshold:',
        'loss_probability_by_threshold': 'Loss Probability by Threshold',
    },
    
    'it': {
        # Header and title
        'page_title': 'Simulatore Monte Carlo per Investimenti',
        'main_title': 'Simulazione Monte Carlo per la Pianificazione Pensionistica',
        'language_selector': 'Lingua',

        # Enhanced disclaimers
        'disclaimers_header': 'Informazioni Importanti e Disclaimer',
        'educational_disclaimer': 'Disclaimer Scopo Educativo',
        'educational_text': 'Questa applicazione è solo a scopo educativo e simula scenari puramente teorici basati su assunzioni semplificate. I risultati non devono essere interpretati come previsioni reali né come raccomandazioni di investimento. Nessuna informazione fornita costituisce consulenza finanziaria, patrimoniale o fiscale.',
        'app_explanation': (
            "Cosa fa questa applicazione?\n"
            "Questa applicazione utilizza il metodo Monte Carlo per generare migliaia di scenari di mercato possibili, "
            "simulando la possibilità che il portafoglio selezionato possa o meno essere adatto al piano pensionistico "
            "scelto in base ai parametri inseriti dall'utente. L'app restituisce una stima della probabilità "
            "di successo del piano e fornisce una panoramica dei possibili risultati (outcome) tenendo conto "
            "dell'inflazione, basata sulle simulazioni delle performance degli asset selezionati."
        ),
        'long_term_disclaimer': 'Focus su Investimenti a Lungo Termine',
        'long_term_text': 'Questo simulatore è specificamente progettato per la pianificazione di investimenti a lungo termine (15+ anni). Le strategie di investimento per orizzonti temporali più brevi potrebbero affrontare sfide e rischi diversi che non sono adeguatamente catturati da questo modello. La pianificazione pensionistica a breve termine richiede approcci e considerazioni differenti.',
        'returns_disclaimer': 'Assunzioni sui Rendimenti degli Asset',
        'returns_text': 'I parametri di rendimento predefiniti sono esempi basati su dati storici realistici che lo sviluppatore considera ragionevoli. Tuttavia, questi sono completamente personalizzabili dall\'utente. Tutte le assunzioni sui rendimenti dovrebbero essere attentamente riviste e adattate in base alla propria ricerca e alle proprie aspettative.',
        'correlation_disclaimer': 'Limitazioni sulla Correlazione tra Asset',
        'correlation_text': 'Questa simulazione non modella le correlazioni tra le diverse classi di asset. Le correlazioni tra asset sono estremamente difficili da parametrizzare accuratamente a causa della loro natura dinamica e delle numerose variabili e incognite coinvolte. Ogni asset viene simulato indipendentemente, il che potrebbe non riflettere il comportamento reale del portafoglio durante eventi di stress di mercato.',
        
        # Real withdrawal disclaimer
        'real_withdrawal_disclaimer': 'Prelievi Reali vs Nominali',
        'real_withdrawal_text': 'Questa app ora supporta importi di prelievo REALI che mantengono il potere d\'acquisto aggiustandosi annualmente all\'inflazione. Se selezioni un prelievo reale di €12.000, manterrai €12.000 di potere d\'acquisto di oggi per tutta la pensione. Con prelievi nominali, il potere d\'acquisto diminuisce nel tempo a causa dell\'inflazione.',
        
        'data_info': 'Informazioni sui Dati',
        'data_text': 'I rendimenti sono basati su dati di mercato globali ed europei degli ultimi 30 anni. I dati potrebbero essere imprecisi o obsoleti e dovrebbero essere utilizzati solo a scopo educativo.',

        # Sidebar parameters
        'simulation_parameters': 'Parametri di Simulazione',
        'general_parameters': 'Parametri Generali',
        'initial_amount': 'Importo iniziale (€)',
        'years_to_retirement': 'Anni alla pensione',
        'years_retired': 'Anni in pensione',
        'annual_contribution': 'Contributo annuale (€)',
        'adjust_contribution_inflation': 'Aggiusta contributo per inflazione',
        'adjust_contribution_inflation_help': 'Se selezionato, il contributo annuale aumenterà ogni anno del tasso di inflazione. Se non selezionato, il contributo rimane fisso.',
        'inflation': 'Inflazione annuale (%)',
        
        # Real withdrawal parameters
        'withdrawal_section_title': 'Impostazioni Prelievi Pensione',
        'use_real_withdrawal': 'Usa prelievo REALE (raccomandato)',
        'use_real_withdrawal_help': 'Se selezionato, l\'importo del prelievo mantiene potere d\'acquisto costante aggiustandosi per l\'inflazione. Se non selezionato, usa un importo nominale fisso che perde potere d\'acquisto nel tempo.',
        'real_withdrawal_amount': 'Prelievo annuale REALE (€ in potere d\'acquisto di oggi)',
        'real_withdrawal_help': 'Questo importo rappresenta il potere d\'acquisto di OGGI. Al pensionamento, sarà automaticamente aggiustato per l\'inflazione durante l\'accumulo, poi continuerà ad aggiustarsi annualmente. Esempio: €12.000 oggi → €22.235 al pensionamento (dopo 25 anni al 2.5%) → €22.791 nel secondo anno, ecc.',
        'nominal_withdrawal_amount': 'Prelievo annuale NOMINALE (€ importo fisso)',
        'nominal_withdrawal_help': 'Questo importo esatto sarà prelevato ogni anno senza aggiustamento per inflazione. Il potere d\'acquisto diminuirà nel tempo.',
        'real_withdrawal_explanation': 'Prelievo reale selezionato: Il tuo potere d\'acquisto rimarrà costante durante la pensione. L\'importo sarà prima aggiustato per l\'inflazione durante l\'accumulo, poi continuerà ad aggiustarsi annualmente durante la pensione.',
        'nominal_withdrawal_explanation': 'Prelievo nominale selezionato: L\'importo in euro rimane fisso, ma il tuo potere d\'acquisto diminuirà nel tempo a causa dell\'inflazione. Dopo 25 anni con inflazione 2.5%, €12.000 avranno il potere d\'acquisto di €6.473 di oggi.',
        
        'withdrawal': 'Prelievo annuale in pensione (€)',
        'capital_gains_tax_rate': 'Aliquota tassazione capital gain (%)',
        'capital_gains_tax_help': 'Aliquota fiscale applicata alla porzione di capital gain dei prelievi. L\'importo effettivo del prelievo sarà ridotto in base alla percentuale di capital gain nel portafoglio.',
        'n_simulations': 'Numero di simulazioni',
        
        # Portfolio configuration
        'portfolio_config': 'Configurazione Portafoglio',
        'accumulation_portfolio': 'Portafoglio Fase di Accumulo',
        'retirement_portfolio': 'Portafoglio Fase Pensionistica',
        'use_same_portfolio': 'Usa stesso portafoglio per entrambe le fasi',
        'use_same_portfolio_help': 'Se selezionato, la stessa allocazione di portafoglio sarà utilizzata sia per la fase di accumulo che per quella pensionistica.',
        
        'investment_profile': 'Profilo di Investimento',
        'accumulation_profile': 'Profilo Accumulo',
        'retirement_profile': 'Profilo Pensione',
        'select_profile': 'Seleziona profilo:',
        'load_profile': 'Carica Profilo Selezionato',
        'allocation_percent': 'Allocazione (%)',
        'ter_percent': 'TER (%)',
        'edit_parameters': 'Modifica Parametri',
        'advanced_parameters': 'Parametri Avanzati',
        'return_percent': 'Rendimento (%)',
        'volatility_percent': 'Volatilità (%)',
        'min_return_percent': 'Rendimento Min (%)',
        'max_return_percent': 'Rendimento Max (%)',
        'return_label': 'Rendimento',
        'volatility_label': 'Volatilità',
        'min_return_label': 'Rendimento Min',
        'max_return_label': 'Rendimento Max',
        'reset_allocations': 'Azzera Allocazioni',
        'balance_allocations': 'Bilancia Allocazioni',
        'total_allocation_error': 'Allocazione totale: {:.1f}% (deve essere 100%)',
        'correct_allocation': 'Allocazione corretta: {:.1f}%',
        
        # Charts and tables
        'allocation_chart': 'Grafico Allocazione',
        'accumulation_chart': 'Grafico Fase Accumulo',
        'retirement_chart': 'Grafico Fase Pensione',
        'portfolio_distribution': 'Distribuzione Portafoglio',
        'no_asset_selected': 'Nessun asset selezionato',
        'asset_summary': 'Riepilogo Asset',
        'accumulation_summary': 'Asset Accumulo',
        'retirement_summary': 'Asset Pensione',
        'no_active_assets': 'Nessun asset attivo',
        
        # Simulation
        'run_simulation': 'AVVIA SIMULAZIONE',
        'select_assets_error': 'Seleziona almeno un asset con allocazione > 0!',
        'select_accumulation_assets_error': 'Seleziona almeno un asset con allocazione > 0 per la fase di accumulo!',
        'select_retirement_assets_error': 'Seleziona almeno un asset con allocazione > 0 per la fase pensionistica!',
        'fix_allocations_error': 'Correggi prima le allocazioni!',
        'fix_accumulation_allocations_error': 'Correggi prima le allocazioni della fase di accumulo!',
        'fix_retirement_allocations_error': 'Correggi prima le allocazioni della fase pensionistica!',
        'simulation_progress': 'Simulazione in corso...',
        'simulation_step': 'Simulazione {} di {}',
        'simulation_completed': 'Simulazione completata!',
        
        # Results
        'simulation_results': 'Risultati Simulazione',
        'total_deposited': 'Totale Depositato',
        'median_accumulation': 'Valore Mediano Accumulo',
        'median_final': 'Valore Mediano Finale',
        'success_rate': 'Tasso di Successo',
        'real_withdrawal_amount_result': 'Importo Prelievo Reale (Dopo Tasse)',
        'accumulation_phase': 'Fase di Accumulo (Con Inflazione)',
        'accumulation_phase_real': 'Fase di Accumulo (Con Inflazione)',
        'accumulation_phase_nominal': 'Fase di Accumulo (Senza Inflazione)',
        'final_values': 'Valori Finali (Con Inflazione)',
        'final_values_info': 'I valori finali sono calcolati considerando l\'inflazione durante la fase di pensionamento',
        'percentile': 'Percentile',
        'value_euro': 'Valore (€)',
        'cagr_percent': 'CAGR (%)',
        'median': 'Mediana',
        'average': 'Media',
        'distribution_accumulation': 'Distribuzione dei Valori di Fine Accumulo (Con Inflazione)',
        'distribution_accumulation_real': 'Distribuzione dei Valori di Fine Accumulo (Con Inflazione)',
        'distribution_accumulation_nominal': 'Distribuzione dei Valori di Fine Accumulo (Senza Inflazione)',
        'distribution_final': 'Distribuzione dei Valori Finali (Con Inflazione)',
        'frequency': 'Frequenza',
        
        # Enhanced chart labels
        'distribution_charts_title': 'Grafici di Distribuzione e Correlazione',
        'distributions_tab': 'Distribuzioni',
        'correlations_tab': 'Correlazioni (Nominali)',
        'comparison_tab': 'Confronto Nominali vs Reali',
        'accumulation_nominal_dist': 'Distribuzione Valori Accumulo (Nominale)',
        'accumulation_real_dist': 'Distribuzione Valori Accumulo (Reale)',
        'final_nominal_dist': 'Distribuzione Valori Finali (Nominali)',
        'final_real_dist': 'Distribuzione Valori Finali (Reali)',
        'accumulation_final_correlation': 'Correlazione Accumulo vs Finale (Nominale)',
        'accumulation_final_heatmap': 'Mappa di Calore: Accumulo → Finale (Nominale)',
        'final_values_comparison': 'Confronto Valori Finali: Nominali vs Reali',
        'final_values_correlation': 'Correlazione Valori Finali: Reali vs Nominali',
        'correlation_label': 'Correlazione',
        'inflation_impact_label': 'Impatto Inflazione Media',
        'inflation_impact_text': 'I valori reali sono mediamente il {:.1f}% dei valori nominali',
        'one_to_one_line': 'Linea 1:1',
        
        # Success messages
        'excellent_success': 'Eccellente! Con {:.1f}% di probabilità di successo, il piano pensionistico appare ben finanziato',
        'fair_success': 'Discreto. Con {:.1f}% di tasso di successo, considera di rivedere la strategia.',
        'warning_success': 'Attenzione! Solo {:.1f}% di probabilità di successo. Aggiustamento della strategia raccomandato.',
        
        # Footer
        'footer': 'Simulatore Monte Carlo per Investimenti - Solo a Scopo Educativo',
        
        # Config errors
        'config_not_found': 'File di configurazione \'{}\' non trovato!',
        'config_load_error': 'Errore nel caricamento del file di configurazione: {}',
        'asset_characteristics_error': 'Errore nel caricamento delle caratteristiche degli asset: {}',
        
        # VaR/CVaR Risk Analysis
        'risk_analysis_title': 'Analisi del Rischio (VaR & CVaR)',
        'var_explanation_title': 'Cosa sono VaR e CVaR?',
        'key_risk_metrics_title': 'Metriche di Rischio Chiave (Valori Finali)',
        'risk_visualizations_title': 'Visualizzazioni VaR e CVaR',
        'distribution_with_var_cvar': 'Distribuzione con VaR/CVaR',
        'phase_comparison': 'Confronto per Fase',
        'var_cvar_table_by_phase': 'Tabella VaR e CVaR per Fase',
        'loss_probability_analysis': 'Analisi Probabilità di Perdita',
        'minimum_value_95_percent': 'Valore minimo nel 95% dei casi',
        'average_value_worst_5_percent': 'Valore medio nei peggiori 5% dei casi',
        'average_value_all_scenarios': 'Valore medio di tutti gli scenari',
        'difference_mean_cvar': 'Differenza tra media e CVaR 5%',
        'high_risk': 'ALTO RISCHIO',
        'moderate_high_risk': 'RISCHIO MODERATO-ALTO',
        'moderate_risk': 'RISCHIO MODERATO',
        'low_risk': 'RISCHIO BASSO',
        'significant_probability_lose_all': 'Significativa probabilità di perdere tutto il capitale',
        'worst_scenarios_very_negative': 'I peggiori scenari possono essere molto negativi',
        'manageable_risk_monitor': 'Rischio gestibile ma da monitorare',
        'worst_scenarios_contained': 'Scenari peggiori relativamente contenuti',
        'final_values_distribution_var_cvar': 'Distribuzione Valori Finali con VaR e CVaR',
        'var_cvar_comparison_phases': 'Confronto VaR e CVaR tra le Fasi',
        'total_loss_probability': 'Probabilità Perdita Totale',
        'prob_final_less_deposited': 'Probabilità che il portfolio finale sia inferiore al totale depositato',
        'average_value_when_loss': 'Valore Medio (quando c\'è perdita)',
        'probability_by_threshold': 'Probabilità per Soglia:',
        'loss_probability_by_threshold': 'Probabilità di Perdita per Soglia',
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
            'Protective': 'Protective',
            'Conservative': 'Conservative',
            'Moderate': 'Moderate', 
            'Dynamic': 'Dynamic',
            'Aggressive': 'Aggressive',
            'StrategicAccumulation': 'Growth Dynamic',
            'Diversified': 'Diversified',
            'StrategicDecumulation': 'Income Dynamic',
            'UserDefined': 'User Defined'
        },
        'it': {
            'Protective': 'Protettivo',
            'Conservative': 'Conservativo',
            'Moderate': 'Moderato',
            'Dynamic': 'Dinamico', 
            'Aggressive': 'Aggressivo',
            'StrategicAccumulation': 'Crescita Dinamica',
            'Diversified': 'Diversificato',
            'StrategicDecumulation': 'Rendita Dinamica',            
            'UserDefined': 'Allocazione Utente'
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
            'IlMattone': 'Real Estate',
            'UserAsset': 'User Custom',
            'UserAsset1': 'User Asset 1',
            'UserAsset2': 'User Asset 2'
        },
        'it': {
            'Stocks': 'Azioni',
            'Bond': 'Obbligazioni', 
            'Gold': 'Oro',
            'REIT': 'Immobiliare',
            'Commodities': 'Materie Prime',
            'Cash': 'Liquidità',
            'IlMattone': 'Il Mattone',
            'UserAsset': 'Asset Custom',
            'UserAsset1': 'Asset Utente 1',
            'UserAsset2': 'Asset Utente 2'
        }
    }
    return assets.get(lang, assets['en'])

