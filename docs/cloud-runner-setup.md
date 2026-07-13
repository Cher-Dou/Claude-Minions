# Cloud Runner Setup: Daily EDC/MDC Research Update

This moves the daily update from a laptop-dependent Codex session to GitHub Actions.

## What It Does

- Runs every day at 14:00 UTC, which is 07:00 America/Los_Angeles during daylight saving time.
- Searches PubMed for the report date.
- Creates a dated Google Doc in `Daily EDC MDC Research Reports`.
- Reads the existing `Evidence Tracker` tab before writing.
- Deduplicates by DOI first, then PMID, then study link/title.
- Appends only new studies to the Google Sheet.
- Optionally emails a notification after the run.

## Required Google Setup

1. Create a Google Cloud service account.
2. Enable these APIs in the Google Cloud project:
   - Google Drive API
   - Google Docs API
   - Google Sheets API
3. Create a JSON key for the service account.
4. Share these Google Drive targets with the service account email as Editor:
   - Folder: `Daily EDC MDC Research Reports`
   - Sheet: `Daily EDC MDC Evidence Tracker`

The service account email looks like:

```text
name@project-id.iam.gserviceaccount.com
```

## Required GitHub Secrets

Add these in the GitHub repository:

`Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`

Required:

- `GOOGLE_SERVICE_ACCOUNT_JSON`: the full service-account JSON key, or base64-encoded JSON.
- `NCBI_EMAIL`: your contact email for PubMed/NCBI request etiquette.

Optional email notification:

- `SMTP_HOST`: for Gmail, use `smtp.gmail.com`.
- `SMTP_PORT`: for Gmail, use `587`.
- `SMTP_USERNAME`: Gmail address or SMTP username.
- `SMTP_PASSWORD`: Gmail app password, not your normal Google password.
- `SMTP_FROM`: sender address; usually the same as `SMTP_USERNAME`.
- `NOTIFY_EMAIL`: recipient email address.

## Manual Backfill

The workflow supports manual runs:

`Actions` -> `Daily EDC MDC Research Update` -> `Run workflow`

Set `report_date` to backfill a day:

```text
2026-07-10
```

The dedupe check still runs, so a backfill will not add papers already in the tracker.

## Notes

- The job can run before your laptop or iPhone is open because GitHub hosts the scheduled runner.
- Your phone only needs Gmail or calendar/email notifications enabled to receive the result.
- If Google credentials are missing or the folder/sheet is not shared with the service account, the job will fail visibly in GitHub Actions instead of silently pretending Drive was updated.
- On failure, the workflow uploads any local Markdown fallback report as a GitHub Actions artifact named `daily-edc-mdc-fallback`.
