# Soil Quality Data Collection

This project is structured into three main parts:

1. **Device (Python)**: Handles device-related functionality and requires a virtual environment.
2. **Server (Node.js)**: Websocket server built with Node.js.
3. **Client (Vite + React)**: Frontend application built using Vite and React.

## Project Structure

.
├── device/ # Python-based device management
├── server/ # Node.js server for Websocket logic
├── client/ # Vite + React frontend web app
└── README.md

## 1. Device (Python)

### Prerequisites

- Python 3.x
- Virtual Environment

### Setup Instructions

1. Navigate to the `device/` folder:

   cd device

2. Create a virtual environment:

   python -m venv venv

3. Activate the virtual environment:

   - On Windows:
     venv\Scripts\activate
   - On macOS/Linux:
     source venv/bin/activate

4. Install dependencies:

   pip install -r requirements.txt

5. Run the Python script:

   python main.py

## 2. Server (Node.js)

### Prerequisites

- Node.js (v14.x or above)

### Setup Instructions

1. Navigate to the `server/` folder:

   cd server

2. Install dependencies:

   npm install

3. Start the server:

   npm run start

   The server will be running on `http://localhost:5861`.

## 3. Client (Vite + React)

### Prerequisites

- Node.js (v14.x or above)

### Setup Instructions

1. Navigate to the `client/` folder:

   cd client

2. Install dependencies:

   npm install

3. Run the development server:

   npm run dev

   The client will be running on `http://localhost:5173`.

## Scripts

| Folder | Script           | Description                      |
| ------ | ---------------- | -------------------------------- |
| device | `python main.py` | Runs the Python script           |
| server | `npm run start`  | Starts the Node.js server        |
| client | `npm run host`   | Starts the Vite + React frontend |

## Contribution

Feel free to submit issues or pull requests to help improve this project.

## License

This project is licensed under the MIT License.
