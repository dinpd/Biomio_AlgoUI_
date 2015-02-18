__author__ = 'andriy.lobashchuk'

FAKE_DB_LIST = [dict(pk=1, name='db_1'), dict(pk=2, name='db_2')]
FAKE_ALGO_LIST = [dict(pk=1, name='algo_1'), dict(pk=2, name='algo_2')]

FAKE_ALGO_DB_SETTINGS = {
    'algo__db': {
        'inputs': {
            'elements': [
                {
                    'label': 'Test1',
                    'default_value': 'test'
                }, {
                    'label': 'Test2',
                    'default_value': 'test_test'
                }
            ],
            'general_label': 'Inputs Test'
        },
        'checkboxes': {
            'elements': [
                {
                    'label': 'Test1',
                    'default_value': True
                }, {
                    'label': 'Test2',
                    'default_value': False
                }
            ],
            'general_label': 'Checkboxes Test'
        },
        'radio_buttons': {
            'elements': [
                'Test1',
                'Test2',
                'Test3'
            ],
            'default_value': 'Test2',
            'general_label': 'Radio Buttons Test'
        },
        'selects': {
            'elements': [
                {
                    'options': [
                        {
                            'value': 1,
                            'label': 'Test 1'
                        }, {
                            'value': 2,
                            'label': 'Test 2'
                        }
                    ],
                    'default_value': 1,
                    'general_label': 'Select 1'
                }, {
                    'options': [
                        {
                            'value': 1,
                            'label': 'Test 1'
                        }, {
                            'value': 2,
                            'label': 'Test 2'
                        }
                    ],
                    'default_value': 2,
                    'general_label': 'Select 2'
                }
            ],
            'general_label': 'Selects Test'
        }
    },

}

VERIFICATION_SETTINGS = {
    'inputs': {
        'elements': [
            {
                'label': "Max Neighbours Distance",
                'default_value': 50,
                'callback': "<function object>"
            }
        ],
        'general_label': 'Verification Settings'
    }
}