from flask import Flask,json,jsonify,json_available
from flask_restplus import Resource,Api,fields
from flask_pymongo import PyMongo
from collections import defaultdict
from bson.json_util import dumps
from flask_cors import CORS
from flask_restplus import cors

app=Flask(__name__)
api=Api(app)
cors=CORS(app)

app.config["MONGO_URI"]='mongodb://localhost:27017/moviesdb'
mongo=PyMongo(app)
imdb_model=api.model('imdb',{'name':fields.String,
                            '99popularity':fields.Float,
                            'director':fields.String,
                            'imdb_score':fields.Float,
                            'genre':fields.String})
collectns=mongo.db.movie

@api.route("/all")
class AllMovies(Resource):
    def get(self):
        all_l=[]
        all_c= collectns.find()
        for i in all_c:
            dic={'name':i['name'],
                "popularity":i["99popularity"],
                'director':i['director'],
                'imdb_score':i['imdb_score'],
                'genre':i['genre']}
            all_l.append(dic)
        return jsonify(all_l)

@api.route("/limit")
class Limited_Movies(Resource):
    def post(self):
        data=api.payload
        lim= data['limit']
        ski = data['skip']
        lim_l=[]
        lim_c= collectns.find().skip(ski).limit(lim)
        for i in lim_c:
            #print(i)
            dic={'name':i['name'],
                "popularity":i["99popularity"],
                'director':i['director'],
                'imdb_score':i['imdb_score'],
                'genre':i['genre']}
            lim_l.append(dic)
        return jsonify(lim_l)

@api.route("/top_dir")
class TopDirector(Resource):
    def get(self):
        top_c=collectns.find()
        top_l=defaultdict(list)
        for i in top_c:
            top_l[i['director']].append(i['name'])
        dire,mov=max(top_l.items(),key=lambda x:len(x[1]))
        return jsonify({'top_dire':dire,"count":len(mov),"mov_lst":mov})

@api.route("/top_ten_/imdb")
class TopTenMovies(Resource):
    def get(self):
        ten_c=collectns.find()
        ten_l=defaultdict(list)
        for i in ten_c:
            ten_l[i['name']].append(float(i['imdb_score']))
        s=sorted(ten_l.items(),key=lambda x:x[1],reverse=True)
        return jsonify({"top10_mov":s[:10]})

@api.route("/least_wat_mov")
class Lwmovies(Resource):
    def get(self):
        least_c=collectns.find()
        least_l=defaultdict(list)
        for i in least_c:
            least_l[i['name']].append(i['imdb_score'])
        s=sorted(least_l.items(),key=lambda x:x[1],reverse=True)
        return {"Least_wat_movie":s[-1]}

@api.route("/popular_genre")
class PopularGenere(Resource):
    def get(self):
        pop_c=collectns.find()
        pop_l=defaultdict(list)
        for i in pop_c:
            pop_l[i['99popularity']].append(i['genre'])
        pop,gen=max(pop_l.items(),key=lambda x:x[0])
        return jsonify({"BG":pop,"popularity":gen})

@api.route("/bst_dir_blw_100")
class BestMovieDirec(Resource):
    def get(self):
        bst_c=collectns.find()
        bst_l=defaultdict(list)
        for i in bst_c[0:100]:
                bst_l[i['director']].append(i['99popularity'])
        s=sorted(bst_l.items(),key=lambda x:max(x[1]),reverse=True)
        r=s[0]
        return jsonify({"best_dir":r})

@api.route("/new")
class PostMethod(Resource):
    @api.expect(imdb_model)
    def post(self):
        data = api.payload
        collectns.insert(data)
        data.pop('_id')
        return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5002)
