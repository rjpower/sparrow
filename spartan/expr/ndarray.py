from .base import Expr
from ..node import Node
from spartan.array import tile, distarray
import numpy as np
from .. import util
from traits.api import Tuple, Bool, PythonValue, HasTraits

class NdArrayExpr(Expr):
  #_members = ['_shape', 'sparse', 'dtype', 'tile_hint', 'reduce_fn']
  _shape = Tuple 
  sparse = Bool 
  dtype = PythonValue(None, desc="np.type or type")
  tile_hint = PythonValue(None, desc="Tuple or None")
  reduce_fn = PythonValue(None, desc="Function or None")

  def __repr__(self):
    return 'dist_array(%s, %s)' % (self.shape, self.dtype)

  def label(self):
    return repr(self)
  
  def visit(self, visitor):
    return NdArrayExpr(_shape=visitor.visit(self.shape),
                       dtype=visitor.visit(self.dtype),
                       tile_hint=self.tile_hint,
                       sparse=self.sparse,
                       reduce_fn=self.reduce_fn)
  
  def dependencies(self):
    return {}
  
  def compute_shape(self):
    return self._shape
 
  def _evaluate(self, ctx, deps):
    shape = self._shape
    dtype = self.dtype
    tile_hint = self.tile_hint
    
    return distarray.create(shape, dtype,
                            reducer=self.reduce_fn,
                            tile_hint=tile_hint,
                            sparse=self.sparse)

def ndarray(shape, 
            dtype=np.float, 
            tile_hint=None,
            reduce_fn=None,
            sparse=False):
  '''
  Lazily create a new distributed array.
  :param shape:
  :param dtype:
  :param tile_hint:
  '''
  return NdArrayExpr(_shape = shape,
                     dtype = dtype,
                     tile_hint = tile_hint,
                     reduce_fn = reduce_fn,
                     sparse = sparse)
