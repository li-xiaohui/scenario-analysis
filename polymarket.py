import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import time


class PolymarketAPI:
    """
    A client for interacting with the Polymarket API to retrieve market data.
    """
    
    def __init__(self):
        """
        Initialize the Polymarket API client.
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://polymarket.com/',
            'Origin': 'https://polymarket.com'
        })
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the Polymarket API.
        
        Args:
            url: Full URL to request
            params: Query parameters
            
        Returns:
            API response as dictionary
        """
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
    
    def get_markets(self, limit: int = 50, offset: int = 0, 
                   status: Optional[str] = None) -> List[Dict]:
        """
        Retrieve markets from Polymarket.
        
        Args:
            limit: Number of markets to retrieve
            offset: Offset for pagination
            status: Filter by market status ('open', 'closed', 'resolved')
            
        Returns:
            List of market data
        """
        url = "https://clob.polymarket.com/markets"
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if status:
            params['status'] = status
            
        response = self._make_request(url, params)
        
        # Handle different response structures
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            if 'data' in response:
                return response['data']
            elif 'markets' in response:
                return response['markets']
            else:
                return [response]  # Single market
        else:
            return []
    
    def get_ongoing_markets(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Retrieve ongoing (open) markets.
        
        Args:
            limit: Number of markets to retrieve
            offset: Offset for pagination
            
        Returns:
            List of ongoing market data
        """
        return self.get_markets(limit=limit, offset=offset, status='open')
    
    def get_resolved_markets(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Retrieve resolved markets.
        
        Args:
            limit: Number of markets to retrieve
            offset: Offset for pagination
            
        Returns:
            List of resolved market data
        """
        return self.get_markets(limit=limit, offset=offset, status='resolved')
    
    def get_market_by_id(self, market_id: str) -> Optional[Dict]:
        """
        Retrieve a specific market by ID.
        
        Args:
            market_id: The market ID
            
        Returns:
            Market data or None if not found
        """
        url = f"https://clob.polymarket.com/markets/{market_id}"
        return self._make_request(url)
    
    def get_market_trades(self, market_id: str, limit: int = 100) -> List[Dict]:
        """
        Retrieve trades for a specific market.
        
        Args:
            market_id: The market ID
            limit: Number of trades to retrieve
            
        Returns:
            List of trade data
        """
        url = f"https://clob.polymarket.com/markets/{market_id}/trades"
        params = {'limit': limit}
        return self._make_request(url, params)
    
    def get_market_orders(self, market_id: str) -> Dict:
        """
        Retrieve order book for a specific market.
        
        Args:
            market_id: The market ID
            
        Returns:
            Order book data
        """
        url = f"https://clob.polymarket.com/markets/{market_id}/orders"
        return self._make_request(url)


def format_market_data(market: Dict) -> Dict:
    """
    Format market data for better readability.
    
    Args:
        market: Raw market data from API
        
    Returns:
        Formatted market data
    """
    if not isinstance(market, dict):
        return {'error': f'Invalid market data: {type(market)}'}
    
    return {
        'id': market.get('id'),
        'question': market.get('question'),
        'description': market.get('description', '')[:200] + '...' if market.get('description') and len(market.get('description', '')) > 200 else market.get('description', ''),
        'status': market.get('status'),
        'end_date': market.get('endDate'),
        'total_liquidity': market.get('totalLiquidity'),
        'total_volume': market.get('totalVolume'),
        'category': market.get('category'),
        'subcategory': market.get('subcategory'),
        'outcomes': [
            {
                'name': outcome.get('name'),
                'probability': outcome.get('probability'),
                'last_price': outcome.get('lastPrice')
            }
            for outcome in market.get('outcomes', []) if isinstance(outcome, dict)
        ],
        'tags': market.get('tags', [])
    }


def main():
    """
    Main function to demonstrate API usage.
    """
    api = PolymarketAPI()
    
    print("=== Polymarket API Demo ===\n")
    
    try:
        # Get ongoing markets
        print("1. Retrieving ongoing markets...")
        ongoing_markets = api.get_ongoing_markets(limit=5)
        print(f"Found {len(ongoing_markets)} ongoing markets\n")
        
        # Debug: Print first market structure
        if ongoing_markets:
            print("DEBUG: First market structure:")
            print(json.dumps(ongoing_markets[0], indent=2)[:500] + "...")
            print()
        
        for i, market in enumerate(ongoing_markets, 1):
            try:
                formatted = format_market_data(market)
                print(f"Ongoing Market {i}:")
                print(f"  Question: {formatted.get('question', 'N/A')}")
                print(f"  Status: {formatted.get('status', 'N/A')}")
                print(f"  End Date: {formatted.get('end_date', 'N/A')}")
                total_volume = formatted.get('total_volume')
                if total_volume and isinstance(total_volume, (int, float)):
                    print(f"  Total Volume: ${total_volume:,.2f}")
                else:
                    print(f"  Total Volume: {total_volume}")
                print(f"  Outcomes: {len(formatted.get('outcomes', []))}")
                print()
            except Exception as e:
                print(f"Error formatting market {i}: {e}")
                print(f"Raw market data: {market}")
                print()
        
        # Get resolved markets
        print("2. Retrieving resolved markets...")
        resolved_markets = api.get_resolved_markets(limit=5)
        print(f"Found {len(resolved_markets)} resolved markets\n")
        
        for i, market in enumerate(resolved_markets, 1):
            try:
                formatted = format_market_data(market)
                print(f"Resolved Market {i}:")
                print(f"  Question: {formatted.get('question', 'N/A')}")
                print(f"  Status: {formatted.get('status', 'N/A')}")
                print(f"  End Date: {formatted.get('end_date', 'N/A')}")
                total_volume = formatted.get('total_volume')
                if total_volume and isinstance(total_volume, (int, float)):
                    print(f"  Total Volume: ${total_volume:,.2f}")
                else:
                    print(f"  Total Volume: {total_volume}")
                print(f"  Outcomes: {len(formatted.get('outcomes', []))}")
                print()
            except Exception as e:
                print(f"Error formatting market {i}: {e}")
                print(f"Raw market data: {market}")
                print()
        
        # If we have markets, get details for the first one
        if ongoing_markets:
            first_market = ongoing_markets[0]
            market_id = first_market.get('id')
            
            if market_id:
                print(f"3. Getting detailed information for market: {first_market.get('question', 'Unknown')}")
                try:
                    market_details = api.get_market_by_id(market_id)
                    if market_details:
                        print(f"  Market ID: {market_details.get('id')}")
                        print(f"  Status: {market_details.get('status')}")
                        total_volume = market_details.get('totalVolume', 0)
                        if isinstance(total_volume, (int, float)):
                            print(f"  Total Volume: ${total_volume:,.2f}")
                        else:
                            print(f"  Total Volume: {total_volume}")
                        print(f"  Outcomes: {len(market_details.get('outcomes', []))}")
                        print()
                except Exception as e:
                    print(f"Error getting market details: {e}")
                    print()
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Polymarket API endpoints may have changed. Please check their documentation for the latest API structure.")


if __name__ == "__main__":
    main()
