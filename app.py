from flask import Flask,render_template,request

app = Flask(__name__)

#@app.route("/results",methods=["GET","POST"])
#def results():
#    return render_template()
                               
@app.route("/", methods=["GET","POST"])
def index():
    if request.method=="GET":
        return render_template("index.html")
    else:
        a = []
        i = 2
        t = []
        try:
            a.append(request.form["a"])
        except:
            pass
        try:
            while(1):
                a.append(request.form["a" + str(i)])
                i = i + 1
        except:
            pass
        i = 1
        try:
            while(1):
                t.append(request.form[str(i)])
                i = i + 1
        except:
            pass
        print(a)
        print(t)
        #Stuff goes here
        return render_template("results.html", a = a, t = t)

if __name__=="__main__":
    app.debug=True
    app.run(host="0.0.0.0",port=5000)
