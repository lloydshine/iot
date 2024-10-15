import { createContext, useContext, useEffect, useState } from "react";
import useWebSocket from "react-use-websocket";

// Define the WebSocketContext
const WebSocketContext = createContext(undefined);

// Custom hook to use WebSocket context
export const useWS = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocket must be used within a WebSocketProvider");
  }
  return context;
};

// Define the WebSocketProvider component
export function WebSocketProvider({ children }) {
  const [soilData, setSoilData] = useState(null);

  const { sendJsonMessage, lastJsonMessage } = useWebSocket(
    "ws://localhost:5861",
    {
      onOpen: () => {
        console.log("WebSocket connection opened");
        const connectionData = {
          event: "connection",
          data: { type: "client" },
        };
        sendJsonMessage(connectionData);
      },
      onClose: () => console.log("WebSocket connection closed"),
    }
  );

  useEffect(() => {
    if (lastJsonMessage) {
      switch (lastJsonMessage.event) {
        case "device-collect":
          console.log(lastJsonMessage.data);
          setSoilData(lastJsonMessage.data);
          break;
        default:
          break;
      }
    }
  }, [lastJsonMessage]);

  return (
    <WebSocketContext.Provider value={{ sendJsonMessage, soilData }}>
      {children}
    </WebSocketContext.Provider>
  );
}
