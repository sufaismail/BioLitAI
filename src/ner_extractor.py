"""
Named Entity Recognition (NER) for extracting biomedical entities
"""

import spacy
from typing import Dict, List, Set
from config import NER_MODEL


class BiomedicalNERExtractor:
    """Extract biomedical entities from text using spaCy"""

    def __init__(self):
        """Initialize the NER model"""
        try:
            self.nlp = spacy.load(NER_MODEL)
        except OSError:
            print(f"Model {NER_MODEL} not found. Please download it using:")
            print(f"python -m spacy download {NER_MODEL}")
            self.nlp = None

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract biomedical entities from text

        Args:
            text: Input text (usually abstract or paper content)

        Returns:
            Dictionary mapping entity types to lists of entities
        """
        if not self.nlp or not text:
            return {
                "diseases": [],
                "genes": [],
                "drugs": [],
                "methods": [],
                "organisms": [],
            }

        try:
            doc = self.nlp(text)

            entities = {
                "diseases": [],
                "genes": [],
                "drugs": [],
                "methods": [],
                "organisms": [],
            }

            # Extract entities based on label
            for ent in doc.ents:
                text_lower = ent.text.lower()

                if ent.label_ == "DISEASE":
                    entities["diseases"].append(ent.text)
                elif ent.label_ in ["GENE", "PROTEIN"]:
                    entities["genes"].append(ent.text)
                elif ent.label_ in ["CHEMICAL", "DRUG"]:
                    entities["drugs"].append(ent.text)
                elif ent.label_ == "GPE":
                    # Use GPE for organisms in biomedical context
                    if any(
                        org in text_lower for org in ["virus", "bacteria", "fungi"]
                    ):
                        entities["organisms"].append(ent.text)

            # Post-process: remove duplicates and normalize
            for key in entities:
                entities[key] = list(set(entities[key]))
                entities[key].sort()

            # Extract methods using keyword matching
            entities["methods"] = self._extract_methods(text)

            return entities

        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {
                "diseases": [],
                "genes": [],
                "drugs": [],
                "methods": [],
                "organisms": [],
            }

    def _extract_methods(self, text: str) -> List[str]:
        """Extract research methods using keyword matching"""
        methods_keywords = {
            "sequencing": ["sequencing", "rna-seq", "dna-seq", "whole genome"],
            "microscopy": ["microscopy", "electron microscopy", "confocal"],
            "crystallography": ["crystallography", "x-ray"],
            "mass spectrometry": ["mass spectrometry", "ms/ms"],
            "pcr": ["pcr", "qpcr", "real-time pcr"],
            "immunoassay": ["elisa", "immunoassay", "western blot"],
            "flow cytometry": ["flow cytometry"],
            "computational": ["machine learning", "deep learning", "neural network"],
        }

        found_methods = set()
        text_lower = text.lower()

        for method, keywords in methods_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_methods.add(method)
                    break

        return sorted(list(found_methods))

    def extract_from_abstract(self, title: str, abstract: str) -> Dict[str, List[str]]:
        """
        Extract entities from paper title and abstract

        Args:
            title: Paper title
            abstract: Paper abstract

        Returns:
            Dictionary of extracted entities
        """
        combined_text = f"{title}. {abstract}"
        return self.extract_entities(combined_text)

    def get_unique_entities(self, papers_data: List[Dict]) -> Dict[str, Set[str]]:
        """
        Get unique entities across multiple papers

        Args:
            papers_data: List of paper data with extracted entities

        Returns:
            Dictionary mapping entity types to sets of unique entities
        """
        unique_entities = {
            "diseases": set(),
            "genes": set(),
            "drugs": set(),
            "methods": set(),
            "organisms": set(),
        }

        for paper in papers_data:
            entities = paper.get("entities", {})
            for entity_type, values in entities.items():
                if entity_type in unique_entities:
                    unique_entities[entity_type].update(values)

        # Convert sets to sorted lists
        return {k: sorted(list(v)) for k, v in unique_entities.items()}
