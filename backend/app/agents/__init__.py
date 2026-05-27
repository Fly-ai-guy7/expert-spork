from app.agents.base import AgentContext, AgentOutput, LegalAgent
from app.agents.damages_calculator import DamagesCalculatorAgent
from app.agents.defense import DefenseAgent
from app.agents.evidence_migration import EvidenceMigrationAgent
from app.agents.judicial import JudicialAgent
from app.agents.precedent_researcher import PrecedentResearcherAgent
from app.agents.procedural_specialist import ProceduralSpecialistAgent
from app.agents.prosecution import ProsecutionAgent
from app.agents.scoring import ScoringAgent

__all__ = [
    "AgentContext",
    "AgentOutput",
    "DamagesCalculatorAgent",
    "DefenseAgent",
    "EvidenceMigrationAgent",
    "JudicialAgent",
    "LegalAgent",
    "PrecedentResearcherAgent",
    "ProceduralSpecialistAgent",
    "ProsecutionAgent",
    "ScoringAgent",
]
