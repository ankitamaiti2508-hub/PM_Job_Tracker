# 🎯 PM Job Tracker — Setup Guide

Automatically scrapes **120+ companies** across Big Tech, AI, E-Commerce, Fintech, B2B SaaS, EdTech, and HealthTech for Senior PM roles in India — and emails you whenever a new job appears.

Runs **4× a day** via GitHub Actions. Completely free.

---

## What's Tracked

| Category         | Companies (sample)                                                                 |
|------------------|------------------------------------------------------------------------------------|
| 🏢 Big Tech       | Google, Microsoft, Amazon, Meta, Apple                                             |
| 🤖 AI / ML        | Sarvam AI, Krutrim, Nvidia, OpenAI, Cohere, Fractal, Observe.AI, Yellow.ai        |
| 🛒 E-Commerce     | Flipkart, Swiggy, Zomato, Meesho, Nykaa, Blinkit, Zepto, BigBasket, Delhivery    |
| 💳 Fintech        | PhonePe, Razorpay, CRED, Groww, Zerodha, Jupiter, Fi, Cashfree, Juspay           |
| 📦 B2B SaaS       | Freshworks, Zoho, Chargebee, Clevertap, MoEngage, Darwinbox, Whatfix, Sprinklr   |
| 🎓 EdTech/Health  | upGrad, PhysicsWallah, Scaler, Practo, PharmEasy, MediBuddy                      |
| 🔧 Dev Tools      | Postman, Browserstack, Hasura, Wingify, WebEngage, Netcore, Helpshift             |
| 📋 Job Boards     | Naukri, LinkedIn                                                                   |

---

## One-Time Setup (10 minutes)

### Step 1 — Fork / create your GitHub repo

Create a new **private** GitHub repo (keep it private so your email creds stay secret).
Upload these 4 files:
```
scraper.py
requirements.txt
seen_jobs.json
.github/workflows/scrape.yml
```

### Step 2 — Enable Gmail App Password

1. Go to your Google Account → **Security**
2. Enable **2-Step Verification** (required)
3. Search for **"App Passwords"** → create one → select "Mail" + "Other (custom)" → name it "PM Tracker"
4. Copy the 16-character password shown — you won't see it again

### Step 3 — Add GitHub Secrets

In your repo → **Settings → Secrets and variables → Actions → New repository secret**

Add these three secrets:

| Secret name      | Value                                      |
|------------------|--------------------------------------------|
| `GMAIL_SENDER`   | your Gmail address (e.g. you@gmail.com)    |
| `GMAIL_PASSWORD` | the 16-char App Password from Step 2       |
| `GMAIL_RECEIVER` | email(s) to notify (comma-separate for multiple) |

### Step 4 — Give Actions write permission

Go to **Settings → Actions → General → Workflow permissions**
→ Select **"Read and write permissions"** → Save

### Step 5 — Run it manually to test

Go to **Actions tab → PM Job Tracker → Run workflow**

You should receive an email within ~2 minutes with all currently open roles (first run will send many — subsequent runs only send new ones).

---

## Schedule

The tracker runs automatically at these IST times:
- 6:00 AM
- 12:00 PM
- 6:00 PM
- 12:00 AM

You can change the schedule in `.github/workflows/scrape.yml`.

---

## Customising Keywords

Edit `KEYWORDS` in `scraper.py` to add/remove job titles you want to track.
Edit `EXCLUDE_TITLE_WORDS` to filter out noise.

---

## Troubleshooting

- **No email received on first run?** Check Actions logs for errors. Most common issue: wrong App Password.
- **Too many irrelevant jobs?** Add more words to `EXCLUDE_TITLE_WORDS`.
- **Missing a company?** Add it to `COMPANY_PAGES` with `type: generic` and the careers URL.
