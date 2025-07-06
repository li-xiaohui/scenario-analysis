# Scenario Analysis Workflow

A LangGraph-based workflow for comprehensive scenario analysis using OpenAI and Tavily search integration.

## Overview

This system implements a three-node workflow for scenario analysis:

1. **Context Finder**: Analyzes user queries to find relevant context and determine if scenario analysis is needed
2. **Scenario Analyst**: Generates possible scenarios based on the context and user query
3. **Event Analyst**: Researches impact to assets and causal relationships for the top scenarios

## Features

- **Intelligent Routing**: Automatically determines if scenario analysis is required
- **Multi-source Research**: Uses Tavily search for real-time information gathering
- **Structured Analysis**: Provides detailed asset impact and causal relationship analysis
- **Top Scenario Selection**: Automatically selects the 2 most important scenarios for detailed analysis

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your-openai-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here
```

Or set them directly in the script:

```python
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"
os.environ["TAVILY_API_KEY"] = "your-tavily-api-key-here"
```

### 3. Get API Keys

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Tavily API Key**: Get from [Tavily](https://tavily.com/)

## Usage

### Basic Usage

```python
from scenario_analyst import run_scenario_analysis

# Run scenario analysis
query = "What are the potential impacts of a major cybersecurity breach on financial institutions?"
result = run_scenario_analysis(query)

# Access results
print(f"Scenarios Required: {result['scenarios_required']}")
print(f"Top Scenarios: {result['top_scenarios']}")
print(f"Asset Impacts: {result['asset_impacts']}")
print(f"Causal Relationships: {result['causal_relationships']}")
```

### Command Line Usage

```bash
python scenario-analyst.py
```

## Workflow Details

### 1. Context Finder Node

**Purpose**: Analyzes user queries and determines if scenario analysis is needed

**Process**:
- Uses Tavily search to gather relevant context
- Analyzes query for scenario-related keywords
- Routes to scenario analysis or provides direct answer

**Keywords that trigger scenario analysis**:
- Future events or possibilities
- Risk assessment
- Impact analysis
- What-if scenarios
- Strategic planning
- Market changes
- Policy changes
- Technology disruptions

### 2. Scenario Analyst Node

**Purpose**: Generates comprehensive scenarios based on context

**Output**: 5-7 detailed scenarios including:
- Scenario name/title
- Description of what happens
- Key drivers and factors
- Timeline (if relevant)
- Probability assessment (high/medium/low)
- Key stakeholders involved

### 3. Event Analyst Node

**Purpose**: Analyzes impact to assets and causal relationships

**Analysis Areas**:
- **Asset Impacts**:
  - Financial assets (stocks, bonds, currencies)
  - Physical assets (infrastructure, property)
  - Human capital
  - Technology assets
  - Natural resources
  - Reputational assets

- **Causal Relationships**:
  - Direct effects
  - Indirect effects
  - Feedback loops
  - Time delays
  - Magnitude of impact

## Example Queries

### Scenario Analysis Required
- "What if there's a major economic recession next year?"
- "How might climate change affect the insurance industry?"
- "What are the potential impacts of AI regulation on tech companies?"

### Direct Answer (No Scenario Analysis)
- "What is the current price of Bitcoin?"
- "Who is the CEO of Apple?"
- "What is the population of New York City?"

## Output Structure

The workflow returns a dictionary with the following structure:

```python
{
    "user_query": str,
    "context": str,
    "scenarios_required": bool,
    "scenarios": List[Dict],  # All generated scenarios
    "top_scenarios": List[Dict],  # Top 2 selected scenarios
    "asset_impacts": Dict,  # Impact analysis for each scenario
    "causal_relationships": Dict,  # Causal relationship analysis
    "messages": List  # Full conversation history
}
```

## Customization

### Modifying Node Behavior

Each node can be customized by modifying the prompt templates:

```python
# Example: Modify scenario analyst prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Your custom system prompt here..."),
    MessagesPlaceholder(variable_name="messages"),
    ("human", "Your custom human prompt here...")
])
```

### Adding New Tools

To add additional tools to the workflow:

```python
from langchain_core.tools import tool

@tool
def custom_tool(query: str) -> str:
    """Your custom tool description."""
    # Tool implementation
    return "Tool result"
```

## Error Handling

The workflow includes basic error handling for:
- API key validation
- Network connectivity issues
- Invalid query formats
- Empty search results

## Performance Considerations

- **API Rate Limits**: Be aware of OpenAI and Tavily rate limits
- **Search Results**: Limited to 5 results per search to manage costs
- **Model Selection**: Uses GPT-4 Turbo for best analysis quality

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure both OpenAI and Tavily API keys are set correctly
2. **Import Errors**: Make sure all dependencies are installed
3. **Network Issues**: Check internet connectivity for search functionality

### Debug Mode

Enable debug output by modifying the main execution:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is open source and available under the MIT License.