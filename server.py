from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from sklearn.neighbors import NearestNeighbors

import pandas as pd
import numpy as np
import json

# EDIT Here: Eg: create_engine('postgresql://postgres:postgres@localhost:5432/database')
db_connect = create_engine('postgresql://username:password@host:port/pluralsight')
app = Flask(__name__)
api = Api(app)

df = pd.read_sql_query('select user_handle, assessment_tag, user_assessment_score from user_assessment_scores ', con=db_connect)
courses_df = df.pivot(index='user_handle', columns='assessment_tag', values='user_assessment_score')
# Filling the courses not taken by a user as -1
courses_df = courses_df.fillna(-1)

class UserScores(Resource):
    def get(self, user_handle):
        conn = db_connect.connect()
        query = conn.execute("select * from user_assessment_scores where user_handle=%d" %int(user_handle))
        result = {'data': [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)

class UserCourseViews(Resource):
    def get(self, user_handle):
        conn = db_connect.connect()
        query = conn.execute("select * from user_course_views where user_handle=%d " %int(user_handle))
        result = {'data': [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)
		
class UserInterests(Resource):
    def get(self, user_handle):
        conn = db_connect.connect()
        query = conn.execute("select * from user_interests where user_handle=%d " %int(user_handle))
        result = {'data': [dict(zip(tuple(query.keys()), i)) for i in query.cursor]}
        return jsonify(result)
        
class UserSimilarity(Resource):
	def get(self, user_handle):
		try:
			user_id = sorted(df['user_handle'].unique())
			user_handle = int(user_handle)
			user_handle = user_id.index(user_handle)
			k = 10
			similar = []
			indices = []
			model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
			model_knn.fit(courses_df)
			
			distances, indices = model_knn.kneighbors(courses_df.iloc[user_handle, :].values.reshape(1, -1), n_neighbors = k)
			similar = 1-distances.flatten()
			print('{0} most similar users for user {1}:\n'.format(k, user_handle))
			similar_users = list()
			keys = ['Index', 'User Handle', 'Similarity Score']
			
			for i in range(0, len(indices.flatten())):
				if indices.flatten()[i]+1 == user_handle:
					continue
				else:
					similar_users.append((i, user_id[indices.flatten()[i]], similar.flatten()[i]))
			result = [dict(zip(keys, similar_user)) for similar_user in similar_users]
			for i in range(0, len(result)):
				result[i]['User Handle'] = int(result[i]['User Handle'])
			result = {'Top 10 Similar Users': result}
			return jsonify(result)
		
		except:
			return jsonify('Try Some other Input Values')
			
api.add_resource(UserScores, '/user_assessment_scores/<user_handle>')
api.add_resource(UserCourseViews, '/user_course_views/<user_handle>')
api.add_resource(UserInterests, '/user_interests/<user_handle>')
api.add_resource(UserSimilarity, '/user_similarity/<user_handle>')


if __name__ == '__main__':
     app.run(port='5431')