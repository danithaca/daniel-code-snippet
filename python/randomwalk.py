# this is a simple example of random walk.
# random walk usually follows this convention:
# F(t+1) = (1-alpha)*S*F(t) + alpha*Y

# library requirement: numpy/scipy, bidict

# TODO: contribute this to Numpy/Scipy, or to GoogleCode and then pypi. (note: can't contributed to igraph, which is written in C)

import itertools, csv
import numpy, scipy.sparse
from bidict import bidict

class BaseRandomWalk(object):
  # alpha is the tele-port factor
  ALPHA = 0.15
  # tolerance to stop iteration. this is the percentage of change.
  TOLERANCE = 0.05


  def initialize(self):
    ''' You need to initialize the algorithm here '''
    assert False, 'Please override.'



  def isFinished(self, Ft1, Ft0):
    assert Ft1.shape == Ft0.shape, 'Ft1 and Ft0 should have the same dimension.'
    diff = numpy.abs(Ft1 - Ft0)
    rowsize, colsize = diff.shape
    
    for i, j in itertools.product(range(rowsize), range(colsize)):
      if Ft0[i,j] == 0 and diff[i,j] == 0:
        continue # we want this condition to avoid divided by zero
      elif Ft0[i,j] == 0 and diff[i,j] != 0:
        return False
      elif diff[i,j]/Ft0[i,j] > self.TOLERANCE:
        return False
    else:
      return True



  # do the iteration.
  def iterate(self):
    Y = self.prepareY()
    S = self.prepareS()
    Ft0 = self.prepareF0()
    alpha = self.ALPHA

    count = 0
    while True:
      if count % 10 == 0:
        print "Iterating round:", count
      count += 1
      # the iteration
      Ft1 = (1-self.ALPHA) * S * Ft0 + self.ALPHA * Y
      if self.isFinished(Ft1, Ft0):
        print "Finish iteration in round:", count
        break
      else:
        Ft0 = Ft1
    return Ft1

  # rows is a list of tuples: (src, dst weight)
  def initFromRows(self, rows):
    # nodeMap is from node_index=>node_name
    self.nodeMap = bidict()
    converted_rows = []
    
    print 'Init graph from rows:', len(rows)
    for src, dst, weight in rows:
      src_index = self.registerNode(src)
      dst_index = self.registerNode(dst)
      converted_rows.append((src_index, dst_index, weight))
    dimension = len(self.nodeMap)
    
    # to have maximum compatibility w/ Matlab or R, we use lil_matrix rather than the dok_matrix, and maintain the index->node mapping ourselves.
    W = scipy.sparse.lil_matrix((dimension, dimension))
    for src_index, dst_index, weight in converted_rows:
      W[src_index, dst_index] = weight
      
    W = W.tocsr()
    #print W.todense()

    # compute D^-1
    dlist = numpy.asarray(W.sum(axis=1).transpose())[0,]
    assert len(dlist) == dimension
    dlist_neg = dlist ** -1
    D_neg = scipy.sparse.spdiags(data=dlist_neg, diags=array([0]), m=dimension, n=dimension)
    
    # compute S=D^-1*W
    S = D_neg * W
    S = S.tocsc()
    self.S = S
    #print S.todense()
      
  
      
  def registerNode(self, node):
    if node not in ~(self.nodeMap):
      index = len(self.nodeMap)
      self.nodeMap[index] = node
    else:
      index = self.nodeMap[:node]
    return index


  def readPairs(self, infile, directed=True):
    """Return the rows of the pairs, appended with weight=1 if unset."""
    f = open(infile, 'r')
    reader =csv.reader(f)
    rows = []

    for row in reader:
      if len(row) == 2:
        row = (row[0], row[1], 1.0)
      elif len(row) == 3:
        weight = float(row[2])
        assert weight >= 0, "The weight has to be greater than 0"
        row = (row[0], row[1], weight)
      else:
        assert False, "A row has to have at least 1 source node and 1 destination node with an optional weight. File: "+infile
      rows.append(row)

      # if the pairs are undirected, append the other direction too.
      if not directed:
        rows.append((row[1], row[0], weight))

    assert len(rows) == len(set(rows)), "Please remove duplicate rows."
    f.close()
    return rows



class PageRank(BaseRandomWalk):
  pass
  


class AbsorbingRandomWalk(BaseRandomWalk):
  pass
  


class LocalConsistencyGlobalConsistency(BaseRandomWalk):
  pass



''' The function call to PageRank algorithm '''
def pagerank(infile, outfile, restart=[], directed=True, alpha=0.15, tolerance=0.01, iteration=100):
  algorithm = PageRank()
  assert infile.endswith('.p'), 'Currently we only support the input file as node-node pairs, and the suffix of the file has to be *.p'
  rows = algorithm.readPairs(infile, directed)
