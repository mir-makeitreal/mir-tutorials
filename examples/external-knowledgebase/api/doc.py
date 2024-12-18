retrieval_doc = {
    'tags': ['Knowledge Retrieval'],
    'summary': 'Retrieve knowledge from a custom knowledge base',
    'description': '사용자가 제공한 query와 설정을 기반으로 관련 정보를 검색합니다.',
    'parameters': [
    {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'Request data in JSON format',
            'schema': {
                'type': 'object',
                'properties': {
                    'knowledge_id': {'type': 'string', 'example': 'dataset-0000'},
                    'query': {'type': 'string', 'example': '어린왕자는 어느 별에서 왔나?'},
                    'retrieval_setting': {
                        'type': 'object',
                        'properties': {
                            'top_k': {'type': 'integer', 'example': 5},
                            'score_threshold': {'type': 'number', 'format': 'float', 'example': 0.01}
                        },
                        'required': ['top_k', 'score_threshold']
                    }
                },
                'required': ['knowledge_id', 'query', 'retrieval_setting']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Successful response with retrieved knowledge records',
            'schema': {
                'type': 'object',
                'properties': {
                    'records': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'metadata': {
                                    'type': 'object',
                                    'properties': {
                                        'path': {'type': 'string'},
                                        'description': {'type': 'string'}
                                    }
                                },
                                'score': {'type': 'number', 'format': 'float'},
                                'title': {'type': 'string'},
                                'content': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        },
        401: {'description': "Invalid Authorization header format"},
        403: {'description': "Authorization failed"},
        404: {'description': "The knowledge does not exist"}
    }
}