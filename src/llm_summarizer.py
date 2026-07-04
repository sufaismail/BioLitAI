"""
LLM-based summarization using Hugging Face Transformers
"""

from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from typing import Optional
import torch
from config import LLM_MODEL, LLM_MAX_LENGTH, LLM_TEMPERATURE, LLM_DEVICE


class BiomedicalSummarizer:
    """Summarize biomedical papers using Mistral-7B"""

    def __init__(self, model_id: str = LLM_MODEL):
        """
        Initialize the summarizer with Mistral-7B

        Args:
            model_id: Hugging Face model ID
        """
        self.model_id = model_id
        self.device = self._get_device()

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float32,
                device_map=self.device,
            )
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
            )
        except Exception as e:
            print(f"Error loading model: {e}")
            print(f"Using fallback summarizer...")
            self.pipeline = None
            self.model = None
            self.tokenizer = None

    def _get_device(self) -> str:
        """Determine device (cuda or cpu)"""
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def summarize(self, abstract: str, title: str = "", max_length: int = 150) -> str:
        """
        Summarize a paper abstract

        Args:
            abstract: Paper abstract text
            title: Paper title (optional)
            max_length: Maximum length of summary

        Returns:
            Summarized text
        """
        if not abstract or len(abstract.strip()) < 50:
            return abstract

        try:
            if self.pipeline:
                return self._summarize_with_llm(abstract, title, max_length)
            else:
                return self._fallback_summarize(abstract, max_length)

        except Exception as e:
            print(f"Error in summarization: {e}")
            return self._fallback_summarize(abstract, max_length)

    def _summarize_with_llm(
        self, abstract: str, title: str, max_length: int
    ) -> str:
        """Summarize using LLM"""
        prompt = f"""Summarize the following biomedical research abstract in {max_length} words or less. 
Focus on key findings and methods.

Title: {title}
Abstract: {abstract}

Summary:"""

        try:
            result = self.pipeline(
                prompt,
                max_length=max_length + 100,
                num_return_sequences=1,
                temperature=LLM_TEMPERATURE,
                do_sample=True,
                truncation=True,
            )

            summary = result[0]["generated_text"]
            # Extract only the summary part (after "Summary:")
            if "Summary:" in summary:
                summary = summary.split("Summary:")[-1].strip()

            return summary[:max_length * 4]  # Approximate character limit

        except Exception as e:
            print(f"LLM summarization error: {e}")
            return self._fallback_summarize(abstract, max_length)

    def _fallback_summarize(self, abstract: str, max_length: int) -> str:
        """
        Fallback summarization using extractive method

        Args:
            abstract: Text to summarize
            max_length: Maximum length of summary

        Returns:
            Summarized text
        """
        sentences = abstract.split(".")
        summary_sentences = []
        current_length = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                sentence_length = len(sentence.split())
                if current_length + sentence_length <= max_length:
                    summary_sentences.append(sentence)
                    current_length += sentence_length

        return ". ".join(summary_sentences) + "."

    def summarize_batch(
        self, papers: list, max_length: int = 150
    ) -> list:
        """
        Summarize multiple papers

        Args:
            papers: List of paper dictionaries with 'abstract' and 'title' keys
            max_length: Maximum length of each summary

        Returns:
            List of papers with added 'summary' key
        """
        for paper in papers:
            abstract = paper.get("abstract", "")
            title = paper.get("title", "")
            paper["summary"] = self.summarize(abstract, title, max_length)

        return papers

    def extract_key_points(self, abstract: str) -> list:
        """
        Extract key points from abstract

        Args:
            abstract: Paper abstract

        Returns:
            List of key points
        """
        if not abstract:
            return []

        try:
            prompt = f"""Extract 3-5 key points from this biomedical abstract:

Abstract: {abstract}

Key points:
1."""

            result = self.pipeline(
                prompt,
                max_length=200,
                num_return_sequences=1,
                temperature=0.5,
                truncation=True,
            )

            text = result[0]["generated_text"]
            if "Key points:" in text:
                points_text = text.split("Key points:")[-1].strip()
                points = [
                    p.strip().lstrip("0123456789.- ")
                    for p in points_text.split("\n")
                    if p.strip()
                ]
                return points[:5]

        except Exception as e:
            print(f"Error extracting key points: {e}")

        return []
