# knowledge_graph_sample.py

sample_kg = {
    "nodes": [
        {"id": "central_bank", "label": "Central Bank", "type": "ORG"},
        {"id": "policy_rate", "label": "Policy Interest Rate", "type": "RATE"},
        {"id": "yield_curve", "label": "Yield Curve", "type": "RATE"},
        {"id": "credit", "label": "Credit Supply", "type": "METRIC"},
        {"id": "exchange_rate", "label": "Exchange Rate", "type": "RATE"},
        {"id": "SPX", "label": "S&P 500 Index (SPX)", "type": "ASSET"},
        {"id": "UST", "label": "US Treasuries (UST)", "type": "ASSET"},
        {"id": "expectations", "label": "Expectations", "type": "METRIC"},
        {"id": "imported_prices", "label": "Imported Good Prices", "type": "METRIC"},
        {"id": "domestic_prices", "label": "Domestic Good Prices", "type": "METRIC"},
        {"id": "output", "label": "Aggregate Output", "type": "METRIC"},
        {"id": "prices", "label": "Aggregate Prices", "type": "METRIC"},
        {"id": "inflation", "label": "Inflation", "type": "METRIC"},
        {"id": "deflation", "label": "Deflation", "type": "METRIC"},
        {"id": "accommodative_policy", "label": "Accommodative Monetary & Fiscal Policies", "type": "POLICY"},
        {"id": "liquidity", "label": "Liquidity Injection", "type": "MEASURE"},
        {"id": "borrowing_spending", "label": "Borrowing and Spending", "type": "METRIC"},
        {"id": "economic_slack", "label": "Economic Slack", "type": "METRIC"},
        {"id": "credit_demand", "label": "Credit Demand", "type": "METRIC"},
        {"id": "demand", "label": "Aggregate Demand", "type": "METRIC"},
        {"id": "supply", "label": "Aggregate Supply", "type": "METRIC"},
        {"id": "supply_demand_imbalance", "label": "Supply-Demand Imbalance", "type": "METRIC"},
        {"id": "fiscal_dominance", "label": "Fiscal Dominance", "type": "POLICY"},
        {"id": "debt_pressure", "label": "High Debt Pressure", "type": "METRIC"},
        {"id": "inflation_expectations", "label": "Inflation Expectations", "type": "METRIC"},
        {"id": "behavior_change", "label": "Behavior Change (Price/Wage Decisions)", "type": "ACTION"},
        {"id": "credibility", "label": "Central Bank Credibility", "type": "METRIC"},
        {"id": "confidence", "label": "Confidence in Central Bank", "type": "METRIC"},
        {"id": "supply_shock", "label": "Supply-Side Shock", "type": "SHOCK"},
        {"id": "cost_increase", "label": "Sudden Cost Increases", "type": "METRIC"},
        {"id": "production", "label": "Production/Distribution", "type": "METRIC"},
        {"id": "geopolitical", "label": "Geopolitical Developments", "type": "EVENT"},
        {"id": "tariff_war", "label": "Tariff Wars with China", "type": "EVENT"},
        {"id": "global_trade", "label": "Global Trade", "type": "METRIC"},
        {"id": "sentiment", "label": "Global Sentiment", "type": "METRIC"},
        {"id": "global_costs", "label": "Global Costs", "type": "METRIC"}
    ],
    "edges": [
        # Central Bank sets policy rate
        {"source": "central_bank", "target": "policy_rate", "relation": "sets", "sign": "+"},
        # Policy rate affects yield curve, credit, exchange rate, SPX, UST, expectations
        {"source": "policy_rate", "target": "yield_curve", "relation": "affects", "sign": "+"},
        {"source": "policy_rate", "target": "credit", "relation": "affects", "sign": "-"},
        {"source": "policy_rate", "target": "exchange_rate", "relation": "affects", "sign": "+"},
        {"source": "policy_rate", "target": "SPX", "relation": "affects", "sign": "-"},
        {"source": "policy_rate", "target": "UST", "relation": "affects", "sign": "+"},
        {"source": "policy_rate", "target": "expectations", "relation": "affects", "sign": "-"},
        # Yield curve affects UST
        {"source": "yield_curve", "target": "UST", "relation": "affects", "sign": "+"},
        # Credit, SPX, UST affect output
        {"source": "credit", "target": "output", "relation": "transmits_to", "sign": "+"},
        {"source": "SPX", "target": "output", "relation": "transmits_to", "sign": "+"},
        {"source": "UST", "target": "output", "relation": "transmits_to", "sign": "-"},
        # Exchange rate affects imported good prices
        {"source": "exchange_rate", "target": "imported_prices", "relation": "affects", "sign": "+"},
        # Output affects domestic good prices
        {"source": "output", "target": "domestic_prices", "relation": "affects", "sign": "+"},
        # Imported and domestic good prices affect aggregate prices
        {"source": "imported_prices", "target": "prices", "relation": "transmits_to", "sign": "+"},
        {"source": "domestic_prices", "target": "prices", "relation": "transmits_to", "sign": "+"},
        # Exchange rate, expectations, output also affect aggregate prices
        {"source": "exchange_rate", "target": "prices", "relation": "transmits_to", "sign": "+"},
        {"source": "expectations", "target": "prices", "relation": "transmits_to", "sign": "+"},
        {"source": "output", "target": "prices", "relation": "affects", "sign": "+"},
        # Prices affect inflation and deflation
        {"source": "prices", "target": "inflation", "relation": "affects", "sign": "+"},
        {"source": "prices", "target": "deflation", "relation": "affects", "sign": "-"},
        # Inflation and deflation affect expectations
        {"source": "inflation", "target": "expectations", "relation": "affects", "sign": "+"},
        {"source": "deflation", "target": "expectations", "relation": "affects", "sign": "-"},
        # Policy rate affects inflation and deflation
        {"source": "policy_rate", "target": "inflation", "relation": "affects", "sign": "-"},
        {"source": "policy_rate", "target": "deflation", "relation": "affects", "sign": "+"},
        # Inflation and deflation affect output
        {"source": "inflation", "target": "output", "relation": "affects", "sign": "-"},
        {"source": "deflation", "target": "output", "relation": "affects", "sign": "-"},
        # --- Core Inflation Transmission Chain ---
        {"source": "accommodative_policy", "target": "liquidity", "relation": "injects", "sign": "+"},
        {"source": "accommodative_policy", "target": "policy_rate", "relation": "keeps_low", "sign": "-"},
        {"source": "liquidity", "target": "borrowing_spending", "relation": "increases", "sign": "+"},
        {"source": "policy_rate", "target": "borrowing_spending", "relation": "increases", "sign": "-"},
        {"source": "borrowing_spending", "target": "economic_slack", "relation": "reduces", "sign": "-"},
        {"source": "borrowing_spending", "target": "credit_demand", "relation": "increases", "sign": "+"},
        {"source": "economic_slack", "target": "prices", "relation": "reduces_slack_raises_prices", "sign": "-"},
        {"source": "credit_demand", "target": "prices", "relation": "raises_prices", "sign": "+"},
        # --- Demand-Supply Imbalance Chain ---
        {"source": "borrowing_spending", "target": "demand", "relation": "increases", "sign": "+"},
        {"source": "demand", "target": "supply_demand_imbalance", "relation": "heightens_imbalance", "sign": "+"},
        {"source": "supply", "target": "supply_demand_imbalance", "relation": "strains_imbalance", "sign": "-"},
        {"source": "supply_demand_imbalance", "target": "inflation", "relation": "increases_risk", "sign": "+"},
        # --- Fiscal Dominance Chain ---
        {"source": "fiscal_dominance", "target": "debt_pressure", "relation": "raises", "sign": "+"},
        {"source": "debt_pressure", "target": "policy_rate", "relation": "pressure_to_keep_low", "sign": "-"},
        {"source": "policy_rate", "target": "inflation", "relation": "keeps_rising", "sign": "-"},
        {"source": "inflation", "target": "inflation_expectations", "relation": "unanchors", "sign": "+"},
        {"source": "inflation_expectations", "target": "behavior_change", "relation": "drives", "sign": "+"},
        {"source": "behavior_change", "target": "inflation", "relation": "reinforces", "sign": "+"},
        # --- Credibility Feedback Loop ---
        {"source": "inflation_expectations", "target": "confidence", "relation": "reduces_confidence", "sign": "-"},
        {"source": "confidence", "target": "credibility", "relation": "reduces_credibility", "sign": "-"},
        {"source": "credibility", "target": "inflation", "relation": "worsens_dynamics", "sign": "+"},
        # --- Supply Shock Chain ---
        {"source": "supply_shock", "target": "cost_increase", "relation": "causes", "sign": "+"},
        {"source": "cost_increase", "target": "production", "relation": "impacts", "sign": "-"},
        {"source": "production", "target": "prices", "relation": "raises_consumer_prices", "sign": "+"},
        # --- Geopolitical Risk Chain ---
        {"source": "geopolitical", "target": "tariff_war", "relation": "leads_to", "sign": "+"},
        {"source": "tariff_war", "target": "global_trade", "relation": "depresses", "sign": "-"},
        {"source": "tariff_war", "target": "sentiment", "relation": "hurts", "sign": "-"},
        {"source": "tariff_war", "target": "global_costs", "relation": "raises", "sign": "+"},
        {"source": "global_costs", "target": "inflation", "relation": "contributes_to", "sign": "+"}
    ]
} 