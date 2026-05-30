#!/usr/bin/env python3
"""Unified CLI for api-model-spy: probe and analyze LLM API endpoints."""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from probe import build_parser as probe_parser, main as probe_main
from analyze import build_parser as analyze_parser, main as analyze_main


def main():
    parser = argparse.ArgumentParser(
        prog="api-model-spy",
        description=(
            "Detect API model dilution and fingerprint which LLM is "
            "actually running behind any endpoint."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- probe subcommand ---
    sp_probe = subparsers.add_parser(
        "probe",
        help="Send fingerprinting probes to a target API.",
        description=(
            "Send fingerprinting probes to a target LLM API endpoint and "
            "record the raw responses for later analysis."
        ),
    )
    sp_probe.add_argument(
        "--api-type",
        required=True,
        choices=["openai", "anthropic"],
        help="API protocol to use: 'openai' (OpenAI-compatible) or 'anthropic'.",
    )
    sp_probe.add_argument(
        "--api-key",
        required=True,
        help="API key for authenticating with the target endpoint.",
    )
    sp_probe.add_argument(
        "--model",
        required=True,
        help="Model identifier to pass to the API (e.g. 'gpt-4-turbo').",
    )
    sp_probe.add_argument(
        "--endpoint",
        default=None,
        help="Base URL of the API endpoint.",
    )
    sp_probe.add_argument(
        "--claimed-model",
        default=None,
        help="The model name the provider claims to serve.",
    )
    sp_probe.add_argument(
        "--output", "-o",
        default=None,
        help="Path to write JSON results. Prints to stdout if omitted.",
    )
    sp_probe.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print progress messages while probing.",
    )

    # --- analyze subcommand ---
    sp_analyze = subparsers.add_parser(
        "analyze",
        help="Analyze probe results and generate a report.",
        description=(
            "Analyze probe results from the probe command and generate a "
            "model-detection report."
        ),
    )
    sp_analyze.add_argument(
        "input_file",
        help="Path to the JSON probe results file.",
    )
    sp_analyze.add_argument(
        "--claimed-model",
        default=None,
        help="Override the claimed model name for dilution detection.",
    )
    sp_analyze.add_argument(
        "--output", "-o",
        default=None,
        help="Path to write the report. Prints to stdout if omitted.",
    )
    sp_analyze.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON instead of a human-readable report.",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "probe":
        argv = []
        argv += ["--api-type", args.api_type]
        argv += ["--api-key", args.api_key]
        argv += ["--model", args.model]
        if args.endpoint:
            argv += ["--endpoint", args.endpoint]
        if args.claimed_model:
            argv += ["--claimed-model", args.claimed_model]
        if args.output:
            argv += ["--output", args.output]
        if args.verbose:
            argv += ["--verbose"]
        probe_main(argv)

    elif args.command == "analyze":
        argv = [args.input_file]
        if args.claimed_model:
            argv += ["--claimed-model", args.claimed_model]
        if args.output:
            argv += ["--output", args.output]
        if args.json_output:
            argv += ["--json"]
        analyze_main(argv)


if __name__ == "__main__":
    main()
