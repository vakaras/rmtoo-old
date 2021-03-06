#
# Requirement Management Toolset
#
#  Unit test for ReqsContinuum
#
# (c) 2010 on flonatel
#
# For licencing details see COPYING
#

import tempfile
import shutil
import StringIO

from rmtoo.lib.ReqsContinuum import ReqsContinuum
from rmtoo.lib.RMTException import RMTException
from rmtoo.lib.RmtooMain import execute_cmds

class TestReqsCont:

    def test_neg_01(self):
        "ReqsContinuum: check exception when vcs is needed but not available"
        try:
            tdir = tempfile.mkdtemp(prefix="rmtoo-tst-ctnt-")

            class Config:
                reqs_spec = {"commit_interval": ["v1", "v7"],
                             "directory": tdir }
                
            ReqsContinuum(None, None, Config)
            assert(False)
        except RMTException, rmte:
            shutil.rmtree(tdir)
            assert(rmte.id()==40)

    def test_neg_02(self):
        "ReqsContinuum: check exception when vcs is needed but not available \
        (entry point in execute_cmds())"

        tdir = tempfile.mkdtemp(prefix="rmtoo-tst-ctnt-")

        class Config:
            reqs_spec = {"commit_interval": ["v1", "v7"],
                         "directory": tdir }

        mstderr = StringIO.StringIO()

        rval = execute_cmds(None, Config, None, None, mstderr)

        assert(rval==False)
        assert(mstderr.getvalue()=="+++ ERROR: Problem reading in "
               "the continuum: '[  40]: Based on the config '['v1', 'v7']' "
               "a repository is needed - but there is none'")
