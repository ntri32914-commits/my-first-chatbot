import wikipedia

def get_research(topic: str) -> str:
    try:
        search_results = wikipedia.search(topic)
        page = wikipedia.page(search_results[0])
        return page.content[0:500]
    except Exception as e:
        return f'Error searching web: {e}'

get_research_tool ={
    "name": "get_research",
    "description": "search wikipedia for a given search term and returns the article content. Use this when the user asks for factual information or wants to research a topic",
    "input_schema": {
        "type": "object",
        "properties": {
            "topic": {
            "type": "string",
            "description": "the topic to research"}
        }, 
        "required": ["topic"]
    }

}

TOOLS =[]
TOOLS.append(get_research_tool)