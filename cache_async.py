import argparse
import asyncio
import logging
import json
import aiohttp
import urllib.parse

from bs4 import BeautifulSoup as bs
from datetime import datetime, timedelta


async def main():
    logging.info("parser started")
    starting_page, depth = parser_args()
    query_to_start = urllib.parse.quote(starting_page, safe='')
    results = await parse(query_to_start, depth)
    with open("wiki.json", 'w') as f:
        json.dump(results, f, indent=4)

def check_depth(depth):
    depth = int(depth)
    if depth < 3:
        raise argparse.ArgumentTypeError("Depth must be at least 3")
    return depth
    
def parser_args():
    parser = argparse.ArgumentParser(description="Cache Wikipedia pages as a graph")
    parser.add_argument(
        "-p",
        "--page",
        default="Python_(programming_language)",
        help="Starting page name",
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=check_depth,
        default=3,
        help="Maximum depth to follow links",
    )
    args = parser.parse_args()
    return args.page, args.depth

async def parse(initial_query: str, depth: int):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        started_at = datetime.now()
        results = {}
        to_gather = {initial_query}
        gathered = set()
        pages_parsed = 0
        
        for level in range(depth):
            queries_to_go = len(to_gather)
            if queries_to_go == 0:
                break
            
            next_level_results = {}
            next_to_gather = set()
            for query in to_gather:
                result = await gather_references_from_page(query, session)
                if result:
                    result_set = set(result)
                    next_level_results[query] = list(result_set)
                    gathered.add(query)
                    next_to_gather |= result_set
                    pages_parsed += 1
                    if pages_parsed >= 1000:
                        break
            
            results.update(next_level_results)
            to_gather = next_to_gather - gathered
            
            if pages_parsed >= 1000:
                break
        
        if(len(results) < 20):
            print(
                f"The page '{initial_query}' has less than 20 links. Please choose another start page."
            )
            return
        logging.info(f"Finished parsing up to level {depth}")
        logging.info(f"Total queries to gather: {len(results)}")
        logging.info(f"Total pages parsed: {pages_parsed}")
        
        finished_at = datetime.now()
        time_estimation = finished_at - started_at
        logging.info(f"Time estimation: {time_estimation.seconds}.{time_estimation.microseconds}s")
      
        return results



async def gather_references_from_pages(
    queries: list[str],
    session: aiohttp.ClientSession,
):
    tasks = [
        gather_references_from_page(query, session)
        for query in queries
    ]
    results = await asyncio.gather(*tasks)
    return {
        query: result
        for query, result
        in zip(queries, results)
    }


async def gather_references_from_page(
    url: str,
    session: aiohttp.ClientSession,
) -> list[str] | None:
    content: str | None = await fetch_query(url, session)
    if content:
        references = extract_references(content)
        return list(references)
    return []


async def fetch_query(
    query: str,
    session: aiohttp.ClientSession
) -> str | None:
    base_url = "https://en.wikipedia.org/wiki/"
    url_to_get = f"{base_url}{query}"
    try:
        async with session.get(url_to_get) as response:
            response.raise_for_status()
            logging.info(" url fetched: %s", url_to_get)
            return await response.text()

    except aiohttp.ClientError as e:
        logging.warning("client side error on url: %s,  %s", url_to_get, e)
    except asyncio.TimeoutError:
        logging.warning("timeout reached on url: %s", url_to_get)
    except Exception as e:
        logging.warning("exception raised on url: %s %s", url_to_get, e)


def extract_references(content: str):
    soup = bs(content, "html.parser")
    content_body = soup.find("div", {"id": "bodyContent"})
    a_tags = content_body.find_all('a', href=True)

    page_titles = set()
    for a_tag in a_tags:
        href = a_tag['href']
        if href.startswith('/wiki/') and ':' not in href:
            page_titles.add(href.split('/')[-1])

    return list(page_titles)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s:%(levelname)s:%(message)s',
        level=logging.DEBUG
    )
    asyncio.run(main())
