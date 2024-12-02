import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def search_web(query: str, num_results: int = 5) -> str:
    """
    Perform a web search using DuckDuckGo and return formatted results
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f"https://html.duckduckgo.com/html/?q={query}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result in soup.find_all('div', class_='result')[:num_results]:
                title = result.find('a', class_='result__a')
                snippet = result.find('a', class_='result__snippet')
                link = title.get('href') if title else None
                
                if title and snippet:
                    results.append({
                        'title': title.text.strip(),
                        'snippet': snippet.text.strip(),
                        'link': link
                    })
            
            # Format results as a string
            formatted_results = ""
            for i, result in enumerate(results, 1):
                formatted_results += f"{i}. {result['title']}\n"
                formatted_results += f"   {result['snippet']}\n"
                formatted_results += f"   Link: {result['link']}\n\n"
            
            return formatted_results if formatted_results else "No results found."
            
        else:
            return f"Error performing web search: {response.status_code}"
            
    except Exception as e:
        return f"Error during web search: {str(e)}"
