# knowledge_graph_sample.py

sample_kg = {
    "nodes": [
        {"id": "government", "label": "Government", "type": "ORG"},
        # {"id": "government_bonds", "label": "Government Bonds", "type": "Security"},
        {"id": "the_fed", "label": "Federal Reserve", "type": "ORG"},
        {"id": "policy_rate", "label": "Policy Interest Rate", "type": "RATE"},
        {"id": "yield_curve", "label": "Yield Curve", "type": "RATE"},
        {"id": "credit", "label": "Credit Supply", "type": "METRIC"},
        {"id": "exchange_rate", "label": "Exchange Rate", "type": "RATE"},
        {"id": "SPX", "label": "S&P 500 Index (SPX)", "type": "ASSET"},
        {"id": "UST", "label": "US Treasuries (UST)", "type": "ASSET"},
        {"id": "inflation_expectations", "label": "Inflation Expectations", "type": "METRIC"},
        {"id": "imported_prices", "label": "Imported Goods Prices", "type": "METRIC"},
        {"id": "domestic_prices", "label": "Domestic Good Prices", "type": "METRIC"},
        {"id": "gdp", "label": "GDP", "type": "METRIC"},
        {"id": "cpi", "label": "CPI", "type": "METRIC"},
        {"id": "inflation", "label": "Inflation", "type": "METRIC"},
        {"id": "deflation", "label": "Deflation", "type": "METRIC"},
        {"id": "monetary_policy", "label": "Monetary Policy", "type": "POLICY"},
        {"id": "fiscal_policy", "label": "Fiscal Policy", "type": "POLICY"},
        {"id": "liquidity", "label": "Liquidity Injection", "type": "MEASURE"},
        {"id": "borrowing_spending", "label": "Borrowing and Spending", "type": "METRIC"},
        {"id": "debt_servicing_costs", "label": "Debt Servicing Costs", "type": "METRIC"},
        {"id": "unemployment_rate", "label": "Unemployment Rate", "type": "METRIC"},
    
        {"id": "credit_demand", "label": "Credit Demand", "type": "METRIC"},
        {"id": "demand", "label": "Aggregate Demand", "type": "METRIC"},
        {"id": "supply", "label": "Aggregate Supply", "type": "METRIC"},
        {"id": "supply_demand_imbalance", "label": "Supply-Demand Imbalance", "type": "METRIC"},
        
        {"id": "national_debt", "label": "National Debt", "type": "METRIC"},
        {"id": "behavior_change", "label": "Behavior Change (Price/Wage Decisions)", "type": "ACTION"},
        {"id": "central_bank_credibility", "label": "Central Bank Credibility", "type": "METRIC"},
        {"id": "confidence_in_central_bank", "label": "Confidence in Central Bank", "type": "METRIC"},
        {"id": "supply_shock", "label": "Supply-Side Shock", "type": "EVENT"},
        {"id": "costs_of_goods_services", "label": "Costs of Goods and Services", "type": "METRIC"},
        {"id": "production", "label": "Production/Distribution", "type": "METRIC"},
        {"id": "tariff", "label": "Tariffs", "type": "EVENT"},
        {"id": "global_trade", "label": "Global Trade", "type": "METRIC"},
        {"id": "sentiment", "label": "Global Sentiment", "type": "METRIC"},
       
    ],
    "edges": [
        # Central Bank Chain
        {"source": "the_fed", "target": "policy_rate", "relation": "sets", "sign": "+/-"},

        # Policy rate affects yield curve, credit, exchange rate, SPX, UST, inflation_expectations
        {"source": "policy_rate", "target": "yield_curve", "relation": "affects", "sign": "+"},
        {"source": "policy_rate", "target": "credit", "relation": "affects", "sign": "-"},
        {"source": "policy_rate", "target": "exchange_rate", "relation": "affects", "sign": "+"},
        {"source": "policy_rate", "target": "SPX", "relation": "affects", "sign": "-"},
        {"source": "policy_rate", "target": "UST", "relation": "affects", "sign": "+"},
        {"source": "policy_rate", "target": "inflation_expectations", "relation": "affects", "sign": "-"},
        # Yield curve affects UST
        {"source": "yield_curve", "target": "UST", "relation": "affects", "sign": "+"},
        {"source": "credit", "target": "gdp", "relation": "affects", "sign": "+"},
        
        # Exchange rate affects imported_prices
        {"source": "exchange_rate", "target": "imported_prices", "relation": "affects", "sign": "-"},
        # GDP affects CPI
        {"source": "gdp", "target": "domestic_prices", "relation": "affects", "sign": "+"},
        # Imported and domestic goods prices affect aggregate prices
        {"source": "imported_prices", "target": "cpi", "relation": "affects", "sign": "+"},
        {"source": "domestic_prices", "target": "cpi", "relation": "affects", "sign": "+"},
        # Exchange rate, inflation_expectations, gdp also affect CPI

        {"source": "inflation_expectations", "target": "cpi", "relation": "affects", "sign": "+"},
        {"source": "gdp", "target": "cpi", "relation": "affects", "sign": "+"},
        # inflation measured by CPI
        {"source": "cpi", "target": "inflation", "relation": "measures", "sign": "+"},
        {"source": "inflation", "target": "the_fed", "relation": "affects", "sign": "+/-"},
        {"source": "unemployment_rate", "target": "the_fed", "relation": "affects", "sign": "+/-"},
        {"source": "government", "target": "the_fed", "relation": "affects", "sign": "+/-"},
        {"source": "debt_servicing_costs", "target": "government", "relation": "affects", "sign": "+/-"},

        # Inflation and deflation affect inflation_expectations
        {"source": "inflation", "target": "inflation_expectations", "relation": "affects", "sign": "+"},
        {"source": "deflation", "target": "inflation_expectations", "relation": "affects", "sign": "-"},
                
        # --- Core Inflation Transmission Chain ---
        {"source": "monetary_policy", "target": "liquidity", "relation": "affects", "sign": "+/-", "description": "Central bank can either inject or withdraw liquidity into the economy"},
        {"source": "monetary_policy", "target": "policy_rate", "relation": "sets", "sign": "+/-"},
        {"source": "liquidity", "target": "borrowing_spending", "relation": "increases", "sign": "+"},
        {"source": "policy_rate", "target": "borrowing_spending", "relation": "increases", "sign": "-"},
        {"source": "borrowing_spending", "target": "credit_demand", "relation": "increases", "sign": "+"},
        
        
        # --- Demand-Supply Imbalance Chain ---
        {"source": "borrowing_spending", "target": "demand", "relation": "increases", "sign": "+"},
        {"source": "demand", "target": "supply_demand_imbalance", "relation": "heightens_imbalance", "sign": "+"},
        {"source": "supply", "target": "supply_demand_imbalance", "relation": "strains_imbalance", "sign": "-"},
        {"source": "supply_demand_imbalance", "target": "inflation", "relation": "increases_risk", "sign": "+"},
        # --- Fiscal Policy Chain ---
        {"source": "fiscal_policy", "target": "national_debt", "relation": "affects", "sign": "+/-"},
        {"source": "fiscal_policy", "target": "borrowing_spending", "relation": "affects", "sign": "+/-"},
        
        {"source": "policy_rate", "target": "debt_servicing_costs", "relation": "affects", "sign": "+"},
        {"source": "national_debt", "target": "debt_servicing_costs", "relation": "affects", "sign": "+"},

    
        {"source": "inflation_expectations", "target": "behavior_change", "relation": "drives", "sign": "+"},
        {"source": "behavior_change", "target": "inflation", "relation": "reinforces", "sign": "+"},
        # --- Credibility Feedback Loop ---
        
        {"source": "confidence_in_central_bank", "target": "central_bank_credibility", "relation": "increases", "sign": "+"},
        {"source": "central_bank_credibility", "target": "inflation", "relation": "reduce", "sign": "-"},
        # --- Supply Shock Chain ---
        {"source": "supply_shock", "target": "costs_of_goods_services", "relation": "increases", "sign": "+"},
        {"source": "costs_of_goods_services", "target": "cpi", "relation": "increases", "sign": "+"},
        
        # --- Geopolitical Risk Chain ---
        {"source": "tariff", "target": "global_trade", "relation": "depresses", "sign": "-"},
        {"source": "tariff", "target": "sentiment", "relation": "hurts", "sign": "-"},
        {"source": "tariff", "target": "costs_of_goods_services", "relation": "increases", "sign": "+"},

        # ---- government bonds ----
        {"source": "government", "target": "UST", "relation": "issues", "sign": "+"},
        {"source": "government", "target": "borrowing_spending", "relation": "sets", "sign": "+/-", "description": "Government sets borrowing and spending levels through fiscal policies"},

        {"source": "the_fed", "target": "UST", "relation": "trades", "sign": "+", "description": "The Federal Reserve trades US Treasuries (UST) to inject or withdraw liquidity"},
        {"source": "the_fed", "target": "liquidity", "relation": "affects", "sign": "+/-", "description": "The Federal Reserve's actions affect liquidity in the financial system"},
    ]
} 