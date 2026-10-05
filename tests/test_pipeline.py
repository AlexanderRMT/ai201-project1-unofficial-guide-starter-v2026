"""Deterministic regression checks; these are not Unit 2 acceptance results."""

import unittest
from unittest.mock import patch

import config
from chunker import split_documents
from ingest import Document, clean_text, load_documents


class ChunkingTests(unittest.TestCase):
    def test_paragraphs_keep_their_title_and_complete_body(self):
        doc = Document("dining.txt", "Commons\n\nLunch takes twenty minutes.\n\nDinner costs $12.50.")
        chunks = split_documents([doc])
        self.assertEqual([c.text for c in chunks], [
            "Commons\n\nLunch takes twenty minutes.",
            "Commons\n\nDinner costs $12.50.",
        ])
        self.assertEqual([c.label for c in chunks], ["dining.txt#0", "dining.txt#1"])
        self.assertTrue(all(c.produced_by == "chunker.py::split_documents" for c in chunks))

    def test_long_paragraph_splits_between_sentences(self):
        sentences = ["The library opens early.", "The dining hall closes late.", "The bus runs hourly."]
        with patch.object(config, "CHUNK_SIZE", 50):
            chunks = split_documents([Document("guide.txt", "Campus\n\n" + " ".join(sentences))])
        self.assertEqual([c.text.split("\n\n", 1)[1] for c in chunks], sentences)

    def test_oversized_single_sentence_is_never_truncated(self):
        sentence = "An unusually long explanation " + "with context " * 20 + "ends here."
        with patch.object(config, "CHUNK_SIZE", 60):
            chunks = split_documents([Document("long.txt", "Title\n\n" + sentence)])
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].text, "Title\n\n" + sentence)

    def test_empty_and_untitled_documents(self):
        chunks = split_documents([Document("empty.txt", "  \n\n"), Document("plain.txt", "One complete thought.")])
        self.assertEqual([c.text for c in chunks], ["One complete thought."])

    def test_cleaning_preserves_paragraph_structure(self):
        self.assertEqual(clean_text("Title\r\n\r\n\r\nA  sentence.\t\tMore.\r\n"),
                         "Title\n\nA sentence. More.")

    def test_corpus_preserves_every_body_paragraph(self):
        for doc in load_documents("campus_life"):
            chunks = split_documents([doc])
            title, *paragraphs = doc.text.split("\n\n")
            with self.subTest(source=doc.source):
                self.assertEqual([c.text for c in chunks], [title + "\n\n" + p for p in paragraphs])


class GateTests(unittest.TestCase):
    def test_empty_far_and_boundary_results_do_not_call_the_model(self):
        import gate
        from app import ask_pipeline
        from store import Result

        for distance in (None, 0.9, config.THRESHOLD):
            hits = [] if distance is None else [Result("Text", "source.txt", "source.txt#0", distance, "test")]
            with self.subTest(distance=distance), patch("store.search", return_value=hits), \
                    patch("generate.answer_from_chunks") as generate_answer:
                outcome = ask_pipeline("An unsupported question")
                self.assertTrue(outcome["refused"])
                self.assertEqual(outcome["answer"], gate.REFUSAL)
                self.assertEqual(outcome["sources"], [])
                self.assertIsNone(outcome["prompt"])
                generate_answer.assert_not_called()

    def test_a_close_result_passes_and_reaches_generation(self):
        from app import ask_pipeline
        from store import Result

        hits = [Result("The wash costs $1.50.", "laundry.txt", "laundry.txt#0", 0.1, "test")]
        with patch("store.search", return_value=hits), \
                patch("generate.answer_from_chunks", return_value="A wash costs $1.50 (laundry.txt).") as generate_answer:
            outcome = ask_pipeline("What does a wash cost?")
        self.assertFalse(outcome["refused"])
        self.assertEqual(outcome["sources"], ["laundry.txt"])
        generate_answer.assert_called_once()


if __name__ == "__main__":
    unittest.main()
