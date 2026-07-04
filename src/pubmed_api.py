"""
PubMed API wrapper for searching and fetching biomedical literature
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import time
from config import PUBMED_SEARCH_URL, PUBMED_FETCH_URL, PUBMED_EMAIL, PUBMED_API_KEY


class PubMedAPI:
    """Wrapper for NCBI PubMed API"""

    def __init__(self, email: str = PUBMED_EMAIL, api_key: str = PUBMED_API_KEY):
        """
        Initialize PubMed API client

        Args:
            email: Email address for NCBI Entrez (required)
            api_key: Optional API key for higher rate limits
        """
        self.email = email
        self.api_key = api_key
        self.session = requests.Session()

    def _get_params(self, additional_params: Dict = None) -> Dict:
        """Build common parameters for API requests"""
        params = {
            "tool": "BioLitAI",
            "email": self.email,
        }
        if self.api_key:
            params["api_key"] = self.api_key
        if additional_params:
            params.update(additional_params)
        return params

    def search(
        self, query: str, max_results: int = 100, sort: str = "relevance"
    ) -> List[str]:
        """
        Search PubMed for papers

        Args:
            query: Search query (MeSH terms or free text)
            max_results: Maximum number of results to return
            sort: Sort order ('relevance' or 'pub_date')

        Returns:
            List of PubMed IDs (PMIDs)
        """
        try:
            params = self._get_params(
                {
                    "db": "pubmed",
                    "term": query,
                    "retmax": max_results,
                    "rettype": "json",
                    "sort": sort,
                }
            )

            response = self.session.get(PUBMED_SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            pmids = data.get("esearchresult", {}).get("idlist", [])
            return pmids

        except requests.RequestException as e:
            print(f"Error searching PubMed: {e}")
            return []

    def fetch_papers(self, pmids: List[str]) -> List[Dict]:
        """
        Fetch paper details from PubMed

        Args:
            pmids: List of PubMed IDs

        Returns:
            List of dictionaries containing paper information
        """
        if not pmids:
            return []

        papers = []
        # Fetch in batches to avoid overwhelming the server
        batch_size = 10
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i : i + batch_size]
            papers.extend(self._fetch_batch(batch))
            time.sleep(0.5)  # Rate limiting

        return papers

    def _fetch_batch(self, pmids: List[str]) -> List[Dict]:
        """Fetch a batch of papers"""
        try:
            params = self._get_params(
                {
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "rettype": "xml",
                    "retmode": "xml",
                }
            )

            response = self.session.get(PUBMED_FETCH_URL, params=params, timeout=10)
            response.raise_for_status()

            papers = self._parse_xml_response(response.text)
            return papers

        except requests.RequestException as e:
            print(f"Error fetching papers: {e}")
            return []

    def _parse_xml_response(self, xml_text: str) -> List[Dict]:
        """Parse XML response from PubMed"""
        papers = []
        try:
            root = ET.fromstring(xml_text)

            for article in root.findall(".//PubmedArticle"):
                paper = self._extract_article_info(article)
                if paper:
                    papers.append(paper)

        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")

        return papers

    def _extract_article_info(self, article: ET.Element) -> Optional[Dict]:
        """Extract relevant information from an article element"""
        try:
            # Get PMID
            pmid = article.findtext(".//PMID")
            if not pmid:
                return None

            # Get title
            title = article.findtext(".//ArticleTitle", "")

            # Get abstract
            abstract_text = article.findtext(".//AbstractText", "")

            # Get authors
            authors = []
            for author in article.findall(".//Author"):
                last_name = author.findtext("LastName", "")
                first_name = author.findtext("ForeName", "")
                if last_name:
                    authors.append(f"{first_name} {last_name}".strip())

            # Get publication date
            pub_date = article.findtext(".//PubDate/Year", "")
            pub_month = article.findtext(".//PubDate/Month", "")
            if pub_month:
                pub_date = f"{pub_month}/{pub_date}"

            # Get journal
            journal = article.findtext(".//Journal/Title", "")

            # Get DOI
            doi = article.findtext(".//ELocationID[@EIdType='doi']", "")

            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract_text,
                "authors": authors,
                "journal": journal,
                "publication_date": pub_date,
                "doi": doi,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            }

        except Exception as e:
            print(f"Error extracting article info: {e}")
            return None

    def get_paper_details(self, pmid: str) -> Optional[Dict]:
        """Get detailed information for a single paper"""
        papers = self._fetch_batch([pmid])
        return papers[0] if papers else None
