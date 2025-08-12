@staticmethod
    def _show_detailed_withdrawal_analysis(results, nominal_withdrawal, use_real_withdrawal, 
                                         inflation_rate, years_to_retirement, years_retired, lang):
        """Show detailed analysis of withdrawal strategy over time - CORRECTED VERSION"""
        st.subheader("📊 " + ("Analisi Dettagliata Prelievi" if lang == 'it' else "Detailed Withdrawal Analysis"))
        
        # Get tax analysis for withdrawal insights
        tax_analysis = results.get('tax_details', [])
        valid_tax_details = [detail for detail in tax_analysis if detail and isinstance(detail, dict)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Withdrawal strategy comparison table
            st.markdown("**" + ("Confronto Strategie di Prelievo" if lang == 'it' else "Withdrawal Strategy Comparison") + "**")
            
            years_sample = [1, 5, 10, 15, 20, 25]
            years_sample = [y for y in years_sample if y <= years_retired]
            
            comparison_data = []
            for year in years_sample:
                if use_real_withdrawal:
                    # CORRECTED: Calculate based on total inflation years from today
                    total_inflation_years = years_to_retirement + (year - 1)
                    nominal_amount = nominal_withdrawal * ((1 + inflation_rate/100) ** total_inflation_years)
                    real_value = nominal_withdrawal  # Constant purchasing power in today's terms
                else:
                    nominal_amount = nominal_withdrawal  # Fixed amount
                    # CORRECTED: Calculate purchasing power in today's terms
                    total_inflation_years = years_to_retirement + (year - 1)
                    real_value = nominal_withdrawal / ((1 + inflation_rate/100) ** total_inflation_years)
                
                comparison_data.append({
                    ('Anno' if lang == 'it' else 'Year'): year,
                    ('Importo Nominale (€)' if lang == 'it' else 'Nominal Amount (€)'): f"{nominal_amount:,.0f}",
                    ('Valore Reale (€)' if lang == 'it' else 'Real Value (€)'): f"{real_value:,.0f}"
                })
            
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True)
        
        with col2:
            # Additional withdrawal insights
            st.markdown("**" + ("Insights Strategia Prelievi" if lang == 'it' else "Withdrawal Strategy Insights") + "**")
            
            # CORRECTED: Calculate total withdrawals over retirement period
            if use_real_withdrawal:
                # Real withdrawal: Calculate total nominal withdrawn correctly
                total_nominal_withdrawn = 0
                for year in range(int(years_retired)):
                    total_inflation_years = years_to_retirement + year
                    annual_withdrawal = nominal_withdrawal * ((1 + inflation_rate/100) ** total_inflation_years)
                    total_nominal_withdrawn += annual_withdrawal
                
                total_real_value = nominal_withdrawal * years_retired  # Constant purchasing power in today's terms
                
                st.metric(
                    "Totale Prelevato (Nominale)" if lang == 'it' else "Total Withdrawn (Nominal)",
                    f"€{total_nominal_withdrawn:,.0f}"
                )
                st.metric(
                    "Valore Reale Totale (Oggi)" if lang == 'it' else "Total Real Value (Today)",
                    f"€{total_real_value:,.0f}"
                )
                st.success("✅ " + ("Potere d'acquisto preservato" if lang == 'it' else "Purchasing power preserved"))
                
            else:
                total_nominal_withdrawn = nominal_withdrawal * years_retired
                # CORRECTED: Calculate real value properly
                total_real_value = 0
                for year in range(int(years_retired)):
                    total_inflation_years = years_to_retirement + year
                    annual_real_value = nominal_withdrawal / ((1 + inflation_rate/100) ** total_inflation_years)
                    total_real_value += annual_real_value
                
                purchasing_power_erosion = (1 - total_real_value/total_nominal_withdrawn) * 100
                
                st.metric(
                    "Totale Prelevato (Nominale)" if lang == 'it' else "Total Withdrawn (Nominal)",
                    f"€{total_nominal_withdrawn:,.0f}"
                )
                st.metric(
                    "Valore Reale Totale (Oggi)" if lang == 'it' else "Total Real Value (Today)",
                    f"€{total_real_value:,.0f}"
                )
                st.error(f"📉 " + ("Erosione potere d'acquisto:" if lang == 'it' else "Purchasing power erosion:") + f" {purchasing_power_erosion:.1f}%")

    @staticmethod
    def _show_key_metrics_with_withdrawal_info(total_deposited, median_accumulation_nominal, 
                                             median_final_nominal, success_rate, nominal_withdrawal, 
                                             use_real_withdrawal, inflation_rate, years_to_retirement, years_retired, lang):
        """Display key metrics with CORRECTED withdrawal information"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(get_text('total_deposited', lang), f"€{total_deposited:,.0f}")
        
        with col2:
            label_nominal = get_text('median_accumulation', lang) + " (Nominale)" if lang == 'it' else get_text('median_accumulation', lang) + " (Nominal)"
            st.metric(label_nominal, f"€{median_accumulation_nominal:,.0f}")
        
        with col3:
            label_final_nominal = get_text('median_final', lang) + " (Nominale)" if lang == 'it' else get_text('median_final', lang) + " (Nominal)"
            st.metric(label_final_nominal, f"€{median_final_nominal:,.0f}")
        
        with col4:
            st.metric(get_text('success_rate', lang), f"{success_rate:.1f}%")
        
        # Withdrawal summary section
        st.markdown("---")
        st.subheader("💰 " + ("Riassunto Strategia Prelievi" if lang == 'it' else "Withdrawal Strategy Summary"))
        
        col1, col2 = st.columns(2)
        
        with col1:
            if use_real_withdrawal:
                st.success("✅ **" + ("Prelievo REALE selezionato" if lang == 'it' else "REAL withdrawal selected") + "**")
                
                # CORRECTED: Calculate progression properly
                first_withdrawal = nominal_withdrawal * ((1 + inflation_rate/100) ** years_to_retirement)
                final_withdrawal = nominal_withdrawal * ((1 + inflation_rate/100) ** (years_to_retirement + years_retired - 1))
                
                st.info(f"""
                **{"Dettagli Prelievo Reale:" if lang == 'it' else "Real Withdrawal Details:"}**
                - {"Potere d'acquisto oggi:" if lang == 'it' else "Today's purchasing power:"} €{nominal_withdrawal:,.0f}
                - {"Primo prelievo (al pensionamento):" if lang == 'it' else "First withdrawal (at retirement):"} €{first_withdrawal:,.0f}
                - {"Ultimo prelievo (anno" if lang == 'it' else "Final withdrawal (year"} {int(years_retired)}): €{final_withdrawal:,.0f}
                - {"Potere d'acquisto:" if lang == 'it' else "Purchasing power:"} {"Costante (€" if lang == 'it' else "Constant (€"}{nominal_withdrawal:,.0f} {"di oggi)" if lang == 'it' else "today's value)"} 💪
                - {"Incremento annuale:" if lang == 'it' else "Annual increase:"} {inflation_rate:.1f}%
                """)
            else:
                st.warning("⚠️ **" + ("Prelievo NOMINALE selezionato" if lang == 'it' else "NOMINAL withdrawal selected") + "**")
                
                # CORRECTED: Calculate purchasing power loss properly
                final_purchasing_power = nominal_withdrawal / ((1 + inflation_rate/100) ** (years_to_retirement + years_retired - 1))
                purchasing_power_loss = (1 - final_purchasing_power/nominal_withdrawal) * 100
                
                st.error(f"""
                **{"Dettagli Prelievo Nominale:" if lang == 'it' else "Nominal Withdrawal Details:"}**
                - {"Importo fisso:" if lang == 'it' else "Fixed amount:"} €{nominal_withdrawal:,.0f} {"ogni anno" if lang == 'it' else "every year"}
                - {"Potere d'acquisto finale:" if lang == 'it' else "Final purchasing power:"} €{final_purchasing_power:,.0f} {"(di oggi)" if lang == 'it' else "(today's value)"}
                - {"Perdita potere d'acquisto:" if lang == 'it' else "Purchasing power loss:"} {purchasing_power_loss:.1f}% 📉
                - {"Incremento annuale:" if lang == 'it' else "Annual increase:"} 0% ({"fisso" if lang == 'it' else "fixed"})
                """)
        
        with col2:
            # CORRECTED: Withdrawal progression chart
            years = list(range(1, int(years_retired) + 1))
            
            if use_real_withdrawal:
                # Real withdrawal progression - corrected calculation
                withdrawal_amounts = []
                purchasing_power = []
                for year in range(int(years_retired)):
                    total_inflation_years = years_to_retirement + year
                    withdrawal_amount = nominal_withdrawal * ((1 + inflation_rate/100) ** total_inflation_years)
                    withdrawal_amounts.append(withdrawal_amount)
                    purchasing_power.append(nominal_withdrawal)  # Constant purchasing power
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=years, y=withdrawal_amounts,
                    mode='lines+markers',
                    name='Importo Nominale' if lang == 'it' else 'Nominal Amount',
                    line=dict(color='blue')
                ))
                fig.add_trace(go.Scatter(
                    x=years, y=purchasing_power,
                    mode='lines+markers',
                    name='Potere d\'Acquisto (Oggi)' if lang == 'it' else 'Purchasing Power (Today)',
                    line=dict(color='green', dash='dash')
                ))
                
                fig.update_layout(
                    title="Progressione Prelievo Reale" if lang == 'it' else "Real Withdrawal Progression",
                    xaxis_title="Anno di Pensione" if lang == 'it' else "Retirement Year",
                    yaxis_title="Importo (€)" if lang == 'it' else "Amount (€)",
                    height=300
                )
            else:
                # Nominal withdrawal progression - corrected calculation
                withdrawal_amounts = [nominal_withdrawal] * int(years_retired)  # Fixed amount
                purchasing_power = []
                for year in range(int(years_retired)):
                    total_inflation_years = years_to_retirement + year
                    real_value = nominal_withdrawal / ((1 + inflation_rate/100) ** total_inflation_years)
                    purchasing_power.append(real_value)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=years, y=withdrawal_amounts,
                    mode='lines+markers',
                    name='Importo Nominale' if lang == 'it' else 'Nominal Amount',
                    line=dict(color='blue')
                ))
                fig.add_trace(go.Scatter(
                    x=years, y=purchasing_power,
                    mode='lines+markers',
                    name='Potere d\'Acquisto (Oggi)' if lang == 'it' else 'Purchasing Power (Today)',
                    line=dict(color='red', dash='dash')
                ))
                
                fig.update_layout(
                    title="Progressione Prelievo Nominale" if lang == 'it' else "Nominal Withdrawal Progression",
                    xaxis_title="Anno di Pensione" if lang == 'it' else "Retirement Year",
                    yaxis_title="Importo (€)" if lang == 'it' else "Amount (€)",
                    height=300
                )
            
            st.plotly_chart(fig, use_container_width=True)
