import unittest

import numpy as np
from spartan import expr
import test_common

ARRAY_SIZE = (10, 10)
tile_hint = [5, 5]

class TestScan(test_common.ClusterTest):
  def test_dense_scan(self):
    axis = 1
    a = expr.ones(ARRAY_SIZE, dtype=np.float32, tile_hint=tile_hint)
    c = expr.scan(a, reduce_fn=np.sum, scan_fn=np.cumsum, accum_fn=None, axis=axis)
    
    print c
  
  def test_sparse_scan(self):
    axis = 1
    a = expr.sparse_diagonal(ARRAY_SIZE, dtype=np.float32, tile_hint=tile_hint)
    c = expr.scan(a, reduce_fn=lambda x, **kw:x.sum(axis=kw['axis']), 
                     scan_fn=lambda x: x.cumsum(), 
                     accum_fn=None, 
                     axis=axis)
    
    print c
  
  def test_sum_scan(self):
    axis = None
    a = expr.ones(ARRAY_SIZE, dtype=np.float32, tile_hint=tile_hint)
    c = expr.scan(a, reduce_fn=np.sum, scan_fn=np.cumsum, accum_fn=None, axis=axis)
    
    print c
    
  def test_noreduce_scan(self):
    a = expr.ones(ARRAY_SIZE, dtype=np.float32, tile_hint=tile_hint)
    c = expr.scan(a, scan_fn=np.cumsum)
    print c
  
  def test_noscan_scan(self):
    a = expr.ones(ARRAY_SIZE, dtype=np.float32, tile_hint=tile_hint)
    c = expr.scan(a, reduce_fn=np.sum)
    print c
    
  def test_noreduce_noscan_scan(self):
    a = expr.ones(ARRAY_SIZE, dtype=np.float32, tile_hint=tile_hint)
    c = expr.scan(a)
    print c
    
if __name__ == '__main__':
  unittest.main()
