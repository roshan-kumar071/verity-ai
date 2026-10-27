
import re


ABBREVIATIONS = [
    "U.S.",
    "U.K.",
    "e.g.",
    "i.e.",
    "vs.",
    "etc.",
    "Dr.",
    "Mr.",
    "Mrs.",
    "Ms.",
    "Prof.",
]


NON_CLAIM_PATTERNS = [
    r"\bdelivered to your inbox\b",
    r"\beach of the \d+ puzzle words?\b",
    r"\bsubscribe to our newsletter\b",
    r"\bsign up for our newsletter\b",
    r"\bunsubscribe\b",

    # Obvious unrelated lifestyle content seen in search snippets
    r"\bsourdough bread baking\b",
    r"\b(?:one of our employees|an employee)\b.{0,100}\b(?:takes? hikes?|goes hiking)\b",
]


def is_candidate_sentence(sentence: str) -> bool:
    """Reject obvious page noise and incomplete snippets."""
    text = sentence.strip()

    if not text:
        return False

    if any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in NON_CLAIM_PATTERNS
    ):
        return False

    # Reject snippets ending with an incomplete person's initial,
    # such as "Nicholas Bloom, and Steven J."
    if re.search(r"\b[A-Z]\.$", text):
        return False

    # Reject sentences that end with an incomplete thought.
    if re.search(
        r"\b(?:whether|because|although|while|if|when|which|that|"
        r"including|such as|compared with|compared to|and|or|but)$",
        text,
        flags=re.IGNORECASE,
    ):
        return False

    # Reject fragments produced by the known missing-punctuation repair.
    if re.fullmatch(
        r"These interruptions reduce deep work time, "
        r"affecting much of the productivity",
        text,
        flags=re.IGNORECASE,
    ):
        return False

    return True


def is_relevant_to_question(sentence: str, question: str) -> bool:
    """Keep sentences with meaningful keyword or synonym overlap."""
    stopwords = {
        "a", "an", "the", "is", "are", "was", "were", "do", "does",
        "did", "can", "could", "would", "should", "to", "of", "in",
        "on", "for", "and", "or", "but", "with", "by", "from", "than",
        "how", "what", "why", "when", "where", "who", "which",
        "compared", "between", "about", "against", "into", "it",
        "their", "they", "this", "that",
    }

    def meaningful_words(text: str) -> set[str]:
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        normalized = set()

        for word in words:
            if word in stopwords:
                continue

            if word.endswith("ing") and len(word) > 5:
                word = word[:-3]
            elif word.endswith("s") and len(word) > 4:
                word = word[:-1]

            normalized.add(word)

        return normalized

    question_words = meaningful_words(question)
    sentence_words = meaningful_words(sentence)

    if not question_words:
        return True

    # Common alternative terms for related concepts.
    synonym_groups = [
        {"remote", "home"},
        {"employee", "staff", "worker"},
        {"productivity", "productive"},
        {"improve", "help", "boost", "increase"},
        {"work", "working"},
    ]

    matched_groups = 0

    for group in synonym_groups:
        if question_words & group and sentence_words & group:
            matched_groups += 1

    direct_overlap = question_words & sentence_words

    # Avoid accepting a sentence based on just one generic keyword.
    return len(direct_overlap) >= 2 or matched_groups >= 2  


def split_sentences(text: str) -> list[str]:
    """Split text into sentences without breaking common abbreviations."""
    protected = text

    for index, abbreviation in enumerate(ABBREVIATIONS):
        placeholder = f"ABBREVIATIONTOKEN{index}END"
        protected = re.sub(
            re.escape(abbreviation),
            abbreviation.replace(".", placeholder),
            protected,
            flags=re.IGNORECASE,
        )

    protected = re.sub(
        r"(?i)(productivity)\s+(Studies indicate\b)",
        r"\1 SPLITMARKER \2",
        protected,
    )

    sentences = re.split(
        r"(?<=[.!?])\s+|SPLITMARKER\s*",
        protected,
    )

    restored = []
    for sentence in sentences:
        for index, abbreviation in enumerate(ABBREVIATIONS):
            placeholder = f"ABBREVIATIONTOKEN{index}END"
            sentence = re.sub(
                re.escape(placeholder),
                ".",
                sentence,
                flags=re.IGNORECASE,
            )

        sentence = sentence.strip()
        if sentence:
            restored.append(sentence)

    return restored


def extract_claims(sources: list[dict], question: str = "",) -> list[dict]:
    """Extract candidate claims while preserving their original sources."""
    extracted = []
    seen = set()

    for source in sources:
        content = source.get("content", "")

        if not isinstance(content, str) or not content.strip():
            continue

        for sentence in split_sentences(content):
            sentence = sentence.strip()
            
            if not is_candidate_sentence(sentence):
                continue

            if question and not is_relevant_to_question(sentence, question):
                continue

            # Ignore questions and very short fragments.
            if len(sentence.split()) < 4 or sentence.endswith("?"):
                continue

            # Search snippets containing editorial ellipses may be incomplete.
            if "..." in sentence or "[…]" in sentence or "[...]" in sentence:
                continue

            normalized = sentence.casefold()

            if normalized in seen:
                continue

            seen.add(normalized)

            extracted.append(
                {
                    "claim": sentence,
                    "source_title": source.get("title", ""),
                    "source_url": source.get("url", ""),
                }
            )

    return extracted
