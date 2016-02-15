from biomio.algorithms.logger import logger
import os

def range_positive_verification_estimation(results):
    rtrue = dict() #0
    rfalse = dict() #0
    for inx in range(0, 20):
        rtrue[str(5 * inx)] = 0
        rfalse[str(5 * inx)] = 0
    for curr in results:
        logger.debug(curr[0])
        if curr[1] is not False:
            # print "yaleB11" == os.path.split(os.path.split(curr.path())[0])[1]
            # print res > self._keysrecg_detector.kodsettings.probability
            # print self._keysrecg_detector.kodsettings.probability
            # print res
            for inx in range(0, 20):
                if ("yaleB11" == os.path.split(os.path.split(curr.path())[0])[1]) == \
                        (curr[1] > 5.0 * inx):
                    value = rtrue.get(str(5 * inx), 0)
                    value += 1
                    rtrue[str(5 * inx)] = value
                else:
                    value = rfalse.get(str(5 * inx), 0)
                    value += 1
                    rfalse[str(5 * inx)] = value
    for inx in range(0, 20):
        logger.debug("Threshold: " + str(5 * inx))
        logger.debug("Positive verification: " + str(rtrue.get(str(5 * inx), 0)) + "\t"
                     + str((rtrue.get(str(5 * inx), 0) / (1.0 * (rtrue.get(str(5 * inx), 0) +
                                                                 rfalse.get(str(5 * inx), 0)))) * 100))
        logger.debug("Negative verification: " + str(rfalse.get(str(5 * inx), 0)) + "\t"
                     + str((rfalse.get(str(5 * inx), 0) / (1.0 * (rtrue.get(str(5 * inx), 0) +
                                                                  rfalse.get(str(5 * inx), 0)))) * 100))

def range_probability_verification_estimation(results):
    prob = dict()
    count = 0
    for curr in results:
        if curr[1] is not False:
            for inx in range(1, 20):
                if curr[1] < 5.0 * inx:
                    value = prob.get(str(5 * inx), 0)
                    value += 1
                    prob[str(5 * inx)] = value
                    count += 1
                    break
    for inx in range(1, 20):
        graph = ""
        val = prob.get(str(5 * inx), 0)
        rel = int((val / (1.0 * count)) * 20)
        for i in range(0, rel, 1):
            graph += "*"
        logger.debug(str(5 * (inx - 1)) + "-" + str(5 * inx) + "%\t= " + str(val) + "\t=\t"
                     + str((val / (1.0 * count)) * 100) + "%\t" + graph)
