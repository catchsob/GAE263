import flask
import rr


app = flask.Flask(__name__)

@app.route('/')
def hello():
    return 'hello Rose'

@app.route('/plates', methods=['POST'])
def plates():
    print(flask.request.method)
    if flask.request.files:
        file = flask.request.files.get('image')
        if file:
            image = file.read()
            if image and isinstance(image, bytes):
                model = flask.request.form.get('model', 'gemini-3.5-flash')

                r = rr.recognize_plates(image, model=model)
                print(r, flush=True)
                if r:
                    return {'success': True, 'plates': r, 'model': model}
                else:
                    return {'success': False, 'model': model, 'reason': 'no car or bad Gemini'}
    return 'Bad Request', 400

if __name__ == '__main__':
    app.run(port=8080)