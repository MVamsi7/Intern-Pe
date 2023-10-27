# -*- coding: utf-8 -*-
"""Task _3 IPL Prediction

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vMCFRa6hCvF_BiOFAlVm0N6QUqoirCkc
"""

import numpy as np
import pandas as pd

match = pd.read_csv('/content/matches.csv')
delivery = pd.read_csv('/content/deliveries.csv')

match.head()

match.shape

delivery.head()

total_score_df = delivery.groupby(['match_id','inning']).sum()['total_runs'].reset_index()

total_score_df = total_score_df[total_score_df['inning'] == 1]

total_score_df

match_df = match.merge(total_score_df[['match_id','total_runs']],left_on='id',right_on='match_id')

match_df

match_df['team1'].unique()

teams = [
    'Sunrisers Hyderabad',
    'Mumbai Indians',
    'Royal Challengers Bangalore',
    'Kolkata Knight Riders',
    'Kings XI Punjab',
    'Chennai Super Kings',
    'Rajasthan Royals',
    'Delhi Capitals'
]

match_df['team1'] = match_df['team1'].str.replace('Delhi Daredevils','Delhi Capitals')
match_df['team2'] = match_df['team2'].str.replace('Delhi Daredevils','Delhi Capitals')

match_df['team1'] = match_df['team1'].str.replace('Deccan Chargers','Sunrisers Hyderabad')
match_df['team2'] = match_df['team2'].str.replace('Deccan Chargers','Sunrisers Hyderabad')

match_df = match_df[match_df['team1'].isin(teams)]
match_df = match_df[match_df['team2'].isin(teams)]

match_df.shape

match_df = match_df[match_df['dl_applied'] == 0]

match_df = match_df[['match_id','city','winner','total_runs']]

delivery_df = match_df.merge(delivery,on='match_id')

delivery_df = delivery_df[delivery_df['inning'] == 2]

delivery_df

delivery_df['current_score'] = delivery_df.groupby('match_id').cumsum()['total_runs_y']

delivery_df['runs_left'] = delivery_df['total_runs_x'] - delivery_df['current_score']

delivery_df['balls_left'] = 126 - (delivery_df['over']*6 + delivery_df['ball'])

delivery_df

delivery_df['player_dismissed'] = delivery_df['player_dismissed'].fillna("0")
delivery_df['player_dismissed'] = delivery_df['player_dismissed'].apply(lambda x:x if x == "0" else "1")
delivery_df['player_dismissed'] = delivery_df['player_dismissed'].astype('int')
wickets = delivery_df.groupby('match_id').cumsum()['player_dismissed'].values
delivery_df['wickets'] = 10 - wickets
delivery_df.head()

delivery_df.head()

# crr = runs/overs
delivery_df['crr'] = (delivery_df['current_score']*6)/(120 - delivery_df['balls_left'])

delivery_df['rrr'] = (delivery_df['runs_left']*6)/delivery_df['balls_left']

def result(row):
    return 1 if row['batting_team'] == row['winner'] else 0

delivery_df['result'] = delivery_df.apply(result,axis=1)

final_df = delivery_df[['batting_team','bowling_team','city','runs_left','balls_left','wickets','total_runs_x','crr','rrr','result']]

final_df = final_df.sample(final_df.shape[0])

final_df.sample()

final_df.dropna(inplace=True)

final_df = final_df[final_df['balls_left'] != 0]

X = final_df.iloc[:,:-1]
y = final_df.iloc[:,-1]
from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=1)

X_train

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

trf = ColumnTransformer([
    ('trf',OneHotEncoder(sparse=False,drop='first'),['batting_team','bowling_team','city'])
]
,remainder='passthrough')

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

pipe = Pipeline(steps=[
    ('step1',trf),
    ('step2',LogisticRegression(solver='liblinear'))
])

pipe.fit(X_train,y_train)

y_pred = pipe.predict(X_test)

from sklearn.metrics import accuracy_score
accuracy_score(y_test,y_pred)

pipe.predict_proba(X_test)[10]

def match_summary(row):
    print("Batting Team-" + row['batting_team'] + " | Bowling Team-" + row['bowling_team'] + " | Target- " + str(row['total_runs_x']))

def match_progression(x_df,match_id,pipe):
    match = x_df[x_df['match_id'] == match_id]
    match = match[(match['ball'] == 6)]
    temp_df = match[['batting_team','bowling_team','city','runs_left','balls_left','wickets','total_runs_x','crr','rrr']].dropna()
    temp_df = temp_df[temp_df['balls_left'] != 0]
    result = pipe.predict_proba(temp_df)
    temp_df['lose'] = np.round(result.T[0]*100,1)
    temp_df['win'] = np.round(result.T[1]*100,1)
    temp_df['end_of_over'] = range(1,temp_df.shape[0]+1)

    target = temp_df['total_runs_x'].values[0]
    runs = list(temp_df['runs_left'].values)
    new_runs = runs[:]
    runs.insert(0,target)
    temp_df['runs_after_over'] = np.array(runs)[:-1] - np.array(new_runs)
    wickets = list(temp_df['wickets'].values)
    new_wickets = wickets[:]
    new_wickets.insert(0,10)
    wickets.append(0)
    w = np.array(wickets)
    nw = np.array(new_wickets)
    temp_df['wickets_in_over'] = (nw - w)[0:temp_df.shape[0]]

    print("Target-",target)
    temp_df = temp_df[['end_of_over','runs_after_over','wickets_in_over','lose','win']]
    return temp_df,target

temp_df,target = match_progression(delivery_df,74,pipe)
temp_df

import matplotlib.pyplot as plt
plt.figure(figsize=(18,8))
plt.plot(temp_df['end_of_over'],temp_df['wickets_in_over'],color='yellow',linewidth=3)
plt.plot(temp_df['end_of_over'],temp_df['win'],color='#00a65a',linewidth=4)
plt.plot(temp_df['end_of_over'],temp_df['lose'],color='red',linewidth=4)
plt.bar(temp_df['end_of_over'],temp_df['runs_after_over'])
plt.title('Target-' + str(target))

teams

delivery_df['city'].unique()

delivery_df['runs_left'].unique()

from ipywidgets import widgets
from IPython.display import display

def predict_winner(b):
    try:
        team1 = team1_entry.value
        team2 = team2_entry.value
        runs_left = int(runs_left_entry.value)
        balls_left = int(balls_left_entry.value)
        wickets = int(wickets_entry.value)
        total_runs_x = int(total_runs_x_entry.value)
        crr = float(crr_entry.value)
        rrr = float(rrr_entry.value)

        # Calculate a simple score (you can replace this with your prediction model)
        score_team1 = int(runs_left + balls_left/6 + wickets*10 - total_runs_x/10 - crr - rrr)
        score_team2 = int(total_runs_x/10 - crr - rrr)

        # Display the predicted winner
        if score_team1 > score_team2:
            result_text.value = f"{team1} is predicted to win with a score of {score_team1}"
        elif score_team1 < score_team2:
            result_text.value = f"{team2} is predicted to win with a score of {score_team2}"
        else:
            result_text.value = "It's a tie!"
    except ValueError:
        result_text.value = "Please enter valid numerical values."

# Create interactive widgets
team1_entry = widgets.Text(description='Team 1:')
team2_entry = widgets.Text(description='Team 2:')
runs_left_entry = widgets.IntText(description='Runs Left:')
balls_left_entry = widgets.IntText(description='Balls Left:')
wickets_entry = widgets.IntText(description='Wickets:')
total_runs_x_entry = widgets.IntText(description='Total Runs:')
crr_entry = widgets.FloatText(description='CRR:')
rrr_entry = widgets.FloatText(description='RRR:')
predict_winner_button = widgets.Button(description='Predict Winner')
result_text = widgets.HTML(value='Prediction will be displayed here.')

# Assign callback function to the button click event
predict_winner_button.on_click(predict_winner)

# Display widgets
display(team1_entry, team2_entry, runs_left_entry, balls_left_entry, wickets_entry, total_runs_x_entry, crr_entry, rrr_entry, predict_winner_button, result_text)