from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.spatial import QhullError, Voronoi

from .errors import GeometryPreflightFailure
from .geometry import exact_core_to_padded


@dataclass(frozen=True)
class CellGeometry:
    area: np.ndarray
    perimeter: np.ndarray


def bounded_core_cells(core_lifts: np.ndarray, padded_lifts: np.ndarray,
                       padded_points: np.ndarray) -> CellGeometry:
    points=np.asarray(padded_points,dtype=np.float64)
    if points.ndim!=2 or points.shape[1]!=2 or not np.isfinite(points).all():
        raise GeometryPreflightFailure("Voronoi points must be finite n×2")
    mapping=exact_core_to_padded(core_lifts,padded_lifts)
    try: diagram=Voronoi(points)
    except QhullError as exc: raise GeometryPreflightFailure("Qhull failure") from exc
    area=np.empty(len(mapping)); perimeter=np.empty(len(mapping))
    for out_i,point_i in enumerate(mapping):
        region=diagram.regions[diagram.point_region[point_i]]
        if not region or -1 in region: raise GeometryPreflightFailure("unbounded core Voronoi cell")
        polygon=diagram.vertices[np.asarray(region,dtype=int)]
        if not np.isfinite(polygon).all(): raise GeometryPreflightFailure("nonfinite Voronoi cell")
        x,y=polygon[:,0],polygon[:,1]
        area[out_i]=.5*abs(float(x@np.roll(y,-1)-y@np.roll(x,-1)))
        perimeter[out_i]=float(np.linalg.norm(polygon-np.roll(polygon,-1,axis=0),axis=1).sum())
    return CellGeometry(area,perimeter)
