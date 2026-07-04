"""
Research Gap Detection using NLP and AI analysis
"""

from typing import Dict, List, Set
from collections import Counter
import re


class ResearchGapDetector:
    """Detect potential research gaps from literature analysis"""

    def __init__(self):
        """Initialize gap detector"""
        self.gap_indicators = {
            "limited": [
                "limited",
                "few",
                "lack of",
                "unclear",
                "unknown",
                "not well understood",
            ],
            "missing": ["no studies", "no data", "not yet", "further research needed"],
            "contradictory": [
                "conflicting",
                "contradictory",
                "inconsistent",
                "controversial",
            ],
            "emerging": ["novel", "new", "emerging", "recent", "unexplored"],
        }

        self.research_areas = [
            "diagnosis",
            "treatment",
            "prognosis",
            "epidemiology",
            "pathophysiology",
            "drug response",
            "biomarkers",
            "genetics",
            "mechanisms",
        ]

    def detect_gaps(self, papers_data: List[Dict]) -> Dict:
        """
        Detect research gaps from a collection of papers

        Args:
            papers_data: List of paper data with abstracts and entities

        Returns:
            Dictionary containing identified gaps and recommendations
        """
        gaps = {
            "content_gaps": [],
            "methodology_gaps": [],
            "population_gaps": [],
            "temporal_gaps": [],
            "geographic_gaps": [],
            "recommendations": [],
        }

        if not papers_data:
            return gaps

        # Analyze papers for gaps
        all_diseases = set()
        all_genes = set()
        all_drugs = set()
        all_methods = set()
        gap_indicators_found = Counter()

        for paper in papers_data:
            abstract = paper.get("abstract", "").lower()
            entities = paper.get("entities", {})

            # Collect entities
            all_diseases.update(entities.get("diseases", []))
            all_genes.update(entities.get("genes", []))
            all_drugs.update(entities.get("drugs", []))
            all_methods.update(entities.get("methods", []))

            # Look for gap indicators
            for gap_type, indicators in self.gap_indicators.items():
                for indicator in indicators:
                    if indicator in abstract:
                        gap_indicators_found[gap_type] += 1

        # Generate content gaps
        gaps["content_gaps"] = self._analyze_content_gaps(
            all_diseases, all_genes, all_drugs, gap_indicators_found
        )

        # Generate methodology gaps
        gaps["methodology_gaps"] = self._analyze_methodology_gaps(all_methods)

        # Generate recommendations
        gaps["recommendations"] = self._generate_recommendations(
            all_diseases, all_genes, gaps["content_gaps"]
        )

        return gaps

    def _analyze_content_gaps(
        self,
        diseases: Set,
        genes: Set,
        drugs: Set,
        gap_indicators: Counter,
    ) -> List[Dict]:
        """Analyze content-related research gaps"""
        gaps = []

        # Gap 1: Limited disease coverage
        if len(diseases) < 5:
            gaps.append(
                {
                    "type": "Limited Disease Coverage",
                    "description": f"Only {len(diseases)} diseases studied. Expand to related conditions.",
                    "severity": "high" if len(diseases) < 3 else "medium",
                    "entities_involved": list(diseases)[:3],
                }
            )

        # Gap 2: Few gene-drug associations
        if len(genes) > 0 and len(drugs) < len(genes) * 0.5:
            gaps.append(
                {
                    "type": "Incomplete Gene-Drug Associations",
                    "description": f"Only {len(drugs)} drugs for {len(genes)} genes. Need more pharmacogenetic studies.",
                    "severity": "medium",
                    "entities_involved": list(genes)[:3],
                }
            )

        # Gap 3: Gap indicators found
        if gap_indicators["limited"] > 0 or gap_indicators["missing"] > 0:
            gaps.append(
                {
                    "type": "Understudied Areas",
                    "description": f"Literature mentions {gap_indicators['limited'] + gap_indicators['missing']} areas with limited research.",
                    "severity": "high",
                    "recommendations": "Conduct original research in these understudied areas",
                }
            )

        return gaps

    def _analyze_methodology_gaps(self, methods: Set) -> List[Dict]:
        """Analyze methodology-related research gaps"""
        gaps = []

        common_methods = {
            "sequencing",
            "microscopy",
            "pcr",
            "mass spectrometry",
            "computational",
        }
        used_methods = methods & common_methods
        unused_methods = common_methods - used_methods

        if len(unused_methods) > 0:
            gaps.append(
                {
                    "type": "Unexplored Methodologies",
                    "description": f"Potential methods not yet applied: {', '.join(unused_methods)}",
                    "severity": "medium",
                    "suggestions": list(unused_methods),
                }
            )

        if len(methods) < 3:
            gaps.append(
                {
                    "type": "Limited Methodological Diversity",
                    "description": "Few different methods used. Consider multi-method approaches.",
                    "severity": "low",
                }
            )

        return gaps

    def _generate_recommendations(
        self, diseases: Set, genes: Set, content_gaps: List[Dict]
    ) -> List[str]:
        """Generate research recommendations based on gaps"""
        recommendations = []

        if len(diseases) > 0:
            disease_list = list(diseases)[:3]
            recommendations.append(
                f"Investigate mechanisms of {disease_list[0]} in underexplored populations"
            )

        if len(genes) > 0:
            gene_list = list(genes)[:3]
            recommendations.append(
                f"Conduct genome-wide association study (GWAS) focusing on {gene_list[0]}"
            )

        if any(gap["type"] == "Incomplete Gene-Drug Associations" for gap in content_gaps):
            recommendations.append(
                "Perform pharmacogenetic studies to identify gene-drug interactions"
            )

        recommendations.extend(
            [
                "Develop novel biomarkers for early disease detection",
                "Conduct longitudinal studies to track disease progression",
                "Perform meta-analysis of existing studies to identify patterns",
                "Investigate environmental factors in disease pathogenesis",
                "Design clinical trials for novel therapeutic approaches",
            ]
        )

        return recommendations[:5]

    def identify_collaborative_opportunities(self, papers_data: List[Dict]) -> List[Dict]:
        """
        Identify potential collaborative research opportunities

        Args:
            papers_data: List of paper data

        Returns:
            List of collaboration opportunities
        """
        opportunities = []

        # Extract all institutions/authors
        all_authors = []
        for paper in papers_data:
            all_authors.extend(paper.get("authors", []))

        author_counts = Counter(all_authors)
        frequent_authors = author_counts.most_common(5)

        # Identify research clusters
        opportunities.append(
            {
                "type": "Author Collaboration",
                "description": f"Top researchers in field: {[a[0] for a in frequent_authors]}",
                "potential_benefit": "Network with leading researchers",
            }
        )

        return opportunities

    def get_future_research_directions(self, papers_data: List[Dict]) -> List[str]:
        """
        Suggest future research directions based on literature trends

        Args:
            papers_data: List of paper data

        Returns:
            List of suggested research directions
        """
        directions = [
            "Personalized medicine approaches based on genetic profiles",
            "Integration of multi-omics data (genomics, proteomics, metabolomics)",
            "Artificial intelligence-assisted diagnosis and prognosis",
            "Real-world evidence studies using electronic health records",
            "Precision prevention strategies for at-risk populations",
            "Development of patient-derived models for drug testing",
            "Immunotherapy combinations for resistant cases",
            "Long-term outcome studies with quality of life measures",
        ]

        # Filter based on content
        if len(papers_data) > 0:
            recent_papers = [
                p
                for p in papers_data
                if int(p.get("publication_date", "2000") or "2000") >= 2020
            ]
            if recent_papers:
                return directions[:5]

        return directions
