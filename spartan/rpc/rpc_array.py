from ._rpc_array import *
from ..array import tile

'''
_rpc_array suppose to provide all APIs needed by RPC to operate
between ndarray and CTile. However, npdate_to_internal is not
easy to integrate to _rpc_array.numpy_to_ctile. This file provides
a consistent import entry for all RPC operations.
'''

def numpy_to_ctile(data):
  shape, dtype, sparse_type, tile_type, tile_data = tile.npdata_to_internal(data)
  return _rpc_array.numpy_to_ctile(shape, dtype, sparse_type, tile_type, tile_data)
