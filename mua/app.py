from mua import Mua

app = Mua()


@app.route('/')
def hello():
    return 'hello'



