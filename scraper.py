import requests
from bs4 import BeautifulSoup
import json, os, smtplib, re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from urllib.parse import urlparse

# ── CONFIGURATION ──────────────────────────────────────────────
GMAIL_SENDER   = os.environ.get("GMAIL_SENDER")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD")
GMAIL_RECEIVER = os.environ.get("GMAIL_RECEIVER")

KEYWORDS = [
    "product manager",
    "senior product manager",
    "associate product manager",
    "group product manager",
    "lead product manager",
    "director of product management",
    "head of product",
    "vp of product",
    "vp, product",
    "product management",
    "principal product manager",
]

EXCLUDE_TITLE_WORDS = [
    "staff ", "technical program", "marketing",
    "data science", "software engineer", "engineer", "analyst",
    "scientist", "designer", "researcher", "intern", "contract",
    "stagiaire", "apprentice", "manager, program", "program manager",
]

EXCLUDE_LOCATIONS = [
    "united states", "usa", "us only", "new york", "san francisco", "seattle",
    "london", "uk only", "united kingdom", "singapore", "dubai", "canada",
    "australia", "germany", "france", "netherlands", "ireland", "poland",
    "mexico", "brazil", "japan", "korea", "china", "hong kong",
    "us, ", "us,", ", tx,", ", wa,", ", ca,", ", ny,",
    "za, ", "za,", "gb, ", "gb,", "sg, ", "sg,",
    "au, ", "au,", "de, ", "de,", "nl, ", "nl,",
    "ca, ", "ca,", "jp, ", "jp,",
    "cape town", "austin", "bellevue", "redmond", "cupertino",
    "menlo park", "new york city", "chicago", "toronto", "vancouver",
]

INDIA_LOCATIONS = [
    "india", "bangalore", "bengaluru", "mumbai", "delhi", "hyderabad",
    "pune", "chennai", "kolkata", "gurugram", "gurgaon", "noida",
    "remote - india", "india remote", "remote india", "apac",
]

SEEN_JOBS_FILE = "seen_jobs.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ── COMPANY CAREER PAGES ───────────────────────────────────────
COMPANY_PAGES = [

    # ══════════════════════════════════════════
    # TIER 1 — BIG TECH (dedicated scrapers)
    # ══════════════════════════════════════════
    {"company": "Google India",     "type": "google"},
    {"company": "Microsoft India",  "type": "microsoft"},
    {"company": "Amazon India",     "type": "amazon"},

    {
        "company": "Meta India",
        "url": "https://www.metacareers.com/jobs?offices[0]=India&roles[0]=product_management",
        "type": "generic",
    },
    {
        "company": "Apple India",
        "url": "https://jobs.apple.com/en-us/search?location=india-IND&team=apps-and-frameworks-SFTWR-AF",
        "type": "generic",
    },

    # ══════════════════════════════════════════
    # TIER 2 — GLOBAL B2B / ENTERPRISE SAAS
    # ══════════════════════════════════════════
    {
        "company": "Salesforce India",
        "url": "https://careers.salesforce.com/en/jobs/?search=product+manager&country=India",
        "type": "generic",
    },
    {
        "company": "SAP India",
        "url": "https://jobs.sap.com/search/?q=product+manager&locname=India",
        "type": "generic",
    },
    {
        "company": "Adobe India",
        "url": "https://careers.adobe.com/us/en/search-results?keywords=product+manager&country=India",
        "type": "generic",
    },
    {
        "company": "Intuit India",
        "url": "https://jobs.intuit.com/search-jobs/product%20manager/India/28287/1/2/6252001/23.1636/80.2064/50/2",
        "type": "generic",
    },
    {
        "company": "Workday India",
        "url": "https://workday.wd5.myworkdayjobs.com/Workday/jobs?q=product+manager&locations=India",
        "type": "generic",
    },
    {
        "company": "ServiceNow India",
        "url": "https://careers.servicenow.com/careers/jobs?query=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "Cisco India",
        "url": "https://jobs.cisco.com/jobs/SearchJobs/product%20manager?listFilterMode=1&location=India",
        "type": "generic",
    },
    {
        "company": "Palo Alto Networks India",
        "url": "https://jobs.paloaltonetworks.com/en/jobs/?search=product+manager&country=India",
        "type": "generic",
    },
    {
        "company": "Qualcomm India",
        "url": "https://careers.qualcomm.com/careers/search?keywords=product+manager&region=India",
        "type": "generic",
    },
    {
        "company": "PayPal India",
        "url": "https://careers.pypl.com/jobs/search?q=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "Atlassian India",
        "url": "https://www.atlassian.com/company/careers/all-jobs?team=Product+Management&location=India",
        "type": "generic",
    },
    {
        "company": "Zendesk India",
        "url": "https://jobs.zendesk.com/us/en/search-results?keywords=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "Splunk India",
        "url": "https://www.splunk.com/en_us/careers/search-jobs.html?q=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "Datadog India",
        "url": "https://careers.datadoghq.com/all-jobs/?search=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "MongoDB India",
        "url": "https://www.mongodb.com/careers/jobs?q=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "Elastic India",
        "url": "https://jobs.elastic.co/#/jobs?search=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "VMware India",
        "url": "https://careers.vmware.com/jobs/search?q=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "Nutanix India",
        "url": "https://jobs.jobvite.com/nutanix/search?q=product+manager&l=India",
        "type": "generic",
    },
    {
        "company": "Twilio India",
        "url": "https://careers.twilio.com/jobs?search=product+manager&location=India",
        "type": "generic",
    },

    # NEW B2B SaaS additions
    {
        "company": "HubSpot India",
        "url": "https://www.hubspot.com/careers/jobs?q=product+manager&country=India",
        "type": "generic",
    },
    {
        "company": "Stripe India",
        "url": "https://stripe.com/jobs/search?q=product+manager&l=India",
        "type": "generic",
    },
    {
        "company": "Notion India",
        "url": "https://www.notion.so/careers?department=Product&location=India",
        "type": "generic",
    },
    {
        "company": "Figma India",
        "url": "https://www.figma.com/careers/?department=Product&location=India",
        "type": "generic",
    },
    {
        "company": "Slack (Salesforce) India",
        "url": "https://slack.com/intl/en-in/careers",
        "type": "generic",
    },
    {
        "company": "Zoom India",
        "url": "https://careers.zoom.us/jobs/search?q=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "DocuSign India",
        "url": "https://careers.docusign.com/jobs?q=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "Okta India",
        "url": "https://www.okta.com/company/careers/product/india/",
        "type": "generic",
    },
    {
        "company": "Snowflake India",
        "url": "https://careers.snowflake.com/us/en/search-results?keywords=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "Confluent India",
        "url": "https://careers.confluent.io/jobs?q=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "HashiCorp India",
        "url": "https://www.hashicorp.com/jobs/product-management?location=India",
        "type": "generic",
    },
    {
        "company": "Amplitude India",
        "url": "https://amplitude.com/careers?department=product&location=India",
        "type": "generic",
    },
    {
        "company": "Mixpanel India",
        "url": "https://mixpanel.com/jobs/?department=product",
        "type": "generic",
    },
    {
        "company": "Chargebee",
        "url": "https://www.chargebee.com/careers/",
        "type": "generic",
    },
    {
        "company": "Zoho",
        "url": "https://careers.zohocorp.com/jobs/Careers?search=product+manager",
        "type": "generic",
    },
    {
        "company": "Freshworks",
        "url": "https://careers.freshworks.com/jobs?q=product+manager&location=India",
        "type": "generic",
    },
    {
        "company": "Clevertap",
        "url": "https://clevertap.com/careers/",
        "type": "generic",
    },
    {
        "company": "Leadsquared",
        "url": "https://www.leadsquared.com/careers/",
        "type": "generic",
    },
    {
        "company": "Icertis",
        "url": "https://www.icertis.com/company/careers/",
        "type": "generic",
    },
    {
        "company": "Capillary Technologies",
        "url": "https://www.capillarytech.com/careers/",
        "type": "generic",
    },
    {
        "company": "Darwinbox",
        "url": "https://darwinbox.com/careers",
        "type": "generic",
    },
    {
        "company": "Kissflow",
        "url": "https://kissflow.com/careers/",
        "type": "generic",
    },
    {
        "company": "Sprinklr India",
        "url": "https://www.sprinklr.com/careers/?location=India",
        "type": "generic",
    },
    {
        "company": "Whatfix",
        "url": "https://whatfix.com/careers/",
        "type": "generic",
    },
    {
        "company": "Uniphore",
        "url": "https://www.uniphore.com/careers/",
        "type": "generic",
    },
    {
        "company": "Yellow.ai",
        "url": "https://yellow.ai/careers/",
        "type": "generic",
    },
    {
        "company": "Exotel",
        "url": "https://exotel.com/careers/",
        "type": "generic",
    },

    # ══════════════════════════════════════════
    # TIER 3 — AI / ML COMPANIES
    # ══════════════════════════════════════════
    {
        "company": "Google DeepMind India",
        "url": "https://careers.google.com/jobs/results/?company=Google&company=YouTube&hl=en_US&jlo=en_US&q=product+manager+deepmind&location=India",
        "type": "generic",
    },
    {
        "company": "OpenAI",
        "url": "https://openai.com/careers/",
        "type": "generic",
    },
    {
        "company": "Anthropic",
        "url": "https://www.anthropic.com/careers",
        "type": "generic",
    },
    {
        "company": "Cohere India",
        "url": "https://cohere.com/careers?department=Product&location=India",
        "type": "generic",
    },
    {
        "company": "Scale AI India",
        "url": "https://scale.com/careers?department=Product",
        "type": "generic",
    },
    {
        "company": "Nvidia India",
        "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/jobs?q=product+manager&locations=India",
        "type": "generic",
    },
    {
        "company": "Sarvam AI",
        "url": "https://www.sarvam.ai/careers",
        "type": "generic",
    },
    {
        "company": "Krutrim",
        "url": "https://krutrim.com/careers",
        "type": "generic",
    },
    {
        "company": "Haptik (Reliance)",
        "url": "https://haptik.ai/careers/",
        "type": "generic",
    },
    {
        "company": "Observe.AI",
        "url": "https://www.observe.ai/company/careers/",
        "type": "generic",
    },
    {
        "company": "Suki AI",
        "url": "https://www.suki.ai/careers/",
        "type": "generic",
    },
    {
        "company": "Turing",
        "url": "https://www.turing.com/careers",
        "type": "generic",
    },
    {
        "company": "Lyzr AI",
        "url": "https://www.lyzr.ai/careers/",
        "type": "generic",
    },
    {
        "company": "Fractal Analytics",
        "url": "https://fractal.ai/careers/",
        "type": "generic",
    },
    {
        "company": "Mu Sigma",
        "url": "https://www.mu-sigma.com/careers/",
        "type": "generic",
    },
    {
        "company": "Tiger Analytics",
        "url": "https://www.tigeranalytics.com/careers/",
        "type": "generic",
    },
    {
        "company": "Sigmoid",
        "url": "https://www.sigmoid.com/careers/",
        "type": "generic",
    },

    # ══════════════════════════════════════════
    # TIER 4 — INDIAN E-COMMERCE & CONSUMER TECH
    # ══════════════════════════════════════════
    {
        "company": "Flipkart",
        "url": "https://www.flipkartcareers.com/#!/joblist",
        "type": "generic",
    },
    {
        "company": "Swiggy",
        "url": "https://careers.swiggy.com/#/careers",
        "type": "generic",
    },
    {
        "company": "Zomato",
        "url": "https://www.zomato.com/careers",
        "type": "generic",
    },
    {
        "company": "PhonePe",
        "url": "https://careers.phonepe.com/jobs",
        "type": "generic",
    },
    {
        "company": "Razorpay",
        "url": "https://razorpay.com/jobs/",
        "type": "generic",
    },
    {
        "company": "Paytm",
        "url": "https://paytm.com/care/job-openings",
        "type": "generic",
    },
    {
        "company": "Meesho",
        "url": "https://meesho.io/careers",
        "type": "generic",
    },
    {
        "company": "CRED",
        "url": "https://careers.cred.club/",
        "type": "generic",
    },
    {
        "company": "Groww",
        "url": "https://groww.in/careers",
        "type": "generic",
    },
    {
        "company": "Zepto",
        "url": "https://www.zepto.com/careers",
        "type": "generic",
    },
    {
        "company": "Blinkit (Zomato)",
        "url": "https://blinkit.com/careers",
        "type": "generic",
    },
    {
        "company": "Ola",
        "url": "https://ola.careers/",
        "type": "generic",
    },
    {
        "company": "Myntra",
        "url": "https://www.myntra.com/careers",
        "type": "generic",
    },
    {
        "company": "Nykaa",
        "url": "https://careers.nykaa.com/jobs",
        "type": "generic",
    },
    {
        "company": "Ajio (Reliance)",
        "url": "https://www.ril.com/ourpeople/careers.aspx",
        "type": "generic",
    },
    {
        "company": "JioMart",
        "url": "https://www.jio.com/en-in/careers/",
        "type": "generic",
    },
    {
        "company": "Tata Digital / Tata Neu",
        "url": "https://www.tata.com/careers",
        "type": "generic",
    },
    {
        "company": "BigBasket (Tata)",
        "url": "https://careers.bigbasket.com/",
        "type": "generic",
    },
    {
        "company": "1mg (Tata)",
        "url": "https://www.1mg.com/careers",
        "type": "generic",
    },
    {
        "company": "Lenskart",
        "url": "https://lenskart.com/careers",
        "type": "generic",
    },
    {
        "company": "Udaan",
        "url": "https://udaan.com/careers.html",
        "type": "generic",
    },
    {
        "company": "Delhivery",
        "url": "https://www.delhivery.com/careers",
        "type": "generic",
    },
    {
        "company": "Shiprocket",
        "url": "https://www.shiprocket.in/careers/",
        "type": "generic",
    },
    {
        "company": "Shadowfax",
        "url": "https://shadowfax.in/careers.html",
        "type": "generic",
    },
    {
        "company": "OfBusiness",
        "url": "https://www.ofbusiness.com/careers",
        "type": "generic",
    },
    {
        "company": "Moglix",
        "url": "https://www.moglix.com/careers",
        "type": "generic",
    },
    {
        "company": "Dealshare",
        "url": "https://www.dealshare.in/careers",
        "type": "generic",
    },

    # ══════════════════════════════════════════
    # TIER 5 — FINTECH
    # ══════════════════════════════════════════
    {
        "company": "Zerodha",
        "url": "https://zerodha.com/careers/",
        "type": "generic",
    },
    {
        "company": "Upstox",
        "url": "https://upstox.com/careers/",
        "type": "generic",
    },
    {
        "company": "Angel One",
        "url": "https://www.angelone.in/careers",
        "type": "generic",
    },
    {
        "company": "BankBazaar",
        "url": "https://www.bankbazaar.com/about/careers.html",
        "type": "generic",
    },
    {
        "company": "PolicyBazaar",
        "url": "https://careers.policybazaar.com/",
        "type": "generic",
    },
    {
        "company": "Slice",
        "url": "https://www.sliceit.com/careers",
        "type": "generic",
    },
    {
        "company": "Jupiter Money",
        "url": "https://jupiter.money/careers/",
        "type": "generic",
    },
    {
        "company": "Fi Money",
        "url": "https://fi.money/careers",
        "type": "generic",
    },
    {
        "company": "Jar",
        "url": "https://myjar.app/careers/",
        "type": "generic",
    },
    {
        "company": "Setu (Pine Labs)",
        "url": "https://setu.co/careers",
        "type": "generic",
    },
    {
        "company": "Cashfree Payments",
        "url": "https://www.cashfree.com/careers/",
        "type": "generic",
    },
    {
        "company": "Juspay",
        "url": "https://juspay.in/careers",
        "type": "generic",
    },
    {
        "company": "Signzy",
        "url": "https://signzy.com/careers/",
        "type": "generic",
    },
    {
        "company": "Perfios",
        "url": "https://www.perfios.com/careers/",
        "type": "generic",
    },

    # ══════════════════════════════════════════
    # TIER 6 — EDTECH & HEALTH TECH
    # ══════════════════════════════════════════
    {
        "company": "Byju's",
        "url": "https://byjus.com/jobs/",
        "type": "generic",
    },
    {
        "company": "Unacademy",
        "url": "https://unacademy.com/careers",
        "type": "generic",
    },
    {
        "company": "upGrad",
        "url": "https://careers.upgrad.com/",
        "type": "generic",
    },
    {
        "company": "PhysicsWallah",
        "url": "https://www.pw.live/careers",
        "type": "generic",
    },
    {
        "company": "Scaler",
        "url": "https://www.scaler.com/careers/",
        "type": "generic",
    },
    {
        "company": "Practo",
        "url": "https://www.practo.com/company/careers",
        "type": "generic",
    },
    {
        "company": "PharmEasy",
        "url": "https://pharmeasy.in/careers/",
        "type": "generic",
    },
    {
        "company": "Healthifyme",
        "url": "https://www.healthifyme.com/careers/",
        "type": "generic",
    },
    {
        "company": "MediBuddy",
        "url": "https://www.medibuddy.in/careers",
        "type": "generic",
    },

    # ══════════════════════════════════════════
    # TIER 7 — SaaS / DEVELOPER TOOLS
    # ══════════════════════════════════════════
    {
        "company": "Postman",
        "url": "https://www.postman.com/company/careers/",
        "type": "generic",
    },
    {
        "company": "Browserstack",
        "url": "https://www.browserstack.com/careers",
        "type": "generic",
    },
    {
        "company": "Druva",
        "url": "https://www.druva.com/about/careers/",
        "type": "generic",
    },
    {
        "company": "InMobi",
        "url": "https://www.inmobi.com/company/careers/",
        "type": "generic",
    },
    {
        "company": "Hasura",
        "url": "https://hasura.io/careers/",
        "type": "generic",
    },
    {
        "company": "Setu",
        "url": "https://setu.co/careers",
        "type": "generic",
    },
    {
        "company": "Mindtickle",
        "url": "https://www.mindtickle.com/company/careers/",
        "type": "generic",
    },
    {
        "company": "Vymo",
        "url": "https://www.getvymo.com/careers/",
        "type": "generic",
    },
    {
        "company": "Innovaccer",
        "url": "https://innovaccer.com/careers/",
        "type": "generic",
    },
    {
        "company": "Gupshup",
        "url": "https://www.gupshup.io/developer/careers",
        "type": "generic",
    },
    {
        "company": "Nimble (formerly Voila)",
        "url": "https://www.nimblework.com/careers/",
        "type": "generic",
    },
    {
        "company": "Helpshift",
        "url": "https://www.helpshift.com/company/careers/",
        "type": "generic",
    },
    {
        "company": "Wingify (VWO)",
        "url": "https://wingify.com/careers/",
        "type": "generic",
    },
    {
        "company": "WebEngage",
        "url": "https://webengage.com/company/careers/",
        "type": "generic",
    },
    {
        "company": "MoEngage",
        "url": "https://www.moengage.com/about/careers/",
        "type": "generic",
    },
    {
        "company": "Netcore Cloud",
        "url": "https://netcorecloud.com/careers/",
        "type": "generic",
    },

    # ══════════════════════════════════════════
    # TIER 8 — IT SERVICES (product roles)
    # ══════════════════════════════════════════
    {
        "company": "Infosys",
        "url": "https://career.infosys.com/jobsearch/joblist",
        "type": "generic",
    },
    {
        "company": "TCS",
        "url": "https://www.tcs.com/careers/tcs-careers",
        "type": "generic",
    },
    {
        "company": "Wipro",
        "url": "https://careers.wipro.com/careers-home/",
        "type": "generic",
    },
    {
        "company": "HCLTech",
        "url": "https://www.hcltech.com/careers",
        "type": "generic",
    },
    {
        "company": "Tech Mahindra",
        "url": "https://careers.techmahindra.com/Search.aspx",
        "type": "generic",
    },
]

JOB_BOARDS = [
    {"name": "Naukri",   "type": "naukri"},
    {"name": "LinkedIn", "type": "linkedin"},
]


# ── HELPERS ────────────────────────────────────────────────────
def load_seen_jobs():
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_seen_jobs(seen):
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(seen, f, indent=2)


def is_relevant_title(title):
    t = title.lower().strip()
    if not any(kw in t for kw in KEYWORDS):
        return False
    if any(ex in t for ex in EXCLUDE_TITLE_WORDS):
        return False
    return True


def is_valid_job_link(link, base_url):
    if not link or not link.startswith("http"):
        return False
    if normalize_link(link) == normalize_link(base_url):
        return False
    parsed = urlparse(link)
    path_parts = [p for p in parsed.path.split("/") if p]
    if len(path_parts) < 2:
        return False
    return True


def validate_link(link, timeout=8):
    try:
        r = requests.head(link, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return r.status_code < 400
    except:
        return False


def is_india_location(location_text):
    text = location_text.lower()
    for loc in EXCLUDE_LOCATIONS:
        if loc in text:
            return False
    for loc in INDIA_LOCATIONS:
        if loc in text:
            return True
    return None


def normalize_link(link):
    if not link:
        return ""
    try:
        parsed = urlparse(link)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
    except:
        return link.split("?")[0].rstrip("/")


def deduplicate(jobs):
    seen_links = {}
    result = []
    for job in jobs:
        key = normalize_link(job["link"])
        if key and key not in seen_links:
            seen_links[key] = True
            result.append(job)
    return result


# ── EMAIL ──────────────────────────────────────────────────────
def send_email(new_jobs):
    subject = f"🎯 {len(new_jobs)} New PM Job(s) in India — {datetime.now().strftime('%d %b %Y, %I:%M %p')}"

    # Group jobs by category for cleaner email
    categories = {
        "🏢 Big Tech": [],
        "🤖 AI / ML": [],
        "🛒 E-Commerce": [],
        "💳 Fintech": [],
        "📦 B2B SaaS": [],
        "🎓 EdTech / HealthTech": [],
        "🔧 Dev Tools / Other": [],
    }

    category_keywords = {
        "🏢 Big Tech":          ["google", "microsoft", "amazon", "meta", "apple"],
        "🤖 AI / ML":           ["ai", "deepmind", "openai", "anthropic", "cohere", "scale", "nvidia", "sarvam", "krutrim", "haptik", "observe", "fractal", "mu sigma", "tiger analytics", "sigmoid", "turing", "lyzr"],
        "🛒 E-Commerce":        ["flipkart", "swiggy", "zomato", "blinkit", "meesho", "myntra", "nykaa", "ajio", "jiomart", "tata", "bigbasket", "1mg", "lenskart", "udaan", "delhivery", "shiprocket", "shadowfax", "ofbusiness", "moglix", "dealshare", "ola", "zepto"],
        "💳 Fintech":           ["phonepe", "razorpay", "paytm", "zerodha", "upstox", "angel", "bankbazaar", "policybazaar", "slice", "jupiter", "fi money", "jar", "setu", "cashfree", "juspay", "signzy", "perfios", "groww", "cred"],
        "📦 B2B SaaS":          ["salesforce", "sap", "adobe", "intuit", "workday", "servicenow", "cisco", "palo alto", "qualcomm", "paypal", "atlassian", "zendesk", "splunk", "datadog", "mongodb", "elastic", "vmware", "nutanix", "twilio", "hubspot", "stripe", "notion", "figma", "slack", "zoom", "docusign", "okta", "snowflake", "confluent", "hashicorp", "amplitude", "mixpanel", "chargebee", "zoho", "freshworks", "clevertap", "leadsquared", "icertis", "capillary", "darwinbox", "kissflow", "sprinklr", "whatfix", "uniphore", "yellow", "exotel"],
        "🎓 EdTech / HealthTech": ["byju", "unacademy", "upgrad", "physicswallah", "scaler", "practo", "pharmeasy", "healthifyme", "medibuddy"],
        "🔧 Dev Tools / Other": [],
    }

    for job in new_jobs:
        co = job["company"].lower()
        placed = False
        for cat, keywords in category_keywords.items():
            if any(kw in co for kw in keywords):
                categories[cat].append(job)
                placed = True
                break
        if not placed:
            categories["🔧 Dev Tools / Other"].append(job)

    sections = ""
    for cat, jobs in categories.items():
        if not jobs:
            continue
        rows = "".join(f"""
        <tr>
          <td style="padding:10px 10px;border-bottom:1px solid #eee;">
            <strong style="font-size:14px;">{j['title']}</strong><br>
            <span style="color:#555;font-size:13px;">{j['company']}</span>
            {"<br><span style='color:#e67e22;font-size:12px;'>📍 " + j.get('location','') + "</span>" if j.get('location') else ""}
          </td>
          <td style="padding:10px 10px;border-bottom:1px solid #eee;white-space:nowrap;vertical-align:middle;">
            <a href="{j['link']}" style="background:#1a73e8;color:white;padding:6px 14px;
               border-radius:4px;text-decoration:none;font-size:13px;">View Job ↗</a>
          </td>
        </tr>""" for j in jobs)

        sections += f"""
        <div style="margin-top:20px;">
          <div style="background:#f0f4ff;padding:8px 12px;border-left:4px solid #1a73e8;
                      font-weight:bold;font-size:14px;color:#1a1a2e;">{cat} — {len(jobs)} role(s)</div>
          <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border:1px solid #eee;border-top:none;">
            {rows}
          </table>
        </div>"""

    html = f"""<html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;padding:0 10px;">
    <div style="background:linear-gradient(135deg,#1a73e8,#0d47a1);padding:24px;border-radius:10px 10px 0 0;">
      <h2 style="color:white;margin:0;font-size:22px;">🎯 New Product Manager Jobs in India</h2>
      <p style="color:#cce0ff;margin:6px 0 0;font-size:13px;">
        {len(new_jobs)} new listing(s) found · {datetime.now().strftime('%d %B %Y, %I:%M %p')}
      </p>
    </div>
    <div style="border:1px solid #ddd;border-top:none;border-radius:0 0 10px 10px;padding:16px 16px 24px;">
      {sections}
      <p style="color:#aaa;font-size:11px;text-align:center;margin-top:28px;">
        PM Job Tracker · GitHub Actions · Ankita's edition 🚀
      </p>
    </div>
    </body></html>"""

    recipients = [email.strip() for email in GMAIL_RECEIVER.split(",")]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_SENDER
    msg["To"]      = ", ".join(recipients)
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL_SENDER, GMAIL_PASSWORD)
        s.sendmail(GMAIL_SENDER, recipients, msg.as_string())
    print(f"✅ Email sent to {len(recipients)} recipient(s) with {len(new_jobs)} jobs.")


# ── SCRAPERS ───────────────────────────────────────────────────
def scrape_google(info):
    jobs = []
    try:
        r = requests.get(
            "https://careers.google.com/api/v3/search/"
            "?q=product+manager&location=India&num=20&page=1",
            headers=HEADERS, timeout=15)
        for job in r.json().get("jobs", []):
            title    = job.get("title", "")
            location = " ".join(job.get("locations", []))
            if not is_relevant_title(title):
                continue
            if is_india_location(location) == False:
                continue
            jid = job.get("id", title)
            jobs.append({
                "id":       f"google_{jid}",
                "title":    title,
                "company":  "Google India",
                "location": location,
                "link":     f"https://careers.google.com/jobs/results/{jid}/",
            })
    except Exception as e:
        print(f"  ⚠️  Google: {e}")
    return jobs


def scrape_amazon(info):
    jobs = []
    try:
        r = requests.get(
            "https://www.amazon.jobs/en/search.json"
            "?base_query=product+manager&loc_query=India&job_count=20&offset=0",
            headers=HEADERS, timeout=15)
        for job in r.json().get("jobs", []):
            title    = job.get("title", "")
            location = job.get("location", "")
            if not is_relevant_title(title):
                continue
            if is_india_location(location) == False:
                continue
            jid = str(job.get("id_icims", ""))
            jobs.append({
                "id":       f"amazon_{jid}",
                "title":    title,
                "company":  "Amazon India",
                "location": location,
                "link":     f"https://www.amazon.jobs/en/jobs/{jid}",
            })
    except Exception as e:
        print(f"  ⚠️  Amazon: {e}")
    return jobs


def scrape_microsoft(info):
    jobs = []
    try:
        r = requests.get(
            "https://jobs.microsoft.com/api/jobs"
            "?q=product+manager&l=India&pg=1&pgSz=20",
            headers=HEADERS, timeout=15)
        data = r.json()
        job_list = (
            data.get("operationResult", {})
                .get("result", {})
                .get("jobs", data.get("value", []))
        )
        for job in job_list:
            title    = job.get("title", "")
            location = job.get("primaryWorkLocation", job.get("location", ""))
            if not is_relevant_title(title):
                continue
            if is_india_location(str(location)) == False:
                continue
            jid = job.get("jobId", job.get("id", ""))
            jobs.append({
                "id":       f"microsoft_{jid}",
                "title":    title,
                "company":  "Microsoft India",
                "location": str(location),
                "link":     f"https://jobs.microsoft.com/en-us/job/{jid}",
            })
    except Exception as e:
        print(f"  ⚠️  Microsoft: {e}")
    return jobs


def scrape_naukri(board):
    jobs = []
    try:
        r = requests.get(
            "https://www.naukri.com/jobapi/v3/search"
            "?noOfResults=30&urlType=search_by_key_loc"
            "&searchType=adv&keyword=product+manager"
            "&location=india&jobAge=1&pageNo=1",
            headers={**HEADERS, "appid": "109", "systemid": "109"},
            timeout=15)
        for job in r.json().get("jobDetails", []):
            title    = job.get("title", "")
            location = (job.get("placeholders", [{}])[0].get("label", "")
                        if job.get("placeholders") else "")
            if not is_relevant_title(title):
                continue
            if is_india_location(location + " india") == False:
                continue
            jid = str(job.get("jobId", ""))
            co  = job.get("companyName", "Unknown")
            jobs.append({
                "id":       f"naukri_{jid}",
                "title":    title,
                "company":  f"{co} (Naukri)",
                "location": location,
                "link":     job.get("jdURL", f"https://www.naukri.com/job-listings-{jid}"),
            })
    except Exception as e:
        print(f"  ⚠️  Naukri: {e}")
    return jobs


def scrape_linkedin(board):
    jobs = []
    try:
        r = requests.get(
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            "?keywords=product+manager&location=India&f_TPR=r7200&start=0",
            headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.find_all("li"):
            t       = card.find("h3", class_="base-search-card__title")
            l       = card.find("a", class_="base-card__full-link")
            c       = card.find("h4", class_="base-search-card__subtitle")
            loc_tag = card.find("span", class_="job-search-card__location")
            if not (t and l):
                continue
            title    = t.get_text(strip=True)
            link     = l.get("href", "").split("?")[0]
            company  = c.get_text(strip=True) if c else "Unknown"
            location = loc_tag.get_text(strip=True) if loc_tag else ""
            if not is_relevant_title(title):
                continue
            if is_india_location(location) == False:
                continue
            jid = link.split("-")[-1] if link else title[:20]
            jobs.append({
                "id":       f"linkedin_{jid}",
                "title":    title,
                "company":  f"{company} (LinkedIn)",
                "location": location,
                "link":     link,
            })
    except Exception as e:
        print(f"  ⚠️  LinkedIn: {e}")
    return jobs


def scrape_generic(info):
    jobs, seen_titles = [], set()
    try:
        r    = requests.get(info["url"], headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup.find_all("a", href=True):
            text = tag.get_text(strip=True)
            if not (10 < len(text) < 120) or text in seen_titles:
                continue
            if not is_relevant_title(text):
                continue
            if is_india_location(text) == False:
                continue
            link = tag.get("href", "")
            if link.startswith("/"):
                b    = urlparse(info["url"])
                link = f"{b.scheme}://{b.netloc}{link}"
            if not is_valid_job_link(link, info["url"]):
                continue
            seen_titles.add(text)
            jobs.append({
                "id":       f"{info['company']}_{text[:50]}".replace(" ", "_"),
                "title":    text,
                "company":  info["company"],
                "location": "India",
                "link":     link,
            })
    except Exception as e:
        print(f"  ⚠️  {info['company']}: {e}")
    return jobs


# ── MAIN ───────────────────────────────────────────────────────
def run():
    print(f"\n{'='*60}")
    print(f"🔍 PM Job Tracker — {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    print(f"   Tracking {len(COMPANY_PAGES)} companies + {len(JOB_BOARDS)} job boards")
    print(f"{'='*60}")

    seen     = load_seen_jobs()
    all_jobs = []

    # Step 1 — Company career pages
    print("\n📋 Checking company career pages...")
    for co in COMPANY_PAGES:
        print(f"  → {co['company']}")
        fn = {
            "google":    scrape_google,
            "amazon":    scrape_amazon,
            "microsoft": scrape_microsoft,
        }.get(co["type"], scrape_generic)
        all_jobs.extend(fn(co))

    # Step 2 — Job boards
    print("\n📋 Checking job boards...")
    for board in JOB_BOARDS:
        print(f"  → {board['name']}")
        fn = {"naukri": scrape_naukri, "linkedin": scrape_linkedin}.get(board["type"])
        if fn:
            all_jobs.extend(fn(board))

    # Step 3 — Deduplicate
    all_jobs = deduplicate(all_jobs)
    print(f"\n🔗 After deduplication: {len(all_jobs)} unique jobs")

    # Step 4 — Filter new
    new_jobs = []
    for job in all_jobs:
        if job["id"] not in seen:
            seen[job["id"]] = datetime.now().isoformat()
            new_jobs.append(job)
            print(f"  ✨ NEW: {job['title']} @ {job['company']} [{job.get('location','')}]")

    # Step 5 — Validate links
    print(f"\n🔎 Validating {len(new_jobs)} job links...")
    valid_jobs = []
    for job in new_jobs:
        if validate_link(job["link"]):
            valid_jobs.append(job)
        else:
            print(f"  ❌ Dead link skipped: {job['title']} — {job['link']}")
    print(f"  ✅ {len(valid_jobs)} valid links remaining")

    save_seen_jobs(seen)

    # Step 6 — Email
    print(f"\n{'─'*60}")
    if valid_jobs:
        print(f"📧 {len(valid_jobs)} new job(s) found! Sending email...")
        send_email(valid_jobs)
    else:
        print("✅ No new jobs this run. All quiet.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
