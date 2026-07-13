#!/usr/bin/env python3
"""Cloud runner for the daily EDC/MDC research update.

The job is designed for GitHub Actions:
1. Search PubMed for the report date.
2. Read the Evidence Tracker and deduplicate by DOI, PMID, then link/title.
3. Create a dated Google Doc in Drive.
4. Append only new, non-duplicate studies to the Google Sheet.
5. Optionally email a completion notification.
"""

from __future__ import annotations

import base64
import datetime as dt
import email.message
import json
import os
import re
import smtplib
import sys
import textwrap
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Iterable
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build


FOLDER_ID = "1MY56-kcIhevXOe4QDVKZm9EM7_QbrGC6"
SPREADSHEET_ID = "1tJKmHG55tMwdzFUhMxKuT-Rx9HiW7lI3CRUNp3Ppxs4"
SHEET_NAME = "Evidence Tracker"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
]


EDC_TERMS = [
    "endocrine disrupting chemicals",
    "endocrine disruptors",
    "metabolic disrupting",
    "obesogen",
    "PFAS",
    "perfluoroalkyl",
    "bisphenol",
    "phthalate",
    "microplastic",
    "nanoplastic",
    "tributyltin",
    "paraben",
    "pesticide",
]

OUTCOME_TERMS = [
    "fertility",
    "infertility",
    "sperm",
    "ovarian",
    "oocyte",
    "testicular",
    "testosterone",
    "steroidogenesis",
    "insulin",
    "beta-cell",
    "adipocyte",
    "adipogenesis",
    "adipose",
    "gut hormone",
    "enteroendocrine",
    "GLP-1",
    "GIP",
    "PYY",
    "ghrelin",
    "microbiome",
    "MASLD",
    "MASH",
    "obesity",
    "metabolic",
    "oxidative stress",
    "inflammation",
    "mitochondrial",
]

NUTRIENT_TERMS = [
    "quercetin",
    "resveratrol",
    "curcumin",
    "anthocyanin",
    "astaxanthin",
    "selenium",
    "vitamin",
    "polyphenol",
    "probiotic",
    "dietary antioxidant",
    "dietary intervention",
    "choline",
]


@dataclass
class Record:
    pmid: str
    doi: str
    title: str
    journal: str
    pub_date: str
    abstract: str

    @property
    def link(self) -> str:
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"


def env_required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def report_date() -> dt.date:
    value = os.environ.get("REPORT_DATE")
    if value:
        return dt.date.fromisoformat(value)
    return dt.datetime.now(ZoneInfo("America/Los_Angeles")).date()


def pubmed_query_for(day: dt.date, broad: bool = False) -> str:
    edc = " OR ".join(f'"{term}"[Title/Abstract]' for term in EDC_TERMS)
    date_part = f'"{day:%Y/%m/%d}"[PDAT]'
    if broad:
        return f"(({edc}) AND {date_part})"
    outcomes = " OR ".join(f'"{term}"[Title/Abstract]' for term in OUTCOME_TERMS + NUTRIENT_TERMS)
    return f"(({edc}) AND ({outcomes}) AND {date_part})"


def ncbi_get(path: str, params: dict[str, str], timeout: int = 45) -> bytes:
    email = os.environ.get("NCBI_EMAIL")
    if email:
        params["email"] = email
    params.setdefault("tool", "claude-minions-daily-edc-mdc")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{path}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


def pubmed_search(day: dt.date) -> list[str]:
    ids: list[str] = []
    for broad in (False, True):
        xml = ncbi_get(
            "esearch.fcgi",
            {
                "db": "pubmed",
                "term": pubmed_query_for(day, broad=broad),
                "retmax": "100",
                "sort": "pub date",
                "retmode": "xml",
            },
        )
        root = ET.fromstring(xml)
        for node in root.findall(".//Id"):
            if node.text and node.text not in ids:
                ids.append(node.text)
    return ids


def text_of(node: ET.Element | None) -> str:
    if node is None:
        return ""
    return " ".join("".join(node.itertext()).split())


def fetch_records(pmids: Iterable[str]) -> list[Record]:
    pmid_list = list(pmids)
    if not pmid_list:
        return []
    xml = ncbi_get(
        "efetch.fcgi",
        {"db": "pubmed", "id": ",".join(pmid_list), "retmode": "xml"},
        timeout=90,
    )
    root = ET.fromstring(xml)
    records: list[Record] = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext("./MedlineCitation/PMID") or ""
        title = text_of(article.find("./MedlineCitation/Article/ArticleTitle"))
        journal = article.findtext("./MedlineCitation/Article/Journal/Title") or ""
        abstract = " ".join(text_of(node) for node in article.findall(".//AbstractText")).strip()
        doi = ""
        for article_id in article.findall("./PubmedData/ArticleIdList/ArticleId"):
            if article_id.attrib.get("IdType") == "doi":
                doi = article_id.text or ""
                break
        pub_date_node = article.find("./MedlineCitation/Article/Journal/JournalIssue/PubDate")
        parts = []
        if pub_date_node is not None:
            for key in ("Year", "Month", "Day"):
                value = pub_date_node.findtext(key)
                if value:
                    parts.append(value)
        records.append(
            Record(
                pmid=pmid,
                doi=doi,
                title=title,
                journal=journal,
                pub_date="-".join(parts),
                abstract=abstract,
            )
        )
    return records


def has_any(text: str, terms: Iterable[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def keep_record(record: Record) -> bool:
    haystack = f"{record.title} {record.abstract}"
    return has_any(haystack, EDC_TERMS) and has_any(haystack, OUTCOME_TERMS + NUTRIENT_TERMS)


def evidence_category(record: Record) -> str:
    text = f"{record.title} {record.abstract}".lower()
    if any(term in text for term in ["nhanes", "cohort", "participants", "women", "men", "patients", "children"]):
        if any(term in text for term in ["cell", "enzyme", "docking", "in vitro"]):
            return "Human + in vitro/mechanistic"
        return "Human/epidemiologic"
    if any(term in text for term in ["mouse", "mice", "rat", "zebrafish", "fish", "larvae", "daphnia"]):
        return "Animal"
    if any(term in text for term in ["cell", "enzyme", "in vitro", "adipocyte"]):
        return "In vitro/mechanistic"
    if "review" in text:
        return "Review"
    return "Unclassified"


def topic_for(record: Record) -> str:
    text = f"{record.title} {record.abstract}".lower()
    if any(term in text for term in ["oocyte", "ovarian", "pcos", "female fertility"]):
        return "Female fertility / ovarian endocrine outcomes"
    if any(term in text for term in ["sperm", "testicular", "testosterone", "steroidogenesis"]):
        return "Male fertility / reproductive steroidogenesis"
    if any(term in text for term in ["insulin", "beta-cell", "masld", "mash"]):
        return "Insulin resistance / metabolic liver disease"
    if any(term in text for term in ["adipocyte", "adipogenesis", "adipose", "obesity"]):
        return "Adipocyte biology / obesity"
    if any(term in text for term in ["microbiome", "gut hormone", "enteroendocrine", "intestinal"]):
        return "Gut biology / microbiome"
    return "EDC/MDC mechanism"


def exposure_for(record: Record) -> str:
    text = f"{record.title} {record.abstract}".lower()
    found = []
    for term in ["PFAS", "bisphenol", "phthalate", "DEHP", "microplastic", "nanoplastic", "tributyltin", "pesticide", "paraben"]:
        if term.lower() in text:
            found.append(term)
    return ", ".join(dict.fromkeys(found)) or "EDC/MDC exposure"


def nutrient_for(record: Record) -> str:
    text = f"{record.title} {record.abstract}".lower()
    found = [term for term in NUTRIENT_TERMS if term.lower() in text]
    return ", ".join(dict.fromkeys(found)) or "None tested"


def sentence(text: str, fallback: str) -> str:
    clean = " ".join(text.split())
    if not clean:
        return fallback
    pieces = re.split(r"(?<=[.!?])\s+", clean)
    return pieces[0][:450]


def row_for(day: dt.date, record: Record, doc_url: str = "") -> list[str]:
    return [
        day.isoformat(),
        topic_for(record),
        exposure_for(record),
        nutrient_for(record),
        record.journal or "Peer-reviewed article",
        sentence(record.abstract, "Recent PubMed record identified within the EDC/MDC search scope."),
        f"Relevant to {topic_for(record).lower()} in the daily EDC/MDC evidence scope.",
        "Automated screening summary; full-text appraisal and exposure-dose assessment may be needed.",
        evidence_category(record),
        f"PMID: {record.pmid}; DOI: {record.doi}" if record.doi else f"PMID: {record.pmid}",
        record.link,
        doc_url,
    ]


def service_account_credentials():
    raw = env_required("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw.strip().startswith("{"):
        info = json.loads(raw)
    else:
        info = json.loads(base64.b64decode(raw).decode("utf-8"))
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)


def get_existing_keys(sheets) -> tuple[set[str], set[str], set[str], set[str]]:
    result = (
        sheets.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=f"'{SHEET_NAME}'!A2:K")
        .execute()
    )
    doi_keys: set[str] = set()
    pmid_keys: set[str] = set()
    link_keys: set[str] = set()
    title_like_keys: set[str] = set()
    for row in result.get("values", []):
        id_cell = row[9] if len(row) > 9 else ""
        link_cell = row[10] if len(row) > 10 else ""
        for doi in re.findall(r"10\.\S+", id_cell, flags=re.I):
            doi_keys.add(doi.rstrip(".,;").lower())
        for pmid in re.findall(r"PMID:\s*(\d+)", id_cell, flags=re.I):
            pmid_keys.add(pmid)
        if link_cell:
            link_keys.add(link_cell.strip().lower())
        if len(row) > 5 and row[5]:
            title_like_keys.add(row[5].strip().lower())
    return doi_keys, pmid_keys, link_keys, title_like_keys


def is_duplicate(record: Record, existing: tuple[set[str], set[str], set[str], set[str]]) -> bool:
    doi_keys, pmid_keys, link_keys, title_like_keys = existing
    if record.doi and record.doi.lower() in doi_keys:
        return True
    if record.pmid and record.pmid in pmid_keys:
        return True
    if record.link.lower() in link_keys:
        return True
    return record.title.strip().lower() in title_like_keys


def create_google_doc(drive, day: dt.date) -> tuple[str, str]:
    title = f"EDC MDC Daily Research Update - {day.isoformat()}"
    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [FOLDER_ID],
    }
    created = drive.files().create(body=file_metadata, fields="id,webViewLink").execute()
    doc_id = created["id"]
    doc_url = created.get("webViewLink") or f"https://docs.google.com/document/d/{doc_id}/edit"
    return doc_id, doc_url


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    def clean(value: str) -> str:
        return str(value).replace("\n", " ").replace("|", "/")

    output = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        output.append("| " + " | ".join(clean(value) for value in row) + " |")
    return "\n".join(output)


def build_report(day: dt.date, rows: list[list[str]], skipped: int, appended: int) -> str:
    table_rows = rows or [[day.isoformat(), "Daily search result", "EDC/MDC scope", "Not applicable", "Search/update status", "No new non-duplicate tracker-eligible study was identified for the report date.", "Deduplication prevents repeatedly adding previously captured studies.", "Automated PubMed search depends on records indexed by run time.", "Status", "N/A", "N/A", ""]]
    headers = [
        "Report Date",
        "Topic",
        "Chemical / Exposure",
        "Nutrient / Intervention",
        "Study Type / Model",
        "Key Findings",
        "Health Relevance",
        "Limitations",
        "Evidence Category",
        "PMID / DOI",
        "Study Link",
        "Daily Report Doc Link",
    ]
    human = [row for row in table_rows if "human" in row[8].lower()]
    animal = [row for row in table_rows if "animal" in row[8].lower()]
    invitro = [row for row in table_rows if "vitro" in row[8].lower() or "mechanistic" in row[8].lower()]
    return "\n\n".join(
        [
            f"EDC MDC Daily Research Update - {day.isoformat()}",
            "Reminder: read today's EDC/MDC research update.",
            "Main takeaways\n"
            f"- New non-duplicate tracker rows appended: {appended}.\n"
            f"- Candidate records skipped as duplicates or out of scope: {skipped}.\n"
            "- Human, animal, and in vitro evidence are separated below so evidence strength is clear.",
            "Daily evidence table\n" + markdown_table(headers, table_rows),
            "Evidence balance\n"
            f"- Human evidence rows: {len(human)}.\n"
            f"- Animal evidence rows: {len(animal)}.\n"
            f"- In vitro/mechanistic evidence rows: {len(invitro)}.",
            "Tracker action\n"
            + (
                f"Evidence Tracker appended with {appended} new non-duplicate study row(s)."
                if appended
                else "Evidence Tracker append skipped because no new non-duplicate study was identified."
            ),
        ]
    )


def append_rows(sheets, rows: list[list[str]]) -> None:
    if not rows:
        return
    sheets.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{SHEET_NAME}'!A:L",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()


def send_email(subject: str, body: str) -> None:
    host = os.environ.get("SMTP_HOST")
    user = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")
    recipient = os.environ.get("NOTIFY_EMAIL")
    if not all([host, user, password, recipient]):
        return
    msg = email.message.EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ.get("SMTP_FROM", user)
    msg["To"] = recipient
    msg.set_content(body)
    port = int(os.environ.get("SMTP_PORT", "587"))
    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)


def main() -> int:
    day = report_date()
    credentials = service_account_credentials()
    drive = build("drive", "v3", credentials=credentials)
    docs = build("docs", "v1", credentials=credentials)
    sheets = build("sheets", "v4", credentials=credentials)

    pmids = pubmed_search(day)
    fetched = fetch_records(pmids)
    scoped = [record for record in fetched if keep_record(record)]
    existing = get_existing_keys(sheets)
    new_records = [record for record in scoped if not is_duplicate(record, existing)]
    skipped = len(fetched) - len(new_records)

    doc_id, doc_url = create_google_doc(drive, day)
    final_rows = [row_for(day, record, doc_url=doc_url) for record in new_records[:12]]

    if final_rows:
        append_rows(sheets, final_rows)

    final_report = build_report(day, final_rows, skipped=skipped, appended=len(final_rows))
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [{"insertText": {"location": {"index": 1}, "text": final_report + "\n\n"}}]},
    ).execute()

    send_email(
        subject=f"EDC/MDC Daily Research Update - {day.isoformat()}",
        body=textwrap.dedent(
            f"""\
            Today's EDC/MDC research update is ready.

            Google Doc: {doc_url}
            Evidence Tracker: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
            Tracker rows appended: {len(final_rows)}
            """
        ),
    )
    print(json.dumps({"date": day.isoformat(), "doc_url": doc_url, "appended_rows": len(final_rows)}))
    return 0


def write_failure_fallback(exc: Exception) -> None:
    try:
        day = report_date()
    except Exception:
        day = dt.datetime.now(ZoneInfo("America/Los_Angeles")).date()
    os.makedirs("outputs", exist_ok=True)
    path = os.path.join("outputs", f"edc-mdc-daily-research-update-{day.isoformat()}-failure.md")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(
            "\n\n".join(
                [
                    f"# EDC MDC Daily Research Update - {day.isoformat()}",
                    "Cloud runner failed before completing Google Drive and tracker updates.",
                    f"Error: `{type(exc).__name__}: {exc}`",
                    "Check the GitHub Actions log and repository secrets. Do not assume Google Drive or the Evidence Tracker were updated for this run.",
                ]
            )
        )
    print(f"Wrote fallback failure report: {path}", file=sys.stderr)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        write_failure_fallback(exc)
        print(f"daily_edc_mdc_cloud_update failed: {exc}", file=sys.stderr)
        raise
