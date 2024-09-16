import os
from apify_client import ApifyClient
from typing_extensions import Annotated
from autogen import ConversableAgent, register_function, config_list_from_json

def scrape_page(url: Annotated[str, "The URL of the web page to scrape"], apify_api_key: str) -> Annotated[str, "Scraped content"]:
    client = ApifyClient(token=apify_api_key)

    run_input = {
        "startUrls": [{"url": url}],
        "useSitemaps": False,
        "crawlerType": "playwright:firefox",
        "includeUrlGlobs": [],
        "excludeUrlGlobs": [],
        "ignoreCanonicalUrl": False,
        "maxCrawlDepth": 0,
        "maxCrawlPages": 1,
        "initialConcurrency": 0,
        "maxConcurrency": 200,
        "initialCookies": [],
        "proxyConfiguration": {"useApifyProxy": True},
        "maxSessionRotations": 10,
        "maxRequestRetries": 5,
        "requestTimeoutSecs": 60,
        "dynamicContentWaitSecs": 10,
        "maxScrollHeightPixels": 5000,
        "removeElementsCssSelector": """nav, footer, script, style, noscript, svg,
    [role=\"alert\"],
    [role=\"banner\"],
    [role=\"dialog\"],
    [role=\"alertdialog\"],
    [role=\"region\"][aria-label*=\"skip\" i],
    [aria-modal=\"true\"]""",
        "removeCookieWarnings": True,
        "clickElementsCssSelector": '[aria-expanded="false"]',
        "htmlTransformer": "readableText",
        "readableTextCharThreshold": 100,
        "aggressivePrune": False,
        "debugMode": True,
        "debugLog": True,
        "saveHtml": True,
        "saveMarkdown": True,
        "saveFiles": False,
        "saveScreenshots": False,
        "maxResults": 9999999,
        "clientSideMinChangePercentage": 15,
        "renderingTypeDetectionPercentage": 10,
    }

    run = client.actor("aYG0l9s7dbB7j3gbS").call(run_input=run_input)

    text_data = ""
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        text_data += item.get("text", "") + "\n"

    return text_data

class WebScraperAgent:
    def __init__(self):
        config_list = config_list_from_json(
            "OAI_CONFIG_LIST",
            filter_dict={
                "model": ["gpt-4"],
            },
        )
        self.apify_api_key = os.getenv("APIFY_API_KEY")

        self.scraper_agent = ConversableAgent(
            "WebScraper",
            llm_config={"config_list": config_list},
            system_message="You are a web scrapper and you can scrape any web page using the tools provided. "
            "Returns 'TERMINATE' when the scraping is done.",
        )

        self.user_proxy_agent = ConversableAgent(
            "UserProxy",
            llm_config=False,
            human_input_mode="NEVER",
            code_execution_config=False,
            is_termination_msg=lambda x: x.get("content", "") is not None and "terminate" in x["content"].lower(),
            default_auto_reply="Please continue if not finished, otherwise return 'TERMINATE'.",
        )

        # Define a properly annotated wrapper function
        def scrape_wrapper(url: Annotated[str, "The URL of the web page to scrape"]) -> Annotated[str, "Scraped content"]:
            return scrape_page(url, self.apify_api_key)

        register_function(
            scrape_wrapper,
            caller=self.scraper_agent,
            executor=self.user_proxy_agent,
            name="scrape_page",
            description="Scrape a web page and return the content.",
        )

    def initiate_chat(self, url: str) -> dict:
        summary_prompt = """Summarize the scraped content and format summary EXACTLY as follows:
        ---
        *Company name*:
        `Acme Corp`
        ---
        *Website*:
        `acmecorp.com`
        ---
        *Description*:
        `Company that does things.`
        ---
        *Tags*:
        `Manufacturing. Retail. E-commerce.`
        ---
        *Takeaways*:
        `Provides shareholders with value by selling products.`
        ---
        """

        chat_result = self.user_proxy_agent.initiate_chat(
            self.scraper_agent,
            message=f"Can you scrape: {url} for me?",
            summary_method="reflection_with_llm",
            summary_args={"summary_prompt": summary_prompt},
        )

        return chat_result
