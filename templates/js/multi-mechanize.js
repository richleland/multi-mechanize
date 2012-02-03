var chart;

$(function(){
  $('.dropdown-toggle').dropdown();

  var options = {
    chart: {
      renderTo: 'chartContainer',
      defaultSeriesType: 'line'
    },
    legend: {
      align: 'right',
      verticalAlign: 'top',
      x: -10,
      y: 10,
      floating: true,
      layout: 'vertical'
    },
    title: {
      text: 'Response Time: 10 sec time-series'
    },
    xAxis: {
      title: {
        text: 'Elapsed Time (secs)'
      },
      categories: [0, 100, 200, 300, 400, 500, 600]
    },
    yAxis: {
      title: {
        text: 'Response Time (secs)'
      }
    },
    series: [
      {
        name: '90%',
        data: [3.570, 3.725, 3.479, 3.545, 3.493, 3.623, 3.544]
      },
      {
        name: '80%',
        data: [3.561, 3.609, 3.447, 3.469, 3.442, 3.437, 3.400]
      },
      {
        name: 'avg',
        data: [3.455, 3.460, 3.346, 3.400, 3.300, 3.260, 3.273]
      }
    ]
  };

  chart = new Highcharts.Chart(options);
});
