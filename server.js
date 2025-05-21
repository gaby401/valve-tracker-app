
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const app = express();
const PORT = 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// In-memory mock DB
let valves = [];

// Create new valve record
app.post('/valves', (req, res) => {
  const valve = req.body;
  valves.push(valve);
  res.status(201).json({ message: 'Valve added', valve });
});

// Get all valves
app.get('/valves', (req, res) => {
  res.json(valves);
});

// Update valve by serial number
app.put('/valves/:sn', (req, res) => {
  const sn = req.params.sn;
  const index = valves.findIndex(v => v.sn === sn);
  if (index !== -1) {
    valves[index] = { ...valves[index], ...req.body };
    res.json({ message: 'Valve updated', valve: valves[index] });
  } else {
    res.status(404).json({ message: 'Valve not found' });
  }
});

// Get a valve by SN
app.get('/valves/:sn', (req, res) => {
  const sn = req.params.sn;
  const valve = valves.find(v => v.sn === sn);
  if (valve) res.json(valve);
  else res.status(404).json({ message: 'Valve not found' });
});

app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
