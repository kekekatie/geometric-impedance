# How to put this in the world — a durable, citable snapshot

*Goal: get the accretion pilot **timestamped, attributed, and citable** now — the
"bus-proof" step. This is deliberately separate from writing a polished paper: it commits
you to nothing and does not stop the ongoing hunt. Pick **one** path below; Path A works
even if the repository is private and is the fastest.*

## Before you deposit — fill in 3 things (5 minutes)

1. **`CITATION.cff`** — your name (and ORCID if you have one) and a **license**.
   - Common choice for a mixed docs+data+code snapshot: **CC-BY-4.0** for the writeups/data
     and **MIT** for the code, or just CC-BY-4.0 for the whole thing. Your call — but pick
     one, because "no license" legally means "all rights reserved" and discourages reuse.
2. **Authorship representation** — decide how to credit the human-led / AI-collaborated
   nature (see the note at the bottom of `CITATION.cff`). A one-line acknowledgement is
   enough for a deposit.
3. **What to include** — the whole `exploratory/accretion_pilot/` folder is self-contained.
   You can deposit just this folder (Path A) or the whole repo at a tag (Path B).

## Path A — direct Zenodo upload (works for a private repo; immediate DOI)

Zenodo (https://zenodo.org, run by CERN; free) gives every upload a permanent DOI.

1. Make a snapshot archive of just this folder, from the repo root:
   ```bash
   git archive --format=zip -o accretion_pilot_2026-09-08.zip HEAD:exploratory/accretion_pilot
   ```
   *(`git archive` captures exactly the committed state — no stray files. If you'd rather
   include the whole repo, use `git archive --format=zip -o snapshot.zip HEAD`.)*
2. On Zenodo: **New upload** → drag the zip in → set **Upload type: Dataset** (or Software)
   → **Title**, **Authors**, **Description** (paste the top of `OVERVIEW.md`), **License**
   (as chosen above) → **Publish**.
3. Zenodo returns a **DOI** immediately. Put it back into `CITATION.cff` (`doi:` field) and
   `OVERVIEW.md`, commit, and you're done. The DOI is permanent even if the repo changes or
   disappears.

*Reserve-DOI tip:* Zenodo lets you **reserve** the DOI before publishing, so you can write
it into the files first, then publish.

## Path B — GitHub Release → Zenodo (best once the repo is public)

1. Enable the repo in your Zenodo account (Settings → GitHub → flip the repo **On**).
2. Tag and release this exact state:
   ```bash
   git tag -a accretion-pilot-v2026.09.08 -m "Accretion pilot snapshot 2026-09-08" fc973a1
   git push origin accretion-pilot-v2026.09.08
   ```
   Then create a **GitHub Release** from that tag (paste `OVERVIEW.md`'s intro as the notes).
3. Zenodo auto-archives the release and issues a DOI. (Requires the repo be public at
   release time; the tag itself is harmless to push on the current branch now.)

## Later, not now — arXiv

arXiv hosts **papers**, not code snapshots, so it belongs to the write-up stage, not this
one. When the Thread-A synthesis becomes a short preprint (`SYNTHESIS_v1_v14.md` is most of
its spine), submit that PDF to arXiv (likely `cs.DM`/`nlin.CG` or `q-bio` depending on
framing) and cite the Zenodo DOI for the code/data. Two natural preprints eventually: the
**v1–v14 accretion arc**, and the **endogenous-growth grammar** thread — they are different
objects and need not wait for each other.

## Checklist

- [ ] `CITATION.cff`: name, (ORCID), **license** filled in
- [ ] authorship/acknowledgement wording decided
- [ ] DOI minted (Path A or B) and written back into `CITATION.cff` + `OVERVIEW.md`
- [ ] (optional) tag pushed so the git state matches the DOI
- [ ] keep hunting 🌱
