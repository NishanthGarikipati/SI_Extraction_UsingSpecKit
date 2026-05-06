from pathlib import Path

path = Path(r'c:\Users\U6052131\OneDrive - Clarivate Analytics\Daily\SPEC KIT\backend\src\services\rag_extractor.py')
text = path.read_text(encoding='utf-8')
old = '''    def _fallback_extract_metadata(self, text_content: str, job_id: str, reason: str) -> ExtractedMetadata:
        """Fallback heuristic extraction when Ollama is unavailable."""
        logger.warning(f"Fallback extraction for job {job_id}: {reason}")

        def first_nonempty_line(text: str) -> Optional[str]:
            for line in text.splitlines():
                line = line.strip()
                if line:
                    return line
            return None

        title = first_nonempty_line(text_content) or "Untitled"
        doi_match = re.search(r'10\.[0-9]{4,9}/[^\s,;\")]+', text_content)
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
            date_match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}", text_content, flags=re.I)
        if date_match:
            publication_date = date_match.group(0).strip()

        journal = None
        journal_match = re.search(r"(?:Proceedings of the|Proceedings of|Journal of|IEEE Transactions on|ACM Transactions on)\s+([A-Za-z0-9 ,:&-]+)", text_content, flags=re.I)
        if journal_match:
            journal = journal_match.group(0).strip()

        authors: List[Author] = []
        author_candidates = re.search(r"(?:Authors?|By)[:\s]*(.+?)(?:\n\n|\nAbstract|\nKeywords|\nIntroduction|\n1\\.)", text_content, flags=re.I | re.S)
        if author_candidates:
            names = re.split(r",| and | & ", author_candidates.group(1))
            for idx, raw_name in enumerate(names[:10], start=1):
                name = raw_name.strip()
                if name:
                    authors.append(Author(
                        id=f"author-{job_id[:8]}-{idx}",
                        name=name,
                        email=None,
                        orcid=None,
                        affiliation_ids=[]
                    ))
        elif title:
            # Fallback: use next line after title as author list
            lines = [line.strip() for line in text_content.splitlines() if line.strip()]
            if len(lines) > 1:
                fallback_authors = re.split(r",| and | & ", lines[1])
                for idx, raw_name in enumerate(fallback_authors[:10], start=1):
                    name = raw_name.strip()
                    if name and len(name.split()) <= 6:
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
'''
new = '''    def _fallback_extract_metadata(self, text_content: str, job_id: str, reason: str, pdf_metadata: Optional[Dict[str, Any]] = None) -> ExtractedMetadata:
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

        doi_match = re.search(r"\b10\.[0-9]{4,9}/[^\s,;\)\"]+", text_content)
        doi = doi_match.group(0) if doi_match else None

        abstract = None
        abstract_block = re.search(
            r"Abstract[:\s]*(.+?)(?:\n\s*\n|\nKeywords|\nIndex Terms|\nIntroduction|\n1\\.|\Z)",
            text_content,
            flags=re.I | re.S
        )
        if abstract_block:
            abstract = abstract_block.group(1).strip()
            if len(abstract) > 1200:
                abstract = abstract[:1200].rsplit(" ", 1)[0]

        keywords = []
        keywords_match = re.search(r"(?:Keywords|Key words|Index Terms?)[:\s]*(.+)", text_content, flags=re.I)
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
        journal_match = re.search(
            r"(?:Proceedings of the|Proceedings of|Journal of|IEEE Transactions on|ACM Transactions on|Nature|Science|PNAS|arXiv|Conference on)\s+([A-Za-z0-9 ,:&-]+)",
            text_content,
            flags=re.I
        )
        if journal_match:
            journal = journal_match.group(0).strip()
        elif pdf_metadata:
            journal = pdf_metadata.get("subject") or pdf_metadata.get("creator") or pdf_metadata.get("producer")
            if journal and len(journal) > 200:
                journal = journal.split(";")[0].strip()

        authors: List[Author] = []
        author_candidates = re.search(
            r"(?:Authors?|By)[:\s]*(.+?)(?:\n\s*\n|\nAbstract|\nKeywords|\nIndex Terms|\nIntroduction|\n1\\.)",
            text_content,
            flags=re.I | re.S
        )
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
        for aff_line in extract_affiliation_lines(text_content):
            affiliations.append(Affiliation(
                id=f"aff-{job_id[:8]}-{len(affiliations)+1}",
                institution=aff_line,
                department=None,
                city=None,
                country=None,
                postal_code=None
            ))

        confidence_scores = ConfidenceScores(
            title=0.60 if title and title != "Untitled" else 0.30,
            doi=0.70 if doi else 0.15,
            authors=0.60 if authors else None,
            abstract=0.55 if abstract else None,
            keywords=0.50 if keywords else None,
            publication_date=0.50 if publication_date else None,
            journal=0.40 if journal else None,
            affiliations=0.35 if affiliations else None
        )

        score_values = [
            s for s in [
                confidence_scores.title,
                confidence_scores.doi,
                confidence_scores.authors,
                confidence_scores.abstract,
                confidence_scores.keywords,
                confidence_scores.publication_date,
                confidence_scores.journal,
                confidence_scores.affiliations,
            ] if s is not None
        ]
        overall_confidence = sum(score_values) / len(score_values) if score_values else 0.3

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
'''
if old not in text:
    raise SystemExit('Old block not found')
text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')
print('patched')
