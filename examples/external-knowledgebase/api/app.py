from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
from api.doc import retrieval_doc
import os

app = Flask(__name__)
app.add_url_rule('/', endpoint='ping', view_func=lambda:'Pong!')
swagger = Swagger(app)  # http://host/apidocs/

# Authorization 키 (환경변수로 관리)
API_KEY = os.getenv("API_KEY", "")

def search_mock(knowledge_id: str, query: str):
    """ 예를 들어 검색 엔진의 실행 결과응답이 다음과 같을 수 있음 """
    search_result = [
        {
            "metadata": {
                "document_name": "The Little Prince.pdf",
                "document_url": "https://example.com/books/little-prince",
                "document_summary": "A poetic tale about a pilot stranded in the desert who meets a young prince visiting Earth from a tiny asteroid.",
                "page": 11,
            },
            "score": 0.98,
            "title": "The Little Prince.pdf",
            "content": "어린 왕자가 떠나온 별이 소행성 B612호라고 믿는 데는 그럴 만한 근거가 있다. 이 소행성을 1909년 딱 한 번 터키 천문학자가 망원경으로 관측한 적이 있다.그래서 그는 국제 천문학 대회에서 자신의 발견을 성대히 증명해 냈다. 그러나 그가 입은 옷 때문에 아무도 그를 믿지 않았다. 어른은 언제나 그렇다.다행히도 소행성 B612호의 명성을 위해 터키의 독재자는 백성에게 서구 의상을 입지 않으면 사형에 처하겠다고 으름장을 놓았다. 그 천문학자는 1920년 매우 세련된 의상을 차려입고 다시 증명했다. 그러자 이번에는 모두 그의 견해를 받아들였다."
        },
        {
            "metadata": {
                "document_name": "Alice in Wonderland.pdf",
                "document_url": "https://example.com/books/alice",
                "document_summary": "A whimsical story about a young girl who falls down a rabbit hole into a fantasy world.",
                "page": 23,
            },
            "score": 0.55,
            "title": "Alice in Wonderland.pdf",
            "content": "앨리스는 곧장 다시 말하기 시작했다. “내가 지구를 곧장 뚫고 지나가는 건지도 모르겠어! 머리를 아래로 향하고 걷는 사람들 사이에 내가 불쑥 나타나면 얼마나 우스꽝스러워 보일까! 반감자들이겠지.”(앨리스는 이번엔 듣고 있는 사람이 아무도 없어서 다행이라고 생각했다. 적절한 단어같지 않았으니까.) “하지만, 그 곳이 어느 나라인지는 물어봐야 할 거야. 실례합니다, 아주머니, 여기가 뉴질랜드인가요? 아니면 오스트레일리아인가요?”(이렇게 말하면서 앨리스는 무릎을 굽혀 예의바르게 인사하려고 했다. 떨어지는 와중에도 허공에서 무릎을 굽히는 멋들어진 인사라니! 당신이라면 그렇게 할 수 있을까?) “그러면 나를 얼마나 무식한 여자애라고 생각하겠어. 아니지, 절대 물어보지 않을거야. 아마 나라 이름이 적혀 있는 곳은 없는지 찾아봐야겠네.”"
        },        
    ]

    return search_result

def search(knowledge_id: str, query: str, top_k: int):
    """ real implementation """
    
    # TODO: To be implemented
    # if not knowledge:
    #     return jsonify({"error_code": 2001, "error_msg": "The knowledge does not exist"}), 404
    
    search_result = []
    return search_result



@app.route('/retrieval', methods=['POST'])
@swag_from(retrieval_doc)
def retrieval():
    """외부 지식 데이터베이스 검색 API"""

    data = request.json
    knowledge_id = data.get("knowledge_id")
    query = data.get("query")
    retrieval_setting = data.get("retrieval_setting")
    top_k = retrieval_setting.get("top_k")
    score_threshold = retrieval_setting.get("score_threshold")


    search_result = search_mock(knowledge_id, query)
    # search_result = search(knowledge_id, query, top_k) # TODO: Use this for real implementation

    ## 검색 엔진 실행 결과를 response 형식으로 변환
    output_results = []
    for s in search_result:
        record = {
            "score": s.get('score'),
            "title": f"{s.get('title')}", 
            "content": s.get('content')
        }
        metadata = s.get('metadata')
        if metadata:
            record["metadata"] = {
                "document_name": metadata.get('document_name'), 
                "document_url": metadata.get('document_url'),
                "document_summary": metadata.get('document_summary'),
                "page": metadata.get('page'),
            }
        output_results.append(record)

    filtered_records = [
        record for record in output_results
        if record["score"] >= score_threshold
    ]
    sorted_records = sorted(filtered_records, key=lambda x: x["score"], reverse=True)[:top_k]

    response_data = {
        "records": sorted_records
    }
    
    return jsonify(response_data), 200


debug = os.getenv("FLASK_ENV") == "development"
if __name__ == '__main__':
    if debug:
        app.run(port=8081, host='0.0.0.0', debug=True)