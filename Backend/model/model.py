#Import Python Library
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib

#Load Data
data = pd.read_csv('house_price.csv')
x=data.iloc[:,0:len(data.columns)-1]
y=data.iloc[:,len(data.columns)-1]

#Divide Training/Test Data แบบ Hold out
x_train, x_test, y_train, y_test = train_test_split(x, y,
                                                    test_size=0.3,
                                                    random_state=0)
#Build Model
net=linear_model.LinearRegression()
net.fit(x_train, y_train)

#Test Model
y_pred=net.predict(x_test)

#Evaluate Model
mape=np.mean(np.absolute(y_test - y_pred) / y_test * 100)
print('MAPE :', np.round(mape,2))

#Export Model
joblib.dump(net,"house_price_model.pkl")