"""
Demo application: Competitor Product Selection

This example demonstrates a 3-step workflow for finding the best competitor
product to benchmark against a seller's product.

Steps:
1. Generate search keywords from product title/category (Gemini LLM)
2. Search and retrieve candidate products (mock API)
3. Apply filters and select the best match
"""

import os
import json
from typing import List, Optional, Tuple
import google.generativeai as genai
from ltrail_sdk import LTrail, JSONFileStorage, BackendClient, BackendStorage


def generate_keywords_with_gemini(
    product_title: str, category: str, api_key: str
) -> Tuple[List[str], str, bool]:
    """
    Generate search keywords using Gemini 2.0 Flash model.

    Args:
        product_title: The product title
        category: The product category
        api_key: Gemini API key

    Returns:
        Tuple of (keywords list, reasoning string, success flag)
    """
    # Configure Gemini
    genai.configure(api_key=api_key)

    # Create model instance
    model = genai.GenerativeModel("gemini-2.0-flash-exp")

    # Create prompt
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
        }}
    """

    try:
        # Generate response
        response = model.generate_content(prompt)

        # Check if response has errors
        if not response or not hasattr(response, "text") or not response.text:
            raise ValueError("Empty response from Gemini API")

        # Extract text
        response_text = response.text.strip()

        # Try to parse as JSON (Gemini might wrap in markdown code blocks)
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()

        # Parse JSON
        result = json.loads(response_text)
        keywords = result.get("keywords", [])
        reasoning = result.get("reasoning", "Generated keywords from product attributes")

        # Fallback if JSON parsing fails
        if not keywords:
            # Try to extract keywords from plain text
            lines = response_text.split("\n")
            keywords = [
                line.strip("- ").strip()
                for line in lines
                if line.strip() and not line.strip().startswith("{")
            ]
            if not keywords:
                keywords = [product_title.lower()]
            reasoning = "Extracted keywords from LLM response"

        return keywords, reasoning, True  # Success

    except json.JSONDecodeError as e:
        # Fallback if JSON parsing fails
        error_msg = f"Could not parse JSON response: {e}"
        print(f"Warning: {error_msg}")
        if "response_text" in locals():
        print(f"Response was: {response_text[:200]}")
        # Return fallback keywords
        return (
            [
                product_title.lower(),
                f"{category.lower()} {product_title.split()[0].lower()}",
            ],
            f"Fallback keywords due to parsing error: {error_msg}",
            False,  # Failed
        )
    except Exception as e:
        # Handle any other errors (including rate limits, API errors, etc.)
        error_type = type(e).__name__
        error_msg = str(e)

        # Check for specific error types
        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            error_msg = f"Rate limit exceeded: {error_msg}"
        elif "403" in error_msg or "permission" in error_msg.lower():
            error_msg = f"Permission denied: {error_msg}"
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            error_msg = f"Unauthorized: {error_msg}"
        else:
            error_msg = f"API error ({error_type}): {error_msg}"

        print(f"Error calling Gemini API: {error_msg}")
        # Return fallback keywords
        return (
            [
                product_title.lower(),
                f"{category.lower()} {product_title.split()[0].lower()}",
            ],
            f"Fallback keywords due to API error: {error_msg}",
            False,  # Failed
        )


def search_products(keywords: list, limit: int = 50) -> list:
    """Simulate product search API."""
    # Mock product data
    mock_products = [
        {
            "asin": "B0COMP01",
            "title": "HydroFlask 32oz Wide Mouth",
            "price": 44.99,
            "rating": 4.5,
            "reviews": 8932,
        },
        {
            "asin": "B0COMP02",
            "title": "Yeti Rambler 26oz",
            "price": 34.99,
            "rating": 4.4,
            "reviews": 5621,
        },
        {
            "asin": "B0COMP03",
            "title": "Generic Water Bottle",
            "price": 8.99,
            "rating": 3.2,
            "reviews": 45,
        },
        {
            "asin": "B0COMP04",
            "title": "Stanley Adventure Quencher 30oz",
            "price": 35.00,
            "rating": 4.3,
            "reviews": 4102,
        },
        {
            "asin": "B0COMP05",
            "title": "Premium Titanium Bottle 32oz",
            "price": 89.00,
            "rating": 4.8,
            "reviews": 234,
        },
    ]
    return mock_products[:limit]


def filter_and_select(reference_product: dict, candidates: list) -> dict:
    """Apply filters and select the best competitor."""
    # Calculate price range (0.5x - 2x of reference)
    min_price = reference_product["price"] * 0.5
    max_price = reference_product["price"] * 2.0
    min_rating = 3.8
    min_reviews = 100

    qualified = []
    for candidate in candidates:
        price_check = min_price <= candidate["price"] <= max_price
        rating_check = candidate["rating"] >= min_rating
        reviews_check = candidate["reviews"] >= min_reviews

        if price_check and rating_check and reviews_check:
            qualified.append(candidate)

    # Select best match (highest review count)
    if qualified:
        best = max(qualified, key=lambda x: x["reviews"])
        return best
    return None


def main():
    """Run the competitor selection workflow."""
    # Get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        print("Please set it with: export GEMINI_API_KEY='your-api-key'")
        print("On Windows PowerShell: $env:GEMINI_API_KEY='your-api-key'")
        print("On Windows CMD: set GEMINI_API_KEY=your-api-key")
        return

    # Reference product
    reference = {
        "asin": "B0XYZ123",
        "title": "ProBrand Steel Bottle 32oz Insulated",
        "price": 29.99,
        "rating": 4.2,
        "reviews": 1247,
        "category": "Sports & Outdoors",
    }

    # Initialize backend client for real-time updates
    # BackendClient will use LTRAIL_BACKEND_URL env var or default to production
    backend_client = BackendClient()  # Uses production backend by default

    # Also use JSON storage as backup
    json_storage = JSONFileStorage(output_dir="traces")

    # Start trace
    ltrail = LTrail.start_trace(
        name="Competitor Selection",
        metadata={"prospect_asin": reference["asin"], "environment": "demo"},
    )

    # Step 1: Keyword Generation with Gemini
    with ltrail.step("keyword_generation", step_type="llm_call") as step:
        step.log_input(
            {
                "product_title": reference["title"],
                "category": reference["category"],
                "model": "gemini-2.0-flash-exp",
            }
        )

        # Call Gemini API
        keywords, llm_reasoning, api_success = generate_keywords_with_gemini(
            reference["title"], reference["category"], api_key
        )

        # Set step status based on API call result
        if not api_success:
            step.set_status("error")

        step.log_output(
            {
                "keywords": keywords,
                "model": "gemini-2.0-flash-exp",
                "llm_reasoning": llm_reasoning,
                "api_success": api_success,
            }
        )
        step.set_reasoning(llm_reasoning)

        # Send step update to backend in real-time
        backend_client.send_step_update(ltrail.trace_id, step.to_dict())

    # Step 2: Candidate Search
    with ltrail.step("candidate_search", step_type="api_call") as step:
        candidates = search_products(keywords, limit=50)
        step.log_input({"keywords": keywords, "limit": 50})
        step.log_output(
            {
                "total_results": 2847,  # Mock total
                "candidates_fetched": len(candidates),
                "candidates": candidates,
            }
        )
        step.set_reasoning(f"Fetched top {len(candidates)} results by relevance")

        # Send step update to backend in real-time
        backend_client.send_step_update(ltrail.trace_id, step.to_dict())

    # Step 3: Filter & Select
    with ltrail.step("apply_filters", step_type="logic") as step:
        min_price = reference["price"] * 0.5
        max_price = reference["price"] * 2.0
        min_rating = 3.8
        min_reviews = 100

        step.log_input(
            {
                "candidates_count": len(candidates),
                "reference_product": reference,
            }
        )

        qualified = []
        for candidate in candidates:
            eval = step.add_evaluation(candidate["asin"], candidate["title"])

            price_check = min_price <= candidate["price"] <= max_price
            rating_check = candidate["rating"] >= min_rating
            reviews_check = candidate["reviews"] >= min_reviews

            eval.add_check(
                "price_range",
                price_check,
                f"${candidate['price']:.2f} is within ${min_price:.2f}-${max_price:.2f}",
            )
            eval.add_check(
                "min_rating",
                rating_check,
                f"{candidate['rating']} >= {min_rating}",
            )
            eval.add_check(
                "min_reviews",
                reviews_check,
                f"{candidate['reviews']} >= {min_reviews}",
            )

            if price_check and rating_check and reviews_check:
                qualified.append(candidate)
                eval.set_status("QUALIFIED")
            else:
                eval.set_status("REJECTED")

        # Select best match
        best_competitor = None
        if qualified:
            best_competitor = max(qualified, key=lambda x: x["reviews"])

        step.log_output(
            {
                "total_evaluated": len(candidates),
                "passed": len(qualified),
                "failed": len(candidates) - len(qualified),
            }
        )
        step.set_reasoning(
            f"Applied price, rating, and review count filters to narrow candidates from {len(candidates)} to {len(qualified)}"
        )

        # Send step update to backend in real-time
        backend_client.send_step_update(ltrail.trace_id, step.to_dict())

    # Complete trace
    final_output = {"selected_competitor": best_competitor} if best_competitor else None
    ltrail.complete(final_output=final_output)

    # Send complete trace to backend (synchronously to ensure it's sent)
    try:
        result = backend_client.send_trace(ltrail, async_send=False)
        if result:
            print(f"✓ Trace sent to backend successfully")
        else:
            print(f"⚠ Warning: Failed to send trace to backend (backend may not be running)")
    except Exception as e:
        print(f"⚠ Warning: Could not send trace to backend: {e}")
        print(f"  Traces are still saved locally. Backend may be unavailable.")

    # Also save to JSON file as backup
    filepath = json_storage.save_trace(ltrail)

    print(f"\n✓ Trace saved to: {filepath}")
    print(f"✓ Selected competitor: {best_competitor['title'] if best_competitor else 'None'}")
    print(f"✓ Trace ID: {ltrail.trace_id}")
    backend_url = backend_client.base_url
    dashboard_url = os.getenv(
        "LTRAIL_DASHBOARD_URL",
        "http://localhost:3000",  # Local dashboard URL
    )
    print(f"✓ View in dashboard: {dashboard_url}")
    print(f"  Or directly: {backend_url}/api/traces/{ltrail.trace_id}")


if __name__ == "__main__":
    main()
