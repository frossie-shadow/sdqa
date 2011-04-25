#! /usr/bin/env python

# 
# LSST Data Management System
# Copyright 2008, 2009, 2010 LSST Corporation.
# 
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the LSST License Statement and 
# the GNU General Public License along with this program.  If not, 
# see <http://www.lsstcorp.org/LegalNotices/>.
#

"""Unit test of stage that does SDQA independent check for WCS failure.
Run with:
   python sdqaWcsFailureCheckStageTest.py
or
   python
   >>> sdqaWcsFailureCheckStageTest
   >>> sdqaWcsFailureCheckStageTest.run()
"""
from __future__ import with_statement
import sys, os
import unittest
import eups
import lsst.utils.tests as utilsTests
import lsst.pex.harness.Clipboard as pexClipboard
import lsst.pex.policy as pexPolicy
import lsst.pex.harness as pexHarness
import lsst.pex.harness.stage as harnessStage
from lsst.pex.harness.simpleStageTester import SimpleStageTester
import lsst.sdqa as sdqa
import lsst.sdqa.pipeline as sdqaPipe
import lsst.afw.detection as afwDetect
import lsst.daf.base as dafBase
import math

class SdqaWcsFailureCheckStageTestCase(unittest.TestCase):
    """A test case for SdqaWcsFailureCheckStage.py"""

    def setUp(self):
        self.ss1 = afwDetect.SourceSet()
        nobj = 100
        for i in range(nobj):
            s = afwDetect.Source()
            s.setId(i)
            s.setRa(math.radians(10 + 0.001*i))
            s.setDec(math.radians(10 + 0.001*i))
            self.ss1.append(s)

    def tearDown(self):
        pass

    def testPipeline(self):
        policyFile = pexPolicy.DefaultPolicyFile("sdqa", 
                                                 "sdqaWcsFailureCheckStagePolicy.paf", "tests")
        policy = pexPolicy.Policy.createPolicy(policyFile)

        tester = SimpleStageTester(sdqaPipe.SdqaWcsFailureCheckStage(policy.get("SdqaWcsFailureCheckStage")))

        clipboard = pexClipboard.Clipboard()

        ccdMetadataKey = policy.get("SdqaWcsFailureCheckStage.inputKeys.ccdMetadataKey")
        dp = dafBase.PropertySet()
        dp.add("ccdExposureId", 123456789)
        clipboard.put(ccdMetadataKey, dp)

        extractedSourceSetKey = policy.get("SdqaWcsFailureCheckStage.inputKeys.extractedSourceSetKey")
        clipboard.put(extractedSourceSetKey, self.ss1)

        tester.runWorker(clipboard)

        res = clipboard.get(policy.get("SdqaWcsFailureCheckStage.outputKeys.astromVerifSdqaRatingsKey"))

        containerSlice2 = res.getSdqaRatings()[0:2]
        print "get ====="
        j = 0
        for s2 in containerSlice2:
            print j, "[", s2.getName(), "]", s2.getValue(), s2.getErr(), s2.getRatingScope()
            j += 1

        assert(res.getSdqaRatings()[0].getName()  == "nAstromVerifMatches")
        assert(res.getSdqaRatings()[0].getValue() == 456789)
        assert(res.getSdqaRatings()[0].getErr()   == 0.0)
        assert(res.getSdqaRatings()[0].getRatingScope() == 1)

        assert(res.getSdqaRatings()[1].getName()  == "astromVerifRmsRadDist")
        assert(res.getSdqaRatings()[1].getValue() == 0.456789)
        assert(res.getSdqaRatings()[1].getErr()   == 0.0)
        assert(res.getSdqaRatings()[1].getRatingScope() == 1)

 
def suite():
    """Returns a suite containing all the test cases in this module."""

    utilsTests.init()

    suites = []

    if not eups.productDir("sdqa"):
        print >> sys.stderr, "sdqa is not setting up; skipping test"
    else:        
        suites += unittest.makeSuite(SdqaWcsFailureCheckStageTestCase)

    suites += unittest.makeSuite(utilsTests.MemoryTestCase)
    return unittest.TestSuite(suites)

def run(exit=False):
    """Run the tests"""
    utilsTests.run(suite(), exit)

if __name__ == "__main__":
    run(True)


