# Parse a list of sublists and return a path to all review pages.
import math
import re
import datefinder
import pandas as pd
from bs4 import BeautifulSoup
from p_tqdm import p_map
from urllib.parse import urlparse

from .urlFunctions import get_URL

def get_proxy():
    proxy = 'test'
    return proxy


# Flatten a list of lists into a single list.
def flatten(list):
    return [item for sublist in list for item in sublist]


# Get the path to the all review page.
def get_all_review_page_url(res: str) -> str:
    productPage = BeautifulSoup(res.text, "html.parser")
    path: str = productPage.find("a", {"data-hook": "see-all-reviews-link-foot"})[
        "href"
    ]
    return path


def extractPage(url: str) -> str:
    r = get_URL(url, get_proxy())
    pageNotLoaded = True
    productPage = BeautifulSoup(r.text, "html.parser")
    checkReviewLen = len(productPage.findAll("i", {"class": "review-rating"}))
    if checkReviewLen > 0:
        pageNotLoaded = False
    while pageNotLoaded:
        r = get_URL(url, get_proxy())
        print('loading ', url)
        productPage = BeautifulSoup(r.text, "html.parser")
        checkReviewLen = len(productPage.findAll("i", {"class": "review-rating"}))
        if checkReviewLen > 0:
            pageNotLoaded = False
    reviewers = []
    reviewersProfile = []
    ratings = []
    ratingsDate = []
    reviewDescriptions = []
    reviewTitles = []
    reviewerVerified = []
    reviewerHelpful = []
    reviewDivs = productPage.findAll(
        "div",
        {"data-hook": "review"},
    )

    for i in range(0, len(reviewDivs)):
        name = reviewDivs[i].findAll("span", {"class": "a-profile-name"})
        reviewers.append(name[0].get_text()) if len(name) > 0 else reviewers.append(" ")

        urlReview = reviewDivs[i].findAll("a", {"class": "a-profile"})
        reviewersProfile.append(urlReview[0]["href"]) if len(
            urlReview
        ) > 0 else reviewersProfile.append(" ")

        avp = reviewDivs[i].findAll("span", {"data-hook": "avp-badge"})
        reviewerVerified.append(1) if len(avp) > 0 else reviewerVerified.append(0)

        helpfulCount = reviewDivs[i].findAll(
            "span", {"data-hook": "helpful-vote-statement"}
        )

        if len(helpfulCount) > 0:
            hcount = re.findall(r"\d+", helpfulCount[0].get_text().replace(",", ""))
            if len(hcount) > 0:
                reviewerHelpful.append(int(hcount[0]))
            else:
                reviewerHelpful.append(0)
        else:
            reviewerHelpful.append(0)

        ratinOfReview = reviewDivs[i].findAll("i", {"class": "review-rating"})
        ratings.append(ratinOfReview[0].get_text()[0]) if len(
            ratinOfReview
        ) > 0 else ratings.append(" ")
        dates = reviewDivs[i].findAll("span", {"class": "review-date"})

        if len(dates) > 0:
            matches = datefinder.find_dates(dates[0].get_text())
            ratingsDate.append(list(matches)[0].strftime("%m/%d/%Y"))
        else:
            ratingsDate(" ")

        title = reviewDivs[i].findAll("a", {"class": "review-title-content"})
        reviewTitles.append(title[0].get_text()) if len(
            title
        ) > 0 else reviewTitles.append(" ")

        desc = reviewDivs[i].findAll("span", {"class": "review-text-content"})
        reviewDescriptions.append(desc[0].get_text()) if len(
            desc
        ) > 0 else reviewDescriptions.append(" ")

    reviewDescriptions[:] = [
        i.lstrip("\n").rstrip("\n").strip() for i in reviewDescriptions
    ]
    reviewDescriptions[:] = [re.sub(" +", " ", i) for i in reviewDescriptions]

    reviewTitles[:] = [i.lstrip("\n").rstrip("\n") for i in reviewTitles]

    return {
        "reviewers": reviewers,
        "reviewerURL": reviewersProfile,
        "verifiedPurchase": reviewerVerified,
        "helpfulVoteStatement": reviewerHelpful,
        "ratings": ratings,
        "reviewTitles": reviewTitles,
        "reviewDescriptions": reviewDescriptions,
        "date": ratingsDate,
    }


# Extracts the total number of reviews from a given URL.
def extractTotalPages(url):
    r = get_URL(url, get_proxy())
    productPage = BeautifulSoup(r.text, "html.parser")
    pageSpanText = productPage.findAll(
        "div", {"data-hook": "cr-filter-info-review-rating-count"}
    )[0].get_text()
    pageSpanText = pageSpanText.split(",")[1]
    totalReviews = int(re.findall(r"\d+", pageSpanText.replace(",", ""))[0])
    return (
        math.ceil(totalReviews / 10),
        productPage.find("title").get_text(),
        totalReviews,
    )

def get_product_id(self):
    product_id = re.findall(r"/dp/(\w+)(?:/|\?|$)", self.url)
    if product_id:
        return product_id[0]

def get_domain(self):
    parsed_url = urlparse(self.url)
    return parsed_url.netloc

def scrape_reviews(product_id, domain):
    first_page_url = f"https://www.amazon.in/dp/product-reviews/{product_id}?pageNumber=1"
    print(f'first_page_url {first_page_url}')
    totalPages, pageTitle, totalReviews = extractTotalPages(first_page_url)

    urlsToFetch = []
    for i in range(1, totalPages + 1):
        urlsToFetch.append(f"https://www.amazon.in/dp/product-reviews/{product_id}/ref=cm_cr_getr_d_paging_btm_next_{i}?pageNumber={i}")

    print('urlsToFetch')
    print(urlsToFetch)

    results = p_map(extractPage, urlsToFetch)
    # print(results)
    res = {}
    for k in results:
        for list in k:
            if list in res:
                res[list] += k[list]
            else:
                res[list] = k[list]

    productReviewsData = pd.DataFrame()
    productReviewsData["verified_purchase"] = res["verifiedPurchase"]
    productReviewsData["rating"] = res["ratings"]
    productReviewsData["review_text"] = res["reviewDescriptions"]

    return productReviewsData
