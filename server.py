from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from sklearn.neighbors import NearestNeighbors

import pandas as pd
import numpy as np

# EDIT Here: Eg: create_engine('postgresql://postgres:postgres@localhost:5432/database')
db_connect = create_engine('postgresql://postgres@localhost:5432/Pluralsight')
app = Flask(__name__)
api = Api(app)
df1 = pd.read_sql_query('select user_handle, course_id, SUM(view_time_seconds) as view_time_seconds from user_course_views group by user_handle, course_id', con=db_connect)
courses_df1 = df1.pivot(index='user_handle', columns='course_id', values='view_time_seconds')
courses_df1 = courses_df1.fillna(-1)
df2 = pd.read_sql_query('select user_handle, assessment_tag, user_assessment_score from user_assessment_scores ', con=db_connect)
courses_df2 = df2.pivot(index='user_handle', columns='assessment_tag', values='user_assessment_score')
# Filling the courses not taken by a user as -1
courses_df2 = courses_df2.fillna(-1)
df3 = pd.read_sql_query('select user_handle, interest_tag from user_interests group by user_handle, interest_tag', con=db_connect)
df3['values'] = 1
courses_df3 = df3.pivot(index='user_handle', columns='interest_tag', values='values')
courses_df3 = courses_df3.fillna(-1)

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
        
class UserScoreSimilarity(Resource):
	def get(self, user_handle):
		try:
			user_id = sorted(df2['user_handle'].unique())
			user_handle = int(user_handle)
			user_handle = user_id.index(user_handle)
			k = 10
			similar = []
			indices = []
			model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
			model_knn.fit(courses_df2)
			
			distances, indices = model_knn.kneighbors(courses_df2.iloc[user_handle, :].values.reshape(1, -1), n_neighbors = k)
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
			result = {'Top 10 Similar Users based on score': result}
			return jsonify(result)
		
		except:
			return jsonify('Try Some other Input Values')

class UserViewSimilarity(Resource):
	def get(self, user_handle):
		try:
			user_id = sorted(df1['user_handle'].unique())
			user_handle = int(user_handle)
			user_handle = user_id.index(user_handle)
			k = 10
			similar = []
			indices = []
			model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
			model_knn.fit(courses_df1)
			
			distances, indices = model_knn.kneighbors(courses_df1.iloc[user_handle, :].values.reshape(1, -1), n_neighbors = k)
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
			result = {'Top 10 Similar Users based on Views': result}
			return jsonify(result)
		
		except:
			return jsonify('Try Some other Input Values')

class UserInterestSimilarity(Resource):
	def get(self, user_handle):
		try:
			user_id = sorted(df3['user_handle'].unique())
			user_handle = int(user_handle)
			user_handle = user_id.index(user_handle)
			k = 10
			similar = []
			indices = []
			model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
			model_knn.fit(courses_df3)
			
			distances, indices = model_knn.kneighbors(courses_df3.iloc[user_handle, :].values.reshape(1, -1), n_neighbors = k)
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
			result = {'Top 10 Similar Users Based on Interest': result}
			return jsonify(result)
		
		except:
			return jsonify('Try Some other Input Values')			

			
api.add_resource(UserScores, '/user_assessment_scores/<user_handle>')
api.add_resource(UserCourseViews, '/user_course_views/<user_handle>')
api.add_resource(UserInterests, '/user_interests/<user_handle>')
api.add_resource(UserScoreSimilarity, '/user_score_similarity/<user_handle>')
api.add_resource(UserViewSimilarity, '/user_view_similarity/<user_handle>')
api.add_resource(UserInterestSimilarity, '/user_interest_similarity/<user_handle>')


if __name__ == '__main__':
     app.run(port='5431')