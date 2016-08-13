from mua import Mua

app = Mua()


@app.route("/")
def hi():
    return "hi"

@app.route("/hello/<username>")
def hello(username):
    return "hello %s"%(username)

if __name__ == "__main__":
    app.run()
