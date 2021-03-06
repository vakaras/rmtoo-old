#
# Requirement Management Toolset
#
# Unit test for ReqHistory
#
# (c) 2010 by flonatel
#
# For licencing details see COPYING
#

from rmtoo.modules.ReqHistory import ReqHistory
from rmtoo.lib.Requirement import Requirement
from rmtoo.lib.RMTException import RMTException
from rmtoo.tests.lib.ReqTag import create_parameters

class TestReqHistory:

    def test_positive_01(self):
        "Requirement Tag History - no tag given"
        opts, config, req = create_parameters()

        rt = ReqHistory(opts, config)
        name, value = rt.rewrite("History-test", req)
        assert(name=="History")
        assert(value==None)

    def test_positive_02(self):
        "Requirement Tag History - History set"
        opts, config, req = create_parameters()
        req = {"History": "something"}

        rt = ReqHistory(opts, config)
        name, value = rt.rewrite("History-test", req)
        assert(name=="History")
        assert(value=="something")

