import numpy as np
import pytest

from gpt_workbench.cleanroom_impl.aggregation import LabelledArray, m9
from gpt_workbench.cleanroom_impl.endpoint import beta_fit
from gpt_workbench.cleanroom_impl.errors import ConformanceError, GeometryPreflightFailure
from gpt_workbench.cleanroom_impl.features import physical_features
from gpt_workbench.cleanroom_impl.geometry import exact_core_to_padded
from gpt_workbench.cleanroom_impl.identity import PatchKey
from gpt_workbench.cleanroom_impl.voronoi import bounded_core_cells


def test_tp_vor_001_bounded_cell_exact_reference():
    padded=np.array([(i,j) for i in range(3) for j in range(3)],int)
    core=np.array([[1,1]],int)
    cell=bounded_core_cells(core,padded,padded.astype(float))
    assert cell.area.tolist()==pytest.approx([1.]) and cell.perimeter.tolist()==pytest.approx([4.])


def test_tp_wire_001_wrong_core_join_fails():
    with pytest.raises(GeometryPreflightFailure): exact_core_to_padded(np.array([[9,9]]),np.array([[0,0],[1,1]]))


def test_tp_neg_001_missing_axis_cell_fails():
    with pytest.raises(ConformanceError):
        m9(LabelledArray(np.zeros((8,6)),("config","offset"),(tuple(range(8)),tuple(range(6)))))


def test_tp_neg_002_nonfinite_fails_or_named_endpoint_route():
    bad=np.ones((2,48)); bad[0,0]=np.nan
    result=beta_fit(bad); assert not result.valid and result.reason=="nonfinite MSD"


def test_tp_neg_004_wrong_physical_source_shape(grid_patch):
    n=len(grid_patch.lifts)
    with pytest.raises(ConformanceError):
        physical_features(grid_patch,np.ones(n-1),np.ones(n),np.ones(n),np.ones(n),np.ones(n))
