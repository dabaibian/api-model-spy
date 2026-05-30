#!/usr/bin/env python3
"""Send fingerprinting probes to a target LLM API and record the results."""

import argparse
import json
import sys
import time

PROBES = [
    {
        "name": "self_identity",
        "prompt": "What model are you? Please state your exact model name and version.",
    },
    {
        "name": "knowledge_cutoff",
        "prompt": (
            "What is the most recent event you have knowledge of? "
            "State your knowledge cutoff date in YYYY-MM format."
        ),
    },
    {
        "name": "strawberry_count",
        "prompt": "How many letter 'r's are in the word 'strawberry'?",
    },
    {
        "name": "decimal_comparison",
        "prompt": "Which is larger, 9.11 or 9.9? Answer with just the number.",
    },
    {
        "name": "multi_step_math",
        "prompt": "What is 17 * 23 + 89 - 14 * 3? Show your work step by step.",
    },
    {
        "name": "logic_puzzle",
        "prompt": (
            "All roses are flowers. Some flowers fade quickly. "
            "Can we conclude that some roses fade quickly? Explain your reasoning."
        ),
    },
    {
        "name": "token_awareness",
        "prompt": (
            "How many tokens does the sentence 'The quick brown fox jumps over the lazy dog' "
            "contain? Estimate and explain."
        ),
    },
    {
        "name": "coding_task",
        "prompt": (
            "Write a Python one-liner that checks if a string is a palindrome. "
            "Return only the code, no explanation."
        ),
    },
]


def _send_openai(client, model, prompt):
    """Send a single prompt via the OpenAI-compatible chat completions API."""
    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=512,
    )
    latency = time.time() - start
    message = response.choices[0].message.content or ""
    usage = None
    if response.usage:
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
        if hasattr(response.usage, "completion_tokens_details"):
            details = response.usage.completion_tokens_details
            if details and hasattr(details, "reasoning_tokens"):
                usage["reasoning_tokens"] = details.reasoning_tokens
    return message.strip(), latency, usage


def _send_anthropic(client, model, prompt):
    """Send a single prompt via the Anthropic messages API."""
    start = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    latency = time.time() - start
    text = ""
    for block in response.content:
        if block.type == "text":
            text += block.text
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return text.strip(), latency, usage


def run_probes(api_type, api_key, model, endpoint, claimed_model, verbose=False):
    """Execute all probes and return a results dict."""
    if api_type == "openai":
        try:
            from openai import OpenAI
        except ImportError:
            sys.exit("Error: 'openai' package is required. Install with: pip install openai")
        kwargs = {"api_key": api_key}
        if endpoint:
            kwargs["base_url"] = endpoint
        client = OpenAI(**kwargs)
        send = lambda prompt: _send_openai(client, model, prompt)
    elif api_type == "anthropic":
        try:
            from anthropic import Anthropic
        except ImportError:
            sys.exit("Error: 'anthropic' package is required. Install with: pip install anthropic")
        client = Anthropic(api_key=api_key)
        send = lambda prompt: _send_anthropic(client, model, prompt)
    else:
        sys.exit(f"Error: unsupported api-type '{api_type}'. Use 'openai' or 'anthropic'.")

    results = {
        "metadata": {
            "api_type": api_type,
            "model_param": model,
            "claimed_model": claimed_model,
            "endpoint": endpoint or "(default)",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "probes": [],
    }

    for probe in PROBES:
        if verbose:
            print(f"  Sending probe: {probe['name']} ...", end=" ", flush=True)
        try:
            response_text, latency, usage = send(probe["prompt"])
            entry = {
                "name": probe["name"],
                "prompt": probe["prompt"],
                "response": response_text,
                "latency_seconds": round(latency, 3),
                "usage": usage,
                "error": None,
            }
            if verbose:
                print(f"done ({latency:.2f}s)")
        except Exception as exc:
            entry = {
                "name": probe["name"],
                "prompt": probe["prompt"],
                "response": None,
                "latency_seconds": None,
                "usage": None,
                "error": str(exc),
            }
            if verbose:
                print(f"FAILED: {exc}")
        results["probes"].append(entry)

    return results


def build_parser():
    """Build and return the argument parser for probe.py."""
    parser = argparse.ArgumentParser(
        prog="probe",
        description=(
            "Send fingerprinting probes to a target LLM API endpoint and "
            "record the raw responses for later analysis."
        ),
    )
    parser.add_argument(
        "--api-type",
        required=True,
        choices=["openai", "anthropic"],
        help="API protocol to use: 'openai' (OpenAI-compatible) or 'anthropic'.",
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="API key for authenticating with the target endpoint.",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Model identifier to pass to the API (e.g. 'gpt-4-turbo').",
    )
    parser.add_argument(
        "--endpoint",
        default=None,
        help=(
            "Base URL of the API endpoint. Defaults to the provider's "
            "official endpoint if omitted."
        ),
    )
    parser.add_argument(
        "--claimed-model",
        default=None,
        help=(
            "The model name the provider *claims* to serve. Used during "
            "analysis to detect dilution."
        ),
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to write JSON results. Prints to stdout if omitted.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print progress messages while probing.",
    )
    return parser


def main(argv=None):
    """Entry point for probe.py."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        print(f"Probing {args.model} via {args.api_type} API ...")

    results = run_probes(
        api_type=args.api_type,
        api_key=args.api_key,
        model=args.model,
        endpoint=args.endpoint,
        claimed_model=args.claimed_model,
        verbose=args.verbose,
    )

    json_output = json.dumps(results, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(json_output + "\n")
        if args.verbose:
            print(f"Results written to {args.output}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
