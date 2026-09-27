"""Plot text built from user data must not reach matplotlib's mathtext parser.

A NeXus run title or a filename can contain a literal `$`. matplotlib parses
`$...$` as math, and a symbol no font provides sends `_mathtext._get_glyph`
into the font-fallback chain that produced the reported `RecursionError`
(872 frames, `_mathtext.py:644 -> 654 -> 654 ...`).

SCOPE NOTE, because it matters for what this file does and does not prove: the
reported traceback arrives via `axis.py:_get_ticklabel_bboxes` — a **tick
label** — and both overplot paths call `ax.set_yscale('log')`, whose tick labels
matplotlib generates as mathtext itself (`'$\\mathdefault{10^{-6}}$'`,
`parse_math=True`). Those are not user data and these tests do not cover them.
See `todo-mathtext-recursion-is-in-the-log-formatter.md`.
"""

import matplotlib
import pytest

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DOLLAR_TITLE = "D2O $5 layer $ sample run 213628"


@pytest.fixture
def axes():
    fig, ax = plt.subplots()
    yield ax
    plt.close(fig)


def test_a_dollar_bearing_title_is_not_parsed_as_math(axes):
    """The builder's title is the NeXus run title — arbitrary text from a file."""
    text = axes.set_title(DOLLAR_TITLE, parse_math=False)
    assert text.get_parse_math() is False
    axes.figure.canvas.draw()


def test_the_overplot_legend_exempts_its_entries(axes):
    """Legend entries are `os.path.basename(fname)` — user-controlled filenames.

    `plot(label=...)` cannot carry `parse_math`, so it must be set on the
    legend's Text artists afterwards. A file named `D2O_$5.dat` is enough.
    """
    from launcher.apps.overplot import _plain_legend

    axes.plot([0, 1], [0, 1], label="D2O_$5_layer.dat")
    legend = _plain_legend(axes)

    assert legend is not None
    assert [t.get_parse_math() for t in legend.get_texts()] == [False]
    axes.figure.canvas.draw()


def test_the_builder_sets_its_title_without_math_parsing():
    """Pins the CALL, structurally.

    An earlier version asserted `"parse_math=False" in source`, which passed
    with the kwarg deleted from the call — because the phrase also appears in
    the comment explaining it. A guard matching a substring both answers share
    (`settings-editor-learning.md` #11), in the guard written to prevent that.

    Parsed with `ast` instead, so only a real keyword on a real `set_title`
    call satisfies it.
    """
    import ast
    import inspect

    from launcher.apps import json_settings_builder

    tree = ast.parse(inspect.getsource(json_settings_builder))
    set_title_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "set_title"
    ]
    assert set_title_calls, "no set_title call found — has the plot moved?"
    for call in set_title_calls:
        exempt = any(
            kw.arg == "parse_math"
            and isinstance(kw.value, ast.Constant)
            and kw.value.value is False
            for kw in call.keywords
        )
        assert exempt, (
            f"a set_title call at line {call.lineno} does not pass "
            f"parse_math=False — a NeXus title with a $ would be math-parsed"
        )


def test_log_tick_labels_are_mathtext_and_are_NOT_covered_here():
    """Documents the gap rather than hiding it.

    This asserts the fact that makes the work order's prescribed fix
    insufficient for the reported traceback: matplotlib generates log tick
    labels as mathtext regardless of anything the launcher does. If a future
    matplotlib stops doing that, this reds and the todo can be closed.
    """
    fig, ax = plt.subplots()
    try:
        ax.plot([1e-3, 1e-1], [1e-4, 1e-1])
        ax.set_yscale("log")
        fig.canvas.draw()
        labels = [t for t in ax.get_yticklabels() if t.get_text()]
        assert labels, "no tick labels were generated"
        assert any(t.get_text().startswith("$") for t in labels), (
            "log tick labels are no longer mathtext — re-check the todo"
        )
        assert all(t.get_parse_math() for t in labels)
    finally:
        plt.close(fig)
