from mua.mua import Mua

app = Mua()


@app.route('/')
def hello():
    return 'hello'


if __name__ == "__main__":
    app.run()

