# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A personal music data pipeline that extracts playlist data from Spotify (via API) and SoundCloud (via web scraping), loads it to Google Cloud Storage and BigQuery, then transforms it with dbt. Dagster orchestrates the pipeline.

## Environment Setup

```bash
virtualenv ./venv
./venv/scripts/activate
pip install -r requirements.txt
pre-commit install
```

Requires a `.env` file with:
- `USERNAME` — Spotify username
- `CLIENT_ID` / `CLIENT_SECRET` — from Spotify Developer Dashboard
- `REDIRECT_URI` — set in the Spotify app settings

Google Cloud credentials go in `util/cred/jordans-cred.json` (service account JSON).

## Running the Pipeline

**Launch the Dagster UI** (entry point is `dagster_spotify_job.py` via `pyproject.toml`):
```bash
dagit
# or
dagster-webserver
```

The `playlist_job` runs three ops in sequence: `save_soundcloud` → `save_spotify` → `gcs_bq_google`.

**Run dbt transformations** (from `dbt/jordans_music/`):
```bash
dbt run          # run all models
dbt test         # run tests
dbt seed         # load CSV seeds
dbt docs generate && dbt docs serve
```

## Code Architecture

### Data Flow
1. **Extract**: `util/spotify_songs.py` (`GetSpotifyPlaylist`) calls the Spotify API via `spotipy`. `util/soundcloud_songs.py` (`GetSoundCloud`) uses Selenium + BeautifulSoup to scrape SoundCloud.
2. **Stage locally**: CSVs written to `data/spotify/` and `data/soundcloud/` with date-stamped filenames.
3. **Load to GCS/BQ**: `util/gcs.py` (`LoadData`) uploads date-stamped CSVs to GCS, merges all historical CSVs per source into a staging CSV, then loads staging to BigQuery using schemas defined in `schemas/playlist_schemas.py`.
4. **Transform**: dbt models in `dbt/jordans_music/models/` — `staging/` deduplicates by `track_id`, `marts/` produces aggregations like top 10 artists.

### Key Files
- `dagster_spotify_job.py` — Dagster job/ops definition; the main orchestration entry point
- `util/spotify_songs.py` — Spotify API client (handles pagination for playlists >100 tracks)
- `util/soundcloud_songs.py` — SoundCloud scraper (requires Chrome + chromedriver)
- `util/gcs.py` — GCS and BigQuery loader; `merge_playlists()` concatenates all historical uploads
- `schemas/playlist_schemas.py` — BigQuery table schemas for Spotify and SoundCloud

### dbt Structure
- `models/staging/staging_music/` — deduplication using `row_number()` window functions
- `models/marts/` — final aggregations (top 10 artists per source)
- Target BigQuery project: `jordans-music-343121`, dataset: `music`

## Linting & Formatting

Pre-commit runs automatically on commit:
- **black** (line length 100)
- **flake8** (max line length 150, F401 ignored)

Manual runs:
```bash
black --line-length=100 .
flake8 --config=setup.cfg .
```
