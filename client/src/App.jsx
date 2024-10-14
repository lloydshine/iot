import { useWS } from "./components/WebSocketProvider";

export default function App() {
  const { soilData, sendJsonMessage } = useWS();

  // If soilData is null or undefined, display default values
  const dataToDisplay = soilData || {
    Nitrogen: 0,
    Phosphorus: 0,
    Potassium: 0,
    Temperature: 0,
    Humidity: 0,
    pH: 0,
  };

  const handleCollectData = () => {
    const collectDataMessage = {
      event: "client-collect",
    };
    sendJsonMessage(collectDataMessage);
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white shadow-lg rounded-lg p-6 sm:p-8 max-w-lg w-full">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
          Soil Analysis Report
        </h2>
        <div className="grid grid-cols-1 gap-4 md:gap-6">
          {Object.entries(dataToDisplay).map(([key, value]) => (
            <div
              key={key}
              className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex justify-between items-center"
            >
              <span className="font-medium text-gray-700">{key}</span>
              <span className="text-gray-600">{value}</span>
            </div>
          ))}
        </div>
        <button
          onClick={handleCollectData}
          className="mt-6 w-full bg-blue-500 text-white font-semibold py-2 rounded-lg hover:bg-blue-600 transition duration-200"
        >
          Collect Data
        </button>
      </div>
    </div>
  );
}
