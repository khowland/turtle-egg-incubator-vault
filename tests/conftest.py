"""
=============================================================================
File:     tests/conftest.py
Project:  Incubator Vault — WINC
Purpose:  Global pytest configuration.

Layer 3 — Anti-Stub Firewall:
  At collection time, this conftest inspects every collected test function.
  If the function body is a single `assert True` statement and nothing else,
  the test is FAILED (not skipped, not passed — FAILED).

  This permanently prevents stub tests from masquerading as green passes.
  If a test is genuinely not yet implemented, mark it with:
      @pytest.mark.skip(reason="TBD: describe what needs testing")

  False-green stubs are a QA integrity violation. They caused show-stopping
  production bugs to ship undetected. This firewall prevents recurrence.
=============================================================================
"""
import ast
import pathlib
import pytest


def pytest_collection_finish(session):
    """
    Anti-Stub Firewall — executed after all tests are collected.
    Fails the session if any test is a naked `assert True` stub.
    """
    stub_violations = []

    for item in session.items:
        try:
            src = pathlib.Path(item.fspath).read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (OSError, SyntaxError):
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name != item.originalname:
                continue

            # Strip leading docstring if present
            body = node.body
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                body = body[1:]  # Skip docstring

            # Detect naked `assert True` as the sole statement
            if (
                len(body) == 1
                and isinstance(body[0], ast.Assert)
                and isinstance(body[0].test, ast.Constant)
                and body[0].test.value is True
            ):
                stub_violations.append(item.nodeid)

    if stub_violations:
        violation_list = "\n  - ".join(stub_violations)
        pytest.fail(
            f"\n\n🚨 ANTI-STUB FIREWALL: {len(stub_violations)} stub test(s) detected.\n"
            f"The following tests contain only `assert True` and test NOTHING:\n\n"
            f"  - {violation_list}\n\n"
            f"Replace each stub with a real assertion, or mark as:\n"
            f"  @pytest.mark.skip(reason='TBD: <what needs testing>')\n\n"
            f"False-green stubs are a QA integrity violation.",
            pytrace=False,
        )
