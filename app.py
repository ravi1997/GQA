from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/info', methods=['GET', 'POST'])
def info():
    data = {
        'method': request.method,
        'url': request.url,
        'remote_addr': request.remote_addr,
        'headers': dict(request.headers),
        'args': request.args.to_dict(),
        'form': request.form.to_dict(),
        'json': request.json,
        'cookies': request.cookies,
        'user_agent': request.user_agent.string,
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
