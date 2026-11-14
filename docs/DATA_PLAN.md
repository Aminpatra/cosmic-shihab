# PSI data plan

**Status: the catalogue is built (tasks 0 to 6). Search inside documents (tasks 7 to 10) is
proposed, for the lead's review.**
Everything below was measured against the live PSI API on 14 November 2026.

## What PSI holds for combustion

24 investigations, 60,866 files, 13.5 TB. We download almost none of it.

| Kind of file | Files | Size | What we do with it |
|---|---|---|---|
| Zips and video (`.zip`, `.ts`, `.mp4`, `.avi`, `.mpg`) | 15,313 | 13,427 GB (99.7%) | List and link only |
| Numeric dumps (`.dat`, almost all in SLICE) | 18,292 | 29.9 GB | List and link only |
| Text logs (`.txt`, `.log`, `.asc`) | 19,574 | 1.1 GB | List and link only, for now |
| Tables (`.csv`, `.xls`, `.xlsx`) | 3,842 | 8.7 GB | Only the 22 experimental tables (210 KB) |
| Documents (`.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`, `.rtf`) | 1,926 | 3.3 GB | Index, most reliable investigations first |
| Other | 1,919 | 1.4 GB | List and link only |

Every investigation has a DOI and is public. Every file is active, visible and unrestricted. 23
investigations carry the CC0-1.0 licence; PSI-10 (ACME Flame Design) states no licence, so its
record needs a note saying so until someone confirms it with PSI.

## Which investigations are reliable

PSI publishes a small "Experimental table" for 20 of the 24 investigations: one row per test or
test day, with the conditions. These tables are the only data that is small, structured and
comparable, so they decide how far we can trust each investigation for ranking and for a model.
All 22 tables were downloaded and their sizes match PSI's file list.

**Tier 1: use for ranking, comparison and the model (8 investigations, 1,850 rows)**

| Accession | Investigation | Rows | Columns | Fire-safety role named by the challenge |
|---|---|---|---|---|
| PSI-107 | SPICE | 469 | 9 | |
| PSI-159 | ACME CFI-G (two tables) | 333 | 18 and 20 | Highest oxygen concentrations tested |
| PSI-10 | ACME Flame Design (two tables; no licence stated) | 327 | 15 and 14 | |
| PSI-69 | FLEX | 274 | 15 | Suppression |
| PSI-25 | BASS-II | 129 | 17 | Flammability of solids |
| PSI-26 | BASS | 122 | 6 | Flammability of solids |
| PSI-101 | SAME-R | 109 | 10 | Detection |
| PSI-39 | CFI | 87 | 10 | |

**Tier 2: show and compare, too few rows to model (12 investigations, 159 rows)**

ACME CLD Flame (32), ACME E-FIELD Flames (32), ACME BRE (18), ACME s-Flame (18), SAFFIRE-II (15),
SLICE (12), FLEX-2 (8), SAME (8), PSI-142 cool-flame study (8, an index of published figures, not
tests), SAFFIRE-I (4), SAFFIRE-III (2), DAFT / DAFT-2 (2).

The Saffire investigations matter most to the challenge but have the smallest tables. FLARE shows
them in full and says plainly that they have few rows.

**Tier 3: catalogue only (4 investigations, no table)**

PSI-60, PSI-62, PSI-115 and PSI-117. These are ground-based modelling studies of other
investigations' data. They appear in the explorer with their summary, DOI and links.

Table columns differ between investigations (FLEX gives pressure and gas fractions, BASS gives a
sample and a material). Nothing is merged across investigations unless the columns mean the same
thing.

## How PSI must be read

Four calls. The API is undocumented, so each one fails loudly if the response changes shape.

1. **List:** `GET /geode-py/ws/repo/search?term=combustion&source=psi&type=investigation&from=<offset>`.
   26 hits, 25 per page. Keep `Research Area == "Combustion Science"` (24).
2. **Record:** `GET /geode-py/ws/repo/investigations/<ACCESSION>`. Gives title, acronym, objective,
   hypothesis, approach, DOI, licence, publications, hardware, `version` and `totalFileSize`.
3. **File list:** `POST /geode-py/ws/files/v2` with
   `{"folder":"psi-data/","fileType":"study","studyId":"<ACCESSION>","version":<version>}`.
   This is the only correct file list.
4. **Download link:** `GET /geode-py/ws/studies/<ACCESSION>/download?file=<file name>&redirect=false`.
   Returns a presigned S3 URL as plain text. It expires after about one hour.

Traps found while testing:

- The `added`, `removed` and `modified` lists inside a record are a change log, not the file list.
  Using them counts deleted files and misses whole investigations (FLEX lists one file there and
  has 6,453).
- The file list repeats some entries. De-duplicate by `id`. The record's `totalFileSize` equals
  the sum before de-duplication, in all 24 investigations, which makes it a completeness check.
- Records are slow and large (up to 8 MB and two minutes). One record arrived cut short twice and
  only came through complete with gzip turned on. Ask for gzip, allow a long timeout, check that
  the response parses, and write to a temporary name before renaming.
- The file list fails with "Version Required" without `version`.
- The download link is looked up by file name, not by path.
- The copies in `datasets/` have lost their original line endings, so their size no longer matches
  PSI's. Raw files need `-text` in `.gitattributes`.

## What goes in the repo

| In git | Not in git |
|---|---|
| `backend/data/`: one normalized metadata file per investigation | Any zip, video or `.dat` file |
| `backend/data/`: one file manifest for all 60,866 files (name, category, size, type, version, date) | `.cache/`: the downloaded documents |
| `datasets/`: the 22 experimental tables, unchanged (210 KB) | Presigned download links |
| `pipeline/`: the harvest and index scripts, and their tests | |
| `pipeline/tests/fixtures/`: a few small saved API responses | |

The search index is rebuilt by a script in `pipeline/` and written to `backend/data/`. Everything in
`backend/` ships in the deployed function, which Vercel limits to 500 MB, and GitHub refuses any
single file over 100 MB. Measure the index before committing it.

## Where the code lives

The folder layout (master prompt, section 13) is a proposal for the lead's approval. It follows
how Vercel deploys:

- **`pipeline/`** holds the harvesting and indexing logic. It runs by hand, is never deployed, and
  may use heavy libraries such as PDF readers. The data-strategy prompt asked for `app/services/`;
  that would put this code and its dependencies inside the deployed function.
- **`backend/app/services/`** holds only what runs on a user's request: looking up a download link
  and querying the index.
- **`backend/data/`** is what the pipeline writes and the API reads. The deployed filesystem is
  read-only, so the API never writes there.
- Backend code must run on Python 3.12 to 3.14, the versions Vercel offers.

## Tasks

Each task is one small change with its own check. Tasks 0 to 6 give FLARE a complete, reliable
catalogue and are **done**: the code is in `pipeline/`, the output in `backend/data/` and
`datasets/`, and `python3 -m unittest discover -s pipeline/tests` runs their 15 checks. Tasks 7
to 10 add search inside documents and are not started.

| # | Task | Done when |
|---|---|---|
| 0 | Create `pipeline/` with its test setup; the cache folder `.cache/` is already ignored | One command runs an empty test suite; `git status` ignores a file placed in `.cache/` |
| 1 | Save sample API responses as test fixtures: one search page, two small records, their file lists, one download-link response with its signature removed | The fixtures load in a test |
| 2 | List investigations, with paging and the research-area filter | Test on the fixture returns 24 of 26; a response without `hits.hits` raises an error |
| 3 | Fetch one record safely (gzip, timeout, parse check, rename) | A cut-short fixture raises an error and leaves no file behind |
| 4 | Fetch and flatten one file list, de-duplicated by `id` | Test on a fixture gives the expected count; the sizes before de-duplication add up to the record's `totalFileSize` |
| 5 | Write the normalized metadata and the manifest for all 24 | 24 investigations, 60,866 files, a DOI on every investigation, a licence or "not stated" on each |
| 6 | Download the 22 experimental tables, unchanged | Sizes equal the manifest; 2,009 rows in total |
| 7 | Download documents into the ignored cache: resumable, skips what is cached, at most one request a second to PSI | Running it twice downloads nothing the second time |
| 8 | Extract text and build a keyword index, each chunk tagged with accession and file name | A query on three fixture documents returns the right chunk with its accession and file name |
| 9 | Serve a download link on request, never stored | Test with a faked PSI response; a link to any host other than `psi-repo-prod.s3.amazonaws.com` is refused |
| 10 | Every search result carries title, acronym and DOI | The API response schema test fails without them |

## Open points

- **Embeddings.** Start with a keyword index. Add embeddings only if time remains after the
  catalogue, ranking and demo work.
- **How much to index before the deadline.** Record text and the 22 tables for all 24
  investigations first, then documents for Tier 1.
