from flask import Flask, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

db = SQLAlchemy()
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ass.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

class Countries(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    cntry = db.Column("Country name:", db.String, unique=True)
    offnames = db.Column("Official name: ", db.String, unique=True)
    capcities = db.Column("Capital city: ", db.String)
    flags = db.Column("Flags: ", db.String)
    natnames = db.Column("Native Name: ", db.String)
    currencies = db.Column("Currency: ", db.String)
    regions = db.Column("Region: ", db.String)
    subregions = db.Column("Subregion: ", db.String)
    langs = db.Column("Language: ", db.String)
    populations = db.Column("Population: ", db.Integer)
    areas = db.Column("Area: ", db.String)

    def __init__(self, cntry, offnames, capcities, flags, natnames, currencies, regions, subregions, langs, populations, areas):
        self.cntry = cntry
        self.offnames = offnames
        self.capcities = capcities
        self.flags = flags
        self.natnames = natnames
        self.currencies = currencies
        self.regions = regions
        self.subregions = subregions
        self.langs = langs
        self.populations = populations
        self.areas = areas

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/result', methods=['GET', 'POST'])
def result():
    country = request.values['country']
    url = 'https://restcountries.com/v3.1/name/' + country
    r = requests.get(url)
    checker = bool(Countries.query.filter_by(cntry=country).scalar())
    if checker == 1 and r.status_code==200:
        dbcountry = db.session.query(Countries.offnames, Countries.capcities, Countries.flags, Countries.natnames,
                                     Countries.currencies, Countries.regions, Countries.subregions, Countries.langs,
                                     Countries.populations, Countries.areas).filter_by(cntry=country).all()
        offname = dbcountry[0][0]
        capcity = dbcountry[0][1]
        flag = dbcountry[0][2]
        natname = dbcountry[0][3]
        currency = dbcountry[0][4]
        region = dbcountry[0][5]
        subregion = dbcountry[0][6]
        lang = dbcountry[0][7]
        population = dbcountry[0][8]
        area = dbcountry[0][9]
        ccity = r.json()[0]['capital'][0]
        wweatherurl = 'https://api.openweathermap.org/data/2.5/weather?q=' + ccity + \
                     '&appid=10e4cf124f42ec60fdc904ac8d1b81ee&units=metric'
        ww = requests.get(wweatherurl)
        wweather = ww.json()['main']['temp']
        wwurl = 'https://openweathermap.org/img/wn/' + ww.json()['weather'][0]['icon'] + '@2x.png'
        return render_template('result.html', offName=offname, weather=wweather, wurl=wwurl,
                               capcity=capcity, flags=flag, natName=natname,
                               currency=currency, capCity=capcity, region=region,
                               subregion=subregion, lang=lang, population=population,
                               area=area)
    elif checker == 0 and r.status_code==200:
        cntry = country
        offName = r.json()[0]['name']['official']
        natName = list(r.json()[0]['name']['nativeName'].values())[0]['official']
        cur = list(r.json()[0]['currencies'].values())[0]
        currency = ', '.join(cur.values())
        capCity = r.json()[0]['capital'][0]
        city = capCity
        region = r.json()[0]['region']
        subregion = r.json()[0]['subregion']
        population = r.json()[0]['population']
        flags = r.json()[0]['flags']['png']
        area = r.json()[0]['area']
        languages = list(r.json()[0]['languages'].values())
        lang = ', '.join(languages)
        weatherurl = 'https://api.openweathermap.org/data/2.5/weather?q=' + city + \
                     '&appid=10e4cf124f42ec60fdc904ac8d1b81ee&units=metric'
        w = requests.get(weatherurl)
        weather = w.json()['main']['temp']
        wurl = 'https://openweathermap.org/img/wn/' + w.json()['weather'][0]['icon'] + '@2x.png'
        countrydb = Countries(cntry=country, offnames=offName, capcities=capCity, flags=flags, natnames=natName,
                              currencies=currency, regions=region, subregions=subregion,
                              langs=lang, populations=population, areas=area)
        db.session.add(countrydb)
        db.session.commit()
        return render_template('result.html', offName=offName, weather=weather, wurl=wurl,
                               capcity=capCity, flags=flags, natName=natName, currency=currency,
                               capCity=capCity, region=region, subregion=subregion,
                               lang=lang, population=population, area=area)
    else:
        return render_template('error.html')
if __name__ == '__main__':
    db.create_all()
    app.run(debug = True)