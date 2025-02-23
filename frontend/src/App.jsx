import { useState, useEffect } from 'react';
import axios from "axios";

import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community'; 
// Register all Community features
ModuleRegistry.registerModules([AllCommunityModule]);

import { AgGridReact } from 'ag-grid-react'; // React Data Grid Component

import reactLogo from './assets/react.svg';
import viteLogo from '/vite.svg';

import './App.css';
import MenuBar from './MenuBar';

function Dashboard() {
  const [rowData, setRowData] = useState([]);
  const [colDefs, setColDefs] = useState([
      { field: "make" },
      { field: "model" },
      { field: "price" },
      { field: "electric" }
  ]);

  useEffect(() => {
      axios.get("http://127.0.0.1:8000/api/hello")
          .then(response => {
              setRowData(response.data.data);
          })
          .catch(error => {
              console.error("Error fetching data:", error);
          });
  }, []);

  return (
    <div style={{ height: 500 }}>
        <AgGridReact
            rowData={rowData}
            columnDefs={colDefs}
        />
    </div>
  )  
}

function HelloWorld() {
  const [message, setMessage] = useState("");

  useEffect(() => {
      axios.get("http://127.0.0.1:8000/api/hello")
          .then(response => {
              setMessage("Data fetched successfully");
          })
          .catch(error => {
              console.error("Error fetching data:", error);
          });
  }, []);

  return (
      <div style={{ textAlign: "center", marginTop: "50px" }}>
          <h1>FastAPI + React</h1>
          <p>API Response: {message}</p>
      </div>
  );
}


function App() {

  return (
    <>
      <div className='bg-gray-300 text-gray-900'>
        <MenuBar />
        <HelloWorld />
        <Dashboard />
      </div>
    </>
  );
}

export default App;
