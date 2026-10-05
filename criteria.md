# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system. The questions and
first three targets were committed before calibration. Criteria 4 and 5 were
AI-drafted at the student's explicit request after implementation and sample
inspection, but **before the ten-question retrieval calibration and Unit 2
acceptance evaluation**. They are not represented as independently
student-written or as predating the starter demonstration.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Each target below includes its test procedure and a corpus-specific reason.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
Run the five `QUESTIONS` in `questions.py` with top-k 5, and read the retrieved
text against the original documents; the `expects` phrases are clues, not a
replacement for checking the full answer. The laundry question needs both a
price and payment methods, and many residence posts contain similar prices,
so 4 of 5 allows one difficult match while requiring coverage of most topics.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
Check every substantive answer to `QUESTIONS`: each must cite at least one
filename from the retrieved chunks in the answer itself. A gate refusal is not
a substantive answer and should not invent a source. Every stored chunk
carries its filename, so requiring a citation for every answer is achievable;
allowing four out of five would leave one piece of student advice untraceable.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
Run each of the five `OUT_OF_SCOPE` questions in `questions.py` once; at least
four must return the refusal without calling the generation function. Retrieval
and the gate are deterministic, so five tries means five distinct questions.
The corpus is limited to campus life, but its computing courses and health
advice may share vocabulary with unrelated questions; 4 of 5 leaves one
borderline match while requiring the gate to stop most unsupported requests.

---

## 4. Chunks preserve complete advice with its topic

At least 9 of the 10 chunks printed by `python app.py chunks -n 10` must
contain the source post's title and at least one complete body sentence,
with no sentence cut off at either boundary, and be no longer than 600
characters including the title. Compare each sample with its named file in
`corpora/campus_life/documents/`; count a chunk as passing only if all four
conditions hold.

**Why this target:** The campus posts separate advice into short paragraphs,
but paragraphs such as "The good" need the residence title to identify their
topic. Requiring 9 of 10 tolerates one awkward paragraph while requiring almost
all samples to preserve sentence context within the chunker's size budget;
requiring fewer would permit several fragments in a small sample.

---

## 5. Cited evidence supports complete answers

For all 5 questions in `QUESTIONS` in `questions.py`, the answer must address
every part of the question, and every factual claim must be explicitly
supported by a retrieved chunk from the filename cited beside that claim.
Compare the answer with its actual retrieved text; a refusal, an omitted
subquestion, an uncited claim, or an unsupported number, time, payment method,
or qualification makes that question fail. The target is 5 of 5 answers.

**Why this target:** Several residences mention similar laundry prices, and
the Morrow House question asks for both the wash price and payment methods;
simply printing a filename does not establish that either detail is supported.
Five of five is stricter than the retrieval target because an unsupported
price or deadline could mislead a student even when most answers are correct.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
