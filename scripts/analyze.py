#!/usr/bin/env python3
"""Analyze probe results and generate a model-detection report."""

import argparse
import json
import re
import sys

MODEL_SIGNATURES = {
    "GPT-3.5 Turbo": {
        "provider": "OpenAI",
        "tier": "budget",
        "tier_rank": 1,
        "identity_keywords": ["gpt-3.5", "gpt 3.5", "chatgpt"],
        "cutoff_before": "2022-01",
        "strawberry_fail": True,
        "decimal_fail": True,
        "has_reasoning_tokens": False,
    },
    "GPT-4": {
        "provider": "OpenAI",
        "tier": "premium",
        "tier_rank": 4,
        "identity_keywords": ["gpt-4", "gpt 4"],
        "cutoff_before": "2023-05",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "GPT-4 Turbo": {
        "provider": "OpenAI",
        "tier": "premium",
        "tier_rank": 4,
        "identity_keywords": ["gpt-4-turbo", "gpt-4 turbo", "gpt4-turbo"],
        "cutoff_before": "2024-01",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "GPT-4o": {
        "provider": "OpenAI",
        "tier": "mid",
        "tier_rank": 3,
        "identity_keywords": ["gpt-4o"],
        "cutoff_before": "2024-01",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "GPT-4o Mini": {
        "provider": "OpenAI",
        "tier": "budget",
        "tier_rank": 1,
        "identity_keywords": ["gpt-4o-mini", "gpt-4o mini"],
        "cutoff_before": "2024-01",
        "strawberry_fail": True,
        "decimal_fail": True,
        "has_reasoning_tokens": False,
    },
    "o1": {
        "provider": "OpenAI",
        "tier": "premium",
        "tier_rank": 5,
        "identity_keywords": ["o1"],
        "cutoff_before": "2024-07",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": True,
    },
    "Claude 3 Haiku": {
        "provider": "Anthropic",
        "tier": "budget",
        "tier_rank": 1,
        "identity_keywords": ["claude 3 haiku", "claude-3-haiku"],
        "cutoff_before": "2024-04",
        "strawberry_fail": True,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "Claude 3 Sonnet": {
        "provider": "Anthropic",
        "tier": "mid",
        "tier_rank": 3,
        "identity_keywords": ["claude 3 sonnet", "claude-3-sonnet"],
        "cutoff_before": "2024-04",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "Claude 3 Opus": {
        "provider": "Anthropic",
        "tier": "premium",
        "tier_rank": 5,
        "identity_keywords": ["claude 3 opus", "claude-3-opus"],
        "cutoff_before": "2024-04",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "Claude 3.5 Sonnet": {
        "provider": "Anthropic",
        "tier": "mid",
        "tier_rank": 3,
        "identity_keywords": ["claude 3.5 sonnet", "claude-3.5-sonnet", "claude-3-5-sonnet"],
        "cutoff_before": "2024-05",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "Claude 3.5 Haiku": {
        "provider": "Anthropic",
        "tier": "budget",
        "tier_rank": 1,
        "identity_keywords": ["claude 3.5 haiku", "claude-3.5-haiku", "claude-3-5-haiku"],
        "cutoff_before": "2024-08",
        "strawberry_fail": True,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "Claude Sonnet 4": {
        "provider": "Anthropic",
        "tier": "mid",
        "tier_rank": 3,
        "identity_keywords": ["claude sonnet 4", "claude-sonnet-4"],
        "cutoff_before": "2025-04",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "Claude Opus 4": {
        "provider": "Anthropic",
        "tier": "premium",
        "tier_rank": 5,
        "identity_keywords": ["claude opus 4", "claude-opus-4"],
        "cutoff_before": "2025-04",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "Gemini 1.5 Pro": {
        "provider": "Google",
        "tier": "mid",
        "tier_rank": 3,
        "identity_keywords": ["gemini 1.5 pro", "gemini-1.5-pro"],
        "cutoff_before": "2024-01",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "Gemini 1.5 Flash": {
        "provider": "Google",
        "tier": "budget",
        "tier_rank": 1,
        "identity_keywords": ["gemini 1.5 flash", "gemini-1.5-flash"],
        "cutoff_before": "2024-01",
        "strawberry_fail": True,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
    "Llama 3 70B": {
        "provider": "Meta",
        "tier": "mid",
        "tier_rank": 2,
        "identity_keywords": ["llama 3", "llama-3", "llama3"],
        "cutoff_before": "2023-12",
        "strawberry_fail": True,
        "decimal_fail": True,
        "has_reasoning_tokens": False,
    },
    "Mistral Large": {
        "provider": "Mistral AI",
        "tier": "mid",
        "tier_rank": 3,
        "identity_keywords": ["mistral large", "mistral-large"],
        "cutoff_before": "2024-01",
        "strawberry_fail": False,
        "decimal_fail": False,
        "has_reasoning_tokens": False,
    },
}

TIER_LABELS = {
    1: "budget",
    2: "mid-low",
    3: "mid",
    4: "premium",
    5: "premium+",
}


def _get_probe(probes, name):
    """Return the probe entry with the given name, or None."""
    for p in probes:
        if p.get("name") == name:
            return p
    return None


def _check_strawberry(response_text):
    """Return True if the model answered the strawberry question correctly (3)."""
    if not response_text:
        return False
    return bool(re.search(r"\b3\b", response_text))


def _check_decimal(response_text):
    """Return True if the model correctly identified 9.9 as larger."""
    if not response_text:
        return False
    return "9.9" in response_text and "9.11" not in response_text.split("9.9")[0][-5:]


def _has_reasoning_tokens(probe_results):
    """Return True if any probe response contained reasoning_tokens in usage."""
    for p in probe_results:
        usage = p.get("usage") or {}
        if usage.get("reasoning_tokens"):
            return True
    return False


def score_models(probe_results):
    """Score each model signature against the probe results. Returns sorted list."""
    scores = {}

    identity_probe = _get_probe(probe_results, "self_identity")
    identity_text = (identity_probe.get("response") or "").lower() if identity_probe else ""

    strawberry_probe = _get_probe(probe_results, "strawberry_count")
    strawberry_correct = _check_strawberry(
        strawberry_probe.get("response") if strawberry_probe else None
    )

    decimal_probe = _get_probe(probe_results, "decimal_comparison")
    decimal_correct = _check_decimal(
        decimal_probe.get("response") if decimal_probe else None
    )

    has_reasoning = _has_reasoning_tokens(probe_results)

    for model_name, sig in MODEL_SIGNATURES.items():
        score = 0

        for kw in sig["identity_keywords"]:
            if kw in identity_text:
                score += 15
                break

        if sig["strawberry_fail"] and not strawberry_correct:
            score += 5
        elif not sig["strawberry_fail"] and strawberry_correct:
            score += 5

        if sig["decimal_fail"] and not decimal_correct:
            score += 5
        elif not sig["decimal_fail"] and decimal_correct:
            score += 5

        if sig["has_reasoning_tokens"] == has_reasoning:
            score += 10
        elif has_reasoning and not sig["has_reasoning_tokens"]:
            score -= 10

        scores[model_name] = score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked


def detect_dilution(claimed_model, detected_model):
    """Compare claimed vs detected model tiers. Returns info dict or None."""
    claimed_sig = None
    for name, sig in MODEL_SIGNATURES.items():
        if name.lower() == (claimed_model or "").lower():
            claimed_sig = sig
            claimed_name = name
            break

    detected_sig = MODEL_SIGNATURES.get(detected_model)

    if not claimed_sig or not detected_sig:
        return None

    tier_drop = claimed_sig["tier_rank"] - detected_sig["tier_rank"]
    if tier_drop > 0:
        return {
            "claimed": claimed_name,
            "claimed_tier": claimed_sig["tier"],
            "detected": detected_model,
            "detected_tier": detected_sig["tier"],
            "tier_drop": tier_drop,
        }
    return None


def generate_report(probe_data, claimed_model=None):
    """Generate a human-readable analysis report string."""
    metadata = probe_data.get("metadata", {})
    probes = probe_data.get("probes", [])
    ranked = score_models(probes)

    top_model, top_score = ranked[0] if ranked else ("Unknown", 0)
    top_sig = MODEL_SIGNATURES.get(top_model, {})

    if top_score >= 30:
        confidence = "HIGH"
    elif top_score >= 15:
        confidence = "MEDIUM"
    else:
        confidence = "LOW"

    claimed = claimed_model or metadata.get("claimed_model")

    lines = [
        "=" * 60,
        "  API MODEL DETECTOR -- ANALYSIS REPORT",
        "=" * 60,
        f"  Model param used: {metadata.get('model_param', 'N/A')}",
        f"  Claimed model   : {claimed or 'N/A'}",
    ]

    dilution = detect_dilution(claimed, top_model) if claimed else None
    if dilution:
        lines += [
            "",
            "  !! DILUTION ALERT",
            f"     Claimed : {dilution['claimed']} ({dilution['claimed_tier']} tier)",
            f"     Detected: {dilution['detected']} ({dilution['detected_tier']} tier)",
            f"     Tier drop: {dilution['tier_drop']} level(s) -- possible model substitution",
        ]

    lines += [
        "",
        f"  DETECTED MODEL : {top_model}",
        f"  Provider       : {top_sig.get('provider', 'Unknown')}",
        f"  Confidence     : {confidence} ({top_score} pts)",
    ]

    identity_probe = _get_probe(probes, "self_identity")
    cutoff_probe = _get_probe(probes, "knowledge_cutoff")
    strawberry_probe = _get_probe(probes, "strawberry_count")
    decimal_probe = _get_probe(probes, "decimal_comparison")

    latencies = [
        p["latency_seconds"]
        for p in probes
        if p.get("latency_seconds") is not None
    ]
    avg_latency = sum(latencies) / len(latencies) if latencies else None

    lines.append("")
    lines.append("  OBSERVATIONS")
    if identity_probe and identity_probe.get("response"):
        resp = identity_probe["response"][:80].replace("\n", " ")
        lines.append(f"  Self-identity  : {resp}")
    if cutoff_probe and cutoff_probe.get("response"):
        resp = cutoff_probe["response"][:60].replace("\n", " ")
        lines.append(f"  Knowledge cutoff: {resp}")
    if strawberry_probe:
        result = "PASS" if _check_strawberry(strawberry_probe.get("response")) else "FAIL"
        lines.append(f"  Strawberry test: {result}")
    if decimal_probe:
        result = "PASS" if _check_decimal(decimal_probe.get("response")) else "FAIL"
        lines.append(f"  Decimal test   : {result}")
    if avg_latency is not None:
        lines.append(f"  Avg latency    : {int(avg_latency * 1000)} ms")

    has_reasoning = _has_reasoning_tokens(probes)
    lines.append(f"  Reasoning tokens: {'YES' if has_reasoning else 'NO'}")

    lines.append("")
    lines.append("  TOP CANDIDATES")
    for i, (name, score) in enumerate(ranked[:5]):
        sig = MODEL_SIGNATURES.get(name, {})
        lines.append(
            f"  #{i + 1}  {name:<20s} score={score:<4d} tier={sig.get('tier', '?')}"
        )

    lines.append("=" * 60)
    return "\n".join(lines)


def build_parser():
    """Build and return the argument parser for analyze.py."""
    parser = argparse.ArgumentParser(
        prog="analyze",
        description=(
            "Analyze probe results from probe.py and generate a "
            "model-detection report."
        ),
    )
    parser.add_argument(
        "input_file",
        help="Path to the JSON probe results file produced by probe.py.",
    )
    parser.add_argument(
        "--claimed-model",
        default=None,
        help=(
            "Override the claimed model name for dilution detection. "
            "If omitted, uses the value from the probe results metadata."
        ),
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to write the report. Prints to stdout if omitted.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON instead of a human-readable report.",
    )
    return parser


def main(argv=None):
    """Entry point for analyze.py."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        with open(args.input_file, "r", encoding="utf-8") as fh:
            probe_data = json.load(fh)
    except FileNotFoundError:
        sys.exit(f"Error: file not found: {args.input_file}")
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: invalid JSON in {args.input_file}: {exc}")

    claimed = args.claimed_model or probe_data.get("metadata", {}).get("claimed_model")

    if args.json_output:
        ranked = score_models(probe_data.get("probes", []))
        top_model = ranked[0][0] if ranked else "Unknown"
        dilution = detect_dilution(claimed, top_model) if claimed else None
        output = json.dumps(
            {
                "detected_model": top_model,
                "scores": dict(ranked[:10]),
                "dilution": dilution,
            },
            indent=2,
            ensure_ascii=False,
        )
    else:
        output = generate_report(probe_data, claimed_model=claimed)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output + "\n")
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
