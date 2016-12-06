from corealgorithms.flows import IAlgorithm


class VerificationTableOutput(IAlgorithm):
    def __init__(self):
        pass

    def apply(self, data):
        if data is None:
            return None
        output = "Verification Estimation: Distance Table\n"
        table_dict = data.get('res_table', {})
        table_ops = data.get('res_options', {})
        precision = table_ops.get('precision', 0)
        count = table_ops.get('count', 0)
        output += "Distance\tCount\tProbability\n"
        for inx in range(0, table_ops.get('steps', 0), 1):
            dist = "{}-{}".format(inx / precision, (inx + 1) / precision)
            output += "{}\t{}\t{}\n".format(dist, table_dict[inx], 100.0 * (table_dict[inx] / (1.0 * count)))
        data.update({'output': output})
        return data
