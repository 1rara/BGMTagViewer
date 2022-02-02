const data = {
  datasets: []
};
let tags = {};
const yTotal = [];
const history = [];

const config = {
  type: 'scatter',
  data: data,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    showLine: true,
    interaction: {
      intersect: false,
      axis: 'x',
      mode: 'nearest',
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Year'
        },
        ticks: {
          callback: value => value
        }
      },
      y: {
        min: 0,
        title: {
          display: true,
          text: 'Popularity(%)'
        },
        ticks: {
          callback: context => {
            return (context < 0.01 && context > 0) ?
              new Intl.NumberFormat('en-US', { notation: "scientific" }).format(context) :
              Intl.NumberFormat().format(context);
          }
        }
      }
    },
    plugins: {
      legend: {
        position: 'top'
      },
      title: {
        display: true,
        text: 'Bangumi Tag Visualizer'
      },
      tooltip: {
        position: 'average',
        titleAlign: 'center',
        callbacks: {
          title: context => context[0].parsed.x,
          label: context => {
            let label = context.dataset.label || '';
            if (label)
              label += ': ';
            if (context.parsed.y !== null) {
              label += (context.parsed.y < 0.01) ?
                new Intl.NumberFormat('en-US', { notation: "scientific" }).format(context.parsed.y) :
                context.parsed.y.toFixed(3);
              label += '%';
            }
            return label;
          }
        }
      }
    },
    elements: {
      line: {
        borderWidth: 3,
        tension: 0.3
      },
      point: {
        pointBorderWidth: 2,
        hitRadius: 10,
        hoverRadius: 8
      }
    }
  },
};

const actions = [
  {
    name: 'Add Dataset',
    handler(chart, targetTag, interval = 1, lowBound = 0, upBound = 9999) {
      if (targetTag === '') return;
      history.push([targetTag, interval, lowBound, upBound]);
      const target = bindName(altNames, targetTag);
      const dsColor = namedColor(chart.data.datasets.length);
      const yvalues = [];

      Object.keys(tags).forEach((v, i) => {
        let key = Math.floor(v / interval) * interval;
        if (v >= lowBound && v <= upBound && tags[v][target]) {
          if (yvalues.at(-1) && key === yvalues.at(-1).x)
            yvalues.at(-1).y += tags[v][target] * 100 / yTotal[i] / interval;
          else
            yvalues.push({ x: key, y: tags[v][target] * 100 / yTotal[i] / interval });
        }
      });

      const newDataset = {
        label: targetTag,
        backgroundColor: dsColor.replace(/[^,]+(?=\))/, '0.5'),
        borderColor: dsColor,
        data: yvalues,
      };

      chart.data.datasets.push(newDataset);
      chart.update();
    }
  },
  {
    name: 'Remove Dataset',
    handler(chart) {
      chart.data.datasets.pop();
      history.pop();
      chart.update();
    }
  }
];

//init graph
Chart.defaults.font.size = 16;
const c = new Chart("mainChart", config);
let altNames = [];

//read query string
const params = Object.fromEntries(new URLSearchParams(window.location.search));
let bind = !params["bind"] || params["bind"] !== "false";

getJSON(bind ? "./data/tags.json" : "./data/tagsRaw.json")
  .then(result => {
    tags = result;
    getJSON("./data/altNames.json")
      .then(res => {
        altNames = res;

        //bind event handlers
        $("#add").click(() => actions[0].handler(c, $("#input").val(), $("#interval").val(),
          $(".slidecontainer input")[0].value, $(".slidecontainer input")[1].value));
        $("#remove").click(() => actions[1].handler(c));

        for (i in tags) {
          let sum = 0;
          for (j in tags[i])
            sum += tags[i][j];
          yTotal.push(sum);
        }
        //console.log(yTotal);

        if (params['tags']) {
          const tarr = JSON.parse(params['tags']);
          for (i in tarr)
            actions[0].handler(c, tarr[i][0], tarr[i][1], tarr[i][2], tarr[i][3]);
        }
      });
  });
