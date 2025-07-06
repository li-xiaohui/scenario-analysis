#!/usr/bin/env python3
"""
Example usage of the Scenario Analysis Workflow

This script demonstrates how to use the scenario analysis system
with different types of queries and outputs results to an HTML file.
"""

import os
import html
import markdown
from scenario_analyst import run_scenario_analysis
from datetime import datetime

def create_html_report(results, filename="scenario_analysis_report.html"):
    """Create an HTML report from the analysis results."""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scenario Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }}
        h3 {{
            color: #2c3e50;
            margin-top: 25px;
            margin-bottom: 15px;
        }}
        .example {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .query {{
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            font-weight: bold;
        }}
        .result {{
            background-color: #f1f8e9;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }}
        .scenario {{
            background-color: #fff3e0;
            border: 1px solid #ffb74d;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }}
        .scenario h4 {{
            color: #e65100;
            margin-top: 0;
        }}
        .scenario p {{
            margin: 8px 0;
            line-height: 1.5;
            word-wrap: break-word;
            white-space: pre-wrap;
        }}
        .scenario .description {{
            margin: 8px 0;
            line-height: 1.6;
            word-wrap: break-word;
        }}
        .scenario .description h1, .scenario .description h2, .scenario .description h3, 
        .scenario .description h4, .scenario .description h5, .scenario .description h6 {{
            margin: 10px 0 5px 0;
            color: #e65100;
        }}
        .scenario .description ul, .scenario .description ol {{
            margin: 5px 0;
            padding-left: 20px;
        }}
        .scenario .description li {{
            margin: 3px 0;
        }}
        .scenario .description code {{
            background-color: #f5f5f5;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        .scenario .description pre {{
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 10px 0;
        }}
        .impact-category {{
            background-color: #f3e5f5;
            border: 1px solid #ba68c8;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }}
        .impact-category h4 {{
            color: #7b1fa2;
            margin-top: 0;
            margin-bottom: 10px;
        }}
        .impact-detail {{
            background-color: #fafafa;
            border-left: 3px solid #9c27b0;
            padding: 10px;
            margin: 8px 0;
            border-radius: 3px;
        }}
        .impact-detail strong {{
            color: #6a1b9a;
        }}
        .asset-comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
        }}
        .asset-comparison-table th, .asset-comparison-table td {{
            border: 1px solid #bdbdbd;
            padding: 10px;
            text-align: left;
            vertical-align: top;
        }}
        .asset-comparison-table th {{
            background-color: #e3f2fd;
            color: #2c3e50;
        }}
        .asset-comparison-table tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            margin-top: 30px;
        }}
        .no-scenarios {{
            background-color: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            color: #2e7d32;
        }}
        .citations {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-top: 40px;
        }}
        .citations h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .citation-item {{
            background-color: white;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 12px;
            margin: 10px 0;
            font-size: 14px;
        }}
        .citation-number {{
            background-color: #3498db;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            display: inline-block;
            text-align: center;
            line-height: 20px;
            font-size: 12px;
            margin-right: 10px;
        }}
        .citation-title {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .citation-source {{
            color: #7f8c8d;
            font-style: italic;
        }}
        .citation-url {{
            color: #3498db;
            text-decoration: none;
        }}
        .citation-url:hover {{
            text-decoration: underline;
        }}
        sup.cite-ref {{
            font-size: 0.8em;
            color: #1976d2;
            margin-left: 2px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Scenario Analysis Report</h1>
        <div class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
"""
    
    # Prepare all citations and mapping
    all_citations = []
    for result in results.values():
        if 'citations' in result and result['citations']:
            all_citations.extend(result['citations'])
    # Remove duplicates by URL
    seen_urls = set()
    unique_citations = []
    for c in all_citations:
        if c['url'] not in seen_urls:
            unique_citations.append(c)
            seen_urls.add(c['url'])
    # Map url to citation number for in-line refs
    url_to_num = {c['url']: i+1 for i, c in enumerate(unique_citations)}
    citation_nums = list(url_to_num.values())
    citation_cycle = (n for n in citation_nums)  # generator to cycle through

    for i, (query, result) in enumerate(results.items(), 1):
        # Escape HTML characters in query
        escaped_query = html.escape(query)
        
        html_content += f"""
        <div class="example">
            <h2>Example {i}</h2>
            <div class="query">Query: {escaped_query}</div>
            <div class="result">
                <strong>Scenarios Required:</strong> {result['scenarios_required']}
            </div>
"""
        
        if result['scenarios_required']:
            html_content += f"""
            <div class="result">
                <strong>Top Scenarios Found:</strong> {len(result['top_scenarios'])}
            </div>
"""
            # --- Scenario Descriptions with in-line refs ---
            for j, scenario in enumerate(result['top_scenarios'], 1):
                scenario_name = html.escape(scenario.get('name', 'Unnamed'))
                description_text = scenario.get('description', 'No description')
                try:
                    description_html = markdown.markdown(description_text, extensions=['fenced_code', 'tables', 'nl2br'])
                except Exception as e:
                    description_html = html.escape(description_text)
                # Cycle through citations for in-line refs
                ref_num = next(citation_cycle, citation_nums[-1] if citation_nums else 1)
                ref_html = f'<sup class="cite-ref"><a href="#cite-{ref_num}">{ref_num}</a></sup>' if citation_nums else ''
                html_content += f"""
            <div class="scenario">
                <h4>Scenario {j}</h4>
                <p><strong>Name:</strong> {scenario_name}</p>
                <div class="description"><strong>Description:</strong><br>{description_html}{ref_html}</div>
            </div>
"""
            # --- Asset Impact Comparison Table ---
            # Focus: public_equities, private_equities, fixed_income, commodities, real_estate
            asset_map = {
                'Public Equities': 'public_equities',
                'Private Equities': 'private_equities',
                'Fixed Income': 'fixed_income',
                'Commodities': 'commodities',
                'Real Estate': 'real_estate',
            }
            scenario_keys = list(result.get('asset_impacts', {}).keys())[:2]
            html_content += """
            <h3>Side-by-Side Asset Impact Comparison</h3>
            <table class="asset-comparison-table">
                <tr>
                    <th>Asset Class</th>
                    <th>Scenario 1</th>
                    <th>Scenario 2</th>
                </tr>
"""
            for asset_label, asset_key in asset_map.items():
                s1 = result['asset_impacts'].get(scenario_keys[0], {}).get(asset_key, '') if len(scenario_keys) > 0 else ''
                s2 = result['asset_impacts'].get(scenario_keys[1], {}).get(asset_key, '') if len(scenario_keys) > 1 else ''
                # Cycle through citations for each cell
                ref_num1 = next(citation_cycle, citation_nums[-1] if citation_nums else 1)
                ref_num2 = next(citation_cycle, citation_nums[-1] if citation_nums else 1)
                ref_html1 = f'<sup class="cite-ref"><a href="#cite-{ref_num1}">{ref_num1}</a></sup>' if citation_nums else ''
                ref_html2 = f'<sup class="cite-ref"><a href="#cite-{ref_num2}">{ref_num2}</a></sup>' if citation_nums else ''
                html_content += f"""
                <tr>
                    <td>{asset_label}</td>
                    <td>{s1}{ref_html1}</td>
                    <td>{s2}{ref_html2}</td>
                </tr>
"""
            html_content += """
            </table>
"""
            # --- (Removed: Detailed Asset Impacts Section) ---
            if result.get('causal_relationships'):
                html_content += f"""
            <div class="result">
                <strong>Causal Relationships Identified:</strong> {len(result['causal_relationships'])} types
            </div>
"""
        else:
            html_content += """
            <div class="no-scenarios">
                Direct answer provided - no scenario analysis needed.
            </div>
"""
        html_content += """
        </div>
"""
    # Citations section (unchanged)
    html_content += """
        <div class=\"citations\">
            <h3>Sources and Citations</h3>
    """
    if unique_citations:
        for i, c in enumerate(unique_citations, 1):
            html_content += f"""
            <div class=\"citation-item\" id=\"cite-{i}\">
                <span class=\"citation-number\">{i}</span>
                <div class=\"citation-title\">{html.escape(c.get('title', 'Source'))}</div>
                <div class=\"citation-source\">{html.escape(c.get('snippet', ''))}</div>
                <a href=\"{html.escape(c.get('url', '#'))}\" class=\"citation-url\" target=\"_blank\">{html.escape(c.get('url', ''))}</a>
            </div>
            """
    else:
        html_content += """
            <p>No external sources were cited for this analysis. The results are based on AI-generated reasoning and scenario frameworks.</p>
        """
    html_content += """
            <p><em>Note: This analysis is generated using AI and should be used as a starting point for further research and validation. All scenarios and impacts should be verified against current market conditions and expert opinions.</em></p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename

def main():
    """Run example queries through the scenario analysis workflow."""
    
    results = {}
    
    # Example 1: Query that requires scenario analysis
    # print("Running Example 1: AI adoption impact on job market...")
    # query1 = "What are the potential impacts of widespread AI adoption on the job market?"
    # result1 = run_scenario_analysis(query1)
    # results[query1] = result1
    
    # # Example 2: Query that doesn't require scenario analysis
    # print("Running Example 2: Tokyo population...")
    # query2 = "What is the current population of Tokyo?"
    # result2 = run_scenario_analysis(query2)
    # results[query2] = result2
    
    # # Example 3: Business scenario analysis
    # print("Running Example 3: Supply chain disruption...")
    # query3 = "How might a major supply chain disruption affect the automotive industry?"
    # result3 = run_scenario_analysis(query3)
    # results[query3] = result3
    
    # Example 4: Tariff scenario analysis
    print("Running Example 4: Tariff scenarios after pause expires...")
    query4 = "What are the possible scenarios for tariffs after the tariff pause expires on July 9?"
    result4 = run_scenario_analysis(query4)
    results[query4] = result4
    
    # Generate HTML report
    print("Generating HTML report...")
    filename = create_html_report(results)
    print(f"Report generated successfully: {filename}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Results written to: {filename}")

if __name__ == "__main__":
    # Check if API keys are set
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        print("ERROR: Please set your API keys before running this example.")
        print("You can set them in the script or create a .env file.")
        print("\nRequired environment variables:")
        print("- OPENAI_API_KEY")
        print("- TAVILY_API_KEY")
        exit(1)
    
    main() 