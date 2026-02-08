"""
Run review script - manual test of the core use case.

Usage: uv run python scripts/run_review.py
"""

import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import get_session
from app.repositories.review_repository import ReviewRepository
from app.services.reviewer_service import ReviewerService
from scripts.seed import seed_database


def main() -> None:
    # 1. Seed the database
    print("Seeding database...")
    ids = seed_database()
    print(f"  Call ID: {ids['call_id']}")
    print(f"  Section 1 ID: {ids['section_1_id']}")
    print()

    # 2. Get session and create service layer
    session = get_session()
    repository = ReviewRepository(session)
    service = ReviewerService(repository)

    # 3. Sample snippet
    snippet_text = """
    This project aims to develop a novel framework for quantum error correction
    that surpasses current thresholds. We will use a combination of topological
    codes and machine learning to achieve fault-tolerant computation.
    """

    # 4. Test case: Section with expectations (should succeed)
    print("=" * 60)
    print("TEST 1: Reviewing Section 1 (has 3 expectations)")
    print("=" * 60)

    try:
        review, cards = service.generate_review(
            node_id=ids["section_1_id"],
            snippet_text=snippet_text,
            call_id=ids["call_id"],
        )
        print(f"✓ Review created: {review.id}")
        print(f"  Status: {review.status}")
        print(f"  Overall Rating: {review.overall_rating}")
        print(f"  Summary: {review.overall_summary}")
        print(f"✓ Generated {len(cards)} ReviewCards:\n")

        for i, card in enumerate(cards, 1):
            print(f"--- Card {i} ---")
            print(f"Expectation ID: {card.node_expectation_id}")
            print(f"Rating: {card.rating}")
            print(f"Feedback: {card.feedback_text}")
            print()

    except ValueError as e:
        print(f"✗ Error: {e}")

    # 5. Test case: Section without expectations (should fail per AD 2.1)
    print("=" * 60)
    print("TEST 2: Reviewing Section 2 (has 0 expectations)")
    print("=" * 60)

    try:
        review, cards = service.generate_review(
            node_id=ids["section_2_id"],
            snippet_text=snippet_text,
            call_id=ids["call_id"],
        )
        print(f"✗ Unexpected success: {review.id}")

    except ValueError as e:
        print(f"✓ Correctly rejected: {e}")

    session.close()
    print("\n" + "=" * 60)
    print("All tests completed!")


if __name__ == "__main__":
    main()
