from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from json import dumps
from sklearn.neighbors import NearestNeighbors

import pandas as pd
import numpy as np

# EDIT Here: Eg: create_engine('postgresql://postgres:postgres@localhost:5432/database')
db_connect = create_engine('postgresql://postgres@localhost:5432/Pluralsight')
app = Flask(__name__)

# Getting rows from user_course_views table
df1 = pd.read_sql_query('select user_handle, course_id, SUM(view_time_seconds) as view_time_seconds from user_course_views group by user_handle, course_id', con=db_connect)
# Pivoting the table for recommendation
courses_df1 = df1.pivot(index='user_handle', columns='course_id', values='view_time_seconds')
# Filling the NaN values with -1 for courses not taken by user
courses_df1 = courses_df1.fillna(-1)

# Getting rows from user_course_views table
df2 = pd.read_sql_query('select user_handle, assessment_tag, user_assessment_score from user_assessment_scores ', con=db_connect)
courses_df2 = df2.pivot(index='user_handle', columns='assessment_tag', values='user_assessment_score')
# Filling the courses not taken by a user as -1
courses_df2 = courses_df2.fillna(-1)

# Getting rows from user_interests table
df3 = pd.read_sql_query('select user_handle, interest_tag from user_interests group by user_handle, interest_tag', con=db_connect)
# Creating new column and fill them as 1, like a score for the interested tags
df3['values'] = 1
# Pivoting the table for recommendation
courses_df3 = df3.pivot(index='user_handle', columns='interest_tag', values='values')
# Filling the NaN values with -1 for courses not taken by user
courses_df3 = courses_df3.fillna(-1)

def nearestNeighborModel(df, courses_df, user_handle):
	try:
		user_id = sorted(df['user_handle'].unique())
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
		result = {'Top 10 Similar Users based on score': result}
		return result
		
	except:
		return 'Try Some other Input Values'

@app.route('/user_score_similarity/<int:user_handle>', methods = ['GET'])
def userScoreSimilarity(user_handle):
	result = nearestNeighborModel(df2, courses_df2, user_handle)
	return jsonify(result)

@app.route('/user_view_similarity/<int:user_handle>', methods = ['GET'])
def userViewSimilarity(user_handle):
	result = nearestNeighborModel(df1, courses_df1, user_handle)
	return jsonify(result)

@app.route('/user_interest_similarity/<int:user_handle>', methods = ['GET'])
def get(user_handle):
	result = nearestNeighborModel(df3, courses_df3, user_handle)
	return jsonify(result)

if __name__ == '__main__':
     app.run(port='5431')