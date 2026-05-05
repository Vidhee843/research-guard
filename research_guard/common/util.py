import httpx
from langchain_community.chat_models import ChatOpenAI

from research_guard.common.models import Config

"""
Improve summarization
Publication memo log 
"""

config = Config(
    {
        "DEBUG": True,
        "DATABASE_URL": "sqlite://resources/db/db.sqlite3",
        "GENERATE_SCHEMAS": True,
        "DETERMINATION_PROMPT": "Is this content related to mathmatics? Only answer with 'yes' or 'no'.",
    }
)
llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
http_client = httpx.AsyncClient()


def get_body_text(soup):
    content_tags = ["p", "div", "article", "section", "main", "span", "li", "td"]
    text_parts = []
    for tag in content_tags:
        for element in soup.find_all(tag):
            text = element.get_text(separator=" ", strip=True)
            if text and len(text.split()) > 2:
                text_parts.append(text)
    return " ".join(text_parts)
