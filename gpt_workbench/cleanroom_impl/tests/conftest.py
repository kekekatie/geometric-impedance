import numpy as np
import pytest

from gpt_workbench.cleanroom_impl.geometry import canonicalize_geometry
from gpt_workbench.cleanroom_impl.identity import PatchKey


@pytest.fixture
def grid_patch():
    side=7
    lifts=np.asarray([(i,j,0,0) for i in range(side) for j in range(side)],dtype=np.int64)
    par=lifts[:,:2].astype(float)
    perp=np.column_stack((par[:,0]+.13*par[:,1],par[:,1]-.07*par[:,0]))
    edges=[]
    for i in range(side):
        for j in range(side):
            k=i*side+j
            if i+1<side: edges.append((k,(i+1)*side+j))
            if j+1<side: edges.append((k,i*side+j+1))
    return canonicalize_geometry(PatchKey(0,0),lifts,par,perp,edges)
