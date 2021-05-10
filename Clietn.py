from flask import Flask,redirect, url_for, render_template, request
from zeep import Client
from fpdf import FPDF
import pdfkit
import base64
dane =""
wsdl = "http://25.76.141.122:8080/ProjektSoapSerwer/Mtgsklep_serwerImplService?wsdl"
Client = Client(wsdl = wsdl)
app = Flask(__name__)
@app.route("/logowanie",methods = ["POST","GET"])
def logowanie():
    if request.method == "POST":
        login = request.form["nm"]
        password = request.form["ps"]
        try:
            konto = Client.service.zaloguj(login,password)
            return redirect(url_for("userr",login = konto.login, haslo = konto.haslo))
        except Exception:
            return "Brak uzytkownika"
    else: 
	    return render_template("logowanie.html")


@app.route("/Sklep/<login>/<haslo>", methods = ["POST","GET"])
def userr(login,haslo):
    magazyn = Client.service.zwroc_magazyn()
    konto = Client.service.zaloguj(login,haslo)
    #print(type(konto)
    ilustracjebase64 = []
    idilosc = []
    for k in magazyn:
        ilustracjebase64.append(base64.b64encode(k.karta.ilustracja).decode())
    for i in range(0,len(magazyn)):
        idilosc.append("id"+str(i))
    if request.method =="POST":
        if request.form["btn"] == "Dodaj do koszyka":
            for i in magazyn:
                if request.form[str(i.karta.nazwa)] != "0":
                    Client.service.dodaj_do_koszyka(konto.login,konto.haslo,i.karta.nazwa,request.form[i.karta.nazwa])
            return render_template("sklep.html",magazyn = magazyn,ilustracje = ilustracjebase64,idilosc=idilosc,konto=konto)
        if request.form["btn"] == "Przejdz do koszyka":
            return redirect(url_for("koszyk",login = konto.login, haslo = konto.haslo))
    else:
        return render_template("sklep.html",magazyn = magazyn,ilustracje = ilustracjebase64,idilosc=idilosc,koszyk = konto.koszyk,konto = konto)

@app.route("/koszyk/<login>/<haslo>",methods = ["POST","GET"])
def koszyk(login,haslo):
    konto = Client.service.zaloguj(login,haslo)
    if request.method == "POST":
        for i in konto.koszyk:
            if i.karta.nazwa in request.form:
                Client.service.usun_z_koszyka(login,haslo,i.karta.nazwa)
                konto = Client.service.zaloguj(login,haslo)
                return render_template("koszyk.html",koszyk = konto.koszyk) 
            elif 'btnn' in request.form:
                global dane
                dane = Client.service.zloz_zamowienie(login,haslo)
                return redirect(url_for("info",login = konto.login, haslo = konto.haslo))
        if 'pow' in request.form:
            return redirect(url_for("userr",login = konto.login, haslo = konto.haslo))
    else:
        return render_template("koszyk.html",koszyk = konto.koszyk)

@app.route("/koszyk/<login>/<haslo>/",methods = ["POST","GET"])
def info(login,haslo):
    global dane
    konto = Client.service.zaloguj(login,haslo)
    if request.method == "POST":
        rf = request.form["btn"]
        if rf=="Powrot do sklepu":
          return redirect(url_for("userr",login = konto.login, haslo = konto.haslo))
        elif rf =="Pobierz potwierdzenie":
            config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
            pdfkit.from_url("http://127.0.0.1:5000/koszyk/Lukasz/Kosmaty/#", 'Potwierdzenie zamowienia.pdf', configuration=config)
            return redirect(url_for("userr",login = konto.login, haslo = konto.haslo))
    else:
        return render_template("info.html", ds = dane,konto=konto)

if __name__ == '__main__':
    app.run(debug=True)
    