# The Unofficial Guide

AlexanderRMT — Unit 1 — `campus_life`

Repository for both units: https://github.com/AlexanderRMT/ai201-project1-unofficial-guide-starter-v2026

## What This Does

The Unofficial Guide searches the 88 student posts in the provided
`campus_life` corpus. It answers questions about housing selection, dining
queues, laundry, courses, and administrative deadlines using local MiniLM
embeddings and a persistent Chroma vector store. A cosine-distance gate rejects
unrelated questions before Gemini is called; accepted questions are answered
from retrieved excerpts with filenames as sources. The documents are fictional
course materials, not claims about Stanford or another real university.

Use **Python 3.11 on Windows**: the starter's pinned `chroma-hnswlib` has a
[Windows wheel for 3.11](https://pypi.org/project/chroma-hnswlib/0.7.6/#files),
whereas attempts with 3.12 and 3.13 here required unavailable C++ build tools.
The existing `.venv` is ready to use. For a fresh clone, install Python 3.11,
then run:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env locally to set GEMINI_API_KEY. Never commit or share the key.
python test.py
python app.py index
python app.py ask "Is the housing lottery random?"
```

Activate the environment in each new terminal. `python app.py ask` starts an
interactive prompt; an empty line exits. `python app.py retrieve "question"`
shows distances without a generation call, and `--show-prompt` on `ask` prints
the exact context and grounding instruction. The complete command reference is
[RUNNING.md](RUNNING.md), which is unchanged. A SOCKS proxy in this development
environment also needed `python -m pip install "socksio>=1,<2"`; this is only
necessary if the SDK reports missing SOCKS support.

The environment check passed all 10 checks, including real embeddings and a
Gemini request. Run `python -m unittest discover -s tests -v` for the eight
deterministic regression tests. They check text preservation, chunk boundaries,
and the gate's control flow; they are not Unit 2 acceptance results.

Scope: required Unit 1 features. No optional stretch features are claimed.

## Chunking Strategy

**Chunk size:** one titled body paragraph, with a soft ceiling of **600
characters including the title**. **Overlap:** **0 body characters**; the
source title is repeated in each chunk. A paragraph over the ceiling is packed
into complete sentences; a single oversized sentence remains whole even if it
exceeds 600 characters. This fallback is not needed for the selected corpus.

The strategy was recorded before implementation. In
`dining_kestrel_commons.txt`, the queue/food advice is separate from the
hours/prices paragraph. `housing_old_brewhouse.txt` separates its description,
advantages, heating problems, and laundry/noise. `course_cs_210.txt` separates
assessment, workload, and lab advice. Keeping these paragraph boundaries makes
each chunk more focused; the repeated title identifies the place or course.
The housing-lottery explanation stays together because the sophomore versus
upperclassman distinction is contained in one paragraph.

The starter's 800-character windows with 120 overlap made **88 chunks from 88
documents**, averaging **317 characters** (178–549). Inspection found **183
body paragraphs**, none longer than **397 characters with its title**. The
600-character ceiling leaves room for complete explanatory paragraphs; it is
a safeguard, while the observed paragraph structure determines the actual
boundaries. The replacement makes **183 chunks**, averaging **167 characters**
(63–397). Zero body overlap avoids duplicating short advice paragraphs in the
top five results. Repeating a title does not restore every preceding detail,
so references to earlier advice remain a limitation to inspect in Unit 2.

`ingest.py::clean_text` normalizes line endings, repeated whitespace, and blank
lines. These provided text files are already free of navigation/advertising
markup; their titles, qualifications, and student reports are retained.
`chunker.py::fallback_split` remains available for comparison: pass
`chunk_size=800, overlap=120` to reproduce the starter settings. Baseline
observations and the original live answer are in
[results/unit1_baseline.txt](results/unit1_baseline.txt).

The required special activity number, measured before replacing the chunker
with `python app.py --corpus advice_threads chunks -n 1`, is **26**.

## Sample Chunks

Exact output texts from `python app.py chunks -n 5`, sampled at positions
0, 36, 72, 108, and 144. Each is produced by `chunker.py::split_documents`.

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — function: `chunker.py::split_documents`

```text
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_cs_340_exams.txt#1` — function: `chunker.py::split_documents`

```text
CS 340 Databases — assessment

Start the term project in week three, not week eight; everyone learns this the hard way.
```

**Chunk 3** — source: `course_phys_130_workload.txt#0` — function: `chunker.py::split_documents`

```text
Workload for PHYS 130 Mechanics

People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time, not optimistic time.
```

**Chunk 4** — source: `dining_verrill_street_grill_followup.txt#1` — function: `chunker.py::split_documents`

```text
Re: Verrill Street Grill

Also worth saying: one register, so the queue is a single line no matter how busy. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_morrow_house.txt#1` — function: `chunker.py::split_documents`

```text
Morrow House — what it's actually like

The good: cheapest housing tier by about $900 a year, and the singles are real singles.
```

The five chunks can independently answer questions about late-drop
transcript marks, when to start the CS 340 project, PHYS 130 workload, the
Verrill Street Grill queue layout, and Morrow House pricing/room type.

## Sample Answer

**Question:** Is the housing lottery random?

**Answer:** Actual Gemini output after rebuilding the paragraph index and
tightening `generate.py::GROUNDING_INSTRUCTION`:

```text
The housing lottery is not entirely random in the way most people assume: rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, with random tie-breaking used only for ties (admin_housing_lottery.txt).

Sources retrieved: admin_housing_lottery.txt, admin_parking_permits.txt, advising_registration.txt, housing_innisfree_hall.txt, housing_morrow_house.txt
```

The answer cites `admin_housing_lottery.txt`; the separate retrieved-sources
line lists all candidate documents, not a claim that every document supports
the answer. [results/unit1_sample_answer.txt](results/unit1_sample_answer.txt)
contains the full prompt and output. The system instruction requires a source
for each factual claim, preservation of numbers and exceptions, and an honest
refusal if the excerpts cannot answer the question. It treats source text as
evidence rather than instructions. This reduces unsupported answers but is not
a proof of factual grounding.

**Retrieval:** `all-MiniLM-L6-v2`, 384 dimensions, Chroma cosine distance, top-k
**5**. `gate.check` runs before generation: empty results or a best distance
greater than or equal to the cutoff return exactly
`I don't have enough information about that.` without a model call. The gate
uses the best match; the grounding instruction still needs to distinguish
supporting evidence from other retrieved material.

**Cutoff status:** currently the starter's **0.6**, pending calibration. The
five in-corpus and five out-of-scope distances have deliberately not been
collected yet: the two student-authored criteria must first be committed.
`python calibrate.py` will record all ten distances and all retrieved chunks
in `results/unit1_retrieval.json` without calling Gemini. After selecting a
cutoff from those measurements, this section must include the ten-row table
and the observed ranges. This is the remaining Milestone 4 requirement.

## How I Used AI

**1. Building from the assignment.** I asked Codex to complete the assignment
to the full specifications. It inspected the corpus and proposed paragraph
chunks with repeated titles, replacing the starter's fixed windows; the
resulting implementation preserves each of the 183 body paragraphs and adds
regression tests for long sentences and gate refusals. Codex performed these
code changes and checks, rather than me independently writing that code. It
also strengthened the grounding instruction after reading the starter prompt.

**2. Changing the commit workflow.** I then explicitly asked Codex to commit
often, keep commits small and scoped, and use only me as the Git author. It
changed the workflow to record the corpus plan, questions, supplied-criterion
explanations, baseline evidence, chunker/tests, grounding instruction, and
calibration command in separate commits. No co-author attribution was added.
I subsequently explicitly asked Codex to draft criteria 4 and 5 too. Those
criteria are AI-assisted, despite the assignment's request for student-written
criteria, and were committed before retrieval calibration but after the
chunker and sample answer existed. This disclosure preserves the actual
sequence rather than claiming independent authorship.

Unit 2 has not been performed. Keep this repository and the original criteria;
use `python run_eval.py --label before` in the next unit, then diagnose a miss,
attempt one improvement, and retain both sets of evidence. Submit the fork URL
above through the Course Portal after the pending criteria and calibration
are finished.
