"""
SQLite database operations for BioLitAI
"""

import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
from config import DB_PATH


class BioLitAIDatabase:
    """SQLite database handler for BioLitAI"""

    def __init__(self, db_path: str = str(DB_PATH)):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Papers table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pmid TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                abstract TEXT,
                authors TEXT,
                journal TEXT,
                publication_date TEXT,
                doi TEXT,
                url TEXT,
                summary TEXT,
                entities TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Search queries table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS search_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                results_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Research gaps table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS research_gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_query_id INTEGER,
                gap_type TEXT,
                description TEXT,
                severity TEXT,
                entities TEXT,
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (search_query_id) REFERENCES search_queries(id)
            )
        """
        )

        # Analyses table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_query_id INTEGER,
                analysis_type TEXT,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (search_query_id) REFERENCES search_queries(id)
            )
        """
        )

        conn.commit()
        conn.close()

    def add_paper(self, paper_data: Dict) -> int:
        """
        Add a paper to the database

        Args:
            paper_data: Dictionary with paper information

        Returns:
            ID of inserted paper or None if duplicate
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO papers (pmid, title, abstract, authors, journal, 
                                   publication_date, doi, url, summary, entities)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    paper_data.get("pmid"),
                    paper_data.get("title"),
                    paper_data.get("abstract"),
                    json.dumps(paper_data.get("authors", [])),
                    paper_data.get("journal"),
                    paper_data.get("publication_date"),
                    paper_data.get("doi"),
                    paper_data.get("url"),
                    paper_data.get("summary"),
                    json.dumps(paper_data.get("entities", {})),
                ),
            )
            conn.commit()
            paper_id = cursor.lastrowid
            return paper_id

        except sqlite3.IntegrityError:
            return None

        finally:
            conn.close()

    def add_papers_batch(self, papers_data: List[Dict]) -> int:
        """
        Add multiple papers to the database

        Args:
            papers_data: List of paper dictionaries

        Returns:
            Number of papers added
        """
        added_count = 0
        for paper in papers_data:
            if self.add_paper(paper):
                added_count += 1
        return added_count

    def get_paper(self, pmid: str) -> Optional[Dict]:
        """Get paper by PMID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM papers WHERE pmid = ?", (pmid,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_dict(row, "papers")
        return None

    def get_all_papers(self, limit: int = 100) -> List[Dict]:
        """Get all papers from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM papers ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(row, "papers") for row in rows]

    def record_search_query(self, query: str, results_count: int) -> int:
        """
        Record a search query

        Args:
            query: Search query string
            results_count: Number of results

        Returns:
            ID of search query record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO search_queries (query, results_count) VALUES (?, ?)",
            (query, results_count),
        )
        conn.commit()
        query_id = cursor.lastrowid
        conn.close()

        return query_id

    def add_research_gap(self, search_query_id: int, gap_data: Dict) -> int:
        """Add a research gap to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO research_gaps 
            (search_query_id, gap_type, description, severity, entities, recommendations)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                search_query_id,
                gap_data.get("type"),
                gap_data.get("description"),
                gap_data.get("severity"),
                json.dumps(gap_data.get("entities_involved", [])),
                json.dumps(gap_data.get("recommendations", [])),
            ),
        )
        conn.commit()
        gap_id = cursor.lastrowid
        conn.close()

        return gap_id

    def get_research_gaps(self, search_query_id: int) -> List[Dict]:
        """Get research gaps for a search query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM research_gaps WHERE search_query_id = ? ORDER BY severity DESC",
            (search_query_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(row, "research_gaps") for row in rows]

    def add_analysis(self, search_query_id: int, analysis_type: str, results: Dict) -> int:
        """Add an analysis result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO analyses (search_query_id, analysis_type, results)
            VALUES (?, ?, ?)
        """,
            (search_query_id, analysis_type, json.dumps(results)),
        )
        conn.commit()
        analysis_id = cursor.lastrowid
        conn.close()

        return analysis_id

    def get_analyses(self, search_query_id: int) -> List[Dict]:
        """Get analyses for a search query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM analyses WHERE search_query_id = ? ORDER BY created_at DESC",
            (search_query_id,),
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(row, "analyses") for row in rows]

    def get_recent_searches(self, limit: int = 10) -> List[Dict]:
        """Get recent search queries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, query, results_count, created_at FROM search_queries 
            ORDER BY created_at DESC LIMIT ?
        """,
            (limit,),
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            {"id": row[0], "query": row[1], "results_count": row[2], "created_at": row[3]}
            for row in rows
        ]

    def _row_to_dict(self, row: tuple, table_name: str) -> Dict:
        """Convert database row to dictionary"""
        if table_name == "papers":
            return {
                "id": row[0],
                "pmid": row[1],
                "title": row[2],
                "abstract": row[3],
                "authors": json.loads(row[4]) if row[4] else [],
                "journal": row[5],
                "publication_date": row[6],
                "doi": row[7],
                "url": row[8],
                "summary": row[9],
                "entities": json.loads(row[10]) if row[10] else {},
                "created_at": row[11],
            }
        elif table_name == "research_gaps":
            return {
                "id": row[0],
                "search_query_id": row[1],
                "type": row[2],
                "description": row[3],
                "severity": row[4],
                "entities_involved": json.loads(row[5]) if row[5] else [],
                "recommendations": json.loads(row[6]) if row[6] else [],
                "created_at": row[7],
            }
        elif table_name == "analyses":
            return {
                "id": row[0],
                "search_query_id": row[1],
                "analysis_type": row[2],
                "results": json.loads(row[3]) if row[3] else {},
                "created_at": row[4],
            }

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM papers")
        papers_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM search_queries")
        searches_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM research_gaps")
        gaps_count = cursor.fetchone()[0]

        conn.close()

        return {
            "papers": papers_count,
            "searches": searches_count,
            "research_gaps": gaps_count,
        }
