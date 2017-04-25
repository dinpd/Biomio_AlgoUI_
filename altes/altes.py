#!/usr/bin/env python2
#
# Copyright 2016-2017 altes Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from altes_tools import read_configuration_file, AVAILABLE_TEST
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('config', type=str, help="altes Configuration Test File Path.")
    args = parser.parse_args()
    configuration = read_configuration_file(args.config)
    if configuration is not None:
        test = AVAILABLE_TEST.get(configuration['test'])
        if test is not None:
            test_inst = test(**configuration['options'])
            for key, stage in configuration['stages'].iteritems():
                test_inst.addStage(key, AVAILABLE_TEST.get(stage)())
            test_inst.apply(configuration['data'])
