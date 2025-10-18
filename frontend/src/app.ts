import express from "express";
import fs from "fs";
import https from "https";
import path from "path";
import send from "send";

const app = express();

const sslOptions = {
  key: process.env.SSL_KEY_FILE ? fs.readFileSync(process.env.SSL_KEY_FILE) : undefined,
  cert: process.env.SSL_CRT_FILE ? fs.readFileSync(process.env.SSL_CRT_FILE) : undefined,
};


// app.use("/static/scripts", express.static(path.join(__dirname, "../lib/static/scripts")));
app.use(express.static(path.join(__dirname, "../lib")));

// Adding tabs to our app. This will setup routes to various views
// Setup home page
app.get("/", (req, res) => {
  send(req, path.join(__dirname, "../lib/index.html")).pipe(res);
});

// Setup the static tab
app.get("/tab", (req, res) => {
  send(req, path.join(__dirname, "")).pipe(res);
});

// Create HTTP server
const port = process.env.port || process.env.PORT || 3333;

if (sslOptions.key && sslOptions.cert) {
  https.createServer(sslOptions, app).listen(port, () => {
    console.log(`Express server listening on port ${port}`);
  });
} else {
  app.listen(port, () => {
    console.log(`Express server listening on port ${port}`);
  });
}
//app.listen(port, () => {
  //console.log(`Express server listening on port ${port}`);
//});
console.log("KEY:", process.env.SSL_KEY_FILE);
console.log("CERT:", process.env.SSL_CRT_FILE);
console.log("SSL key loaded:", !!sslOptions.key);
console.log("SSL cert loaded:", !!sslOptions.cert);
