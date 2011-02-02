# for jython use: remove the encoding gbk. otherwise, add it.
import random, csv, math, shutil, os, fnmatch, os.path, itertools

# p and q are lists of discrete random variable distributions.
def kl_divergence(p, q):
  if len(p) != len(q): raise Exception('should pass in variables with the same number')
  if sum(p) != 1 or sum(q) != 1: raise Exception('a random variable distribution should sum up to 1')
  t = zip(p, q)
  return sum([ti[0]*math.log(ti[0]/ti[1],2) for ti in t])


# randomly copy $num of files from src to dst
# src folder can't have sub-folder
def random_sample_files(src, dst, num):
  if type(src)==type([]):
    dirs = src  # multiple dirs
  else:
    dirs = [src]
  files = []
  for dir in dirs:
    for f in os.listdir(dir):
      files.append(dir+'/'+f)
  print 'Files pool:', len(files)
  s = random.sample(files, num)
  for f in s:
    shutil.copy(f, dst+'/'+os.path.basename(f))



# not working!!!
def gbk_to_utf8(dir):
  files = os.listdir(dir)
  for file in files:
    file = open(dir+'/'+file, 'rw')
    print file.read()


# filter string in a line, and then sort
def filter_sort(filename, filter_str, sort_field_index):
  f = open(filename, 'r')
  lst=[]
  for line in f:
    if line.find(filter_str) != -1:
      line = line.strip()
      fields = line.split(',')
      lst.append((int(fields[sort_field_index]), line))
  lst = sorted(lst, lambda x,y: cmp(x[0],y[0]), None, True)
  for i in lst: print i[1]


def rolling_sum(alist, step):
  results = []
  length = len(alist) - step + 1
  for i in range(length):
    results.append( sum(alist[i : (i+step)]) )
  return results


def remove_empty_lines(file):
  f = open(file, 'r')
  lines = f.readlines()
  f.close()
  f = open(file, 'w')
  for l in lines:
    if l.strip()=='': continue
    print >>f, l,
  f.close()

  
def count_lines(dir, pattern):
  files = os.listdir(dir)
  filecount = 0
  linecount = 0
  for file in files:
    if fnmatch.fnmatch(file, pattern):
      print file
      filecount += 1
      file = open(dir+'/'+file, 'r')
      linecount += len(file.readlines())
      file.close()
  print "total line numbers", linecount, "in", filecount, "files"


# return a random number between [0, len(pdf)], according to the probability given by pdf
def multinomial_distribution(pdf):
  if sum(pdf) != 1:
    pdf = [float(i)/sum(pdf) for i in pdf]
  assert sum(pdf) == 1
  r = random.random()
  for i in range(len(pdf)):
    if r < pdf[i]:
      return i
    else:
      r = r - pdf[i]
  assert False

# given the dist_pool, test accuracy on random guess and simulation
# dist_pool = [0 for i in range(37)] + [1 for i in range(3)] + [2 for i in range(181)] + [3 for i in range(57)]
def simulate_random_guess(dist_pool, trials=100000):
  simulation = []
  guess = []
  for i in range(trials):
    simulation.append(random.choice(dist_pool))
    #guess.append(random.randint(0,3))
    guess.append(random.choice(dist_pool))
  correct = [t[0]==t[1] for t in zip(simulation, guess)].count(True)
  print "Correct guesses: %3.2f%%" % (float(correct)/trials*100)

# given the dist_pool to generate random guesses, test over the testing set
# eg. dist_pool=[0,1], testing_set= [0,]*20+[1,]*30
def simulate_random_guess_set(dist_pool, testing_set, trials=100000):
  correct = 0
  for i in range(trials):
    for testpoint in testing_set:
      if testpoint == random.choice(dist_pool): 
        correct += 1
  print "Correct guesses: %3.2f%%" % (float(correct)/(trials*len(testing_set)) * 100)

# write csv
def write_csv(filename, header, rows):
  f = open(filename, 'w')
  writer = csv.writer(f)
  writer.writerow(header)
  for row in rows:
    assert len(row) == len(header), "header %s, row %s" % (str(header), str(row))
    writer.writerow(row)
  f.close()
  #print "Successfully wrote to CSV file:", filename, len(rows)

# colselector is a list column#
def read_csv(filename, header=None, rowfilter=lambda x: True, colselector=None):
  if colselector != None:
    assert all([i in range(len(header)) for i in colselector])
  f = open(filename, 'r')
  reader = csv.reader(f)
  firstline = reader.next()
  if header!=None: assert tuple(header) == tuple(firstline)
  rows = []
  for row in reader:
    assert len(row) == len(header)
    if rowfilter(row):
      if colselector == None:
        rows.append(row)
      else:
        rows.append(tuple([row[i] for i in colselector]))
  #print "Successfully read CSV file:", filename, len(rows)
  f.close()
  return rows


# base/ours: list of labels from the gold standard and our result.
# return: precision, recall, true_positive, (true+false positive), (true positive + false negative)
def precision_recall(label, ours, base):
  assert len(base) == len(ours)
  base_num = sum([1 if b==label else 0 for b in base])
  ours_num = sum([1 if o==label else 0 for o in ours])
  true_positive = sum([1 if b==label and o==label else 0 for b, o in zip(base, ours)])
  if ours_num == 0:
    print "Warning: precision denominator zero!"
    precision = 0.0
  else:
    precision = float(true_positive)/float(ours_num)
  if base_num == 0:
    print "Warning: recall denominator zero!"
    recall = 0.0
  else:
    float(true_positive)/float(base_num) 
  return precision, recall, true_positive, ours_num, base_num


# t1: id-data1, t2: id-data2
# return: id-data1-data2
def inner_join(t1, t2):
  rows = []
  d1 = {};
  for id, data1 in t1: d1[id] = data1
  for id, data2 in t2:
    if id in d1:
      rows.append((id, d1[id], data2))
  return rows

# t1: id-[list of data], t2: id-[list of data]
# return: id-list1-list2
def inner_join_x(t1, t2):
  rows = []
  d1 = {};
  for r1 in t1:
    assert len(r1) >= 2
    d1[r1[0]] = r1[1:]
  for r2 in t2:
    assert len(r2) >= 2
    if r2[0] in d1:
      rows.append([r2[0],] + d1[r2[0]] + r2[1:])
  return rows

def dedup(alist):
  pool = set()
  for i in alist:
    pool.add(i)
  return list(pool)


if __name__ == '__main__':
  #p = [0.5, 0.1, 0.4]
  #q = [0.2, 0.5, 0.3]
  #print kl_divergence(p, q)
  #print rolling_sum([1,2,3,4,5], 3)

  #r = '/Users/danithaca/Desktop/tianya/'
  #random_sample_files([r+'tiger-txt', r+'milk-txt'], r+'random70', 70)
  
  #remove_empty_lines('../data/termsusage_v2.1.txt')
  #count_lines(r'D:\Work\+project\balance\digg_cls\classification_algorithm', '*.m')
  #simulate_random_guess()
  #for i in range(100): print multinomial_distribution([0.02, 0.48, 0.0001, 0.4999])
  #simulate_random_guess_set([1,]*234+[0,]*73, [1,]*234+[0,]*73, 1000000)
  simulate_random_guess_set([1,]*62+[0,]*69+[1,]*234+[0,]*73, [1,]*62+[0,]*69+[1,]*234+[0,]*73)
