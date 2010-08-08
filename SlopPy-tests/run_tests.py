# run SlopPy regression test suite

import os, sys, re, shutil, filecmp, optparse, difflib

SLOPPY_BIN = '~/SlopPy/python.exe'

# all tests are found in this directory:
REGTEST_DIR = 'regression-tests/'

SLOP_VERBOSE_LOG = 'slop_verbose.log'

ALL_TESTS = [e for e in os.listdir(REGTEST_DIR) if e.endswith('.py')]

def execute(test_script):
  assert os.path.isfile(test_script)
  os.system("%s %s > /dev/null 2> /dev/null" % (SLOPPY_BIN, test_script))

def clobber_golden_file(golden_file):
  print '  Overriding golden file'
  shutil.copy(SLOP_VERBOSE_LOG, golden_file)


# returns True if there is a diff, False otherwise
def diff_test_golden_data(golden_file):
  assert os.path.isfile(SLOP_VERBOSE_LOG)
  assert os.path.isfile(golden_file)
  return open(SLOP_VERBOSE_LOG).readlines() != \
         open(golden_file).readlines()


def diff_test_output(test_name):
  golden_file = os.path.join(REGTEST_DIR, test_name[:-3] + '.golden')
  assert os.path.isfile(golden_file)
  assert os.path.isfile(SLOP_VERBOSE_LOG)

  golden_s = open(golden_file).readlines()
  out_s = open(SLOP_VERBOSE_LOG).readlines()

  for line in difflib.unified_diff(golden_s, out_s, \
                                   fromfile=golden_file, tofile=SLOP_VERBOSE_LOG):
    print line,


def run_test(test_name, clobber_golden=False):
  print 'Testing', test_name
  assert test_name.endswith('.py')
  if os.path.isfile(SLOP_VERBOSE_LOG):
    os.remove(SLOP_VERBOSE_LOG)

  test_script = os.path.join(REGTEST_DIR, test_name)
  execute(test_script)

  golden_file = os.path.join(REGTEST_DIR, test_name[:-3] + '.golden')
  if os.path.isfile(golden_file):
    diff_test_golden_data(golden_file)
    if clobber_golden:
      clobber_golden_file(golden_file)
  else:
    clobber_golden_file(golden_file)


def run_all_tests(clobber=False):
  for t in ALL_TESTS:
    run_test(t, clobber)

def diff_all_test_outputs():
  for t in ALL_TESTS:
    print '=== diffing', t, '==='
    diff_test_output(t)


if __name__ == "__main__":
  parser = optparse.OptionParser()
  parser.add_option("--all", action="store_true", dest="run_all",
                    help="Run all tests")
  parser.add_option("--only-clobber", action="store_true", dest="only_clobber",
                    help="Clobber ALL golden files WITHOUT re-running tests")
  parser.add_option("--clobber", action="store_true", dest="clobber",
                    help="Clobber golden files when running tests")
  parser.add_option("--test", dest="test_name",
                    help="Run one test")
  parser.add_option("--difftest", dest="diff_test_name",
                    help="Diff the .out and .golden for one test")
  parser.add_option("--diffall", action="store_true", dest="diff_all",
                    help="Diff the .out and .golden for all tests")
  (options, args) = parser.parse_args()
  if options.run_all:
    if options.clobber:
      print 'Running all tests and clobbering results ...'
    else:
      print 'Running all tests ...'
    run_all_tests(options.clobber)

  elif options.diff_all:
    diff_all_test_outputs()
  elif options.diff_test_name:
    diff_test_output(options.diff_test_name)
  elif options.test_name:
    run_test(options.test_name, options.clobber)
  elif options.only_clobber:
    for t in ALL_TESTS:
      golden_file = os.path.join(REGTEST_DIR, t[:-3] + '.golden')
      clobber_golden_file(golden_file)
  else:
    parser.print_help()
