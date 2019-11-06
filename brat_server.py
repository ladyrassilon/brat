from io import StringIO

from flask import Flask, request, jsonify

from server.src.server import serve

app = Flask(__name__)

@app.route("/ajax.cgi", methods=("GET", "POST"))
def ajax_cgi():
    try:
        remote_addr = request.environ['REMOTE_ADDR']
    except KeyError:
        remote_addr = None
    try:
        remote_host = request.environ['REMOTE_HOST']
    except KeyError:
        remote_host = None
    try:
        cookie_data = request.environ['HTTP_COOKIE']
    except KeyError:
        cookie_data = None

    params = request.form

    # Call main server
    cookie_hdrs, response_data = serve(params, remote_addr, remote_host,
                                       cookie_data)

    return jsonify(response_data[1])
    # Package and send response
    if cookie_hdrs is not None:
        response_hdrs = [hdr for hdr in cookie_hdrs]
    else:
        response_hdrs = []
    response_hdrs.extend(response_data[0])

    output = StringIO()

    output.write('\n'.join('%s: %s' % (k, v) for k, v in response_hdrs))
    output.write('\n')
    output.write('\n')
    output.write(response_data[1])

    final_output = output.getvalue()
    output.close()
    return final_output

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)