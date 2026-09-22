"""
ExpertLens AI — Transcript Parser

Extracts structured metadata and speaker turns from expert interview transcripts.
Handles the specific format used in the European Robotic Surgery Market transcripts.

Expected format:
    Expert N – <Name>
    Role: <Role>
    Market: <Country>
    
    HH:MM
    Speaker: Text...
"""

import re
from dataclasses import dataclass, field


@dataclass
class ParsedTurn:
    """A single speaker turn extracted from a transcript."""
    timestamp: str
    speaker: str
    text: str
    index: int


@dataclass
class ParsedTranscript:
    """Complete parsed transcript with metadata and turns."""
    expert_name: str = ""
    expert_role: str = ""
    country: str = ""
    turns: list[ParsedTurn] = field(default_factory=list)
    raw_text: str = ""

    @property
    def expert_turns(self) -> list[ParsedTurn]:
        """Return only the expert's turns (not interviewer)."""
        return [t for t in self.turns if "interviewer" not in t.speaker.lower()]


def parse_transcript(text: str, filename: str = "") -> ParsedTranscript:
    """
    Parse a transcript file into structured metadata and speaker turns.
    Supports standard, markdown, and inline timestamp formats.
    
    Args:
        text: Raw transcript text content
        filename: Original filename for reference
        
    Returns:
        ParsedTranscript with expert metadata and timestamped turns
    """
    result = ParsedTranscript(raw_text=text)
    lines = text.strip().replace('\r\n', '\n').split('\n')

    # Pass 1: Extract header metadata (first 30 lines)
    for raw_line in lines[:30]:
        line = re.sub(r'[*_#]', '', raw_line).strip()
        if not line or line.startswith('---'):
            continue

        # Stop header scan if we hit a timestamp turn
        if re.search(r'\b\d{1,2}:\d{2}\b', line) and ':' in line and not line.lower().startswith(('market', 'country', 'role', 'expert')):
            break

        # Check Expert Name
        name_match = re.match(
            r'^(?:Expert\s+name|Expert(?:\s+\d+)?|Expert)\s*[:–\-—]*\s*(.+)$',
            line,
            re.IGNORECASE
        )
        if name_match and not result.expert_name:
            cand = re.sub(r'^[:–\-—\s]+', '', name_match.group(1)).strip()
            # If line is like "Expert 4 — Italy", cand is "Italy"
            if cand.lower() in ("italy", "france", "germany", "united kingdom", "uk", "spain", "sweden", "netherlands"):
                if not result.country:
                    result.country = cand
            else:
                result.expert_name = cand
            continue

        # Header with dash e.g. "# Expert 4 — Italy" or "Expert 4 - France"
        dash_header = re.match(r'^Expert(?:\s+\d+)?\s*[—–\-]\s*(.+)$', line, re.IGNORECASE)
        if dash_header:
            val = re.sub(r'^[:–\-—\s]+', '', dash_header.group(1)).strip()
            if val.lower() in ("italy", "france", "germany", "united kingdom", "uk", "spain", "sweden", "netherlands"):
                if not result.country:
                    result.country = val
            elif not result.expert_name:
                result.expert_name = val
            continue

        # Role
        role_match = re.match(r'^(?:Role|Title|Specialty)\s*[:–\-—]*\s*(.+)$', line, re.IGNORECASE)
        if role_match and not result.expert_role:
            result.expert_role = re.sub(r'^[:–\-—\s]+', '', role_match.group(1)).strip()
            continue

        # Market / Country
        market_match = re.match(r'^(?:Market|Country)\s*[:–\-—]*\s*(.+)$', line, re.IGNORECASE)
        if market_match and not result.country:
            result.country = re.sub(r'^[:–\-—\s]+', '', market_match.group(1)).strip()
            continue

    # Pass 2: Parse speaker turns (both separate timestamp and inline timestamp formats)
    inline_pattern = re.compile(
        r'^\s*[*_#]*\s*\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*[*_]*\s*(?:–|-)?\s*[*_]*\s*([^:\n*]+?)\s*[*_]*:\s*(.+)$'
    )
    timestamp_only_pattern = re.compile(
        r'^\s*[*_#]*\s*\[?(\d{1,2}:\d{2}(?::\d{2})?)\]?\s*[*_#]*\s*$'
    )
    speaker_only_pattern = re.compile(
        r'^\s*[*_#]*\s*([^:\n*]+?)\s*[*_]*:\s*(.+)$'
    )

    current_timestamp = None
    current_speaker = None
    current_text_parts: list[str] = []
    turn_index = 0

    def flush_turn():
        nonlocal turn_index
        if current_timestamp and current_speaker and current_text_parts:
            # Clean markdown from text
            clean_text = ' '.join(current_text_parts).strip()
            clean_text = re.sub(r'[*_]', '', clean_text).strip()
            clean_speaker = re.sub(r'[*_]', '', current_speaker).strip()
            clean_speaker = re.sub(r'^[:–\-—\s]+|[:–\-—\s]+$', '', clean_speaker).strip()
            if clean_text:
                result.turns.append(ParsedTurn(
                    timestamp=current_timestamp,
                    speaker=clean_speaker,
                    text=clean_text,
                    index=turn_index,
                ))
                turn_index += 1

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('---'):
            continue

        # 1. Try inline timestamp pattern: [00:18] Dr. Marco Rossi: Text...
        inline_match = inline_pattern.match(stripped)
        if inline_match:
            potential_speaker = inline_match.group(2).strip()
            if potential_speaker.lower() not in ('role', 'market', 'country', 'expert', 'interview topic', 'transcript type'):
                flush_turn()
                current_timestamp = inline_match.group(1)
                current_speaker = potential_speaker
                current_text_parts = [inline_match.group(3).strip()]
                continue

        # 2. Try timestamp on its own line: 00:18 or [00:18]
        ts_match = timestamp_only_pattern.match(stripped)
        if ts_match:
            flush_turn()
            current_timestamp = ts_match.group(1)
            current_speaker = None
            current_text_parts = []
            continue

        # 3. Check for Speaker: text after timestamp line
        if current_timestamp and current_speaker is None:
            spk_match = speaker_only_pattern.match(stripped)
            if spk_match:
                potential_speaker = spk_match.group(1).strip()
                if potential_speaker.lower() in ('role', 'market', 'country', 'expert', 'interview topic', 'transcript type'):
                    continue
                current_speaker = potential_speaker
                current_text_parts = [spk_match.group(2).strip()]
                continue

        # 4. Continuation of current text
        if current_speaker and stripped:
            current_text_parts.append(stripped)

    # Flush the last turn
    flush_turn()

    # Fallbacks for missing expert name or country
    if not result.expert_name and result.turns:
        # Find first non-interviewer speaker
        for turn in result.turns:
            if "interviewer" not in turn.speaker.lower():
                result.expert_name = turn.speaker
                break

    if not result.country and filename:
        for c in ("Italy", "France", "Germany", "United Kingdom", "UK", "Spain", "Sweden", "Netherlands"):
            if c.lower() in filename.lower():
                result.country = "United Kingdom" if c == "UK" else c
                break

    if not result.expert_role:
        result.expert_role = "Expert Consultant"

    return result


def parse_interview_guide(text: str) -> list[str]:
    """
    Parse the interview guide to extract the six questions.
    
    Args:
        text: Raw interview guide text
        
    Returns:
        List of question strings
    """
    questions = []
    for line in text.strip().split('\n'):
        line = line.strip()
        # Match numbered questions: "1. How would you..."
        match = re.match(r'^\d+\.\s+(.+)$', line)
        if match:
            questions.append(match.group(1).strip())
    return questions
