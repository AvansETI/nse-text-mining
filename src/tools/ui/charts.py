def get_pie_chart_options(labels, data):
    if len(labels) != len(data):
        raise Exception("Length of labels and data has to be the same")

    options = {
        'legend': {
            'orient': 'vertical',
            'x': 'left',
            'y': 'bottom',
            'data': labels,
            'textStyle': {
                'color': '#FFFFFF'
                },
            },
        'series': [
            {
                'type': 'pie',
                'color': [
                    '#C20030',
                    '#555555'
                    ],
                'radius': ['50%', '70%'],
                'avoidLabelOverlap': False,
                'label': {
                    'show': False,
                    'position': 'center'
                    },
                'labelLine': {
                    'show': False
                    },
                'emphasis': {
                    'label': {
                        'show': True,
                        'fontSize': '20',
                                    'fontWeight': 'bold',
                                    'color': 'white'
                        }
                    },
                'data': [{'name': label, 'value': data[label]} for label in labels]
                },
            ]
        }

    return options
