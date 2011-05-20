''' this is a simple example of random walk.

random walk usually follows this convention:
F(t+1) = (1-alpha)*S*F(t) + alpha*Y

default notations:
W: the adjacency matrix. W[i,j]=weight of edge i-j
S: transition matrix. S = D^-1 * W, or S = D^-1/2 * W * D^1/2

library requirement: numpy/scipy, bidict

'''

# TODO: contribute this to Numpy/Scipy, or to GoogleCode and then pypi. (note: can't contributed to igraph, which is written in C)

import itertools, csv
import numpy, scipy.sparse
from bidict import bidict


def _read_pairs(infile, directed=True):
  '''Return the rows of the pairs, appended with weight=1 if unset. Don not allow duplicates, but allow self loops'''
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
    elif len(row) == 0:
      continue
    else:
      assert False, "A row has to have at least 1 source node and 1 destination node with an optional weight: " + str(row)
    rows.append(row)

    # if the pairs are undirected, append the other direction too.
    if not directed:
      rows.append((row[1], row[0], row[2]))

  assert len(rows) == len(set(rows)), "Please remove duplicate rows."
  f.close()
  return rows


def _convert_node_mapping(rows):
  '''Return a bidict node_map with node_index=>node_name, and the converted rows'''
  node_map = bidict()
  converted_rows = []

  def register_node(node):
    if node not in ~node_map:
      index = len(node_map)
      node_map[index] = node
    else:
      index = node_map[:node]
    return index

  for src, dst, weight in rows:
    src_index = register_node(src)
    dst_index = register_node(dst)
    converted_rows.append((src_index, dst_index, weight))

  return node_map, converted_rows



def _fix_dangling(rows, node_map):
  ''' Function to handle dangling nodes by adding links from these nodes to all other nodes.
  Dangling nodes (nodes with no outlinks) could create problem for the PageRank algorithm because they would absorb all random walk.
  In the original pagerank algorithm, the dangling nodes were simple removed. Here we assume they would jump back to any nodes.
  '''
  good_nodes = set([])
  for id1, id2, weight in rows:
    # only src node is counted as good nodes.
    good_nodes.add(id1)
  dangling = set(node_map.keys()) - good_nodes
  print 'Dangling nodes:', len(dangling)
  fixed = list(rows)
  for n1 in dangling:
    for n2 in (set(node_map.keys())):
      fixed.append((n1, n2, 1.0))
  return fixed




def _create_W(rows, size):
  '''This W is the adjacency matrix'''
  # to have maximum compatibility w/ Matlab or R, we use lil_matrix rather than the dok_matrix, and maintain the index->node mapping ourselves.
  W = scipy.sparse.lil_matrix((size, size))
  for src_index, dst_index, weight in rows:
    W[src_index, dst_index] = weight
  W = W.tocsr()
  return W


def _compute_S(W):
  '''Return S as the transition matrix from adjacency matrix W'''

  # compute D^-1
  # axis=1 means sum over columns for each row. here means sum over out-degree.
  #dlist = numpy.asarray(W.sum(axis=0))[0]
  dlist = numpy.asarray(W.sum(axis=1).transpose())[0]
  assert len(dlist) == W.shape[0] == W.shape[1]
  # note: if dangling node not fixed, this will cause divided by zero
  dlist_neg = dlist ** -1
  D_neg = scipy.sparse.spdiags(data=dlist_neg, diags=numpy.array([0]), m=len(dlist), n=len(dlist))

  # compute S=(D^-1*W)'
  S = (D_neg * W).transpose()
  return S.tocsc()



def _save_F(result, node_map, outfile):
  '''Save the result (in a list) to the outfile'''
  assert len(result) == len(node_map)
  print "Saving result to:", outfile
  f = open(outfile, 'w')
  writer = csv.writer(f)
  for i, score in enumerate(result):
    writer.writerow((node_map[i], score))
  f.close()



def _is_converged(Ft1, Ft0, tolerance):
  '''Test if iteration should finish. "tolerance" is percentage-based.'''
  assert Ft1.shape == Ft0.shape, 'Ft1 and Ft0 should have the same dimension.'
  diff = numpy.abs(Ft1 - Ft0)
  rowsize, colsize = diff.shape

  for i, j in itertools.product(range(rowsize), range(colsize)):
    if Ft0[i,j] == 0 and diff[i,j] == 0:
      continue # we want this condition to avoid divided by zero
    elif Ft0[i,j] == 0 and diff[i,j] != 0:
      return False
    elif diff[i,j]/Ft0[i,j] > tolerance:
      return False
  else:
    return True



def _pagerank_iterate(S, Y, F0, alpha=0.15, tolerance=0.01):
  '''Run the iteration using pagerank algorithm.'''
  Ft0 = F0
  count = 0
  while True:
    if count % 10 == 0:
      print "Iterating round:", count
    count += 1
    # the iteration
    Ft1 = (1-alpha) * S * Ft0 + alpha * Y
    if _is_converged(Ft1, Ft0, tolerance):
      print "Finish iteration in round:", count
      break
    else:
      Ft0 = Ft1
  return Ft1




def pagerank(infile, outfile, restart=[], directed=True, alpha=0.15, tolerance=0.01):
  '''This function calculates the pagerank algorithm. Successfully tested with the 3-nodes example in Page&Brin 1998'''
  assert infile.endswith('.p'), 'Currently we only support the input file as node-node pairs, and the suffix of the file has to be *.p'
  rows = _read_pairs(infile, directed)
  node_map, converted_rows = _convert_node_mapping(rows)
  fixed_converted_rows = _fix_dangling(converted_rows, node_map)
  W = _create_W(fixed_converted_rows, len(node_map))
  S = _compute_S(W)
  del(W)  # to save RAM.
  if len(restart) == 0:
    Y = numpy.ones((len(node_map), 1))
  else:
    Y = numpy.zeros((len(node_map), 1))
    for n in restart:
      assert n in ~node_map, 'Restart node has to be in existing nodes: '+n
      Y[node_map[:n], 0] = 1.0
  Y = Y / Y.sum()
  print 'Start iterating...'
  F = _pagerank_iterate(S, Y, Y, alpha, tolerance)
  #print F
  result = F.transpose()[0].tolist()
  _save_F(result, node_map, outfile)



if __name__ == '__main__':
  pagerank('/tmp/testu.p', '/tmp/result.txt', directed=False)