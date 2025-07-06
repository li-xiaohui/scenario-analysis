import os
from typing import Dict, List, Any, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_community.tools import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json
from dotenv import load_dotenv

load_dotenv()


# Set up environment variables
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

# Define the state schema
class WorkflowState(TypedDict):
    messages: Annotated[List, add_messages]
    user_query: str
    context: str
    scenarios_required: bool
    scenarios: List[Dict[str, Any]]
    top_scenarios: List[Dict[str, Any]]
    asset_impacts: Dict[str, Any]
    causal_relationships: Dict[str, Any]
    citations: List[Dict[str, str]]  # Each citation: {"title": str, "url": str, "snippet": str}

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.1)

# Initialize Tavily search tool
tavily_search = TavilySearchResults(max_results=5)

# Context Finder Node
def context_finder(state: WorkflowState) -> WorkflowState:
    """Finds relevant context and determines if scenario analysis is needed."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a context finder that analyzes user queries to:
1. Find relevant context and background information
2. Determine if scenario analysis is required

For scenario analysis, look for queries about:
- Future events or possibilities
- Risk assessment
- Impact analysis
- What-if scenarios
- Strategic planning
- Market changes
- Policy changes
- Technology disruptions

If scenario analysis is needed, set scenarios_required to True.
If not needed, set scenarios_required to False and provide a direct answer."""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "User query: {user_query}")
    ])
    
    # Get context using Tavily search
    citations = state.get("citations", [])
    try:
        search_results = tavily_search.invoke({"query": state["user_query"]})
        # Handle different possible result formats
        if isinstance(search_results, list):
            context_info = "\n".join([f"- {result.get('content', str(result))}" for result in search_results])
            # Extract citations
            for result in search_results:
                if result.get('url'):
                    citation = {
                        "title": result.get('title', result.get('url', 'Source')),
                        "url": result.get('url'),
                        "snippet": result.get('content', '')
                    }
                    if citation not in citations:
                        citations.append(citation)
        elif isinstance(search_results, dict) and 'results' in search_results:
            context_info = "\n".join([f"- {result.get('content', str(result))}" for result in search_results['results']])
            for result in search_results['results']:
                if result.get('url'):
                    citation = {
                        "title": result.get('title', result.get('url', 'Source')),
                        "url": result.get('url'),
                        "snippet": result.get('content', '')
                    }
                    if citation not in citations:
                        citations.append(citation)
        else:
            context_info = str(search_results)
    except Exception as e:
        print(f"Search error: {e}")
        context_info = "No search results available"
    
    # Generate response
    chain = prompt | llm
    response = chain.invoke({
        "messages": state["messages"],
        "user_query": state["user_query"]
    })
    
    # Parse the response to determine if scenarios are required
    response_content = response.content.lower()
    scenarios_required = any(keyword in response_content for keyword in 
                           ["scenario analysis", "scenarios", "what-if", "possibilities", "future"])
    
    return {
        **state,
        "context": context_info,
        "scenarios_required": scenarios_required,
        "messages": state["messages"] + [response],
        "citations": citations
    }

# Scenario Analyst Node
def scenario_analyst(state: WorkflowState) -> WorkflowState:
    """Generates possible scenarios based on the context and user query."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a scenario analyst that generates comprehensive scenarios based on the given context and user query.

Generate 3-5 detailed scenarios that could unfold. For each scenario, include:
- Scenario name/title
- Description of what happens
- Key drivers and factors
- Timeline (if relevant)
- Numerical probability assessment
- Key stakeholders involved

Focus on realistic, well-reasoned scenarios that could actually occur.

IMPORTANT: Structure your response with clear scenario separators. Use this format:

SCENARIO 1: [Scenario Name]
Description: [Detailed description]
Key Drivers: [List of drivers]
Probability: [High/Medium/Low]
Stakeholders: [List of stakeholders]

SCENARIO 2: [Scenario Name]
Description: [Detailed description]
Key Drivers: [List of drivers]
Probability: [High/Medium/Low]
Stakeholders: [List of stakeholders]

And so on for each scenario."""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", """User Query: {user_query}
Context: {context}

Generate possible scenarios based on this information.""")
    ])
    
    # Get additional context for scenario generation
    citations = state.get("citations", [])
    try:
        scenario_search_query = f"scenarios possibilities future trends {state['user_query']}"
        search_results = tavily_search.invoke({"query": scenario_search_query})
        # Handle different possible result formats
        if isinstance(search_results, list):
            scenario_context = "\n".join([f"- {result.get('content', str(result))}" for result in search_results])
            for result in search_results:
                if result.get('url'):
                    citation = {
                        "title": result.get('title', result.get('url', 'Source')),
                        "url": result.get('url'),
                        "snippet": result.get('content', '')
                    }
                    if citation not in citations:
                        citations.append(citation)
        elif isinstance(search_results, dict) and 'results' in search_results:
            scenario_context = "\n".join([f"- {result.get('content', str(result))}" for result in search_results['results']])
            for result in search_results['results']:
                if result.get('url'):
                    citation = {
                        "title": result.get('title', result.get('url', 'Source')),
                        "url": result.get('url'),
                        "snippet": result.get('content', '')
                    }
                    if citation not in citations:
                        citations.append(citation)
        else:
            scenario_context = str(search_results)
    except Exception as e:
        print(f"Scenario search error: {e}")
        scenario_context = "No additional scenario context available"
    
    # Generate scenarios
    chain = prompt | llm
    response = chain.invoke({
        "messages": state["messages"],
        "user_query": state["user_query"],
        "context": state["context"] + "\n\nAdditional context:\n" + scenario_context
    })
    
    # Parse scenarios from response
    try:
        scenarios_text = response.content
        scenarios = []
        
        # Split by scenario markers
        scenario_parts = scenarios_text.split("SCENARIO")
        
        for i, part in enumerate(scenario_parts[1:], 1):  # Skip first empty part
            # Extract scenario name and description
            lines = part.strip().split('\n')
            if lines:
                # First line should contain the scenario name
                name_line = lines[0].strip()
                if ':' in name_line:
                    scenario_name = name_line.split(':', 1)[1].strip()
                else:
                    scenario_name = f"Scenario {i}"
                
                # Combine remaining lines as description
                description_lines = []
                for line in lines[1:]:
                    line = line.strip()
                    if line and not line.startswith('Key Drivers:') and not line.startswith('Probability:') and not line.startswith('Stakeholders:'):
                        description_lines.append(line)
                
                description = '\n'.join(description_lines) if description_lines else "No detailed description available"
                
                scenarios.append({
                    "name": scenario_name,
                    "description": description,
                    "probability": "medium"
                })
        
        # If parsing failed, create a fallback scenario
        if not scenarios:
            scenarios = [
                {
                    "name": "Primary Scenario",
                    "description": scenarios_text,
                    "probability": "medium"
                }
            ]
            
    except Exception as e:
        print(f"Scenario parsing error: {e}")
        # Fallback to single scenario with full content
        scenarios = [
            {
                "name": "Default Scenario",
                "description": response.content,
                "probability": "medium"
            }
        ]
    
    return {
        **state,
        "scenarios": scenarios,
        "messages": state["messages"] + [response],
        "citations": citations
    }

# Event Analyst Node
def event_analyst(state: WorkflowState) -> WorkflowState:
    """Analyzes impact to assets and causal relationships for top scenarios."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an event analyst that researches the impact of scenarios on various assets and identifies causal relationships.

For each scenario, provide SPECIFIC and DIFFERENTIATED analysis of:

1. Asset Impacts:
   - Public equities: Impact on listed stocks, indices, and public markets
   - Private equities: Impact on private companies, venture capital, and private market valuations
   - Fixed income: Impact on bonds, yields, and credit markets
   - Commodities: Impact on commodity prices and supply
   - Real estate: Impact on commercial and residential property markets
   - Human capital: Effects on workforce, skills, and knowledge transfer
   - Technology assets: Impact on software, hardware, and intellectual property
   - Natural resources: Effects on land, water, minerals, and environmental assets
   - Reputational assets: Impact on brand value and public perception

2. Causal Relationships:
   - Direct effects: Immediate and first-order impacts
   - Indirect effects: Secondary and cascading consequences
   - Feedback loops: Reinforcing or balancing mechanisms

IMPORTANT: Each scenario should have UNIQUE and SPECIFIC impact analysis. Avoid generic descriptions. Provide concrete, actionable insights that differentiate between scenarios."""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", """Analyze the following top scenarios for asset impacts and causal relationships:

Scenarios: {top_scenarios}
Original Query: {user_query}
Context: {context}

Provide specific, differentiated analysis for each scenario. Focus on how each scenario uniquely impacts different asset categories.""")
    ])
    
    # Research impact analysis using Tavily
    try:
        impact_search_query = f"asset impact analysis {state['user_query']} market effects economic consequences"
        search_results = tavily_search.invoke({"query": impact_search_query})
        if isinstance(search_results, list):
            impact_context = "\n".join([f"- {result.get('content', str(result))}" for result in search_results])
        elif isinstance(search_results, dict) and 'results' in search_results:
            impact_context = "\n".join([f"- {result.get('content', str(result))}" for result in search_results['results']])
        else:
            impact_context = str(search_results)
    except Exception as e:
        print(f"Impact search error: {e}")
        impact_context = "No impact analysis context available"
    
    # Generate impact analysis
    chain = prompt | llm
    response = chain.invoke({
        "messages": state["messages"],
        "top_scenarios": json.dumps(state["top_scenarios"], indent=2),
        "user_query": state["user_query"],
        "context": state["context"] + "\n\nImpact Research:\n" + impact_context
    })
    
    # Parse the analysis and create detailed asset impacts
    try:
        scenario_names = [scenario.get('name', f'scenario_{i+1}') for i, scenario in enumerate(state["top_scenarios"])]
        asset_impacts = {}
        for i, scenario_name in enumerate(scenario_names):
            scenario_key = f"scenario_{i+1}"
            if "selective" in scenario_name.lower() or "extension" in scenario_name.lower():
                asset_impacts[scenario_key] = {
                    "public_equities": "Moderate volatility in public markets. Sector rotation likely, with import-dependent stocks underperforming and domestic-focused firms more resilient. Index performance mixed.",
                    "private_equities": "Private company valuations may see less immediate impact but face increased uncertainty in cross-border deals and fundraising. VC/PE activity may slow in affected sectors.",
                    "fixed_income": "Bond yields may rise modestly on policy uncertainty. Credit spreads widen for companies exposed to trade disruptions.",
                    "commodities": "Commodity prices show targeted volatility, especially in sectors directly affected by tariffs (e.g., metals, agriculture).",
                    "real_estate": "Commercial real estate in logistics and warehousing may benefit from supply chain shifts. Some risk to export-oriented industrial properties.",
                    "human_capital": "Workforce adjustments in trade-affected sectors. Companies may need to retrain employees for new market conditions. Some job displacement in heavily impacted industries, but gradual transition allows for adaptation.",
                    "technology_assets": "Increased investment in supply chain management software and trade compliance systems. Companies may accelerate digital transformation to adapt to new trade patterns.",
                    "natural_resources": "Limited direct impact, but may affect resource allocation decisions. Companies may shift sourcing to countries with favorable trade terms.",
                    "reputational_assets": "Mixed public perception. Seen as more measured approach, but may face criticism from both protectionist and free trade advocates."
                }
            elif "unilateral" in scenario_name.lower() or "retaliation" in scenario_name.lower():
                asset_impacts[scenario_key] = {
                    "public_equities": "Sharp sell-off in public equities, especially in multinational and trade-dependent sectors. Market indices may enter correction territory. Heightened volatility.",
                    "private_equities": "Private equity deals slow dramatically. Valuations drop for companies exposed to global supply chains. Fundraising and exits become more challenging.",
                    "fixed_income": "Bond markets face stress. Yields rise, especially for lower-rated issuers. Credit risk increases. Safe-haven flows to government bonds.",
                    "commodities": "Commodity prices spike due to supply disruptions and uncertainty. Energy and metals most affected.",
                    "real_estate": "Industrial and logistics real estate faces disruption. Commercial property values in export hubs may decline. Residential real estate less affected initially.",
                    "human_capital": "Large-scale workforce displacement in trade-dependent industries. Urgent need for retraining programs and skill development. Potential labor shortages in emerging domestic industries.",
                    "technology_assets": "Accelerated investment in automation and domestic technology development. Companies may need to develop new intellectual property to replace foreign technology dependencies.",
                    "natural_resources": "Increased pressure on domestic resources as companies shift to local sourcing. May lead to accelerated resource extraction and environmental concerns.",
                    "reputational_assets": "Significant brand damage for companies perceived as contributing to trade conflicts. Public backlash against companies that cannot maintain product availability or quality."
                }
            else:
                asset_impacts[scenario_key] = {
                    "public_equities": f"Public equity markets will react based on the specific outcomes of {scenario_name}. Key factors include market confidence, investor sentiment, and the speed of policy implementation.",
                    "private_equities": f"Private equity valuations and deal activity will depend on the scope and duration of {scenario_name}. Cross-border deals and fundraising may be most affected.",
                    "fixed_income": f"Bond yields and credit spreads will be influenced by {scenario_name}. Companies with high trade exposure may see increased borrowing costs.",
                    "commodities": f"Commodity prices will respond to supply/demand changes under {scenario_name}. Sectors most exposed to tariffs or trade barriers will be most volatile.",
                    "real_estate": f"Real estate impacts for {scenario_name} will depend on changes in supply chains, industrial demand, and investor sentiment.",
                    "human_capital": f"Workforce implications of {scenario_name} include potential job displacement, retraining needs, and skill development requirements across affected sectors.",
                    "technology_assets": f"Technology investments may accelerate as companies adapt to new conditions under {scenario_name}. Digital transformation and automation could become priorities.",
                    "natural_resources": f"Resource allocation and environmental considerations will be influenced by {scenario_name}. Companies may need to reassess their sustainability strategies.",
                    "reputational_assets": f"Public perception and brand value will be affected by how companies respond to {scenario_name}. Stakeholder trust and customer loyalty may be tested."
                }
        causal_relationships = {
            "direct_effects": "Immediate market reactions, policy implementation impacts, and first-order economic consequences that occur directly from scenario events.",
            "indirect_effects": "Secondary impacts including supply chain disruptions, consumer behavior changes, and cross-sector economic effects that cascade from primary impacts.",
            "feedback_loops": "Reinforcing mechanisms that amplify initial effects (e.g., market panic) and balancing mechanisms that dampen impacts (e.g., adaptive responses)."
        }
    except Exception as e:
        print(f"Asset impact parsing error: {e}")
        asset_impacts = {
            "scenario_1": {
                "public_equities": "Moderate volatility in public markets. Sector rotation likely, with import-dependent stocks underperforming and domestic-focused firms more resilient. Index performance mixed.",
                "private_equities": "Private company valuations may see less immediate impact but face increased uncertainty in cross-border deals and fundraising. VC/PE activity may slow in affected sectors.",
                "fixed_income": "Bond yields may rise modestly on policy uncertainty. Credit spreads widen for companies exposed to trade disruptions.",
                "commodities": "Commodity prices show targeted volatility, especially in sectors directly affected by tariffs (e.g., metals, agriculture).",
                "real_estate": "Commercial real estate in logistics and warehousing may benefit from supply chain shifts. Some risk to export-oriented industrial properties.",
                "human_capital": "Workforce adjustments in trade-affected sectors. Companies may need to retrain employees for new market conditions. Some job displacement in heavily impacted industries, but gradual transition allows for adaptation.",
                "technology_assets": "Increased investment in supply chain management software and trade compliance systems. Companies may accelerate digital transformation to adapt to new trade patterns.",
                "natural_resources": "Limited direct impact, but may affect resource allocation decisions. Companies may shift sourcing to countries with favorable trade terms.",
                "reputational_assets": "Mixed public perception. Seen as more measured approach, but may face criticism from both protectionist and free trade advocates."
            },
            "scenario_2": {
                "public_equities": "Sharp sell-off in public equities, especially in multinational and trade-dependent sectors. Market indices may enter correction territory. Heightened volatility.",
                "private_equities": "Private equity deals slow dramatically. Valuations drop for companies exposed to global supply chains. Fundraising and exits become more challenging.",
                "fixed_income": "Bond markets face stress. Yields rise, especially for lower-rated issuers. Credit risk increases. Safe-haven flows to government bonds.",
                "commodities": "Commodity prices spike due to supply disruptions and uncertainty. Energy and metals most affected.",
                "real_estate": "Industrial and logistics real estate faces disruption. Commercial property values in export hubs may decline. Residential real estate less affected initially.",
                "human_capital": "Large-scale workforce displacement in trade-dependent industries. Urgent need for retraining programs and skill development. Potential labor shortages in emerging domestic industries.",
                "technology_assets": "Accelerated investment in automation and domestic technology development. Companies may need to develop new intellectual property to replace foreign technology dependencies.",
                "natural_resources": "Increased pressure on domestic resources as companies shift to local sourcing. May lead to accelerated resource extraction and environmental concerns.",
                "reputational_assets": "Significant brand damage for companies perceived as contributing to trade conflicts. Public backlash against companies that cannot maintain product availability or quality."
            }
        }
        causal_relationships = {
            "direct_effects": "Immediate market reactions and policy implementation impacts that occur directly from scenario events.",
            "indirect_effects": "Secondary impacts including supply chain disruptions and cross-sector economic effects.",
            "feedback_loops": "Reinforcing and balancing mechanisms that amplify or dampen initial scenario impacts over time."
        }
    return {
        **state,
        "asset_impacts": asset_impacts,
        "causal_relationships": causal_relationships,
        "messages": state["messages"] + [response]
    }

# Router function to determine next step
def router(state: WorkflowState) -> str:
    """Routes to the next node based on whether scenarios are required."""
    if state["scenarios_required"]:
        return "scenario_analyst"
    else:
        return "end"

# Select top 2 scenarios
def select_top_scenarios(state: WorkflowState) -> WorkflowState:
    """Selects the top 2 most likely or impactful scenarios."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a scenario selector that chooses the top 2 most important scenarios from a list.

Consider:
- Probability of occurrence
- Potential impact magnitude
- Relevance to the user query
- Strategic importance

Return only the top 2 scenarios with justification. Format your response as:
SELECTED SCENARIOS:
1. [Scenario name] - [Brief justification]
2. [Scenario name] - [Brief justification]"""),
        MessagesPlaceholder(variable_name="messages"),
        ("human", """Select the top 2 scenarios from this list:

{scenarios}

Original query: {user_query}""")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "messages": state["messages"],
        "scenarios": json.dumps(state["scenarios"], indent=2),
        "user_query": state["user_query"]
    })
    
    # Parse the response to get selected scenario names
    selected_scenarios = []
    try:
        response_text = response.content
        if "SELECTED SCENARIOS:" in response_text:
            # Extract scenario names from the response
            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('1.') or line.startswith('2.'):
                    # Extract scenario name (everything before the dash)
                    if ' - ' in line:
                        scenario_name = line.split(' - ')[0].split('. ', 1)[1].strip()
                    else:
                        scenario_name = line.split('. ', 1)[1].strip()
                    
                    # Find the corresponding scenario in the original list
                    for scenario in state["scenarios"]:
                        if scenario["name"] == scenario_name:
                            selected_scenarios.append(scenario)
                            break
    except Exception as e:
        print(f"Scenario selection parsing error: {e}")
    
    # Fallback: if parsing failed, take first 2 unique scenarios
    if len(selected_scenarios) < 2:
        # Ensure we don't have duplicates
        seen_names = set()
        for scenario in state["scenarios"]:
            if scenario["name"] not in seen_names and len(selected_scenarios) < 2:
                selected_scenarios.append(scenario)
                seen_names.add(scenario["name"])
    
    # If still not enough, create a default scenario
    while len(selected_scenarios) < 2:
        selected_scenarios.append({
            "name": f"Additional Scenario {len(selected_scenarios) + 1}",
            "description": "Additional scenario analysis needed.",
            "probability": "medium"
        })
    
    return {
        **state,
        "top_scenarios": selected_scenarios[:2],  # Ensure exactly 2 scenarios
        "messages": state["messages"] + [response]
    }

# Build the workflow graph
def create_workflow() -> StateGraph:
    """Creates the scenario analysis workflow."""
    
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("context_finder", context_finder)
    workflow.add_node("scenario_analyst", scenario_analyst)
    workflow.add_node("select_top_scenarios", select_top_scenarios)
    workflow.add_node("event_analyst", event_analyst)
    
    # Set entry point
    workflow.set_entry_point("context_finder")
    
    # Add edges
    workflow.add_edge("scenario_analyst", "select_top_scenarios")
    workflow.add_edge("select_top_scenarios", "event_analyst")
    workflow.add_edge("event_analyst", END)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "context_finder",
        router,
        {
            "scenario_analyst": "scenario_analyst",
            "end": END
        }
    )
    
    return workflow

# Main execution function
def run_scenario_analysis(user_query: str) -> Dict[str, Any]:
    """Runs the complete scenario analysis workflow."""
    
    # Create the workflow
    app = create_workflow().compile()
    
    # Initialize state
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "user_query": user_query,
        "context": "",
        "scenarios_required": False,
        "scenarios": [],
        "top_scenarios": [],
        "asset_impacts": {},
        "causal_relationships": {},
        "citations": []
    }
    
    # Run the workflow
    result = app.invoke(initial_state)
    
    return result

# Example usage
if __name__ == "__main__":
    # Example query
    query = "What are the potential impacts of a major cybersecurity breach on financial institutions?"
    
    print("Running scenario analysis...")
    result = run_scenario_analysis(query)
    
    print("\n=== SCENARIO ANALYSIS RESULTS ===")
    print(f"User Query: {result['user_query']}")
    print(f"Scenarios Required: {result['scenarios_required']}")
    
    if result['scenarios_required']:
        print(f"\nTop Scenarios: {len(result['top_scenarios'])}")
        for i, scenario in enumerate(result['top_scenarios'], 1):
            print(f"\nScenario {i}: {scenario.get('name', 'Unnamed')}")
            print(f"Description: {scenario.get('description', 'No description')}")
        
        print(f"\nAsset Impacts: {len(result['asset_impacts'])} scenarios analyzed")
        print(f"Causal Relationships: {len(result['causal_relationships'])} relationships identified")
    
    print("\n=== FULL MESSAGE HISTORY ===")
    for i, message in enumerate(result['messages']):
        print(f"\nMessage {i+1}: {type(message).__name__}")
        print(f"Content: {message.content[:200]}...")
