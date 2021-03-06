#
# rmtoo
#   Free and Open Source Requirements Management Tool
#
#  Blackbox rmtoo test
#
# (c) 2010-2011 by flonatel
#
# For licencing details see COPYING
#

import os

from rmtoo.lib.RmtooMain import main
from rmtoo.tests.lib.BBHelper import prepare_result_is_dir, compare_results, \
    cleanup_std_log, delete_result_is_dir, extract_container_files

mdir = "tests/blackbox-test/bb001-test"

class TestBB001:

    def test_pos_001(self):
        "BB Basic with one requirement - reqs only from git"

        def myexit(n):
            pass

        mout, merr = prepare_result_is_dir()
        main(["-f", mdir + "/input/Config1.py", "-m", ".."], mout, merr,
             exitfun=myexit)
        cleanup_std_log(mout, merr)
        extract_container_files(["reqspricing.ods",])
        missing_files, additional_files, diffs = compare_results(mdir)
        assert(len(missing_files)==0)
        assert(len(additional_files)==0)

        if len(diffs)!=0:
            print("DIFFS '%s'" % diffs)

        assert(len(diffs)==0)
        delete_result_is_dir()
