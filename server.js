const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

const DATA_FILE = path.join(__dirname, 'valves.json');

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

function readValves() {
  try {
    const data = fs.readFileSync(DATA_FILE);
    return JSON.parse(data);
  } catch {
    return [];
  }
}

function writeValves(valves) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(valves, null, 2));
}

app.get('/valves', (req, res) => {
  const valves = readValves();
  res.json(valves);
});

app.get('/valves/:sn', (req, res) => {
  const valves = readValves();
  const valve = valves.find(v => v.sn === req.params.sn);
  if (valve) res.json(valve);
  else res.status(404).send('Valve not found');
});

app.post('/valves', (req, res) => {
  const valves = readValves();
  valves.push(req.body);
  writeValves(valves);
  res.status(201).json(req.body);
});

app.put('/valves/:sn', (req, res) => {
  let valves = readValves();
  const index = valves.findIndex(v => v.sn === req.params.sn);
  if (index !== -1) {
    valves[index] = req.body;
    writeValves(valves);
    res.json(valves[index]);
  } else {
    res.status(404).send('Valve not found');
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});