# -*- coding: utf-8 -*-
"""Kickstarter_trial

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aYLV9M1K6RwOGv2HrESdy6JHAlNdye3y
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import warnings
warnings.simplefilter('ignore', UserWarning)

# read the data from ks-projects-201801.csv - 378,661 projects.
dataframe = pd.read_csv('/content/drive/MyDrive/Kickstarter/ks-projects-201801.csv')

# show information and data types of the data attributes.
dataframe.info()

dataframe.head

dataframe["state"].unique()

# projects state ratio
(dataframe['state'].value_counts()/len(dataframe))*100

# plot state distribution.
sns.catplot('state',data=dataframe,kind='count', height=6)

# num of launched projects per day of week 
dataframe.groupby([(pd.to_datetime(dataframe.launched).dt.strftime("%A"))]).size().plot(kind='bar',figsize=(10,5))

# total projects per year
dataframe.groupby([(pd.to_datetime(dataframe.launched).dt.year)]).size()

dataframe.groupby([(pd.to_datetime(dataframe.launched).dt.year)]).size().plot(figsize=(10,5))

# i will reduce datapoints to get more clean data
start_date = '2013-01-01'
dataframe = dataframe[dataframe['launched'] >= start_date]
dataframe.groupby([(pd.to_datetime(dataframe.launched).dt.year)]).size().plot(figsize=(10,5))

# average pledged amount in USD
round(dataframe['usd_pledged_real'].mean())

# average backers
int(dataframe['backers'].mean())

# average projects goal in usd
round(dataframe['usd_goal_real'].mean())

# heat map of average backers by country and main_category
pivot_table = dataframe.pivot_table(index='main_category', 
                   columns='country', 
                   values='backers', 
                   aggfunc='mean')
sns.heatmap(pivot_table)

# for the prediction purpose, i will filter the data
# to have only successful and failed projects.
dataframe = dataframe.loc[dataframe['state'].isin(['successful', 'failed'])]

# projects main category ratio
(dataframe['main_category'].value_counts()/len(dataframe))*100

# plot main category ratio distibution
(dataframe['main_category'].value_counts()/len(dataframe)).plot.pie(y='mass', figsize=(5, 5))

# count projects by country
dataframe['country'].value_counts()

# plot country distribution
sns.catplot('country',data=dataframe, order = dataframe['country'].value_counts().index,kind='count', height=6,)

# now country/state distribution.
sns.catplot("country", hue="state", kind="count",edgecolor=".6", data=dataframe, order = dataframe['country'].value_counts().index);

# checking which columns has null values
dataframe.isnull().sum()

# we can see that usd_pledged are the only column that has null values
# we will drop this column and so all columns that is known just after project is launched like
# pledged, backers, usd_pledged_real
# name, ID also are not influcing the machine learning process , so i will delete it as well.
dataframe = dataframe.drop(['ID', 'name', 'usd pledged', 'pledged', 'backers', 'usd_pledged_real'], axis=1)

# the dataframe now 
dataframe.head()

# encode string values to integers for the macheine learning purpose
countryTransformer = preprocessing.LabelEncoder()
currencyTransformer = preprocessing.LabelEncoder()
main_categoryTransformer = preprocessing.LabelEncoder()
categoryTransformer = preprocessing.LabelEncoder()
dataframe['country'] = countryTransformer.fit_transform(dataframe['country'])
dataframe['currency'] = currencyTransformer.fit_transform(dataframe['currency'])
dataframe['main_category'] = main_categoryTransformer.fit_transform(dataframe['main_category'])
dataframe['category'] = categoryTransformer.fit_transform(dataframe['category'])

# convert dates to Unix time in nano seconds
dataframe["launched"] = pd.to_datetime(dataframe["launched"])
dataframe["deadline"] = pd.to_datetime(dataframe["deadline"])

# and now i will add a new feature based on deadline and launched
# project_length will be deadline - launched
dataframe["project_length"] = dataframe["deadline"] - dataframe["launched"]

# and now there is no need for deadline and launched
dataframe = dataframe.drop(['deadline', 'launched'], axis=1)

dataframe["project_length"] = dataframe.project_length.values.astype(np.int64)
dataframe.head()

# X is the dataframe without the state column
X = dataframe.drop('state', axis=1)
# Y is the state column
Y = dataframe['state']

# here we are splitting the data into 80% and 20%
# 80% is for the model training X_train, Y_train
# 20% is for the model testing X_test, Y_test
# we will predict the state of X_test and compare it to the real data Y_test
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

# now let us check multiplue classification machine learning models


# prepare models
classifiers = [
    DecisionTreeClassifier(),
    GradientBoostingClassifier(),
    KNeighborsClassifier(),
    RandomForestClassifier(),
    GaussianNB()
]

# evaluate one by one to check who is the most accuracte 
for clf in classifiers:
    clf.fit(X_train, Y_train)
    
    print("="*30)
    print(clf.__class__.__name__)    
    
    prediction = clf.predict(X_test)
    acc = accuracy_score(Y_test, prediction)
    
    print("Accuracy: {:.2%}".format(acc))

print("="*30)
print('Finish')

# we can see that GradientBoostingClassifier is the most accurist model
# so lets perform fine tuning on the learning_rate attribute of the model
learning_rates = [1, 0.7, 0.5, 0.25, 0.1, 0.01]
for lrn in learning_rates:
    clf = GradientBoostingClassifier(learning_rate=lrn)
    clf.fit(X_train, Y_train)
    print("="*30)
    print(lrn)
    prediction = clf.predict(X_test)
    acc = accuracy_score(Y_test, prediction)
    print("Accuracy: {:.2%}".format(acc))
    
print("="*30)
print('Finish')

# we will use the best performance learning rate
# in fact, we can get more accuracy if we have more informative data features.
 
clf = GradientBoostingClassifier(learning_rate=0.7)
clf.fit(X_train, Y_train)
print('****Results****')
prediction = clf.predict(X_test)
acc = accuracy_score(Y_test, prediction)
print("Accuracy: {:.2%}".format(acc))

# comparing prediction to true data
np.column_stack((prediction,Y_test))

# let us see the feature importance order of the predition model.
feats = {}
for feature, importance in zip(X_train.columns, clf.feature_importances_):
    feats[feature] = importance #add the name/value pair 

importances = pd.DataFrame.from_dict(feats, orient='index').rename(columns={0: 'Feature-importance'})
importances.sort_values(by='Feature-importance').plot(kind='bar', rot=45)

futureData = pd.DataFrame(columns=['category', 'main_category', 'currency', 'deadline', 'goal', 'launched', 'country', 'usd_goal_real'])
futureData.loc[0] = ['Restaurants', 'Food', 'USD', '2019-07-30', '60000.0', '2019-04-01 12:00:00','US', '60000.00']

futureData.head()

futureData['country'] = countryTransformer.transform(futureData['country'])
futureData['currency'] = currencyTransformer.transform(futureData['currency'])
futureData['main_category'] = main_categoryTransformer.transform(futureData['main_category'])
futureData['category'] = categoryTransformer.transform(futureData['category'])

futureData["launched"] = pd.to_datetime(futureData["launched"])
futureData["deadline"] = pd.to_datetime(futureData["deadline"])
futureData["deadline"] =  futureData.deadline.values.astype(np.int64)
futureData["launched"] =  futureData.launched.values.astype(np.int64)

futureData["project_length"] = futureData["deadline"] - futureData["launched"]
futureData = futureData.drop(['deadline', 'launched'], axis=1)

futureData.head()

prediction = clf.predict(futureData)
prediction