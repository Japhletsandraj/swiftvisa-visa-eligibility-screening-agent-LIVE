import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime

from retriever import VisaPolicyRetriever
from llm_integration import ChatAnywhereLLM
from config.config import LOGGING_CONFIG, FAISS_CONFIG
from utils.Country_config import COUNTRY_CONFIG

# Setup logging
logging.basicConfig(
    level=LOGGING_CONFIG["level"],
    format=LOGGING_CONFIG["format"],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG["log_file"]),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Default country for backwards compatibility
DEFAULT_COUNTRY = "uk"


class SwiftVisaRAG:
    """
    Complete RAG pipeline for visa eligibility screening.
    Supports multiple countries — each gets its own FAISS index.
    """

    def __init__(self, country: str = DEFAULT_COUNTRY):
        """
        Initialize RAG pipeline for a specific country.

        Args:
            country: Country code (uk | canada | australia | new_zealand).
                     Defaults to 'uk' for backwards compatibility.
        """
        if country not in COUNTRY_CONFIG:
            raise ValueError(
                f"Unsupported country '{country}'. "
                f"Supported: {list(COUNTRY_CONFIG.keys())}"
            )

        self.country = country
        self.country_display = COUNTRY_CONFIG[country]["display_name"]

        logger.info(f"[INIT] SwiftVisa RAG Pipeline — {self.country_display}")

        # Resolve the FAISS index path for this country
        index_path = FAISS_CONFIG["index_paths"].get(country)
        if not index_path:
            raise ValueError(f"No FAISS index path configured for country '{country}'")

        # Initialize components — pass country-specific index path to retriever
        self.retriever = VisaPolicyRetriever(vectorstore_path=index_path)
        self.llm = ChatAnywhereLLM()

        # Conversation history for multi-turn conversations
        self.conversation_history = []

        logger.info(f"[READY] RAG pipeline ready for {self.country_display}")

    # ── Public API ────────────────────────────────────────────────────────────

    def answer_question(
        self,
        question: str,
        visa_type: Optional[str] = None,
        top_k: int = 3,
        country: Optional[str] = None,   # ignored — kept for call-site compatibility
    ) -> Dict:
        """Answer a visa-related question using RAG."""
        logger.info(f"[QA] '{question}' | country={self.country} | visa={visa_type}")

        retrieved = self.retriever.retrieve(
            query=question,
            visa_type_filter=visa_type,
            top_k=top_k
        )

        if not retrieved:
            return {
                "question": question,
                "answer": (
                    "I couldn't find relevant information in the visa policies to answer "
                    "your question. Please try rephrasing or ask about a specific visa type."
                ),
                "sources": [],
                "retrieved_chunks": 0,
                "country": self.country,
            }

        context = self.retriever.format_context_for_llm(retrieved)
        answer = self.llm.answer_question(question=question, context=context)

        return {
            "question": question,
            "answer": answer,
            "sources": self._format_sources(retrieved),
            "retrieved_chunks": len(retrieved),
            "visa_type_filter": visa_type,
            "country": self.country,
            "timestamp": datetime.now().isoformat(),
        }

    def evaluate_eligibility(
        self,
        user_profile: Dict,
        visa_type: str,
        country: Optional[str] = None,   # ignored — kept for call-site compatibility
    ) -> Dict:
        """
        Evaluate a user's visa eligibility against policy documents.

        Args:
            user_profile: Dictionary of form field values from app.py.
            visa_type:    Visa type key (e.g. 'student', 'student_permit').
            country:      Accepted but ignored; the instance already knows its country.
        """
        logger.info(
            f"[EVAL] country={self.country} visa={visa_type}\n"
            f"{json.dumps(user_profile, indent=2)}"
        )

        query = (
            f"What are the eligibility requirements and criteria for a "
            f"{visa_type.replace('_', ' ')} in {self.country_display}?"
        )

        user_context = {**user_profile, "visa_type": visa_type, "country": self.country}
        retrieved = self.retriever.retrieve_with_context(
            query=query,
            user_context=user_context,
            top_k=5
        )

        if not retrieved:
            return {
                "evaluation": (
                    f"No policy information found for the {visa_type.replace('_', ' ')} "
                    f"({self.country_display}). Ensure the vector store has been built "
                    f"for this country."
                ),
                "eligibility": "Unknown",
                "sources": [],
                "country": self.country,
            }

        context = self.retriever.format_context_for_llm(retrieved)

        evaluation = self.llm.evaluate_eligibility(
            user_profile=user_profile,
            visa_type=f"{visa_type} ({self.country_display})",
            context=context,
            country=self.country_display,
        )

        return {
            "visa_type": visa_type,
            "user_profile": user_profile,
            "evaluation": evaluation,
            "sources": self._format_sources(retrieved),
            "retrieved_chunks": len(retrieved),
            "country": self.country,
            "timestamp": datetime.now().isoformat(),
        }

    def chat(
        self,
        user_message: str,
        use_retrieval: bool = True,
        visa_type: Optional[str] = None,
        country: Optional[str] = None,   # ignored — kept for call-site compatibility
    ) -> Dict:
        """Chat interface with optional RAG retrieval."""
        logger.info(f"[CHAT] country={self.country} '{user_message}'")

        context = None
        retrieved_chunks = 0

        if use_retrieval:
            retrieved = self.retriever.retrieve(
                query=user_message,
                visa_type_filter=visa_type,
                top_k=5
            )
            if retrieved:
                context = self.retriever.format_context_for_llm(retrieved)
                retrieved_chunks = len(retrieved)

        response = self.llm.chat(
            user_message=user_message,
            conversation_history=self.conversation_history,
            context=context
        )

        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response})

        # Keep only last 10 messages
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

        return {
            "user_message": user_message,
            "response": response,
            "retrieved_chunks": retrieved_chunks,
            "country": self.country,
            "timestamp": datetime.now().isoformat(),
        }

    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
        logger.info(f"[RESET] Conversation history cleared for {self.country_display}")

    def get_statistics(self) -> Dict:
        """Return pipeline statistics."""
        return {
            "country": self.country,
            "country_display": self.country_display,
            "retriever_stats": self.retriever.get_statistics(),
            "llm_config": {
                "model": self.llm.model,
                "base_url": self.llm.base_url,
                "temperature": self.llm.temperature,
            },
            "conversation_length": len(self.conversation_history),
        }

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _format_sources(self, retrieved: List[Dict]) -> List[Dict]:
        return [
            {
                "visa_type": chunk["metadata"].get("visa_type", "unknown"),
                "source_file": chunk["metadata"].get("source_file", "unknown"),
                "relevance_score": chunk["score"],
            }
            for chunk in retrieved
        ]


# ── CLI helpers (interactive + automated tests) ───────────────────────────────

def _pick_country() -> str:
    print("\nSelect country:")
    options = list(COUNTRY_CONFIG.keys())
    for i, code in enumerate(options, 1):
        print(f"  {i}. {COUNTRY_CONFIG[code]['flag']} {COUNTRY_CONFIG[code]['display_name']}")
    choice = input("Choice: ").strip()
    try:
        return options[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid — defaulting to UK")
        return "uk"


def _visa_menu(country: str) -> Dict[str, str]:
    visa_types = COUNTRY_CONFIG[country]["visa_types"]
    return {str(i + 1): vt for i, vt in enumerate(visa_types)}


def interactive_test():
    print("\n" + "=" * 80)
    print(" SwiftVisa RAG Pipeline — Interactive Test")
    print("=" * 80)
    print("\nCommands: 'q <question>'  'e' (evaluate)  'stats'  'reset'  'country'  'quit'")
    print("=" * 80)

    country = _pick_country()
    try:
        rag = SwiftVisaRAG(country=country)
    except Exception as e:
        print(f"\nError initialising RAG pipeline: {e}")
        return

    while True:
        try:
            user_input = input("\n You: ").strip()
            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("\nGoodbye!")
                break

            elif user_input.lower() == "country":
                country = _pick_country()
                rag = SwiftVisaRAG(country=country)
                print(f"Switched to {COUNTRY_CONFIG[country]['display_name']}")

            elif user_input.lower() == "stats":
                print(json.dumps(rag.get_statistics(), indent=2))

            elif user_input.lower() == "reset":
                rag.reset_conversation()
                print("Conversation reset")

            elif user_input.lower().startswith("q "):
                question = user_input[2:].strip()
                visa_map = _visa_menu(country)
                print("\nVisa type filter (Enter = all):")
                for k, v in visa_map.items():
                    print(f"  {k}. {v}")
                pick = input("Filter: ").strip()
                visa_filter = visa_map.get(pick)
                result = rag.answer_question(question, visa_type=visa_filter)
                print(f"\nAnswer ({result['retrieved_chunks']} sources):")
                print("-" * 80)
                print(result["answer"])

            elif user_input.lower() == "e":
                visa_map = _visa_menu(country)
                print("\nSelect visa type:")
                for k, v in visa_map.items():
                    print(f"  {k}. {v}")
                pick = input("Choice: ").strip()
                visa_type = visa_map.get(pick)
                if not visa_type:
                    print("Invalid choice"); continue

                print(f"\nEnter profile details for {visa_type.replace('_', ' ').title()}:")
                user_profile = {
                    "Age": input("Age: ").strip(),
                    "Nationality": input("Nationality: ").strip(),
                    "Education": input("Education: ").strip(),
                    "Employment Status": input("Employment Status: ").strip(),
                }
                print("\nEvaluating…")
                result = rag.evaluate_eligibility(user_profile, visa_type)
                print("\n" + "=" * 80)
                print(result["evaluation"])
                print("=" * 80)
                print(f"Based on {result['retrieved_chunks']} policy documents")

            else:
                result = rag.chat(user_input)
                print(f"\n {result['response']}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            logger.exception("Error in interactive test")


def automated_test():
    print("\n" + "=" * 80)
    print(" SwiftVisa RAG Pipeline — Automated Tests")
    print("=" * 80)

    test_cases = [
        {
            "country": "uk",
            "questions": [
                ("What are the financial requirements for a student visa?", "student"),
                ("Can I work with a graduate visa?", "graduate"),
                ("What is the minimum salary for a skilled worker visa?", "skilled_worker"),
            ],
            "profile": {
                "Age": "24", "Nationality": "Indian",
                "Education": "Bachelor's Degree",
                "English Test Score": "IELTS 7.0",
                "Financial Proof": "£12,000",
            },
            "eval_visa": "student",
        },
        {
            "country": "canada",
            "questions": [
                ("What are the requirements for a study permit?", "student_permit"),
                ("What is Express Entry?", "express_entry"),
            ],
            "profile": {
                "Age": "26", "Nationality": "Nigerian",
                "Education": "Bachelor's Degree",
                "Language Test": "IELTS 7.5",
                "Financial Proof": "CAD 15,000",
            },
            "eval_visa": "student_permit",
        },
    ]

    for tc in test_cases:
        country = tc["country"]
        print(f"\n{'='*70}")
        print(f" Testing: {COUNTRY_CONFIG[country]['flag']} {COUNTRY_CONFIG[country]['display_name']}")
        print(f"{'='*70}")

        try:
            rag = SwiftVisaRAG(country=country)
        except Exception as e:
            print(f"  Skipped — could not load RAG: {e}")
            continue

        for question, visa_type in tc["questions"]:
            print(f"\n Q: {question}")
            result = rag.answer_question(question, visa_type=visa_type)
            print(f" A ({result['retrieved_chunks']} sources): {result['answer'][:250]}…")

        print(f"\n Eligibility eval — {tc['eval_visa']}:")
        result = rag.evaluate_eligibility(tc["profile"], tc["eval_visa"])
        print(result["evaluation"][:400] + "…")

    print("\n" + "=" * 80)
    print(" All tests complete!")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        automated_test()
    else:
        interactive_test()