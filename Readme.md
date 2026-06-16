# Email Header Analyzer

A Python tool for security analysts that parses raw email headers and surfaces the details that matter most in phishing and email-abuse investigations — sender identity, authentication results, and the full delivery path — in a clean, readable format.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Sender analysis** — extracts and normalizes sender-related fields so identity mismatches are easy to spot.
- **Authentication results** — parses SPF, DKIM, and DMARC outcomes to highlight spoofing and alignment failures at a glance.
- **Routing reconstruction** — rebuilds the chain of `Received` hops in true chronological order, showing the path a message actually took.
- **Timezone-aware timestamps** — preserves the original time zone on each hop, making delivery delays and anomalies easy to read.
- **Browser-based interface** — a lightweight NiceGUI front end for pasting headers and reviewing parsed results.

## Requirements

- Python 3.10 or later
- Dependencies listed in `requirements.txt`

## Installation

```bash
git clone https://github.com/<your-username>/header_analyzer.git
cd header_analyzer
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

Launch the analyzer:

```bash
python main.py
```

Open the local URL shown in the terminal, paste a raw email header into the input field, and review the parsed sender, authentication, and routing details.

## License

Released under the [MIT License](LICENSE).