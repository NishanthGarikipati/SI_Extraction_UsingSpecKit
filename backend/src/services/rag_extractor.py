"""
RAG (Retrieval-Augmented Generation) metadata extraction using Ollama and LLaMA 2
"""
import json
import logging
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime
import re
import uuid
import httpx

from src.config import get_settings
from src.models.metadata import ExtractedMetadata, Author, Affiliation, ConfidenceScores


logger = logging.getLogger(__name__)
settings = get_settings()


class OllamaConnectionError(Exception):
    """Raised when connection to Ollama fails."""
    pass


class ExtractionTimeoutError(Exception):
    """Raised when extraction times out."""
    pass


class MetadataExtractionError(Exception):
    """Raised when metadata extraction fails."""
    pass


class RAGExtractor:
    """Extracts academic metadata from PDFs using RAG with Ollama/LLaMA 2."""
    
    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.model = settings.ollama_model
        self.timeout = settings.extraction_timeout_seconds
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load extraction prompt template."""
        template = """You are an expert academic metadata extractor. Your task is to extract key metadata from the provided PDF text.

IMPORTANT: Extract ONLY information present in the text. Do NOT make up or assume values.

PDF Text:
{text}

Please extract and return valid JSON with the following fields:
- title (string, required): The article/paper title. Extract from the beginning of the text.
- doi (string, optional): Digital Object Identifier in format 10.xxxx/xxxx
- abstract (string, optional): The paper's abstract or summary
- keywords (array of strings, optional): Keywords or tags related to the paper
- publication_date (string, optional): Publication date in ISO 8601 format (YYYY-MM-DD)
- journal (string, optional): Name of the journal or conference
- authors (array, optional): List of authors with their details. Each author should have: name (required), email (optional), orcid (optional)
- affiliations (array, optional): Institutional affiliations mentioned. Each should have: institution (required), department (optional), city (optional), country (optional)
- confidence_scores (object): Your confidence level (0.0-1.0) for each extracted field

CRITICAL RULES:
1. If a field is not found in the text, set it to null (not a default value)
2. For confidence_scores, use 0.0-1.0 based on how confident you are that the extracted value is correct
3. Return ONLY valid JSON with no additional text before or after
4. Ensure all values in confidence_scores are between 0.0 and 1.0

Example format:
{
    "title": "Extracted title from text",
    "doi": "10.xxxx/xxxx",
    "abstract": "The abstract text",
    "keywords": ["keyword1", "keyword2"],
    "publication_date": "2024-05-01",
    "journal": "Journal Name",
    "authors": [
        {{"name": "John Doe", "email": "john@example.com", "orcid": null}},
        {{"name": "Jane Smith", "email": null, "orcid": null}}
    ],
    "affiliations": [
        {{"institution": "MIT", "department": "CSAIL", "city": "Cambridge", "country": "USA"}}
    ],
    "confidence_scores": {
        "title": 0.95,
        "doi": 0.80,
        "abstract": 0.90,
        "keywords": 0.85,
        "publication_date": 0.70,
        "journal": 0.85,
        "authors": 0.80,
        "affiliations": 0.75
    }
}

Now extract metadata from the PDF text provided above:"""
        return template
    
    async def extract_metadata_async(
        self,
        text_content: str,
        job_id: str,
        retry_count: int = 0,
        max_retries: int = 3,
        pdf_metadata: Optional[Dict[str, Any]] = None
    ) -> ExtractedMetadata:
        """
        Extract metadata from PDF text using Ollama/LLaMA 2.
        
        Args:
            text_content: Extracted text from PDF
            job_id: Extraction job ID
            retry_count: Current retry attempt
            max_retries: Maximum retry attempts
            
        Returns:
            ExtractedMetadata with extracted fields
            
        Raises:
            MetadataExtractionError: If extraction fails
            ExtractionTimeoutError: If extraction times out
        """
        try:
            # Prepare prompt
            prompt = self.prompt_template.replace("{text}", text_content[:5000])  # Limit text
            
            # Call Ollama API
            llm_output = await self._call_ollama(prompt)
            
            # Parse response
            metadata = self._parse_extraction_response(llm_output, job_id)
            
            logger.info(f"Extraction successful for job {job_id}")
            return metadata
            
        except ExtractionTimeoutError:
            if retry_count < max_retries:
                logger.warning(f"Extraction timeout for job {job_id}, retrying... ({retry_count + 1}/{max_retries})")
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                return await self.extract_metadata_async(text_content, job_id, retry_count + 1, max_retries)
            else:
                raise
        except (OllamaConnectionError, ExtractionTimeoutError, MetadataExtractionError) as e:
            logger.warning(f"Ollama extraction failed for job {job_id}: {str(e)}. Falling back to heuristic extraction.")
            return self._fallback_extract_metadata(text_content, job_id, str(e), pdf_metadata)
        except Exception as e:
            logger.error(f"Extraction error for job {job_id}: {str(e)}")
            if retry_count < max_retries:
                await asyncio.sleep(2 ** retry_count)
                return await self.extract_metadata_async(text_content, job_id, retry_count + 1, max_retries)
            else:
                raise MetadataExtractionError(str(e))
    
    async def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API to generate response.
        
        Args:
            prompt: Input prompt for LLM
            
        Returns:
            LLM generated response
            
        Raises:
            OllamaConnectionError: If connection fails
            ExtractionTimeoutError: If operation times out
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.3  # Lower temperature for more deterministic output
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            
        except asyncio.TimeoutError:
            raise ExtractionTimeoutError("Ollama request timed out")
        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"Failed to connect to Ollama at {self.ollama_host}: {str(e)}")
        except httpx.HTTPError as e:
            raise OllamaConnectionError(f"Ollama API error: {str(e)}")
        except Exception as e:
            raise OllamaConnectionError(f"Failed to call Ollama: {str(e)}")

    def _fallback_extract_metadata(self, text_content: str, job_id: str, reason: str, pdf_metadata: Optional[Dict[str, Any]] = None) -> ExtractedMetadata:
        """Fallback heuristic extraction when Ollama is unavailable."""
        logger.warning(f"Fallback extraction for job {job_id}: {reason}")

        def first_nonempty_line(text: str) -> Optional[str]:
            for line in text.splitlines():
                line = line.strip()
                if line:
                    return line
            return None

        def normalize_date(date_text: str) -> Optional[str]:
            if not date_text:
                return None

            cleaned = re.sub(r"(?<=\d)(st|nd|rd|th)\b", "", date_text.strip(), flags=re.I)
            cleaned = re.sub(r"^(Published\s+on|Published|Publication Date|Published:)[:\s]*", "", cleaned, flags=re.I)

            for fmt in [
                "%Y-%m-%d",
                "%B %d, %Y",
                "%b %d, %Y",
                "%d %B %Y",
                "%d %b %Y",
                "%B %Y",
                "%b %Y",
                "%Y",
            ]:
                try:
                    parsed = datetime.strptime(cleaned, fmt).date()
                    return parsed.isoformat()
                except ValueError:
                    continue

            year_match = re.search(r"\b(19|20)\d{2}\b", cleaned)
            return year_match.group(0) if year_match else None

        def extract_author_names(raw_author_text: str) -> List[str]:
            if not raw_author_text:
                return []

            names = re.split(r"\s*(?:,|;| and | & |\n)\s*", raw_author_text)
            parsed = []
            for name in names:
                normalized = name.strip()
                if normalized and len(normalized.split()) <= 8 and re.search(r"[A-Za-z]", normalized):
                    parsed.append(normalized)
            return parsed

        def extract_affiliation_lines(text: str) -> List[str]:
            affiliations = []
            for line in text.splitlines():
                cleaned = line.strip()
                if not cleaned:
                    continue
                if re.search(r"\b(?:University|Institute|College|School|Laboratory|Center|Centre|Hospital|Research|Department|Dept)\b", cleaned, flags=re.I):
                    if cleaned not in affiliations:
                        affiliations.append(cleaned)
                elif re.search(r"\b(?:Inc|LLC|Corp|Corporation|GmbH|Ltd)\b", cleaned) and len(cleaned.split()) > 2:
                    if cleaned not in affiliations:
                        affiliations.append(cleaned)
            return affiliations

        title = None
        if pdf_metadata:
            title = pdf_metadata.get("title") or None

        title = title or first_nonempty_line(text_content) or "Untitled"
        doi_match = re.search(r'10\.[0-9]{4,9}/[^\s,;")]+', text_content)
        doi = doi_match.group(0) if doi_match else None

        abstract = None
        abstract_block = re.search(r"Abstract[:\s]*(.+?)(?:\n\s*\n|\nKeywords|\nIntroduction|\n1\\.|\Z)", text_content, flags=re.I | re.S)
        if abstract_block:
            abstract = abstract_block.group(1).strip()
            if len(abstract) > 1000:
                abstract = abstract[:1000].rsplit(" ", 1)[0]

        keywords = []
        keywords_match = re.search(r"Keywords?[:\s]*(.+)", text_content, flags=re.I)
        if keywords_match:
            raw_keywords = re.split(r"[,;]\s*", keywords_match.group(1))
            keywords = [kw.strip() for kw in raw_keywords if kw.strip()][:20]

        publication_date = None
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", text_content)
        if not date_match:
            date_match = re.search(r"(?:Published(?:\s+on)?|Publication Date|Published:)[:\s]*(.+)", text_content, flags=re.I)
        if date_match:
            date_text = date_match.group(1) if date_match.lastindex and date_match.lastindex >= 1 else date_match.group(0)
            publication_date = normalize_date(date_text)
        else:
            month_year_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", text_content, flags=re.I)
            if month_year_match:
                publication_date = normalize_date(month_year_match.group(0))

        journal = None
        journal_match = re.search(r"(?:Proceedings of the|Proceedings of|Journal of|IEEE Transactions on|ACM Transactions on|Nature|Science|PNAS|arXiv|Conference on)\s+([A-Za-z0-9 ,:&-]+)", text_content, flags=re.I)
        if journal_match:
            journal = journal_match.group(0).strip()
        elif pdf_metadata:
            journal = pdf_metadata.get("subject") or pdf_metadata.get("creator") or pdf_metadata.get("producer")
            if journal and len(journal) > 200:
                journal = journal.split(";")[0].strip()

        authors: List[Author] = []
        author_candidates = re.search(r"(?:Authors?|By)[:\s]*(.+?)(?:\n\s*\n|\nAbstract|\nKeywords|\nIndex Terms|\nIntroduction|\n1\\.)", text_content, flags=re.I | re.S)
        if author_candidates:
            names = extract_author_names(author_candidates.group(1))
            for idx, name in enumerate(names[:10], start=1):
                authors.append(Author(
                    id=f"author-{job_id[:8]}-{idx}",
                    name=name,
                    email=None,
                    orcid=None,
                    affiliation_ids=[]
                ))
        elif pdf_metadata and pdf_metadata.get("author"):
            names = extract_author_names(pdf_metadata.get("author", ""))
            for idx, name in enumerate(names[:10], start=1):
                authors.append(Author(
                    id=f"author-{job_id[:8]}-{idx}",
                    name=name,
                    email=None,
                    orcid=None,
                    affiliation_ids=[]
                ))
        elif title:
            lines = [line.strip() for line in text_content.splitlines() if line.strip()]
            if len(lines) > 1:
                fallback_authors = extract_author_names(lines[1])
                for idx, name in enumerate(fallback_authors[:10], start=1):
                    authors.append(Author(
                        id=f"author-{job_id[:8]}-{idx}",
                        name=name,
                        email=None,
                        orcid=None,
                        affiliation_ids=[]
                    ))

        affiliations: List[Affiliation] = []
        affiliation_match = re.search(r"(University|Institute|Department|Laboratory|College|School)[^\n,]*", text_content, flags=re.I)
        if affiliation_match:
            institution = affiliation_match.group(0).strip()
            affiliations.append(Affiliation(
                id=f"aff-{job_id[:8]}-1",
                institution=institution,
                department=None,
                city=None,
                country=None,
                postal_code=None
            ))

        confidence_scores = ConfidenceScores(
            title=0.25 if title else None,
            doi=0.30 if doi else None,
            authors=0.25 if authors else None,
            abstract=0.20 if abstract else None,
            keywords=0.20 if keywords else None,
            publication_date=0.20 if publication_date else None,
            journal=0.20 if journal else None,
            affiliations=0.15 if affiliations else None
        )

        overall_confidence = sum([s for s in [
            confidence_scores.title,
            confidence_scores.doi,
            confidence_scores.authors,
            confidence_scores.abstract,
            confidence_scores.keywords,
            confidence_scores.publication_date,
            confidence_scores.journal,
            confidence_scores.affiliations
        ] if s is not None]) / len([s for s in [
            confidence_scores.title,
            confidence_scores.doi,
            confidence_scores.authors,
            confidence_scores.abstract,
            confidence_scores.keywords,
            confidence_scores.publication_date,
            confidence_scores.journal,
            confidence_scores.affiliations
        ] if s is not None]) if any([
            confidence_scores.title,
            confidence_scores.doi,
            confidence_scores.authors,
            confidence_scores.abstract,
            confidence_scores.keywords,
            confidence_scores.publication_date,
            confidence_scores.journal,
            confidence_scores.affiliations
        ]) else 0.2

        return ExtractedMetadata(
            id=f"metadata-{job_id}",
            extraction_job_id=job_id,
            title=title,
            doi=doi,
            abstract=abstract,
            keywords=keywords,
            publication_date=publication_date,
            journal=journal,
            authors=authors,
            affiliations=affiliations,
            confidence_scores=confidence_scores,
            overall_confidence=overall_confidence,
            extraction_timestamp=datetime.utcnow()
        )

    def _parse_extraction_response(
        self,
        llm_output: str,
        job_id: str
    ) -> ExtractedMetadata:
        """
        Parse LLM output and create ExtractedMetadata object.
        
        Args:
            llm_output: Raw output from LLM
            job_id: Extraction job ID
            
        Returns:
            Validated ExtractedMetadata object
            
        Raises:
            MetadataExtractionError: If parsing fails
        """
        try:
            # Extract JSON from response (may have additional text)
            json_match = re.search(r'\{[\s\S]*\}', llm_output)
            if not json_match:
                raise MetadataExtractionError("No JSON found in LLM output")
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            # Extract and process authors
            authors = []
            for i, author_data in enumerate(data.get("authors", [])):
                author = Author(
                    id=f"author-{i:03d}",
                    name=author_data.get("name", ""),
                    email=author_data.get("email"),
                    orcid=author_data.get("orcid"),
                    affiliation_ids=author_data.get("affiliation_ids", [])
                )
                if author.name:
                    authors.append(author)
            
            # Extract and process affiliations
            affiliations = []
            for i, aff_data in enumerate(data.get("affiliations", [])):
                aff = Affiliation(
                    id=f"aff-{i:03d}",
                    institution=aff_data.get("institution", ""),
                    department=aff_data.get("department"),
                    city=aff_data.get("city"),
                    country=aff_data.get("country"),
                    postal_code=aff_data.get("postal_code")
                )
                if aff.institution:
                    affiliations.append(aff)
            
            # Extract confidence scores
            scores_data = data.get("confidence_scores", {})
            confidence_scores = ConfidenceScores(
                title=scores_data.get("title", 0.5),
                doi=scores_data.get("doi"),
                authors=scores_data.get("authors"),
                abstract=scores_data.get("abstract"),
                keywords=scores_data.get("keywords"),
                publication_date=scores_data.get("publication_date"),
                journal=scores_data.get("journal"),
                affiliations=scores_data.get("affiliations")
            )
            
            # Calculate overall confidence
            valid_scores = [s for s in [
                confidence_scores.title,
                confidence_scores.doi,
                confidence_scores.authors,
                confidence_scores.abstract,
            ] if s is not None]
            
            overall_confidence = sum(valid_scores) / len(valid_scores) if valid_scores else 0.5
            
            # Create ExtractedMetadata
            metadata = ExtractedMetadata(
                id=f"metadata-{job_id}",
                extraction_job_id=job_id,
                title=data.get("title", "Untitled"),
                doi=data.get("doi"),
                abstract=data.get("abstract"),
                keywords=data.get("keywords", []),
                publication_date=data.get("publication_date"),
                journal=data.get("journal"),
                authors=authors,
                affiliations=affiliations,
                confidence_scores=confidence_scores,
                overall_confidence=overall_confidence,
                extraction_timestamp=datetime.utcnow()
            )
            
            logger.info(f"Successfully parsed metadata for job {job_id}")
            return metadata
            
        except json.JSONDecodeError as e:
            raise MetadataExtractionError(f"Failed to parse JSON from LLM output: {str(e)}")
        except Exception as e:
            raise MetadataExtractionError(f"Failed to parse extraction response: {str(e)}")
