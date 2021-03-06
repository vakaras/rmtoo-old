#
# Requirement Management Toolset
#
# Unit test for RDepNo Directed Digraph
# (which finds strongly connected components)
#
# (c) 2010 on flonatel
#
# For licencing details see COPYING
#

from rmtoo.tests.lib.RDep import create_parameters
from rmtoo.modules.RDepNoDirectedCircles import RDepNoDirectedCircles

class TestRDepSCC:

    def test_positive_01(self):
        "Two node one edge digraph B -> A"
        opts, config, reqset = create_parameters({"B": ["A"], "A": [] })
        reqset.graph_master_node = reqset.find("A")

        rdep = RDepNoDirectedCircles(opts, config)
        result = rdep.rewrite(reqset)

        assert(result==True)

    def test_positive_01(self):
        "small digraph D -> B -> A and D -> C -> A"
        opts, config, reqset = create_parameters(
            {"D": ["B", "C"], "C": ["A"], "B": ["A"], "A": [] })
        reqset.graph_master_node = reqset.find("A")

        rdep = RDepNoDirectedCircles(opts, config)
        result = rdep.rewrite(reqset)

        assert(result==True)

    def test_negative_01(self):
        "small digraph D -> B -> A and A -> C -> D"
        opts, config, reqset = create_parameters(
            {"D": ["B"], "C": ["D"], "B": ["A"], "A": ["C"] })
        reqset.graph_master_node = reqset.find("A")

        rdep = RDepNoDirectedCircles(opts, config)
        result = rdep.rewrite(reqset)

        assert(result==False)

