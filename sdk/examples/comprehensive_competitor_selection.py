"""
Comprehensive Competitor Product Selection Example

This example demonstrates a complete 5-step workflow for finding the best competitor
product to benchmark against a seller's product, with full X-Ray visibility.

Steps:
1. Generate search keywords from product title/category (LLM - non-deterministic)
2. Search and retrieve candidate products (API - large result set)
3. Apply filters (price range, rating threshold, review count, category match)
4. Use LLM to evaluate relevance and eliminate false positives (LLM - non-deterministic)
5. Rank and select the single best competitor
"""

import os
import json
import time
from typing import List, Optional, Tuple, Dict, Any
import google.generativeai as genai

# try:
#     import google.genai as genai
# except ImportError:
#     # Fallback to deprecated package if new one not available
#     import warnings

#     warnings.filterwarnings("ignore", category=FutureWarning)

from ltrail_sdk import LTrail, JSONFileStorage, BackendClient, BackendStorage


def generate_keywords_with_llm(
    product_title: str, category: str, api_key: str
) -> Tuple[List[str], str, bool]:
    """
    Step 1: Generate search keywords using Gemini LLM.

    Args:
        product_title: The product title
        category: The product category
        api_key: Gemini API key

    Returns:
        Tuple of (keywords list, reasoning string, success flag)
    """
    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""Given the following product information, generate 3-5 search keywords that would help find similar competitor products on an e-commerce platform.

Product Title: {product_title}
Category: {category}

Generate keywords that:
1. Capture the key product attributes (material, size, features)
2. Are commonly used in product searches
3. Would help find direct competitors

Return your response as a JSON object with two fields:
- "keywords": an array of 3-5 keyword strings
- "reasoning": a brief explanation of why these keywords were chosen

Example format:
{{
    "keywords": ["stainless steel water bottle insulated", "vacuum insulated bottle 32oz", "insulated flask"],
    "reasoning": "Extracted key attributes: material (stainless steel), capacity (32oz), and key feature (insulated/vacuum)"
}}"""

    try:
        response = model.generate_content(prompt)

        if not response or not hasattr(response, "text") or not response.text:
            raise ValueError("Empty response from Gemini API")

        response_text = response.text.strip()

        # Clean markdown code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        # Parse JSON
        result = json.loads(response_text)
        keywords = result.get("keywords", [])
        reasoning = result.get("reasoning", "Generated keywords from product attributes")

        if not keywords:
            keywords = [product_title.lower()]
            reasoning = "Fallback: used product title as keyword"

        return keywords, reasoning, True

    except json.JSONDecodeError as e:
        error_msg = f"Could not parse JSON response: {e}"
        return (
            [product_title.lower(), f"{category.lower()} {product_title.split()[0].lower()}"],
            f"Fallback keywords due to parsing error: {error_msg}",
            False,
        )
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)

        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            error_msg = f"Rate limit exceeded: {error_msg}"
        elif "403" in error_msg or "permission" in error_msg.lower():
            error_msg = f"Permission denied: {error_msg}"
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            error_msg = f"Unauthorized: {error_msg}"
        else:
            error_msg = f"API error ({error_type}): {error_msg}"

        return (
            [product_title.lower(), f"{category.lower()} {product_title.split()[0].lower()}"],
            f"Fallback keywords due to API error: {error_msg}",
            False,
        )


def search_products(keywords: List[str], limit: int = 50) -> Tuple[List[Dict[str, Any]], int]:
    """
    Step 2: Search and retrieve candidate products (mock API).

    Args:
        keywords: List of search keywords
        limit: Maximum number of results to return

    Returns:
        Tuple of (products list, total_results count)
    """
    # Simulate API delay
    time.sleep(0.1)

    # Mock product database
    mock_products = [
        {
            "asin": "B0COMP01",
            "title": "HydroFlask 32oz Wide Mouth Water Bottle",
            "price": 44.99,
            "rating": 4.5,
            "reviews": 8932,
            "category": "Sports & Outdoors > Water Bottles",
        },
        {
            "asin": "B0COMP02",
            "title": "Yeti Rambler 26oz Insulated Bottle",
            "price": 34.99,
            "rating": 4.4,
            "reviews": 5621,
            "category": "Sports & Outdoors > Water Bottles",
        },
        {
            "asin": "B0COMP03",
            "title": "Generic Water Bottle Plastic",
            "price": 8.99,
            "rating": 3.2,
            "reviews": 45,
            "category": "Sports & Outdoors > Water Bottles",
        },
        {
            "asin": "B0COMP04",
            "title": "Stanley Adventure Quencher 30oz",
            "price": 35.00,
            "rating": 4.3,
            "reviews": 4102,
            "category": "Sports & Outdoors > Water Bottles",
        },
        {
            "asin": "B0COMP05",
            "title": "Premium Titanium Bottle 32oz Insulated",
            "price": 89.00,
            "rating": 4.8,
            "reviews": 234,
            "category": "Sports & Outdoors > Water Bottles",
        },
        {
            "asin": "B0COMP06",
            "title": "Replacement Lid for HydroFlask",
            "price": 12.99,
            "rating": 4.6,
            "reviews": 3421,
            "category": "Sports & Outdoors > Water Bottle Accessories",
        },
        {
            "asin": "B0COMP07",
            "title": "Water Bottle Cleaning Brush Set",
            "price": 9.99,
            "rating": 4.7,
            "reviews": 2103,
            "category": "Sports & Outdoors > Water Bottle Accessories",
        },
        {
            "asin": "B0COMP08",
            "title": "CamelBak Chute Mag 32oz",
            "price": 29.99,
            "rating": 4.5,
            "reviews": 6789,
            "category": "Sports & Outdoors > Water Bottles",
        },
        {
            "asin": "B0COMP09",
            "title": "Nalgene Wide Mouth 32oz",
            "price": 14.99,
            "rating": 4.2,
            "reviews": 5234,
            "category": "Sports & Outdoors > Water Bottles",
        },
        {
            "asin": "B0COMP10",
            "title": "Klean Kanteen Classic 32oz",
            "price": 39.99,
            "rating": 4.4,
            "reviews": 4567,
            "category": "Sports & Outdoors > Water Bottles",
        },
    ]

    # Simulate search results (in real scenario, this would be an API call)
    total_results = 2847  # Mock total from search API
    return mock_products[:limit], total_results


def apply_filters(
    reference_product: Dict[str, Any], candidates: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Step 3: Apply filters to narrow down candidates.

    Args:
        reference_product: The reference product to compare against
        candidates: List of candidate products

    Returns:
        Tuple of (qualified products, rejected products)
    """
    min_price = reference_product["price"] * 0.5
    max_price = reference_product["price"] * 2.0
    min_rating = 3.8
    min_reviews = 100

    qualified = []
    rejected = []

    for candidate in candidates:
        price_check = min_price <= candidate["price"] <= max_price
        rating_check = candidate["rating"] >= min_rating
        reviews_check = candidate["reviews"] >= min_reviews
        category_match = "Water Bottle" in candidate.get(
            "category", ""
        ) and "Accessories" not in candidate.get("category", "")

        if price_check and rating_check and reviews_check and category_match:
            qualified.append(candidate)
        else:
            rejected.append(candidate)

    return qualified, rejected


def evaluate_relevance_with_llm(
    reference_product: Dict[str, Any], candidates: List[Dict[str, Any]], api_key: str
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], str, bool]:
    """
    Step 4: Use LLM to evaluate relevance and eliminate false positives.

    Args:
        reference_product: The reference product
        candidates: List of candidate products to evaluate
        api_key: Gemini API key

    Returns:
        Tuple of (confirmed competitors, false positives, reasoning, success flag)
    """
    if not candidates:
        return [], [], "No candidates to evaluate", True

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Build evaluation prompt
    candidates_text = "\n".join(
        [
            f"- {c['title']} (${c['price']:.2f}, {c['rating']}★, {c['reviews']} reviews)"
            for c in candidates
        ]
    )

    prompt = f"""Given the reference product below, determine which candidates are TRUE COMPETITORS (same product type) vs FALSE POSITIVES (accessories, replacement parts, bundles, or unrelated items).

Reference Product:
Title: {reference_product['title']}
Category: {reference_product.get('category', 'Unknown')}
Price: ${reference_product['price']:.2f}

Candidates to evaluate:
{candidates_text}

For each candidate, determine if it's a true competitor or false positive.

Return your response as a JSON object with this structure:
{{
    "evaluations": [
        {{
            "title": "product title",
            "is_competitor": true/false,
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation"
        }}
    ],
    "summary": "overall summary of evaluation"
}}"""

    try:
        response = model.generate_content(prompt)

        if not response or not hasattr(response, "text") or not response.text:
            raise ValueError("Empty response from Gemini API")

        response_text = response.text.strip()

        # Clean markdown
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        result = json.loads(response_text)
        evaluations = result.get("evaluations", [])
        summary = result.get("summary", "LLM evaluation completed")

        # Match evaluations to candidates
        confirmed = []
        false_positives = []

        for eval_data in evaluations:
            title = eval_data.get("title", "")
            is_competitor = eval_data.get("is_competitor", False)
            confidence = eval_data.get("confidence", 0.5)
            reasoning = eval_data.get("reasoning", "")

            # Find matching candidate
            candidate = next(
                (
                    c
                    for c in candidates
                    if title.lower() in c["title"].lower() or c["title"].lower() in title.lower()
                ),
                None,
            )

            if candidate:
                candidate["llm_evaluation"] = {
                    "is_competitor": is_competitor,
                    "confidence": confidence,
                    "reasoning": reasoning,
                }

                if is_competitor and confidence > 0.7:
                    confirmed.append(candidate)
                else:
                    false_positives.append(candidate)

        # If LLM didn't match all, assume remaining are competitors
        matched_titles = {c["title"] for c in confirmed + false_positives}
        for candidate in candidates:
            if candidate["title"] not in matched_titles:
                # Default to competitor if not explicitly marked as false positive
                confirmed.append(candidate)

        return confirmed, false_positives, summary, True

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)

        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            error_msg = f"Rate limit exceeded: {error_msg}"
        else:
            error_msg = f"LLM evaluation error ({error_type}): {error_msg}"

        # On error, assume all are competitors (fail open)
        return (
            candidates,
            [],
            f"Fallback: All candidates assumed competitors due to error: {error_msg}",
            False,
        )


def rank_and_select(
    reference_product: Dict[str, Any], competitors: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Step 5: Rank and select the single best competitor.

    Args:
        reference_product: The reference product
        competitors: List of confirmed competitor products

    Returns:
        The best competitor product or None
    """
    if not competitors:
        return None

    def calculate_score(candidate: Dict[str, Any]) -> float:
        """Calculate ranking score for a candidate."""
        # Primary: review count (normalized)
        max_reviews = max((c["reviews"] for c in competitors), default=1)
        review_score = candidate["reviews"] / max_reviews

        # Secondary: rating (normalized)
        max_rating = max((c["rating"] for c in competitors), default=5.0)
        rating_score = candidate["rating"] / max_rating

        # Tertiary: price proximity (closer to reference is better)
        price_diff = abs(candidate["price"] - reference_product["price"])
        max_price_diff = max(
            (abs(c["price"] - reference_product["price"]) for c in competitors), default=1.0
        )
        price_proximity_score = 1.0 - (price_diff / max_price_diff) if max_price_diff > 0 else 0.5

        # LLM confidence boost (if available)
        llm_boost = 1.0
        if "llm_evaluation" in candidate:
            llm_boost = candidate["llm_evaluation"].get("confidence", 0.5)

        # Weighted combination
        total_score = (
            review_score * 0.5  # 50% weight on reviews
            + rating_score * 0.3  # 30% weight on rating
            + price_proximity_score * 0.15  # 15% weight on price proximity
            + llm_boost * 0.05  # 5% weight on LLM confidence
        )

        return total_score

    # Rank all competitors
    ranked = sorted(competitors, key=calculate_score, reverse=True)

    # Store scores for debugging
    for i, candidate in enumerate(ranked):
        candidate["ranking_score"] = calculate_score(candidate)
        candidate["rank"] = i + 1

    return ranked[0] if ranked else None


def main():
    """Run the comprehensive competitor selection workflow."""
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set it with: export GEMINI_API_KEY='your-api-key'")
        print("On Windows PowerShell: $env:GEMINI_API_KEY='your-api-key'")
        return

    # Reference product
    reference = {
        "asin": "B0XYZ123",
        "title": "ProBrand Steel Bottle 32oz Insulated",
        "price": 29.99,
        "rating": 4.2,
        "reviews": 1247,
        "category": "Sports & Outdoors > Water Bottles",
    }

    # Initialize backend client and storage
    # BackendClient will use LTRAIL_BACKEND_URL env var or default to production
    backend_client = BackendClient()  # Uses production backend by default
    json_storage = JSONFileStorage(output_dir="traces")

    # Start trace
    ltrail = LTrail.start_trace(
        name="Comprehensive Competitor Selection",
        metadata={
            "prospect_asin": reference["asin"],
            "environment": "demo",
            "workflow_version": "5-step",
        },
    )

    # Step 1: Keyword Generation (LLM)
    with ltrail.step("keyword_generation", step_type="llm_call") as step:
        step.log_input(
            {
                "product_title": reference["title"],
                "category": reference["category"],
                "model": "gemini-2.5-flash",
            }
        )

        keywords, reasoning, success = generate_keywords_with_llm(
            reference["title"], reference["category"], api_key
        )

        if not success:
            step.set_status("error")

        step.log_output(
            {
                "keywords": keywords,
                "model": "gemini-2.5-flash",
                "reasoning": reasoning,
                "api_success": success,
            }
        )
        step.set_reasoning(reasoning)
        backend_client.send_step_update(ltrail.trace_id, step.to_dict())

    # Step 2: Candidate Search (API)
    with ltrail.step("candidate_search", step_type="api_call") as step:
        candidates, total_results = search_products(keywords, limit=50)

        step.log_input(
            {
                "keywords": keywords,
                "limit": 50,
            }
        )
        step.log_output(
            {
                "total_results": total_results,
                "candidates_fetched": len(candidates),
                "candidates": candidates,
            }
        )
        step.set_reasoning(
            f"Fetched top {len(candidates)} results from {total_results} total matches"
        )
        backend_client.send_step_update(ltrail.trace_id, step.to_dict())

    # Step 3: Apply Filters
    with ltrail.step("apply_filters", step_type="logic") as step:
        min_price = reference["price"] * 0.5
        max_price = reference["price"] * 2.0
        min_rating = 3.8
        min_reviews = 100

        step.log_input(
            {
                "candidates_count": len(candidates),
                "reference_product": reference,
                "filters": {
                    "price_range": {
                        "min": min_price,
                        "max": max_price,
                        "rule": "0.5x - 2x of reference",
                    },
                    "min_rating": {"value": min_rating, "rule": "Must be at least 3.8 stars"},
                    "min_reviews": {"value": min_reviews, "rule": "Must have at least 100 reviews"},
                    "category_match": {
                        "rule": "Must be in Water Bottles category, not accessories"
                    },
                },
            }
        )

        qualified, rejected = apply_filters(reference, candidates)

        # Log evaluations for each candidate
        for candidate in candidates:
            eval_obj = step.add_evaluation(candidate["asin"], candidate["title"])

            price_check = min_price <= candidate["price"] <= max_price
            rating_check = candidate["rating"] >= min_rating
            reviews_check = candidate["reviews"] >= min_reviews
            category_check = "Water Bottle" in candidate.get(
                "category", ""
            ) and "Accessories" not in candidate.get("category", "")

            eval_obj.add_check(
                "price_range",
                price_check,
                (
                    f"${candidate['price']:.2f} is within ${min_price:.2f}-${max_price:.2f}"
                    if price_check
                    else f"${candidate['price']:.2f} is outside ${min_price:.2f}-${max_price:.2f}"
                ),
            )
            eval_obj.add_check(
                "min_rating",
                rating_check,
                (
                    f"{candidate['rating']} >= {min_rating}"
                    if rating_check
                    else f"{candidate['rating']} < {min_rating}"
                ),
            )
            eval_obj.add_check(
                "min_reviews",
                reviews_check,
                (
                    f"{candidate['reviews']} >= {min_reviews}"
                    if reviews_check
                    else f"{candidate['reviews']} < {min_reviews}"
                ),
            )
            eval_obj.add_check(
                "category_match",
                category_check,
                "Category matches" if category_check else "Category mismatch or accessory",
            )

            if candidate in qualified:
                eval_obj.set_status("QUALIFIED")
            else:
                eval_obj.set_status("REJECTED")

        step.log_output(
            {
                "total_evaluated": len(candidates),
                "qualified": len(qualified),
                "rejected": len(rejected),
            }
        )
        step.set_reasoning(f"Applied filters: {len(qualified)} qualified, {len(rejected)} rejected")
        backend_client.send_step_update(ltrail.trace_id, step.to_dict())

    # Step 4: LLM Relevance Evaluation
    with ltrail.step("llm_relevance_evaluation", step_type="llm_call") as step:
        step.log_input(
            {
                "candidates_count": len(qualified),
                "reference_product": reference,
                "model": "gemini-2.5-flash",
            }
        )

        confirmed, false_positives, llm_reasoning, llm_success = evaluate_relevance_with_llm(
            reference, qualified, api_key
        )

        if not llm_success:
            step.set_status("error")

        # Log LLM evaluations
        for candidate in qualified:
            eval_obj = step.add_evaluation(candidate["asin"], candidate["title"])

            if "llm_evaluation" in candidate:
                eval_data = candidate["llm_evaluation"]
                eval_obj.add_check(
                    "is_competitor",
                    eval_data["is_competitor"],
                    eval_data["reasoning"],
                )
                eval_obj.add_check(
                    "confidence",
                    eval_data["confidence"] > 0.7,
                    f"Confidence: {eval_data['confidence']:.2f}",
                )

                if candidate in confirmed:
                    eval_obj.set_status("CONFIRMED_COMPETITOR")
                else:
                    eval_obj.set_status("FALSE_POSITIVE")

        step.log_output(
            {
                "total_evaluated": len(qualified),
                "confirmed_competitors": len(confirmed),
                "false_positives_removed": len(false_positives),
                "evaluations": [
                    {
                        "asin": c["asin"],
                        "title": c["title"],
                        "is_competitor": c.get("llm_evaluation", {}).get("is_competitor", True),
                        "confidence": c.get("llm_evaluation", {}).get("confidence", 0.5),
                    }
                    for c in qualified
                ],
            }
        )
        step.set_reasoning(llm_reasoning)
        backend_client.send_step_update(ltrail.trace_id, step.to_dict())

    # Step 5: Rank and Select
    with ltrail.step("rank_and_select", step_type="logic") as step:
        step.log_input(
            {
                "candidates_count": len(confirmed),
                "reference_product": reference,
                "ranking_criteria": {
                    "primary": "review_count",
                    "secondary": "rating",
                    "tertiary": "price_proximity",
                    "llm_confidence": "boost_factor",
                },
            }
        )

        best_competitor = rank_and_select(reference, confirmed)

        # Log ranking details
        ranked_list = sorted(confirmed, key=lambda x: x.get("ranking_score", 0), reverse=True)

        step.log_output(
            {
                "selected_competitor": best_competitor,
                "ranked_candidates": [
                    {
                        "rank": c.get("rank", 0),
                        "asin": c["asin"],
                        "title": c["title"],
                        "metrics": {
                            "price": c["price"],
                            "rating": c["rating"],
                            "reviews": c["reviews"],
                        },
                        "ranking_score": c.get("ranking_score", 0),
                    }
                    for c in ranked_list[:5]  # Top 5
                ],
            }
        )

        if best_competitor:
            step.set_reasoning(
                f"Selected {best_competitor['title']} with score {best_competitor.get('ranking_score', 0):.2f} "
                f"(reviews: {best_competitor['reviews']}, rating: {best_competitor['rating']}★)"
            )
        else:
            step.set_status("error")
            step.set_reasoning("No competitor selected - no qualified candidates")

        backend_client.send_step_update(ltrail.trace_id, step.to_dict())

    # Complete trace
    final_output = {"selected_competitor": best_competitor} if best_competitor else None
    ltrail.complete(final_output=final_output)

    # Send complete trace to backend
    try:
        result = backend_client.send_trace(ltrail, async_send=False)
        if result:
            print(f"✓ Trace sent to backend successfully")
        else:
            print(f"⚠ Warning: Failed to send trace to backend (backend may not be running)")
    except Exception as e:
        print(f"⚠ Warning: Could not send trace to backend: {e}")
        print(f"  Traces are still saved locally. Backend may be unavailable.")

    # Save to JSON file as backup
    filepath = json_storage.save_trace(ltrail)

    print(f"\n{'='*60}")
    print(f"✓ Trace saved to: {filepath}")
    print(f"✓ Trace ID: {ltrail.trace_id}")
    print(f"✓ Selected competitor: {best_competitor['title'] if best_competitor else 'None'}")
    if best_competitor:
        print(f"  - Price: ${best_competitor['price']:.2f}")
        print(f"  - Rating: {best_competitor['rating']}★")
        print(f"  - Reviews: {best_competitor['reviews']:,}")
        print(f"  - Ranking Score: {best_competitor.get('ranking_score', 0):.2f}")
    backend_url = backend_client.base_url
    dashboard_url = os.getenv(
        "LTRAIL_DASHBOARD_URL",
        "http://localhost:3000",  # Local dashboard URL
    )
    print(f"✓ View in dashboard: {dashboard_url}")
    print(f"  Or directly: {backend_url}/api/traces/{ltrail.trace_id}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
