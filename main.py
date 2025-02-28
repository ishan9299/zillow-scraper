import os
import re
import sys
import time
import json
import random
import requests
import urllib.parse
import pandas as pd
import concurrent.futures

from queue import Queue
from datetime import date
from seleniumbase import SB
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium.webdriver.common.action_chains import ActionChains

ua = UserAgent(platforms="desktop")

def generate_randomua():
    random_ua = ""
    while True:
        random_ua = ua.random
        if "Macintosh" not in random_ua and "Mac OS" not in random_ua:
            break

    return random_ua

def delay():
    sleep_time = random.uniform(3, 7)
    time.sleep(sleep_time)

def format_zillow_url(params, county):
    query_string = urllib.parse.quote(json.dumps(params, separators=(',', ':')))
    return f"https://www.zillow.com/{county}/houses/for_sale/?searchQueryState={query_string}"


def load_array_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def load_counties(url, county_name_file, state_codes):
    if os.path.exists(county_name_file):
        counties = load_array_from_file(county_name_file)
        return counties
    else:
        state_urls = [f"{url}{code}/" for code in state_codes]

        state_response = []
        for i, url in enumerate(state_urls, start=1):
            print("i: ", i, "url: ", url)
            try:
                delay()

                random_ua = generate_randomua()
                headers["user-agent"] = random_ua


                res = requests.get(url, headers=headers)
                state_response.append(res)

                time.sleep(20)

            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")

        state_soups = [BeautifulSoup(res.text, "html.parser") for res in state_response]

        for state_soup in state_soups:
            section = state_soup.find("section", class_="bh-content-component")
            li_in_section = section.find_all("li")
            for li in li_in_section:
                a = li.find("a")
                county_name = a.text.strip()
                counties.append(county_name)

        with open(county_name_file, 'w') as file:
            for item in counties:
                file.write(str(item) + '\n')

        return counties


MAX_RETRIES=2

def scrapeData(county, params, us_states, df, scrapes, blocked):
    county_in_url_form = county.replace(" ", "-").lower()
    print("doing it for the county of: ", county)

    value_pnd_true = None
    value_pnd_false = None
    avg_cost_county = None

    with SB(uc=True, locale_code="en", ad_block=True) as sb:

        params["filterState"]["pnd"]["value"] = True
        url = format_zillow_url(params, county_in_url_form)

        sb.open(url)
        try:
            sb.scroll_to_bottom()
            sb.sleep(2)
            sb.wait_for_element_visible("span.result-count", timeout=15)
            value_pnd_true = sb.get_text("span.result-count")
            print(f"{county} PND True is: {value_pnd_true}")
        except Exception as e:
            blocked = 1
            return blocked


        params["filterState"]["pnd"]["value"] = False
        url = format_zillow_url(params, county_in_url_form)

        sb.open(url)
        try:
            sb.scroll_to_bottom()
            sb.sleep(2)
            sb.wait_for_element_visible("span.result-count", timeout=15)
            value_pnd_false = sb.get_text("span[class='result-count']")
            print(f"{county} PND False is: {value_pnd_false}")
        except Exception as e:
            blocked = 1
            return blocked


        avg_cost_url = "https://www.zillow.com/home-values/102001/united-states/"
        sb.open(avg_cost_url)
        try:
            sb.sleep(5)
            county_with_enter = county + "\n"
            sb.type('[title="input-for-adornedinput"]', f"{county_with_enter}")
            sb.sleep(2)
            sb.click('button[type="submit"]')
            sb.sleep(2)
            sb.wait_for_element_visible("h2[class='Text-c11n-8-102-0__sc-aiai24-0 fHIMjn']", timeout=15)
            avg_cost_county = sb.get_text("h2[class='Text-c11n-8-102-0__sc-aiai24-0 fHIMjn']")
            print(f"{county} avg cost is: {avg_cost_county}")
        except Exception as e:
            blocked = 1
            return blocked

    county_name_proper = county[:-3] + ", " + us_states[f"{county[-2:]}"]

    pnd_true_num = None
    pnd_false_num = None
    if value_pnd_true:
        pnd_true_num = int(value_pnd_true.replace("results", "").strip().replace(",", ""))
    if value_pnd_false:
        pnd_false_num = int(value_pnd_false.replace("results", "").strip().replace(",", ""))

    percentage_pending = None
    if pnd_true_num and pnd_false_num:
        percentage_pending = (pnd_true_num - pnd_false_num) / pnd_true_num

    df.loc[len(df)] = [county_name_proper, value_pnd_true, value_pnd_false, percentage_pending, avg_cost_county]

    return blocked

def main():

    headers = {
            "authority": "www.zillow.com",
            "method": "GET",
            "path": "/homes/Los-Angeles,-CA_rb/?category=RECENT_SEARCH",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.5",
            "priority": "u=0, i",
            "referer": "https://www.google.com/",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": generate_randomua()
    }

    params = {
            "pagination": {},
            "isMapVisible": "false",
            "filterState": {
                "sort": {"value": "globalrelevanceex"},
                "built": {
                    "min": 0,
                    "max": 2021
                },
                "pnd": {"value": True},
                "tow": {"value": False},
                "mf": {"value": False},
                "con": {"value": False},
                "land": {"value": False},
                "apa": {"value": False},
                "manu": {"value": False},
                "apco": {"value": False},
            },
    }

    state_codes = [
            "ak", "al", "ar", "as", "az", "ca", "co", "ct",
            "de", "fl", "ga", "gu", "hi", "ia", "id", "il",
            "in", "ks", "ky", "la", "ma", "md", "me", "mi",
            "mn", "mo", "mp", "ms", "mt", "nc", "nd", "ne",
            "nh", "nj", "nm", "nv", "oh", "ok", "or", "pa",
            "pr", "ri", "sc", "sd", "tn", "tx", "ut", "va",
            "vi", "vt", "wa", "dc", "wi", "wv", "wy",
    ]


    us_states = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "GU": "Guam",
        "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
        "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
        "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
        "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
        "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
        "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
        "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "PR": "Puerto Rico",
        "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
        "TN": "Tennessee", "TX": "Texas", "TT": "Trust Territories", "UT": "Utah",
        "VT": "Vermont", "VA": "Virginia", "VI": "Virgin Islands", "WA": "Washington",
        "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
        "AS": "American Samoa", "MP": "Northern Mariana Islands"
    }


    pop_url = "https://api.census.gov/data/2020/dec/pl?get=NAME,P1_001N&for=county:*"

    pop_df = pd.DataFrame(columns=['County', 'Population'])

    response = requests.get(pop_url)
    if response.status_code == 200:
        data = response.json()  # Convert API response to JSON
        headers = data[0]  # Extract headers
        values = data[1:]  # Extract data

        # Convert to Pandas DataFrame
        df = pd.DataFrame(values, columns=headers)
        df = df[['NAME', 'P1_001N']]  # Keep only county name and population
        df.columns = ['County', 'Population']  # Rename columns
        df['Population'] = df['Population'].astype(int)  # Convert population to int

        df["County"] = df["County"].str.replace("-", " ")
        pop_df = df

    url = "https://www.zillow.com/browse/homes/"


    county_name_file = sys.argv[1]
    counties = load_counties(url, county_name_file, state_codes)

    file_num_match = re.search(r"\d+", county_name_file)
    file_num = file_num_match.group() if file_num_match else "unknown"

    today = date.today()

    main_data_csv_df = pd.DataFrame({
        'county': [],
        'pnd_true': [],
        'pnd_false': [],
        'avg_cost': [],
        'percentage_pending': [],
        'Population': [],
    })

    main_data_csv_path = f"data/data_{today}.csv"
    if os.path.exists(main_data_csv_path):
        print("file exists")
    else:
        with open(main_data_csv_path, "w") as file:
            main_data_csv_df.to_csv(main_data_csv_path, index = False)

    retry = 0
    while retry < MAX_RETRIES:
        if len(counties) > 0:
            df = pd.DataFrame({
                'county': [],
                'pnd_true': [],
                'pnd_false': [],
                'percentage_pending': [],
                'avg_cost': []
            })

            scrapes = 0

            blocked = 0
            for county in counties:
                blocked = scrapeData(county, params, us_states, df, scrapes, blocked)
                if blocked == 0:
                    scrapes += 1
                    counties.remove(county)
                else:
                    print("This county is blocked")

        retry += 1
        print("data to csv")
        print("counties as of now", counties)

        pop_df = pop_df.rename(columns={'County': 'county'})
        merged_df = df.merge(pop_df, on='county', how='left')
        merged_df = merged_df[['county', 'pnd_true', 'pnd_false', 'avg_cost', 'percentage_pending', 'Population']]
        merged_df.to_csv(main_data_csv_path, mode = "a", header=False, index = False)

main()
