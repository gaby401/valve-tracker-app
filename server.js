const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

let valves = [];

app.get('/valves', (req, res) => {
  res.json(valves);
});

app.get('/valves/:sn', (req, res) => {
  const valve = valves.find(v => v.sn === req.params.sn);
  if (valve) {
    res.json(valve);
  } else {
    res.status(404).send('Valve not found');
  }
});

app.post('/valves', (req, res) => {
  const valve = req.body;
  valves.push(valve);
  res.status(201).json(valve);
});

app.put('/valves/:sn', (req, res) => {
  const index = valves.findIndex(v => v.sn === req.params.sn);
  if (index !== -1) {
    valves[index] = req.body;
    res.json(valves[index]);
  } else {
    res.status(404).send('Valve not found');
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
