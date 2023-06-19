from selenium import webdriver
from bs4 import BeautifulSoup
import datefinder
import re
import os
import math
import pandas as pd
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options


class AmazonScraper:
    def __init__(self, url, token) -> None:
        self.url = url
        self.token = token
        print(f'token {token}')
        print(f'url {url}')

    def parse_from_review_divs(self, review_divs):
        ratings = []
        review_text = []
        verified = []

        for i in range(0, len(review_divs)):
            review = review_divs[i]
            avp = review.findAll("span", {"data-hook": "avp-badge"})
            verified.append(1) if len(avp) > 0 else verified.append(0)

            rating = review.findAll("i", {"class": "review-rating"})
            ratings.append(int(rating[0].get_text()[0])) if len(
                rating
            ) > 0 else ratings.append(" ")

            desc = review_divs[i].findAll("span", {"class": "review-text-content"})
            review_text.append(desc[0].get_text()) if len(
                desc
            ) > 0 else review_text.append(" ")

        review_text[:] = [i.lstrip("\n").rstrip("\n").strip() for i in review_text]
        review_text[:] = [re.sub(" +", " ", i) for i in review_text]

        return {"rating": ratings, "review_text": review_text, "verified_purchase": verified}

    def get_product_id(self):
        product_id = re.findall(r"/dp/(\w+)(?:/|\?|$)", self.url)
        if product_id:
            return product_id[0]

    def get_domain(self):
        parsed_url = urlparse(self.url)
        return parsed_url.netloc.replace('www.', '')

    def get_page_count(self, page):
        span_text = page.findAll(
            "div", {"data-hook": "cr-filter-info-review-rating-count"}
        )[0].get_text()
        span_text = span_text.split(",")[1]
        total_reviews = int(re.findall(r"\d+", span_text.replace(",", ""))[0])
        return math.ceil(total_reviews / 10)
        # return 4

    def get_page(self, page_url):
        print(f'get_page {page_url}')
        domain = self.get_domain()

        session_token = self.token
        b_domain = f".{domain}"
        
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--crash-dumps-dir=/tmp")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        # options.add_argument('--proxy-server=%s' % proxy)

        chrome_prefs = {}
        options.experimental_options["prefs"] = chrome_prefs
        options.experimental_options["useAutomationExtension"] = False
        chrome_prefs['profile.managed_default_content_settings.images'] = {'images': 2}
        chrome_prefs["profile.default_content_settings"] = {"images": 2}

        browser = webdriver.Chrome(options=options)
        browser.get(page_url)
        browser.add_cookie(
            {"name": "session-token", "value": session_token, "domain": b_domain}
        )
        browser.get(page_url)
        page = BeautifulSoup(browser.page_source, "html.parser")
        browser.quit()
        return page

    def scrape_reviews(self, page_limit=None):
        domain = self.get_domain()        
        product_id = self.get_product_id()

        page_urls = []
        loaded_pages = []

        first_page_url = f"https://{domain}/dp/product-reviews/{product_id}?pageNumber=1"
        first_page = self.get_page(first_page_url)
        loaded_pages.append(first_page)
        
        total_pages = self.get_page_count(first_page)
        if page_limit and page_limit < total_pages:
            total_pages = page_limit

        for i in range(2, total_pages + 1):
            page_urls.append(f"https://{domain}/dp/product-reviews/{product_id}/ref=cm_cr_getr_d_paging_btm_next_{i}?pageNumber={i}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            new_pages = executor.map(self.get_page, page_urls)
            loaded_pages = loaded_pages + list(new_pages)

        reviews_pd = None
        for p in loaded_pages:
            review_divs = p.findAll(
                "div",
                {"data-hook": "review"},
            )
            reviews_list = self.parse_from_review_divs(review_divs)
            if reviews_pd is None:
                reviews_pd = pd.DataFrame(reviews_list)
            else:
                df = pd.DataFrame(reviews_list)
                print(f'appending {len(df)}')
                reviews_pd = pd.concat([reviews_pd, df], ignore_index=True)
                print(f'new len {len(reviews_pd)}')
        return reviews_pd
