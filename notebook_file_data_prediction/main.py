# import numpy as np
# a = np.zeros((156816, 36, 53806), dtype='uint8')
import json
import os
import numpy as np
import matplotlib.pyplot as plt
#import pandas as pd
#import collections


from sklearn.linear_model import LinearRegression
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.ensemble import BaggingRegressor
from sklearn.ensemble import GradientBoostingRegressor as GBR
from sklearn import linear_model
from sklearn import tree

from dataset_analysis import read_dataframe, create_dateTime, create_month
from dataset_analysis import choose_month, drop_month_year, ascending_dataframe, rearrange_dataframe
from dataset_analysis import check_blast_furnace, check_target_column, dataframe_reset_index
from dataset_analysis import drop_nan_value, drop_unique_valued_columns, drop_string_column, dataframe_datetime

#from dataset_analysis import feature_selection_with_selectKbest
from dataset_analysis import pearson_correlation
from dataset_analysis import make_dataframe_with_high_correlated_value
from dataset_analysis import score_checking_with_cross_validation
# from dataset_analysis import dataframe_date_time_type
from dataset_analysis import draw_graph
from dataset_analysis import draw_feature_vs_target

from model_file import make_dataset, scikit_learn_model
from model_file import plot_graph, evaluation_metrices
from model_file import NN_model
from model_file import make_dataset_LSTM, split_sequence, LSTM_model, plot_history, vanilla_lstm
from keras.models import load_model
from keras.callbacks import LearningRateScheduler, ModelCheckpoint

from dataset_analysis import test_stationarity, tsplot_dataset, tsplot
from model_file import make_dataset_arima, StartARIMAForecasting

with open('variable_config.json', 'r') as f:
    config = json.load(f)

filepath = config['DEFAULT']['file_path']
filepath_ubuntu = config['DEFAULT']['file_path_ubuntu']
filepath_ubuntu_1 = config['DEFAULT']['file_path_ubuntu_1']
feb_march_file = config['DEFAULT']['feb_march_file']

filepath_server_feb_march = config['DEFAULT']['file_path_server_feb_march']
filepath_server_april_may = config['DEFAULT']['file_path_server_april_may']
filepath_server_june_july = config['DEFAULT']['file_path_server_june_july']

filepath_ubuntu_feb_march = config['DEFAULT']['file_ubuntu_feb_march']
filepath_ubuntu_april_may = config['DEFAULT']['file_ubuntu_april_may']
filepath_ubuntu_june_july = config['DEFAULT']['file_ubuntu_june_july']

filepath_windows_feb_march = config['DEFAULT']['file_windows_feb_march']
filepath_windows_april_may = config['DEFAULT']['file_windows_april_may']
filepath_windows_june_july = config['DEFAULT']['file_windows_june_july']


start_pos = config['DEFAULT']['start_point_dataframe']
end_pos = config['DEFAULT']['end_point_dataframe']
date_column = config['DEFAULT']['date_column']
target_column = config['DEFAULT']['target_column']
req_drop_value_target = config['DEFAULT']['req_drop_value_target']
furnace_signal_column_a = config['DEFAULT']['blast_furnace_signal_a']
furnace_signal_column_b = config['DEFAULT']['blast_furnace_signal_b']
value_A = config['DEFAULT']['req_value_of_blast_furnace_A']
value_B = config['DEFAULT']['req_value_of_blast_furnace_B']
max_best_number = config['DEFAULT']['max_best_number']
correlation_threshold_min_value = config['DEFAULT']['correlation_threshold_min_value']
correlation_threshold_max_value = config['DEFAULT']['correlation_threshold_max_value']
required_number_of_test_data = config['DEFAULT']['required_number_of_test_data']
subfolder_feature_vs_target = config['DEFAULT']['subfolder_feature_vs_target']
evaluation_metrics_file_name = config['DEFAULT']['evaluation_metrics_file']
number_of_step_lstm = config['DEFAULT']['n_steps_lstm']
epochs = config['DEFAULT']['epochs']
batch_size = config['DEFAULT']['batch_size']


print(filepath_ubuntu_feb_march)

from datetime import date
today = date.today()
print("Today's date:", today)


current_directory = os.getcwd()
print('current_directory is: ',current_directory)
address = 'image_folder_local'
final_directory = current_directory+'/'+str(address)
if not os.path.exists(final_directory):
    os.makedirs(final_directory)
    print('created : ', final_directory)
else:
    print(' has already created',final_directory)
    pass



evaluation_metrics_file_path = final_directory+'/'+evaluation_metrics_file_name
if not os.path.isfile(evaluation_metrics_file_path):
    f = open(evaluation_metrics_file_path,'a')
    f.close()
    print('metrics file now created')
else:
    os.remove(evaluation_metrics_file_path)
    f = open(evaluation_metrics_file_path,'a')
    f.close()
    print('metrics file removed and created')
    

dataframe_read = read_dataframe(filepath_ubuntu_feb_march)
cols_list = ['longTime',furnace_signal_column_a,furnace_signal_column_b,target_column,'RWWIHOBG9_V0','AEWIGHG9__P0','AEWIGHG9__T0']
dataframe_sliced = dataframe_read.iloc[:][cols_list]  #this is done here due to overcome the huge time of processing on a big data. cols_list array includes the column which are
                                                        #highly correlated with the target variable. This highly correlatd info got from the training or first stage of coding.
                                                        # finding high correlation part is also given later. just uncomment that part to use.

dataframe_with_date = create_dateTime(dataframe_sliced,'row_ID','Unnamed: 0') # here row ID and unnamed have written beacuse slicing the main datfarame got from the IAT department generated
                                                                # this columns.
dataframe_include_month, month_array_df = create_month(dataframe_with_date, 'month', target_column) #this code generate month value in numeric order by taing value from dateTime column
                                                                                                    # january -- 1, february --2 etc.
dataframe_with_specific_month = choose_month(dataframe_include_month,'month') # this line take value from the "month" column and keep only specific month.
                                                                                    # please take a look in the body of the function.
dataframe_with_specific_month_reset = drop_month_year(dataframe_with_specific_month) # here, drop of the month column is possible though it it omitted here. No need.

# print(dataframe_read.shape)
# plt.plot(dataframe_read[target_column], color = 'blue')
# plt.plot(dataframe_read[furnace_signal_column_a], color = 'red')
# plt.plot(dataframe_read[furnace_signal_column_b], color = 'green')
# plt.legend([target_column, furnace_signal_column_a, furnace_signal_column_b], loc='best')
# # plt.xlim(0,initial_dataframe.shape[0]+10)
# plt.xticks(np.arange(0,dataframe_read.shape[0],5000),rotation='vertical')
# plt.xlabel('Numebr of observation')
# plt.ylabel('Value')
# #plt.savefig('blast_vs_target_pre.png',bbox_inches='tight')
# plt.rcParams['figure.figsize'] = (12,5)



dataframe_ascending = ascending_dataframe(dataframe_with_specific_month_reset, start_pos,dataframe_with_specific_month_reset.shape[0]) # this code arrange the dataset in ascending order
                                                                                                                        # with respect to time (smallest to largest)
index_array=[0,-1]
req_column_name = [date_column, target_column]
# req_column_name = [date_column, furnace_signal_column]
dataframe_rearranged = rearrange_dataframe(dataframe_ascending,req_column_name,index_array)
dataframe_clean_furnace_column = check_blast_furnace(dataframe_rearranged, furnace_signal_column_a, value_A,
                                                               furnace_signal_column_b, value_B) # this line check is there any anomaly in the blast furnace A and B's column
                                                                                                # and remove that rows


dataframe_clean_target_column = check_target_column(dataframe_clean_furnace_column,
                                                                  target_column, req_drop_value_target) # It checks the target column and remove the rows whos value is less than
                                                                                                        # a minimum value. in this task that was chosen as 60.

dataframe_free_from_furnace_target_column_anomaly = dataframe_reset_index(dataframe_clean_target_column)
print(dataframe_free_from_furnace_target_column_anomaly.shape)

plt.plot(dataframe_free_from_furnace_target_column_anomaly [target_column], color = 'blue')
plt.plot(dataframe_free_from_furnace_target_column_anomaly [furnace_signal_column_a], color = 'red')
plt.plot(dataframe_free_from_furnace_target_column_anomaly [furnace_signal_column_b], color = 'green')
plt.legend([target_column, furnace_signal_column_a, furnace_signal_column_b], loc='center left')
# plt.xlim(0,initial_dataframe.shape[0]+10)
plt.xticks(np.arange(0,dataframe_free_from_furnace_target_column_anomaly .shape[0],5000),rotation='vertical')
plt.xlabel('Numebr of observation')
plt.ylabel('Value')
#plt.savefig('blast_vs_target_post.png',bbox_inches='tight')
plt.rcParams['figure.figsize'] = (12, 5)


dataframe_drop_nan = drop_nan_value(dataframe_free_from_furnace_target_column_anomaly)
dataframe_drop_unique_valued_column = drop_unique_valued_columns(dataframe_drop_nan)
dataframe_drop_string = drop_string_column(dataframe_drop_unique_valued_column)
dataframe_drop_string.dtypes

# =============================================================================
# dataframe_read = None
# dataframe_with_date = None
# dataframe_with_specific_month = None
# dataframe_with_specific_month_reset = None
# dataframe_ascending = None
# dataframe_rearranged = None
# dataframe_clean_furnace_column = None
# dataframe_clean_target_column = None
# dataframe_drop_nan = None
# dataframe_drop_unique_valued_column = None
# =============================================================================


print(dataframe_drop_string.shape)

plt.plot(dataframe_drop_string[target_column], color = 'blue')
# plt.plot(dataframe_no_string[furnace_signal_column_a], color = 'red')
# plt.plot(dataframe_no_string[furnace_signal_column_b], color = 'green')
# plt.legend([target_column, furnace_signal_column_a, furnace_signal_column_b], loc='upper left')
plt.legend([target_column], loc='best')
plt.xticks(np.arange(0,dataframe_drop_string.shape[0],1000),rotation='vertical')
plt.xlabel('Numebr of observation')
plt.ylabel('Value')
#plt.savefig('final_target_column.png',bbox_inches='tight')
# plt.xlim(0,initial_dataframe.shape[0]+10)
# plt.xticks(np.arange(0,initial_dataframe.shape[0],))
plt.rcParams['figure.figsize'] = (12, 5)


dataframe_datetime = dataframe_datetime(dataframe_drop_string)
print(dataframe_datetime.shape)
#sklearn_feature_best_dataframe = feature_selection_with_selectKbest(dataframe_datetime,max_best_number)
#sklearn_correlation = pearson_correlation(sklearn_feature_best_dataframe)

main_correlation = pearson_correlation(dataframe_datetime)

main_frame = dataframe_datetime
correlated_frame = main_correlation
print(main_frame.shape)
print(correlated_frame.shape)
print(correlated_frame)
# main_frame = sklearn_feature_best_dataframe
# correlated_frame = sklearn_correlation

dataframe_high_correlation = make_dataframe_with_high_correlated_value(main_frame,correlated_frame,
                                                             correlation_threshold_min_value, correlation_threshold_max_value)

print(dataframe_high_correlation.shape)
dataframe_high_correlation.describe()

dataframe_resample = dataframe_high_correlation.resample('1min').mean()
dataframe_resample_copy = dataframe_resample.copy()
dataframe_resample_copy = dataframe_resample_copy.reset_index()

dataframe_interpolate = dataframe_resample.interpolate('linear')
dataframe_interpolate_copy = dataframe_interpolate.copy()
dataframe_interpolate_copy = dataframe_interpolate_copy.reset_index()

# following two lines anyone can use to plot feature vs target graph.

# subfolder_1 = 'feature_vs_target'+'_'+str(today)
# draw_feature_vs_target = draw_feature_vs_target(dataframe_interpolate,final_directory,subfolder_1)


# Here, train and test set are going to be made
train_input, train_output, test_input, test_output = make_dataset(dataframe_interpolate,required_number_of_test_data)

model_list = [LinearRegression(fit_intercept=True),linear_model.Lasso(alpha=0.1),linear_model.Ridge(alpha=.5),
              linear_model.BayesianRidge(), tree.DecisionTreeRegressor(max_depth=2),ExtraTreesRegressor(),
              BaggingRegressor(ExtraTreesRegressor()),GBR()]
name = ['LinearRegression','Lasso','Ridge','BayesianRidge','tree','ExtraTreesRegressor','BaggingRegressor','GBR']

    

model = scikit_learn_model(model_list, name, train_input, train_output, test_input, test_output,
                           final_directory, evaluation_metrics_file_path)    # this function will take the model_list array and perform training and testing operation and finally
                                                                            # save result in a text file and graph in a specific fiolder named by the model name.

# import tkinter
# # import matplotlib
# # matplotlib.get_backend()
# import matplotlib
# matplotlib.use('TkAgg')
# plt.plot(dataframe_no_zero_value_target_column[target_column], color = 'blue')
# # plt.show()
# # plt.interactive(False)
# plt.show(block=False)
# plt.ioff()
# # plt.interactive(False)


# print(len(dataframe_high_correlation.columns))
# subfolder_1 = 'feature_vs_target'+'_'+str(today)
# draw_feature_vs_target = draw_feature_vs_target(dataframe_high_correlation,final_directory,subfolder_1)

# df = dataframe_date_time_type(dataframe_high_correlation)
# # df = dataframe_date_time_type(temp_frame_1)
#
# dict_of_dates = {k: v for k, v in df.groupby('Date')}
# dict_of_day_type = {k:v for k,v in df.groupby('TypeofDAY')}
# dict_of_day_name = {k:v for k,v in df.groupby('day_name')}
#
#
# date_key_value = collections.OrderedDict(dict_of_dates)
# day_type_key_value = collections.OrderedDict(dict_of_day_type)
# day_name_key_value = collections.OrderedDict(dict_of_day_name)
#
# draw_graph_date = draw_graph(date_key_value,dict_of_dates, target_column,final_directory, subfolder_name = '3_date_fig_target')
# draw_graph_week = draw_graph(day_type_key_value,dict_of_day_type, target_column,final_directory, subfolder_name = '3_week_fig_target')
# draw_graph_day = draw_graph(day_name_key_value,dict_of_day_name, target_column,final_directory, subfolder_name = '3_day_fig_target')

#train_output_cv = np.reshape(train_output,(-1,1))

# =============================================================================
# cross validation scores checking
# =============================================================================

score_checking_with_cross_validation(model_list, train_input, train_output, evaluation_metrics_file_path,name) # cross validation process used to check the accuracy



#from sklearn.ensemble import RandomForestRegressor
#from sklearn.model_selection import KFold
#kf = KFold(n_splits = 5, shuffle = True)
##rf_reg = RandomForestRegressor()
#scores = []
#for i in range(5):
#    result = next(kf.split(train_input), None)
#    print(result)
#    x_train = train_input[result[0]]
#    print(x_train)
#    x_test = train_input[result[1]]
#    y_train = train_output[result[0]]
#    y_test = train_output[result[1]]
#    model = my_model.fit(x_train,y_train)
#    predictions = my_model.predict(x_test)
#    np.append(scores,model.score(x_test,y_test))
#print('Scores from each Iteration: ', scores)
#print('Average K-Fold Score :' , np.mean(scores))


#my_model.fit(train_input, train_output)
#my_pred = my_model.predict(test_input)
#plt.plot((min(test_output), max(test_output)), (min(my_pred), max(my_pred)), color='red')
#plt.scatter(test_output, my_pred, color='blue')

# from sklearn import linear_model
#from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
#import math
#print('r_2 statistic: %.2f' % r2_score(test_output,my_pred))
#print("Mean_absolute_error: %.2f" % mean_absolute_error(test_output,my_pred))
#print("Mean squared error: %.2f" % mean_squared_error(test_output,my_pred))
#RMSE=math.sqrt(mean_squared_error(test_output,my_pred))
#print('RMSE: ',RMSE)
    
    

# =============================================================================
# Check learning curve 
# =============================================================================

# import sklearn
# from sklearn.model_selection import learning_curve
# extratreereg = sklearn.tree.ExtraTreeRegressor()
# extratreereg.fit(train_input, train_output)
#
# train_sizes, train_scores, validation_scores = learning_curve(extratreereg,train_input,train_output,
#                                                               cv = 5,scoring = 'neg_mean_squared_error',n_jobs=10)
#
# train_sizes
#
# print('Training scores:\n\n', train_scores)
# print('\n', '-' * 70) # separator to make the output easy to read
# print('\nValidation scores:\n\n', validation_scores)
#
# import pandas as pd
# train_scores_mean = -train_scores.mean(axis = 1)
# validation_scores_mean = -validation_scores.mean(axis = 1)
# print('Mean training scores\n\n', pd.Series(train_scores_mean, index = train_sizes))
# print('\n', '-' * 20) # separator
# print('\nMean validation scores\n\n',pd.Series(validation_scores_mean, index = train_sizes))
#
# import matplotlib.pyplot as plt
#
# plt.style.use('seaborn')
# plt.plot(train_sizes, train_scores_mean, label = 'Training error')
# plt.plot(train_sizes, validation_scores_mean, label = 'Validation error')
# plt.ylabel('MSE', fontsize = 14)
# plt.xlabel('Training set size', fontsize = 14)
# plt.title('Learning curves for a linear regression model', fontsize = 18, y = 1.03)
# plt.legend()
# plt.ylim(0,50)
# plt.show()

# =============================================================================
# Neural Network
# =============================================================================

# from keras.models import Sequential
# from keras.layers import Dense, Activation, Flatten
# from sklearn.metrics import mean_absolute_error

lr = 0.01
def lr_schedule(epoch):
    print('epoch is: ', epoch)
    return lr * (0.1 ** int(epoch / 10))

NN_model_1 = NN_model(train_input)
# NN_model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['mean_absolute_error','accuracy'])
NN_model_1.compile(optimizer='adam', loss='mse',metrics=['mse','accuracy'])
NN_model_1.summary()

train_model_NN = NN_model_1.fit(train_input, train_output, batch_size=batch_size, epochs=epochs, verbose=1,
                              validation_split=0.2,shuffle=True,callbacks=[LearningRateScheduler(lr_schedule)])


# observe learning curve with Neural Network
print(train_model_NN.history.keys())
history_graph_NN = "NN"
plot_history(train_model_NN,history_graph_NN)

NN_model_1.save("Neural_Network.h5") # save the trained model to use later
load_trained_NN = load_model("Neural_Network.h5") # load the saved model
# predicted_output_NN = load_trained_NN.predict(test_input) # uncomment this line if saved model needs to load for prediction
predicted_output_NN = NN_model_1.predict(test_input)
test_output_NN = np.reshape(test_output,(-1,1)) # reshaping to 2D array is necessary to plot as the predicted output of NN is 2 dimensional
print(test_output_NN.shape)
plot_graph(test_output_NN, predicted_output_NN, final_directory,'Neural_Network') # plotting result curve
evaluation_metrices(test_output_NN,predicted_output_NN,final_directory,'Neural Netowrk', evaluation_metrics_file_path) # storing evaluation result




# =============================================================================
# Vanilla LSTM
# =============================================================================
multiple_ip_train_data, multiple_ip_test_set = make_dataset_LSTM(dataframe_interpolate, required_number_of_test_data) # A separate procedure of making dataset for vanilla LSTM

X_train_vanilla, y_train_vanilla = split_sequence(multiple_ip_train_data, number_of_step_lstm) # dividing in sequence for LSTM
print('X_train_vanilla shape: ',X_train_vanilla.shape,'\t dimension: ',X_train_vanilla.ndim,'\t size: ',X_train_vanilla.size)
print('y_train_vanilla shape: ',y_train_vanilla.shape,'\t dimension: ',y_train_vanilla.ndim,'\t size: ',y_train_vanilla.size)

X_train_vanilla = X_train_vanilla.reshape((X_train_vanilla.shape[0], X_train_vanilla.shape[1], X_train_vanilla.shape[-1]))
print(X_train_vanilla.shape)

n_steps_vanilla = number_of_step_lstm
n_features_vanilla = X_train_vanilla.shape[-1]
vanilla_model = vanilla_lstm(n_steps_vanilla, n_features_vanilla)
vanilla_model.compile(optimizer='adam', loss='mse',metrics=['accuracy'])
vanilla_model.summary()
train_model_vanilla = vanilla_model.fit(X_train_vanilla, y_train_vanilla, batch_size=batch_size, epochs=epochs, verbose=1,validation_split=0.2,
                                        shuffle=True,callbacks=[LearningRateScheduler(lr_schedule)])


print(train_model_vanilla.history.keys())
plot_history(train_model_vanilla,history_graph_NN="vanilla_lstm")

vanilla_model.save("VANILLA_LSTM.h5")
load_trained_VANILLA_LSTM=load_model("VANILLA_LSTM.h5")
test_ip_vanilla,test_op_vanilla=split_sequence(multiple_ip_test_set,number_of_step_lstm)
n_features_test = test_ip_vanilla.shape[-1]
X_test_ip_vanilla=test_ip_vanilla.reshape((test_ip_vanilla.shape[0], test_ip_vanilla.shape[1], n_features_test))
yhat_vanilla_loaded = vanilla_model.predict(X_test_ip_vanilla, verbose=1)
print(yhat_vanilla_loaded.shape)
# evaluate the model
_, train_mse = vanilla_model.evaluate(X_train_vanilla, y_train_vanilla, verbose=0)
_, test_mse = vanilla_model.evaluate(X_test_ip_vanilla, test_op_vanilla, verbose=0)
print('Train: %.3f, Test: %.3f' % (train_mse, test_mse))

evaluation_metrices(test_op_vanilla, yhat_vanilla_loaded, final_directory, 'VANILLA_LSTM',evaluation_metrics_file_path)
test_op_vanilla_reshape = np.reshape(test_op_vanilla,(-1,1))
print(test_op_vanilla_reshape.shape)
print(yhat_vanilla_loaded.shape)
plot_graph(test_op_vanilla_reshape, yhat_vanilla_loaded, final_directory,'vanilla_LSTM')




# =============================================================================
# ARIMA
# =============================================================================
import re
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt
import statsmodels.tsa.api as smt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dateutil.relativedelta import relativedelta
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
# from sklearn.model_selection import cross_val_predict
import warnings
warnings.filterwarnings("ignore")
from matplotlib import pyplot
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf


df = dataframe_interpolate[[target_column]]
print(type(df))
print(df.shape)

stat, p = stats.normaltest(df.iloc[:,-1])
print('Statistics=%.3f, p=%.3f' % (stat, p))
alpha = 0.05
if p > alpha:
    print('Data looks Gaussian (fail to reject H0)')
else:
    print('Data does not look Gaussian (reject H0)')
# from dataset_analysis import test_stationarity


test_stationarity(df.iloc[:,-1]) # It checks the stationarity of the dataset

n_sample, ts_train, ts_test = tsplot_dataset(df, target_column) # make array for drawing ts_plot

tsplot(ts_train, title='Output of the Turbine 9; Signal: '+str(target_column), lags=62) # draw plot for time series, acf, pacf

plot_acf(df.iloc[:,-1], lags=62)
plt.xlabel('lags')
plt.ylabel('correlation')
# plt.savefig('acf plot code.png',bbox_inches='tight')
pyplot.show()
# plt.figure()
plot_pacf(df.iloc[:,-1], lags=62)
plt.xlabel('lags')
plt.ylabel('correlation')
# plt.savefig('pacf plot code.png',bbox_inches='tight')
pyplot.show()


train_set_arima, test_set_arima = make_dataset_arima(df, required_number_of_test_data = 5)
print('train_set_arima shape: ', train_set_arima.shape)
print('test_set_arima shape: ', test_set_arima.shape)

Actual = [x for x in train_set_arima]
Predictions_ARIMA = list()


count_1=1
for timepoint in range(len(test_set_arima)):
#     print('I am in for loop')
    ActualValue =  test_set_arima[timepoint]
    #forcast value
    Prediction = StartARIMAForecasting(Actual, 2,0,0)
    print('count=%d, Actual=%f, Predicted=%f' % (count_1 ,ActualValue, Prediction))
    count_1+=1
    #add it in the list
    Predictions_ARIMA.append(Prediction)
    Actual.append(ActualValue)

plot_graph(test_set_arima, Predictions_ARIMA, final_directory, 'ARIMA_200')
evaluation_metrices(test_set_arima, Predictions_ARIMA,final_directory,'ARIMA_200', evaluation_metrics_file_path)

# =============================================================================
# Auto ARIMA
# =============================================================================


from pmdarima.arima import auto_arima
#training model
model_auto_arima = auto_arima(train_set_arima, trace=True,start_p=0, start_q=0, start_P=0, start_Q=0,
                  max_p=2, max_q=2, max_P=2, max_Q=2, seasonal=True,
                  stepwise=False, suppress_warnings=True, D=1, max_D=2,
                  error_action='ignore',approximation = False)
#fitting model
model_auto_arima.fit(train_set_arima)
predicted_auto_arima = model_auto_arima.predict(100)

print(type(predicted_auto_arima))
print(predicted_auto_arima.shape)
plt.plot(train_set_arima)
plt.plot(predicted_auto_arima)
plt.show()
plot_graph(test_set_arima, Predictions_ARIMA, final_directory, 'Auto_ARIMA')
evaluation_metrices(test_set_arima, Predictions_ARIMA,final_directory,'Auto_ARIMA', evaluation_metrics_file_path)
print(test_set_arima.shape)
