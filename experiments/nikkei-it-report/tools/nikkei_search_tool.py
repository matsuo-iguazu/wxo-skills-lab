from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType, ExpectedCredentials
from ibm_watsonx_orchestrate.run import connections
from pydantic import BaseModel, Field
from typing import List
import urllib.request
import urllib.error
import json

TAVILY_APP_ID = "tavily"


class NikkeiHeadline(BaseModel):
    """日経新聞の見出し1件"""
    title: str = Field(description="記事の見出しタイトル")
    url: str = Field(description="記事のURL")
    pub_date: str = Field(description="掲載日時")


class NikkeiSearchResult(BaseModel):
    """日経新聞見出し検索結果"""
    headlines: List[NikkeiHeadline] = Field(description="取得した見出し一覧")
    count: int = Field(description="取得件数")
    source: str = Field(description="検索に使用した情報源")


@tool(
    permission=ToolPermission.READ_ONLY,
    expected_credentials=[
        ExpectedCredentials(app_id=TAVILY_APP_ID, type=ConnectionType.API_KEY_AUTH)
    ]
)
def search_nikkei_headlines(max_results: int = 10) -> NikkeiSearchResult:
    """日経新聞の最新主要見出しを Tavily 検索 API で取得する。

    Tavily の site: 検索フィルタを使って nikkei.com の記事見出しを収集する。
    最大 max_results 件を返す。

    Args:
        max_results (int): 取得する最大件数（デフォルト10件）

    Returns:
        NikkeiSearchResult: 取得した見出し一覧と件数
    """
    conn = connections.api_key_auth(TAVILY_APP_ID)
    api_key = conn.api_key

    payload = json.dumps({
        "api_key": api_key,
        "query": "日本経済新聞 ニュース",
        "include_domains": ["nikkei.com"],
        "max_results": max_results,
        "topic": "news",
        "days": 1,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return NikkeiSearchResult(headlines=[], count=0, source=f"Tavily API (HTTPエラー {e.code}: {body})")
    except Exception as e:
        return NikkeiSearchResult(headlines=[], count=0, source=f"Tavily API (エラー: {e})")

    headlines: List[NikkeiHeadline] = []
    for result in data.get("results", []):
        title = (result.get("title") or "").strip()
        url = (result.get("url") or "").strip()
        published_date = result.get("published_date") or ""

        if not title or not url:
            continue

        headlines.append(NikkeiHeadline(
            title=title,
            url=url,
            pub_date=published_date,
        ))

    return NikkeiSearchResult(
        headlines=headlines,
        count=len(headlines),
        source="Tavily API (site:nikkei.com)",
    )
