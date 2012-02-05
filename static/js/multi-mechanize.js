var responseTimeLineGraphOptions = {
  chart: {
    defaultSeriesType: 'line',
    animation: false,
    borderColor: '#E5E5E5',
    borderWidth: 1
  },
  legend: {
    align: 'right',
    backgroundColor: '#FFF',
    verticalAlign: 'top',
    x: -10,
    y: 10,
    floating: true,
    layout: 'vertical'
  },
  title: {
    text: ''
  },
  xAxis: {
    title: {
      text: 'Elapsed Time (secs)'
    },
    gridLineWidth: 1,
    gridLineDashStyle: 'dot'
  },
  yAxis: {
    title: {
      text: 'Response Time (secs)'
    },
    min: 0
  },
  plotOptions: {
    line: {
      pointStart: 0
    }
  },
  series: [
    {
      name: '90%'
    },
    {
      name: '80%'
    },
    {
      name: 'avg'
    }
  ]
};

var responseTimeScatterGraphOptions = {
  chart: {
    defaultSeriesType: 'scatter',
    animation: false,
    borderColor: '#E5E5E5',
    borderWidth: 1
  },
  legend: {
    enabled: false
  },
  title: {
    text: 'Response Time: raw data (all points)'
  },
  xAxis: {
    title: {
      text: 'Elapsed Time (secs)'
    },
    gridLineWidth: 1,
    gridLineDashStyle: 'dot'
  },
  yAxis: {
    title: {
      text: 'Response Time (secs)'
    },
    min: 0
  },
  series: [
    {
      name: 'response time'
    }
  ]
};

var throuputGraphOptions = {
  chart: {
    defaultSeriesType: 'line',
    animation: false,
    borderColor: '#E5E5E5',
    borderWidth: 1
  },
  legend: {
    enabled: false
  },
  title: {
    text: ''
  },
  xAxis: {
    title: {
      text: 'Elapsed Time (secs)'
    },
    gridLineWidth: 1,
    gridLineDashStyle: 'dot'
  },
  yAxis: {
    title: {
      text: 'Transactions Per Second (count)'
    },
    min: 0
  },
  plotOptions: {
    line: {
      pointStart: 0
    }
  },
  series: [
    {
      name: 'transactions'
    }
  ]
};

var charts = {};
var generateCharts = function(timerName, tsInterval, lineTitle, lineData, scatterData, tputTitle, tputData) {
  
  // render the response time line graph
  var divName = 'responseTimeLineGraph-' + timerName;
  responseTimeLineGraphOptions.chart.renderTo = divName;
  responseTimeLineGraphOptions.title.text = lineTitle;
  responseTimeLineGraphOptions.plotOptions.line.pointInterval = tsInterval;
  responseTimeLineGraphOptions.series[0].data = lineData[0];
  responseTimeLineGraphOptions.series[1].data = lineData[1];
  responseTimeLineGraphOptions.series[2].data = lineData[2];
  charts[divName] = new Highcharts.Chart(responseTimeLineGraphOptions);

  // render the response time scatter graph
  divName = 'responseTimeScatterGraph-' + timerName;
  responseTimeScatterGraphOptions.chart.renderTo = divName;
  responseTimeScatterGraphOptions.series[0].data = scatterData;
  charts[divName] = new Highcharts.Chart(responseTimeScatterGraphOptions);

  // render the throughput graph
  divName = 'throughputGraph-' + timerName;
  throuputGraphOptions.chart.renderTo = divName;
  throuputGraphOptions.title.text = tputTitle;
  throuputGraphOptions.plotOptions.line.pointInterval = tsInterval;
  throuputGraphOptions.series[0].data = tputData;
  charts[divName] = new Highcharts.Chart(throuputGraphOptions);
};
