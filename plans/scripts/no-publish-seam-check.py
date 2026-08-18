#!/usr/bin/env python3
"""Behavioral check for the REF_L/shared no-publish seam (slug no-publish-seam).

Verifies, without importing the facility shim (its module-level
``lr_autoreduce`` import cannot resolve outside the deployed env), that
``autoreduce/reduce_REF_L.py``:

  A. computes ``publish`` from ``sys.argv`` accepting BOTH spellings
     (``--no-publish`` and ``--no_publish``) as suppression requests;
  B. gates the shadow-reduction forwarding on the caller's ``publish``
     composed with the ``new_publish`` operator knob:
     append ``--no_publish``  iff  not (publish and new_publish).

RED before the fix (hyphen spelling ignored; gate ignores ``publish``),
GREEN after. Run:  python3 no-publish-seam-check.py <path-to-shim>
"""

import ast
import sys


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        fail("usage: no-publish-seam-check.py <path-to-reduce_REF_L.py>")
    with open(sys.argv[1], encoding="utf-8") as fh:
        src = fh.read()
    tree = ast.parse(src)

    # --- A: the publish = ... assignment, executed against fake argv ---
    assigns = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(getattr(t, "id", "") == "publish" for t in node.targets)
    ]
    if len(assigns) != 1:
        fail(f"expected exactly 1 assignment to 'publish', found {len(assigns)}")
    line = ast.get_source_segment(src, assigns[0])
    cases = [
        (["s", "f", "o"], True),
        (["s", "f", "o", "--no_publish"], False),
        (["s", "f", "o", "--no-publish"], False),
    ]
    for argv, expected in cases:
        namespace = {"sys": type("FakeSys", (), {"argv": argv})}
        exec(line, namespace)  # noqa: S102 — executing the audited line is the test
        if namespace["publish"] is not expected:
            fail(f"publish scan: argv={argv[3:]} -> {namespace['publish']}, want {expected}")
    print("OK: publish scan suppresses on both spellings")

    # --- B: the shadow-forwarding gate truth table ---
    gates = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.If)
        and "new_publish" in (ast.get_source_segment(src, node.test) or "")
    ]
    if len(gates) != 1:
        fail(f"expected exactly 1 gate If referencing 'new_publish', found {len(gates)}")
    test_src = ast.get_source_segment(src, gates[0].test)
    for pub in (True, False):
        for knob in (True, False):
            want = not (pub and knob)
            got = bool(eval(test_src, {"publish": pub, "new_publish": knob}))  # noqa: S307
            if got is not want:
                fail(
                    f"gate '{test_src}': publish={pub} new_publish={knob} "
                    f"-> append={got}, want {want}"
                )
    print("OK: shadow gate composes caller publish with new_publish knob")
    print("GREEN: no-publish seam checks pass")


if __name__ == "__main__":
    main()
