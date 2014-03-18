'''FilterFiltering expressions.

These are generated by a __getitem__ call to an `Expr`, when
passed a non-numeric, non-tuple type, (e.g. x[idx_x]).
'''
import numpy as np

from .. import util, blob_ctx
from ..array import extent, tile, distarray
from ..core import LocalKernelResult
from ..util import Assert, join_tuple
from .base import Expr, ListExpr, TupleExpr
from . import base
from traits.api import Instance, PythonValue

class FilterExpr(Expr):
  '''Represents an indexing operation.
  
  Attributes:
    src: `Expr` to index into
    idx: `tuple` (for slicing) or `Expr` (for bool/integer indexing) 
  '''
  #_members = ['src', 'idx']
  src = Instance(Expr) 
  idx = PythonValue(None, desc="Tuple or Expr")

  def __init__(self, *args, **kw):
    super(FilterExpr, self).__init__(*args, **kw)
    assert not isinstance(self.src, ListExpr)
    assert not isinstance(self.idx, ListExpr)
    assert not isinstance(self.idx, TupleExpr)

  def label(self):
    return 'slice(%s)' % self.idx

  def compute_shape(self):
    if isinstance(self.idx, (int, slice, tuple)):
      src_shape = self.src.compute_shape()
      ex = extent.from_shape(src_shape)
      slice_ex = extent.compute_slice(ex, self.idx)
      return slice_ex.shape
    else:
      raise base.NotShapeable

  def _evaluate(self, ctx, deps):
    src = deps['src']
    idx = deps['idx']

    assert not isinstance(idx, list)
    util.log_debug('Evaluating index: %s', idx)
    return eval_index(ctx, src, idx)


def _int_index_mapper(ex, src, idx, dst):
  '''Kernel function for indexing via an integer array.
  
  Iterate over entries in ``idx`` and fetch the values
  from ``src``, writing into ``dst``.
  
  Args:
    ex: `Extent` to process.
    src (DistArray):
    idx (DistArray):
    dst (DistArray):
  '''
  idx_vals = idx.fetch(extent.drop_axis(ex, -1))

  output = []
  for dst_idx, src_idx in enumerate(idx_vals):
    output.append(src.select(src_idx))

  output_ex = extent.create(
    ([ex.ul[0]] + [0] * (len(dst.shape) - 1)),
    ([ex.lr[0]] + list(output[0].shape)),
    (dst.shape))

  #util.log_info('%s %s', output_ex.shape, np.array(output).shape)
  output_tile = tile.from_data(np.array(output))
  tile_id = blob_ctx.get().create(output_tile).wait().tile_id
  return LocalKernelResult(result=[(output_ex, tile_id)])


def _bool_index_mapper(ex, src, idx):
  '''Kernel function for boolean indexing.
  
  Fetches the input file from ``src`` and applies the mask from ``idx``.
  
  Args:
    ex: `Extent` to process.
    src (DistArray):
    idx (DistArray):
  '''

  val = src.fetch(ex)
  mask = idx.fetch(ex)

  #util.log_info('\nVal: %s\n Mask: %s', val, mask)
  masked_val = np.ma.masked_array(val, mask)
  output_tile = tile.from_data(masked_val)
  tile_id = blob_ctx.get().create(output_tile).wait().tile_id
  return LocalKernelResult(result=[(ex, tile_id)])


def eval_index(ctx, src, idx):
  '''
  Index an array by another array (boolean or integer).
  
  Args:
    ctx: `BlobCtx`
    src: :py:class:`DistArray` to read from
    idx: `DistArray` of bool or integer index.
    
  Returns:
    DistArray: The result of src[idx] 
  '''

  Assert.isinstance(idx, (np.ndarray, distarray.DistArray))

  if idx.dtype == np.bool:
    # return a new array masked by `idx`
    dst = src.map_to_array(_bool_index_mapper, kw={'src': src, 'idx': idx})
    return dst
  else:
    util.log_info('Integer indexing...')

    Assert.eq(len(idx.shape), 1)

    # create empty destination of same first dimension as the index array
    dst = distarray.create(join_tuple([idx.shape[0]], src.shape[1:]), dtype=src.dtype)

    # map over it, fetching the appropriate values for each tile.
    return dst.map_to_array(_int_index_mapper, kw={'src': src, 'idx': idx, 'dst': dst})

    
