const http = require("http");
const { WebSocketServer } = require("ws");

const server = http.createServer();
const wsServer = new WebSocketServer({ server });

const port = 5861;
const host = "localhost";

let connections = [];

// Function to broadcast a message to all clients
const broadcastToClients = (message) => {
  connections.forEach((conn) => {
    if (
      conn.connection.readyState === conn.connection.OPEN &&
      conn.type !== "device"
    ) {
      conn.connection.send(JSON.stringify(message));
    }
  });
};

// Function to send a message specifically to the device
const broadcastToDevice = (message) => {
  const deviceConnection = connections.find((conn) => conn.type === "device");
  if (
    deviceConnection &&
    deviceConnection.connection.readyState === deviceConnection.connection.OPEN
  ) {
    deviceConnection.connection.send(JSON.stringify(message));
  }
};

wsServer.on("connection", (connection, request) => {
  connection.on("message", (message) => {
    try {
      const data = JSON.parse(message);
      console.log("Data Received:", data);

      switch (data.event) {
        case "connection":
          console.log(`${data.data.type} connected`);
          connections.push({ connection, type: data.data.type });
          break;
        case "device-collect":
          broadcastToClients(data);
          break;
        case "client-collect":
          console.log("Collecting data from the device...");
          broadcastToDevice(data);
          break;
        default:
          console.warn("Unknown event type:", data.event);
      }
    } catch (err) {
      console.error("Error parsing JSON:", err);
    }
  });

  connection.on("close", () => {
    // Remove connection from the list
    connections = connections.filter((conn) => conn.connection !== connection);
    console.log(
      "Connection closed. Remaining connections:",
      connections.length
    );
  });
});

server.listen(port, host, () => {
  console.log(`WebSocket server is listening on ws://${host}:${port}`);
});
