"""
ExpertLens AI — Transcript Classification Dataset

Multi-label ground truth classification for transcript chunks.
Taxonomy:
- ADOPTION
- BARRIER
- ECONOMICS
- ROI
- TRAINING
- CLINICAL_OUTCOME
- OUTLOOK
- PURCHASING_TIMELINE
- UTILIZATION
- FUNDING
"""

from typing import List, Set
from pydantic import BaseModel


class LabeledChunk(BaseModel):
    """A transcript chunk with ground truth topic labels."""
    chunk_id: str
    country: str
    expert: str
    timestamp: str
    text: str
    labels: List[str]


CLASSIFICATION_TAXONOMY = [
    "ADOPTION",
    "BARRIER",
    "ECONOMICS",
    "ROI",
    "TRAINING",
    "CLINICAL_OUTCOME",
    "OUTLOOK",
    "PURCHASING_TIMELINE",
    "UTILIZATION",
    "FUNDING",
]

# Ground-truth classified chunks from the 3 real transcripts
CLASSIFICATION_BENCHMARK: List[LabeledChunk] = [
    LabeledChunk(
        chunk_id="FR-001",
        country="France",
        expert="Dr. Jean Martin",
        timestamp="00:18",
        text="Adoption is growing, but it is still concentrated in larger academic hospitals and private centres with stronger capital budgets. Smaller regional hospitals are much slower.",
        labels=["ADOPTION", "FUNDING"],
    ),
    LabeledChunk(
        chunk_id="FR-002",
        country="France",
        expert="Dr. Jean Martin",
        timestamp="01:20",
        text="The biggest issue is still capital budget approval. Hospitals may like the technology clinically, but purchasing committees need a strong economic case before approving a system.",
        labels=["BARRIER", "ECONOMICS", "FUNDING"],
    ),
    LabeledChunk(
        chunk_id="FR-003",
        country="France",
        expert="Dr. Jean Martin",
        timestamp="02:18",
        text="Very important. The clinical argument may get surgeons interested, but the finance team wants to understand utilisation, procedure volume, maintenance cost and whether the system will actually pay for itself.",
        labels=["ECONOMICS", "ROI", "UTILIZATION"],
    ),
    LabeledChunk(
        chunk_id="FR-004",
        country="France",
        expert="Dr. Jean Martin",
        timestamp="03:10",
        text="Training matters, especially in the first year. If only one surgeon can use the system, the economics become difficult. Hospitals want several surgeons trained so utilisation is high enough.",
        labels=["TRAINING", "ECONOMICS", "UTILIZATION"],
    ),
    LabeledChunk(
        chunk_id="FR-005",
        country="France",
        expert="Dr. Jean Martin",
        timestamp="04:08",
        text="Clinical outcomes are necessary, but they are not enough on their own. If two systems offer similar outcomes, the hospital will look hard at economics and utilisation.",
        labels=["CLINICAL_OUTCOME", "ECONOMICS", "UTILIZATION"],
    ),
    LabeledChunk(
        chunk_id="FR-006",
        country="France",
        expert="Dr. Jean Martin",
        timestamp="05:07",
        text="I expect adoption to continue increasing, probably steadily rather than explosively. I would expect maybe 15 to 20 percent more procedures annually in some of the stronger centres, but smaller hospitals will remain slower.",
        labels=["ADOPTION", "OUTLOOK"],
    ),
    LabeledChunk(
        chunk_id="FR-007",
        country="France",
        expert="Dr. Jean Martin",
        timestamp="06:08",
        text="Six to twelve months is realistic once the hospital becomes serious. It can be longer if the capital committee pushes the purchase into the next budget cycle.",
        labels=["PURCHASING_TIMELINE", "FUNDING"],
    ),
    LabeledChunk(
        chunk_id="DE-001",
        country="Germany",
        expert="Anna Keller",
        timestamp="00:16",
        text="It is growing, but adoption is quite uneven. Large university hospitals are much more advanced, while many smaller hospitals are still waiting.",
        labels=["ADOPTION"],
    ),
    LabeledChunk(
        chunk_id="DE-002",
        country="Germany",
        expert="Anna Keller",
        timestamp="01:10",
        text="Cost is the first barrier. These are large capital purchases, and hospital finances are under pressure. The second issue is proving that the system will be used enough.",
        labels=["BARRIER", "ECONOMICS", "UTILIZATION", "FUNDING"],
    ),
    LabeledChunk(
        chunk_id="DE-003",
        country="Germany",
        expert="Anna Keller",
        timestamp="02:08",
        text="We look at total cost of ownership, expected procedure volume, maintenance, service contracts and training requirements. A strong clinical case helps, but the economic case decides whether it gets approved.",
        labels=["ECONOMICS", "ROI", "TRAINING", "UTILIZATION"],
    ),
    LabeledChunk(
        chunk_id="DE-004",
        country="Germany",
        expert="Anna Keller",
        timestamp="03:05",
        text="Very important operationally. If the hospital buys a system but only one surgeon is comfortable using it, utilisation will be poor. That weakens the business case.",
        labels=["TRAINING", "UTILIZATION", "ECONOMICS"],
    ),
    LabeledChunk(
        chunk_id="DE-005",
        country="Germany",
        expert="Anna Keller",
        timestamp="04:09",
        text="Yes, but I would not expect a dramatic jump. I think growth will be gradual, especially because many hospitals have other competing capital priorities.",
        labels=["ADOPTION", "OUTLOOK", "FUNDING"],
    ),
    LabeledChunk(
        chunk_id="DE-006",
        country="Germany",
        expert="Anna Keller",
        timestamp="05:08",
        text="I would expect continued growth, but probably closer to high single digits or low double digits in procedure volumes rather than something like 20 percent across the whole market.",
        labels=["OUTLOOK", "ADOPTION"],
    ),
    LabeledChunk(
        chunk_id="DE-007",
        country="Germany",
        expert="Anna Keller",
        timestamp="06:05",
        text="Nine to eighteen months is common. Procurement, clinical leadership, finance and management all need to align, so it can move slowly.",
        labels=["PURCHASING_TIMELINE"],
    ),
    LabeledChunk(
        chunk_id="UK-001",
        country="United Kingdom",
        expert="Dr. Emily Carter",
        timestamp="00:14",
        text="Adoption is increasing, and in some larger NHS trusts robotic surgery is becoming standard for selected procedures. But access still varies significantly by hospital.",
        labels=["ADOPTION"],
    ),
    LabeledChunk(
        chunk_id="UK-002",
        country="United Kingdom",
        expert="Dr. Emily Carter",
        timestamp="01:05",
        text="Funding is important, but I would say training capacity is just as important. You can buy a system, but if you cannot train enough surgeons and theatre staff, adoption stalls.",
        labels=["BARRIER", "FUNDING", "TRAINING"],
    ),
    LabeledChunk(
        chunk_id="UK-003",
        country="United Kingdom",
        expert="Dr. Emily Carter",
        timestamp="02:07",
        text="It matters, but the discussion is not always purely financial. Hospitals also consider patient outcomes, length of stay, surgeon recruitment and whether the technology improves their clinical position.",
        labels=["ROI", "CLINICAL_OUTCOME", "ECONOMICS"],
    ),
    LabeledChunk(
        chunk_id="UK-004",
        country="United Kingdom",
        expert="Dr. Emily Carter",
        timestamp="03:10",
        text="I would say economics and clinical strategy are balanced. I would not say finance alone decides the purchase.",
        labels=["ECONOMICS", "CLINICAL_OUTCOME"],
    ),
    LabeledChunk(
        chunk_id="UK-005",
        country="United Kingdom",
        expert="Dr. Emily Carter",
        timestamp="04:06",
        text="I am quite positive. I think adoption could accelerate if training expands and systems become more cost competitive. I could see procedure growth above 15 percent annually in some areas.",
        labels=["OUTLOOK", "TRAINING", "ADOPTION"],
    ),
    LabeledChunk(
        chunk_id="UK-006",
        country="United Kingdom",
        expert="Dr. Emily Carter",
        timestamp="05:04",
        text="Around six to nine months can happen if funding is already available. If the trust has to wait for a new capital cycle, it can take much longer.",
        labels=["PURCHASING_TIMELINE", "FUNDING"],
    ),
]
