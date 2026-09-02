class ConformanceError(ValueError):
    """An input or workflow boundary violates a frozen contract."""


class GeometryPreflightFailure(ConformanceError):
    """Geometry is not eligible to reach propagation."""


class LeakageError(ConformanceError):
    """A fitted object contains a held-out identity."""


class ReproducibilityFailure(ConformanceError):
    """A randomisation cannot be reproduced uniquely."""
