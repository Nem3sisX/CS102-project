from tkinter import *

root = Tk()
root.title(string="HashFinancial")

frame1=Frame(root)
frame1.pack(side=TOP,fill=X)

frame2=Frame(root)
frame2.pack(side=TOP, fill=X)


# **** ToolBar *******

hashfinance=Frame(frame1,bg='green')
hashfinance.pack(side=TOP,fill=X)
hashname = Label(hashfinance, text='HashFinance', bg="green", fg='white')
hashname.pack(fill=X)


# ****** main centre window *****
symbol=Label(frame2,text='Enter Stock Symbol : ')
symbol.grid(row=4,column=0,sticky=E)

entry1=Entry(frame2)
entry1.grid(row=4,column=1)


def Predictive_Analysis():
    import quandl
    import math, datetime
    import numpy as np
    from sklearn import preprocessing, model_selection
    from sklearn.linear_model import LinearRegression
    import matplotlib.pyplot as plt
    from matplotlib import style
    import pickle
    style.use('ggplot')
    val = 'WIKI/' + entry1.get()
    df = quandl.get(val)

    df = df[['Adj. Open', 'Adj. High', 'Adj. Low', 'Adj. Close', 'Adj. Volume']]

    df['HL_PCT'] = (df['Adj. High'] - df['Adj. Close']) * 100 / (df['Adj. High'] + df['Adj. Close'])
    df['PCT_change'] = (df['Adj. Close'] - df['Adj. Open']) * 100 / df['Adj. Open']

    df = df[['Adj. Close', 'HL_PCT', 'PCT_change', 'Adj. Volume']]

    forecast_col = 'Adj. Close'
    df.fillna(-99999, inplace=True)

    forecast_out = int(math.ceil(0.01 * len(df)))
    df['label'] = df[forecast_col].shift(-forecast_out)

    X = np.array(df.drop(['label'], 1))
    X = preprocessing.scale(X)
    X_lately = X[-forecast_out:]
    X = X[:-forecast_out]

    df.dropna(inplace=True)
    Y = np.array(df['label'])

    X_train, X_test, Y_train, Y_test = model_selection.train_test_split(X, Y, test_size=0.2)
    clf = LinearRegression(n_jobs=-1)
    clf.fit(X_train, Y_train)
    with open('linearregression.pickle', 'wb') as f:
        pickle.dump(clf, f)

    pickle_in = open('linearregression.pickle', 'rb')
    clf = pickle.load(pickle_in)
    accuracy = clf.score(X_test, Y_test)

    forecast_set = clf.predict(X_lately)

    print(accuracy)
    df['Forecast'] = np.nan

    last_date = df.iloc[-1].name
    last_unix = last_date.timestamp()
    one_day = 86400
    next_unix = last_unix + one_day

    for i in forecast_set:
        next_date = datetime.datetime.fromtimestamp(next_unix)
        next_unix += one_day
        df.loc[next_date] = [np.nan for _ in range(len(df.columns) - 1)] + [i]

    last_row_before_forecast = df.loc[last_date]
    df.loc[last_date] = np.hstack((last_row_before_forecast.values[:-1], last_row_before_forecast[forecast_col]))

    df['Adj. Close'].plot()
    df['Forecast'].plot()
    plt.legend(loc=4)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()


predict=Button(frame2,text='Predict Now', fg="green", command = Predictive_Analysis)
predict.grid(columnspan=2)


# **** StatusBar ******************
status= Label(root,text='Live Stock Price : ',bd=1,relief=SUNKEN,anchor=W)
status.pack(side=BOTTOM, fill=X)

root.mainloop()
