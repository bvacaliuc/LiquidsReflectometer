"""Canonical value domains for the reduction configuration.

One definition per domain, imported by both the code that *enforces* it and the
code that *offers* it to a user. Before this module the settings editor's
choice lists hand-mirrored bare local lists inside
:mod:`lr_reduction.nr_reduction_calc`, which is a copy waiting to drift: the
editor would go on offering a value the reducer had stopped accepting, and
nothing would notice until a reduction failed.

Deliberately dependency-free — stdlib only, no numpy, matplotlib or Qt — so the
settings model can import it without dragging the reduction stack in.

Spellings here are the canonical, human-facing ones. The reducer lower-cases
before comparing (``nr_reduction_calc.py`` in ``NRReduction.__init__``), so
``lowered()`` produces the form it matches against.
"""


def lowered(choices):
    """Return ``choices`` lower-cased, the form the reducer compares against."""
    return [choice.lower() for choice in choices]


#: Lambda-to-Q conversion, per angle (``NRReductionConfig.method_per_run``).
METHOD_CHOICES = ("meanTheta", "constantQ", "constantTOF")

#: Source of the theta value (``NRReductionConfig.useCalcTheta``).
#:
#: NOT a boolean, despite its name and its ``False`` default: the reducer
#: accepts these two strings and treats a legacy ``True`` as an alias for
#: ``detector_angle``. A settings editor that renders it as a checkbox cannot
#: express ``sample_angle`` at all, and silently downgrades a loaded one.
CALC_THETA_CHOICES = ("detector_angle", "sample_angle")

#: Detector resolution function (``NRReductionConfig.DetResFn``), dispatched in
#: ``nr_reduction_calc._calc_detector_convolution``.
DET_RES_CHOICES = ("rectangular", "gaussian")

#: Specular peak shape (``NRReductionConfig.peak_type``), dispatched in
#: ``nr_tools.fit_peak``.
PEAK_TYPE_CHOICES = ("gauss", "supergauss")
