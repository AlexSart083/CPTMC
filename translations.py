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
            "**What does this application do?**\n"
            "This application uses the Monte Carlo method to generate thousands of possible market scenarios, "
            "simulating whether the selected portfolio may or may not be suitable for the retirement plan "
            "chosen, based on the parameters entered by the user. The app estimates the probability of success "
            "of the plan and delivers an overview of possible outcomes while factoring in inflation, based on the "
            "performance simulations of the selected assets."
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
        'adjust_contribution_inflation': '📈 Adjust contribution for inflation',
        'adjust_contribution_inflation_help': 'If checked, the annual contribution will increase each year by the inflation rate. If unchecked, the contribution remains fixed.',
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
        'edit_parameters': '✏️ Edit Parameters
