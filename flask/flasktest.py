from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload_file():
    print(request.files)
    #file = request.files['file']
    #file.save('uploads/' + file.filename)
    file = request.files.get('file_name')
    print(type(file), file)
    print(file.filename)
    file.save('uploads/test.py')
    return 'file uploaded successfully'

@app.route('/test', methods=['GET'])
def test():
    print(request.args)
    print(request.path)
    return 'test' 

if __name__ == '__main__':
    app.run()

# 测试
# curl -X GET "http://127.0.0.1:5000/test?pageNum=1&pageSize=100" -H "accept: application/json" -v
# curl -F "file_name=@obs_client.py" -X POST "http://127.0.0.1:5000/upload"
# curl -X GET "http://127.0.0.1:5011/api/v2/taskboard/task/page?pageNum=1&pageSize=100" -H "accept: application/json"
# curl -X POST "http://127.0.0.1:5011/api/v2/taskboard/launchTask" -H "accept: application/json" -H "Content-Type: application/json" -d '{ "configType": 2}'
# curl -X DELETE "http://127.0.0.1:5011/api/v2/taskboard/task/delete" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"taskId\": \"369\"}"