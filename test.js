const http = require('http');

const data = JSON.stringify({
  messages: [{ role: "user", content: "hi" }],
  model: "mistral-large-latest",
  temperature: 0.2
});

const options = {
  hostname: 'localhost',
  port: 8000,
  path: '/api/v1/projects/art/chat/stream',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

const req = http.request(options, (res) => {
  console.log(`STATUS: ${res.statusCode}`);
  res.on('data', (chunk) => {
    console.log(`BODY: ${chunk}`);
  });
});

req.on('error', (e) => {
  console.error(`problem with request: ${e.message}`);
});

req.write(data);
req.end();
