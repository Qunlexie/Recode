#!/usr/bin/env python3
"""End-to-end code validation pipeline.

The previous implementation relied on many ad-hoc text heuristics that fought
each other and occasionally truncated code. This module redesigns the pipeline
around a small set of well-defined stages:

1. Normalisation – replace problematic Unicode symbols, normalise whitespace.
2. Parsing – attempt an `ast.parse` of the normalised source.
3. Formatting – when parsing succeeds, run the source through `black` to obtain
   canonical layout.
4. Validation – re-parse the formatted output and collect structured warnings.

Each stage receives and returns a clear contract so that failures can be
reported precisely instead of being silently “fixed”.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import black
import streamlit as st


class ValidationLevel(Enum):
    """Validation levels for code checking"""
    BASIC = "basic"
    STRICT = "strict"
    COMPREHENSIVE = "comprehensive"


@dataclass
class ValidationResult:
    """Result of code validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    fixed_code: str
    validation_level: ValidationLevel


@dataclass
class NormalisationReport:
    """Information captured during the normalisation stage."""

    code: str
    warnings: List[str] = field(default_factory=list)
    replacement_counts: Dict[str, int] = field(default_factory=dict)


@dataclass
class ParseResult:
    """Outcome of attempting to parse Python source."""

    success: bool
    tree: Optional[ast.AST] = None
    error: Optional[str] = None


class CodeValidator:
    """End-to-end validation pipeline built from explicit stages."""

    UNICODE_REPLACEMENTS: Dict[str, str] = {
        "→": "->",
        "≤": "<=",
        "≥": ">=",
        "≠": "!=",
        "∞": "float(\"inf\")",
        "∅": "set()",
        "∈": "in",
        "∉": "not in",
        "∧": "and",
        "∨": "or",
        "¬": "not",
        "∀": "# for all",
        "∃": "# exists",
        "≈": "==",
        "≡": "==",
        "≢": "!=",
        "≮": ">=",
        "≯": "<=",
        "×": "*",
        "÷": "/",
        "±": "+/-",
    }

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.COMPREHENSIVE) -> None:
        self.validation_level = validation_level

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def validate_and_fix_code(self, code: str, debug: bool = False) -> ValidationResult:
        """Validate *code* and return a structured report."""

        if not code or not code.strip():
            warnings = ["Empty code provided"]
            suggestions = ["Provide code to validate"]
            return ValidationResult(
                is_valid=True,
                errors=[],
                warnings=warnings,
                suggestions=suggestions,
                fixed_code=code,
                validation_level=self.validation_level,
            )

        normalised = self._normalise_code(code)
        warnings: List[str] = list(normalised.warnings)
        suggestions: List[str] = []

        working_code = normalised.code

        parse_before = self._parse_source(working_code)
        if not parse_before.success:
            error_message = parse_before.error or "Unknown parse failure"
            return ValidationResult(
                is_valid=False,
                errors=[error_message],
                warnings=warnings,
                suggestions=suggestions,
                fixed_code=working_code,
                validation_level=self.validation_level,
            )

        formatted_code, formatting_warnings = self._format_code(working_code)
        warnings.extend(formatting_warnings)

        parse_after = self._parse_source(formatted_code)
        if not parse_after.success:
            error_message = parse_after.error or "Formatted code failed to parse"
            return ValidationResult(
                is_valid=False,
                errors=[error_message],
                warnings=warnings,
                suggestions=suggestions,
                fixed_code=working_code,
                validation_level=self.validation_level,
            )

        analysis_warnings, analysis_suggestions = self._analyse_ast(parse_after.tree)
        warnings.extend(analysis_warnings)
        suggestions.extend(analysis_suggestions)

        if debug:
            self._emit_debug_info(
                original=code,
                normalised=normalised.code,
                formatted=formatted_code,
                warnings=warnings,
            )

        return ValidationResult(
            is_valid=True,
            errors=[],
            warnings=warnings,
            suggestions=suggestions,
            fixed_code=formatted_code,
            validation_level=self.validation_level,
        )

    # ------------------------------------------------------------------
    # Pipeline stages
    # ------------------------------------------------------------------
    def _normalise_code(self, code: str) -> NormalisationReport:
        """Replace known Unicode symbols and normalise whitespace."""

        replacement_counts: Dict[str, int] = {}
        normalised = code.replace("\r\n", "\n").replace("\r", "\n")

        for symbol, replacement in self.UNICODE_REPLACEMENTS.items():
            if symbol in normalised:
                replacement_counts[symbol] = normalised.count(symbol)
                normalised = normalised.replace(symbol, replacement)

        # Strip trailing spaces per line while retaining blank lines for readability
        normalised_lines = [line.rstrip() for line in normalised.split("\n")]
        # Preserve trailing newline for formatter compatibility
        normalised = "\n".join(normalised_lines)
        if not normalised.endswith("\n"):
            normalised += "\n"

        warnings = []
        if replacement_counts:
            summary = ", ".join(f"{sym}→{rep}" for sym, rep in replacement_counts.items())
            warnings.append(f"Replaced Unicode symbols: {summary}")

        return NormalisationReport(code=normalised, warnings=warnings, replacement_counts=replacement_counts)

    def _parse_source(self, source: str) -> ParseResult:
        """Attempt to parse *source* and capture any syntax errors."""

        try:
            tree = ast.parse(source)
        except SyntaxError as exc:  # pragma: no cover - exercised via tests
            location = f"line {exc.lineno}, column {exc.offset}" if exc.lineno else "unknown location"
            message = f"Syntax error at {location}: {exc.msg}"
            return ParseResult(success=False, error=message)
        except Exception as exc:  # pragma: no cover - defensive
            return ParseResult(success=False, error=f"Parsing failed: {exc}")

        return ParseResult(success=True, tree=tree)

    def _format_code(self, source: str) -> tuple[str, List[str]]:
        """Format the source with black, returning (code, warnings)."""

        try:
            formatted = black.format_str(source, mode=black.FileMode())
            return formatted, []
        except Exception as exc:  # pragma: no cover - black errors rare but possible
            warning = f"Black formatting failed: {exc}"
            return source, [warning]

    def _auto_fix_indentation(
        self, source: str, parse_error: Optional[str]
    ) -> tuple[str, bool]:
        """Heuristic indentation repair for obvious colon-without-block issues."""

        if not parse_error or "expected an indented block" not in parse_error.lower():
            return source, False

        lines = source.split("\n")
        fixed_lines: List[str] = []
        i = 0
        modified = False

        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            fixed_lines.append(line)

            if stripped.endswith(":"):
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    fixed_lines.append(lines[j])
                    j += 1

                if j < len(lines):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= indent and next_line.strip():
                        target_indent = indent + 4
                        fixed_lines[-1] = " " * target_indent + stripped

                        next_line = " " * (indent + 8) + next_line.lstrip()
                        fixed_lines.append(next_line)
                        modified = True
                        j += 1

                        while j < len(lines):
                            block_line = lines[j]
                            block_stripped = block_line.strip()
                            block_indent = len(block_line) - len(block_line.lstrip())
                            if not block_stripped:
                                fixed_lines.append(block_line)
                                j += 1
                                continue
                            if block_indent <= indent and block_stripped:
                                break

                            adjusted_indent = block_indent + 4
                            if block_indent <= indent:
                                adjusted_indent = indent + 8

                            fixed_lines.append(" " * adjusted_indent + block_stripped)
                            modified = True
                            j += 1

                        i = j - 1

            i += 1

        fixed_source = "\n".join(fixed_lines)
        if not fixed_source.endswith("\n"):
            fixed_source += "\n"

        return fixed_source, modified

    def _analyse_ast(self, tree: Optional[ast.AST]) -> tuple[List[str], List[str]]:
        """Perform lightweight analysis and return (warnings, suggestions)."""

        if tree is None:
            return [], []

        warnings: List[str] = []
        suggestions: List[str] = []

        # Example heuristic: warn if module contains only pass / docstring
        has_executable_nodes = any(
            not isinstance(node, (ast.Expr, ast.Pass)) for node in tree.body
        )
        if not has_executable_nodes:
            warnings.append("Code contains no executable statements.")

        # If there are annotations referencing typing names without imports, offer a suggestion
        typing_names = {"List", "Dict", "Set", "Tuple", "Optional"}
        referenced = set()

        class TypingVisitor(ast.NodeVisitor):
            def visit_Name(self, node: ast.Name) -> None:  # type: ignore[override]
                if node.id in typing_names:
                    referenced.add(node.id)
                self.generic_visit(node)

        TypingVisitor().visit(tree)

        if referenced and self.validation_level != ValidationLevel.BASIC:
            names = ", ".join(sorted(referenced))
            suggestions.append(
                f"Consider importing typing symbols: {names}"
            )

        return warnings, suggestions

    # ------------------------------------------------------------------
    # Debug helpers
    # ------------------------------------------------------------------
    def _emit_debug_info(
        self,
        *,
        original: str,
        normalised: str,
        formatted: str,
        warnings: List[str],
    ) -> None:
        if not st:
            return

        st.write("ℹ️ **Validator Debug Info**")
        st.write(f"Original length: {len(original)}")
        st.write(f"Normalised length: {len(normalised)}")
        st.write(f"Formatted length: {len(formatted)}")
        if warnings:
            st.write("Warnings emitted during validation:")
            for warn in warnings:
                st.write(f"- {warn}")

    # Compatibility helper -------------------------------------------------
    def _clean_unicode_characters(self, code: str) -> str:
        """Expose the normaliser's Unicode replacement step for legacy helpers."""

        return self._normalise_code(code).code


class BatchCodeCleaner:
    """Utility for running the validator across many stored problems."""

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.COMPREHENSIVE) -> None:
        self.validator = CodeValidator(validation_level)

    def clean_database_problems(self, problems: List[Dict]) -> List[Dict]:
        cleaned: List[Dict] = []
        for problem in problems:
            updated = problem.copy()
            solution = problem.get("solution_code")
            if solution:
                result = self.validator.validate_and_fix_code(solution)
                updated["solution_code"] = result.fixed_code
                updated["validation_errors"] = result.errors
                updated["validation_warnings"] = result.warnings
                updated["is_valid_code"] = result.is_valid
            cleaned.append(updated)
        return cleaned

    def generate_cleaning_report(self, problems: List[Dict]) -> Dict[str, Any]:
        total = len(problems)
        valid = sum(1 for problem in problems if problem.get("is_valid_code", True))
        with_errors = sum(1 for problem in problems if problem.get("validation_errors"))
        with_warnings = sum(1 for problem in problems if problem.get("validation_warnings"))
        success_rate = (valid / total * 100) if total else 0.0
        return {
            "total_problems": total,
            "valid_problems": valid,
            "problems_with_errors": with_errors,
            "problems_with_warnings": with_warnings,
            "success_rate": success_rate,
        }


# Convenience wrappers ---------------------------------------------------
def validate_code(code: str, debug: bool = False) -> ValidationResult:
    return CodeValidator().validate_and_fix_code(code, debug)


def fix_code_indentation(code: str) -> str:
    return validate_code(code).fixed_code


def clean_unicode_characters(code: str) -> str:
    return CodeValidator()._clean_unicode_characters(code)


if __name__ == "__main__":  # pragma: no cover - manual smoke test
    sample = """
class Solution: def maxSlidingWindow(self, nums: List[int], k: int) → List[int]: if not nums or k ≤ 0: return []
result = []
window = deque ()
"""

    result = validate_code(sample, debug=True)
    print("Valid:", result.is_valid)
    print("Warnings:", result.warnings)
    print(result.fixed_code)


