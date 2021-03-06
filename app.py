from flask import Flask, render_template, request, redirect
from flask_bootstrap import Bootstrap
from flask_datepicker import datepicker
import os
from config import Config
from models import StockForm
import requests
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, PrintfTickFormatter
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.config.from_object(Config)

Bootstrap(app)
datepicker(app)

def plot_stock(stock_symbol,month):
    start_date = datetime.strptime(month,'%Y-%m-%d')
    end_date = start_date+relativedelta(months=1)
    stockrequest = requests.get('https://www.quandl.com/api/v3/datasets/WIKI/{}/data.json'.format(stock_symbol),
          params={'start_date':start_date.strftime("%Y-%m-%d"),
                  'end_date':end_date.strftime("%Y-%m-%d"),
                  'api_key': app.config['API_KEY'],
                  })

    if stockrequest.status_code!=200:
        raise requests.RequestException("Quandl did not respond correctly\nStatus Code {}\nURL {}\nJSON {}".format(stockrequest.status_code,stockrequest.url,stockrequest.json()))
    stock_json = stockrequest.json()["dataset_data"] 
    default_padding=30
    chart_inner_left_padding=0.015
    df = pd.DataFrame(stock_json["data"],columns=stock_json["column_names"])
    print(df)
    df['DateTime']=pd.to_datetime(df['Date'],unit='ns')
    csource = ColumnDataSource(df)
    hover_tool = HoverTool(
            tooltips=[('Close Price ($)', '@Close'), ('Date', '@Date')],
                      mode='vline'
                )
    p = figure(title="Stock Price for {}".format(stock_symbol),x_axis_type='datetime',tools=[hover_tool])
    p.xaxis.axis_label='Date'
    p.x_range.range_padding = chart_inner_left_padding
    p.yaxis.axis_label = 'Close Price ($)'
    p.yaxis.axis_label_standoff = default_padding
    p.xaxis.axis_label_standoff = default_padding
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.line(x='DateTime',y='Close',source=csource,line_width=2)
    return p

@app.route('/',methods=['GET','POST'])
def index():
  form = StockForm(request.form)
  if not form.validate_on_submit():
      return render_template('index.html',form=form)
  if request.method == 'POST':
      month = request.form['month']
      plot = plot_stock(request.form['stock_ticker'],month)
      print(plot)
      script, div = components(plot)
      return render_template('graph.html',stockEntered=True,form=form,script=script,div=div,ticker=request.form['stock_ticker'])

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507)
