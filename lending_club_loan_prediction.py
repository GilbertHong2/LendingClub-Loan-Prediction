# LendingClub Loan Prediction

import pandas as pd
import numpy as np

from tabulate import tabulate

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

df = pd.read_csv('loan-clean-version.csv')
df.head()

"""# 1. Data Exploration

##full description of each fields:

LoanStatNew	 | Description
--- | ---
zip_code	|The first 3 numbers of the zip code provided by the borrower in the loan application.
addr_state	|The state provided by the borrower in the loan application
annual_inc|	The annual income provided by the borrower during registration.
collection_recovery_fee |	post charge off collection fee
collections_12_mths_ex_med |	Number of collections in 12 months excluding medical collections
delinq_2yrs	|The number of 30+ days past-due incidences of delinquency in the borrower’s credit file for the past 2 years
desc |	Loan description provided by the borrower
dti	| A ratio calculated using the borrower’s total monthly debt payments on the total debt obligations, excluding mortgage and the requested LC loan, divided by the borrower’s self-reported monthly income.
earliest_cr_line	|The month the borrower’s earliest reported credit line was opened
emp_length|	Employment length in years. Possible values are between 0 and 10 where 0 means less than one year and 10 means ten or more years.
emp_title|	The job title supplied by the Borrower when applying for the loan.
fico_range_high	|The upper boundary of range the borrower’s FICO belongs to.
fico_range_low|	The lower boundary of range the borrower’s FICO belongs to.
funded_amnt |	The total amount committed to that loan at that point in time.
funded_amnt_inv|	The total amount committed by investors for that loan at that point in time.
grade |	LC assigned loan grade
home_ownership|	The home ownership status provided by the borrower during registration. Our values are: RENT, OWN, MORTGAGE, OTHER.
id |	A unique LC assigned ID for the loan listing.
initial_list_status |	The initial listing status of the loan. Possible values are – W, F
inq_last_6mths |	The number of inquiries by creditors during the past 6 months.
installment	| The monthly payment owed by the borrower if the loan originates.
int_rate |	Interest Rate on the loan
is_inc_v |	Indicates if income was verified by LC, not verified, or if the income source was verified
issue_d	 | The month which the loan was funded
last_credit_pull_d |	The most recent month LC pulled credit for this loan
last_fico_range_high |	The last upper boundary of range the borrower’s FICO belongs to pulled.
last_fico_range_low |	The last lower boundary of range the borrower’s FICO belongs to pulled.
last_pymnt_amnt	| Last total payment amount received
last_pymnt_d |	Last month payment was received
loan_amnt |	The listed amount of the loan applied for by the borrower. If at some point in time, the credit department reduces the loan amount, then it will be reflected in this value.
loan_status |	Current status of the loan
member_id |	A unique LC assigned Id for the borrower member.
mths_since_last_delinq	| The number of months since the borrower’s last delinquency.
mths_since_last_major_derog	| Months since most recent 90-day or worse rating
mths_since_last_record |	The number of months since the last public record.
next_pymnt_d	| Next scheduled payment date
open_acc	| The number of open credit lines in the borrower’s credit file.
out_prncp |	Remaining outstanding principal for total amount funded
out_prncp_inv	| Remaining outstanding principal for portion of total amount funded by investors
policy_code |	Publicly available policy_code=1, new products not publicly available policy_code=2
pub_rec	|Number of derogatory public records
purpose	| A category provided by the borrower for the loan request.
pymnt_plan |	Indicates if a payment plan has been put in place for the loan
recoveries |	post charge off gross recovery
revol_bal |	Total credit revolving balance
revol_util|	Revolving line utilization rate, or the amount of credit the borrower is using relative to all available revolving credit.
sub_grade |	LC assigned loan subgrade
term	| The number of payments on the loan. Values are in months and can be either 36 or 60.
title |	The loan title provided by the borrower
total_acc	| The total number of credit lines currently in the borrower’s credit file
total_pymnt	|Payments received to date for total amount funded
total_pymnt_inv |	Payments received to date for portion of total amount funded by investors
total_rec_int	| Interest received to date
total_rec_late_fee|	Late fees received to date
total_rec_prncp	| Principal received to date
url	| URL for the LC page with listing data.
"""

# check data info
df.info()

#check the unique values for each column
df.nunique()

# check missing values
df.isnull().sum()

# check the distribution of target variable loan_status
df.loc[:,'loan_status'].value_counts()

"""### Exploratory Data Analysis


"""

# correlation heat map of numerical features
import seaborn as sns
import matplotlib.pyplot as plt
sns.set()

numCol = []
for col in df:
  if df[col].dtype == float:
    numCol.append(col)
corr = df[numCol].corr()

ax = sns.heatmap(
    corr, 
    vmin=-1, vmax=1, center=0,
    cmap=sns.diverging_palette(20, 220, n=200),
    square=True
)
ax.set_xticklabels(
    ax.get_xticklabels(),
    rotation=45,
    horizontalalignment='right')

# check the actual values of correlations
corr_score = df[numCol].corr()
corr_score

"""Some corresponding features (like total_pymnt and total_pymnt_inv) have high correlation."""

# explore purpose category
df["purpose"].value_counts().plot(kind='barh')

# explore purpose category
# most common loan values
df["loan_amnt"].value_counts()[:20].plot(kind='bar', title="LC Loan Amount")

df["loan_amnt"].value_counts()[:10].plot(kind='bar', title="LC Loan Amount")

# explore purpose category
df["home_ownership"].value_counts().plot(kind='bar', color='red')

df["home_ownership"].value_counts().plot(kind='pie')

df["emp_length"].value_counts().plot(kind='bar', color='blue')

# total loan amount issued by State
df_location = df.groupby("addr_state",).sum().reset_index()
df_location = df_location.filter(["addr_state", "loan_amnt"], axis = 1)

df_location.head()

import plotly.graph_objects as go

fig = go.Figure(data=go.Choropleth(
    locations=df_location['addr_state'], # Spatial coordinates
    z = df_location['loan_amnt'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "USD",
))

fig.update_layout(
    title_text = 'Total amount issued by State',
    geo_scope='usa', # limited map scope to USA
)

fig.show()

# log of total amount
import math
# use np here for larger list

fig2 = go.Figure(data=go.Choropleth(
    locations=df_location['addr_state'], # Spatial coordinates
    z = [math.log(n) for n in (df_location['loan_amnt'].astype(float))], # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "log USD",
))

fig2.update_layout(
    title_text = 'Total amount issued by State',
    geo_scope='usa', # limited map scope to USA
)

fig2.show()

# grade distribution plot
plt.figure(figsize=(16, 6))
plt.subplot(1, 2, 1)
sns.countplot(x="grade", data= df, order = df['grade'].value_counts().index)

# understand categorical feature
_,axss = plt.subplots(3,2, figsize=[30,20])
sns.countplot(x='loan_status', hue='term', data=df, ax=axss[0][0])
sns.countplot(x='loan_status', hue='grade', data=df, ax=axss[0][1])
sns.countplot(x='loan_status', hue='emp_length', data=df, ax=axss[1][0])
sns.countplot(x='loan_status', hue='home_ownership', data=df, ax=axss[1][1])
sns.countplot(x='loan_status', hue='verification_status', data=df, ax=axss[2][0])
sns.countplot(x='loan_status', hue='purpose', data=df, ax=axss[2][1])

"""# 2. Data cleaning and Feature Preprocessing

## Data Description
"""

df.head()

df.describe()

"""## Data Cleaning"""

# Data Cleaning / Integration
class_mapping = {label:idx for idx, label in enumerate(np.unique(df['term']))}
df['term']=df['term'].map(class_mapping)
class_mapping = {label:idx for idx, label in enumerate(np.unique(df['grade']))}
df['grade']=df['grade'].map(class_mapping)
class_mapping = {label:idx for idx, label in enumerate(np.unique(df['home_ownership']))}
df['home_ownership']=df['home_ownership'].map(class_mapping)

class_mapping = {label:idx for idx, label in enumerate(np.unique(df['verification_status']))}
df['verification_status']=df['verification_status'].map(class_mapping)

class_mapping = {label:idx for idx, label in enumerate(np.unique(df['purpose']))}
df['purpose']=df['purpose'].map(class_mapping)

class_mapping = {label:idx for idx, label in enumerate(np.unique(df['addr_state']))}
df['addr_state']=df['addr_state'].map(class_mapping)

class_mapping = {'Fully Paid' : 0, 'Charged Off' : 1}
df['loan_status']=df['loan_status'].map(class_mapping)

df.head()

# deal with missing value
df = df.select_dtypes(include=[np.number]).interpolate().dropna()

# drop high correlation and high variance colums
df = df.drop(["total_pymnt"], axis=1)
df = df.drop(["total_pymnt_inv"], axis=1)
df = df.drop(["total_rec_int"], axis=1)
df = df.drop(["id"], axis=1)
df = df.drop(["total_rec_prncp"], axis=1)

df.head(10)

"""## Data Split """

# split dataset
from sklearn.model_selection import train_test_split

yPredict = df.loan_status
XClean = df.drop(["loan_status"], axis=1)

# Reserve 25% for testing
X_train, X_test, y_train, y_test = train_test_split(XClean, yPredict, random_state=42, test_size=.25)

X_train.head()

y_train.head()

"""## Data preprocessing"""

# transform file
# standardization
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

"""# 3: Model Training and Selection

### Build Models: RandomForest/ Kneighbors/ LogisticRegression
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier 
from sklearn.linear_model import LogisticRegression

# Logistic Regression
classifier_logistic = LogisticRegression()

# K Nearest Neighbors
classifier_KNN = KNeighborsClassifier()

# Random Forest
classifier_RF = RandomForestClassifier()

classifier_logistic.fit(X_train, y_train)

from sklearn.metrics import classification_report,confusion_matrix
prediction_Regression = classifier_logistic.predict(X_test)
print(classification_report(y_test,prediction_Regression))

classifier_KNN.fit(X_train, y_train)

prediction_KNN = classifier_KNN.predict(X_test)
print(classification_report(y_test,prediction_KNN))

classifier_RF.fit(X_train, y_train)

prediction_RF = classifier_RF.predict(X_test)
print(classification_report(y_test,prediction_RF))

print(prediction_RF)

"""### Cross Validation"""

# Use 5-fold Cross Validation to get the accuracy for different models
from sklearn import model_selection

model_names = ['Logistic Regression','KNN','Random Forest']
model_list = [classifier_logistic, classifier_KNN, classifier_RF]
count = 0

for classifier in model_list:
    cv_score = model_selection.cross_val_score(classifier, X_train, y_train, cv=10)
    print(cv_score)
    print('Model accuracy of ' + model_names[count] + ' is ' + str(cv_score.mean()))
    count += 1

"""Logistic Regression has the best performance in these three models

## Alternative Model: SVM
"""

from sklearn.svm import SVC 

classifier_SVC = SVC()

cv_score = model_selection.cross_val_score(classifier_SVC, X_train, y_train, cv=10)
print('Model accuracy of SVM is: ' + str(cv_score.mean()))

classifier_SVC.fit(X_train,y_train)
SVC_predictions = classifier_SVC.predict(X_test)
print(classification_report(y_test,SVC_predictions))

"""## Other Models: simple Nerual Network"""

from sklearn.neural_network import MLPClassifier
mlp = MLPClassifier(hidden_layer_sizes=(30,30,30))
mlp.fit(X_train,y_train)

predictions = mlp.predict(X_test)
from sklearn.metrics import classification_report,confusion_matrix
print(confusion_matrix(y_test,predictions))

print(classification_report(y_test,predictions))

"""# 4. Feature Importance"""

X_with_corr = XClean.copy()
X_with_corr.head()

y=yPredict.copy()

# check feature importance of random forest for feature selection
forest = RandomForestClassifier()
forest.fit(XClean, yPredict)

importances = forest.feature_importances_
indices = np.argsort(importances)[::-1]

# Print the feature ranking
print("Feature importance ranking by Random Forest Model:")
for ind in range(XClean.shape[1]):
  print ("{0} : {1}".format(XClean.columns[indices[ind]],round(importances[indices[ind]], 4)))

# add L1 regularization to logistic regression
# check the coef for feature selection
scaler = StandardScaler()
X_l1 = scaler.fit_transform(X_with_corr)
LRmodel_l1 = LogisticRegression(penalty="l1", C = 10, solver='liblinear')
LRmodel_l1.fit(X_l1, yPredict)

indices = np.argsort(abs(LRmodel_l1.coef_[0]))[::-1]

print ("Logistic Regression (L1) Coefficients")
for ind in range(X_with_corr.shape[1]):
  print ("{0} : {1}".format(X_with_corr.columns[indices[ind]],round(LRmodel_l1.coef_[0][indices[ind]], 4)))

# add L2 regularization to logistic regression
# check the coef for feature selection
scaler = StandardScaler()
X_l2 = scaler.fit_transform(X_with_corr)
LRmodel_l2 = LogisticRegression(penalty="l2", C = 10, solver='liblinear')
LRmodel_l2.fit(X_l2, yPredict)

indices = np.argsort(abs(LRmodel_l2.coef_[0]))[::-1]

print ("Logistic Regression (L2) Coefficients")
for ind in range(X_with_corr.shape[1]):
  print ("{0} : {1}".format(X_with_corr.columns[indices[ind]],round(LRmodel_l2.coef_[0][indices[ind]], 4)))

"""# 5 : Summary and Discussion

From the model results, we see that Logistic Regression Model, Random Forest Model and KNN Model, as well as the SVM Model, all have similar accuracy, yet the KNN model has the best F1 score and the SVM model has the worst F1 score. The feature selection for the logistic regression model indicates that the most important factors affecting the default possibility on a loan likely comes from the interest rate, the annual income, the funded amount and the term of the loan, which are very reasonable factors. Feature selection is done this way because the logistic regression model has the best interpretability when all the models have similar performance. The models can be reevaluated using the most important features after selection, which would perhaps improve the model performance of the KNN and RF models slightly. Boosting, ensemble and other improvement methods can also be used to improve the models. 
"""
