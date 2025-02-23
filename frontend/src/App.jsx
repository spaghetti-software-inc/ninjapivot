// App.jsx
import React, { useState, useEffect, useRef } from 'react';

import myLogo from './assets/logo_128px.png';
import './App.css'

function App() {
  // State variables
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const pollingIntervalRef = useRef(null);

  // Drag & drop handlers
  const handleFileDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // File input change handler
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  // Remove selected file
  const removeFile = () => {
    setFile(null);
  };

  // Upload the file to the backend
  const handleUpload = async () => {
    if (!file) return;
    setError(null);
    setIsUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.error || 'Upload failed');
        setIsUploading(false);
        return;
      }

      const data = await response.json();
      setJobId(data.job_id);
    } catch (err) {
      console.error(err);
      setError('An unexpected error occurred during upload.');
    }
    setIsUploading(false);
  };

  // Poll the backend for status updates once a jobId is set
  useEffect(() => {
    if (!jobId) return;
    pollingIntervalRef.current = setInterval(async () => {
      try {
        const res = await fetch(`/status/${jobId}`);
        if (!res.ok) {
          const errorData = await res.json();
          setError(errorData.error || 'Error retrieving status');
          clearInterval(pollingIntervalRef.current);
          return;
        }
        const statusData = await res.json();
        setProgress(statusData.progress);
        setStatusMessage(statusData.status_message);
        setIsComplete(statusData.is_complete);

        // Once complete, stop polling and set the PDF URL
        if (statusData.is_complete) {
          clearInterval(pollingIntervalRef.current);
          setPdfUrl(`/result/${jobId}`);
        }
      } catch (err) {
        console.error(err);
        setError('An unexpected error occurred while checking status.');
        clearInterval(pollingIntervalRef.current);
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(pollingIntervalRef.current);
  }, [jobId]);

  // Render the upload page if no job has been initiated
  if (!jobId) {
    return (
      <div className="min-h-screen bg-gray-200 flex flex-col items-center justify-center p-4">
        {/* Header Section */}
        <header className="mb-8 text-center">
          <h1 className="text-5xl font-extrabold text-blue-600">Ninjapivot</h1>
          <img src={myLogo} className="logo mx-auto" alt="Ninjapivot logo" />
          <p className="mt-2 text-xl text-gray-700">Your Automated Statistician</p>
        </header>
        {/* Card Section */}
        <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 border-b pb-2">
            Upload CSV
          </h2>
          {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
          <div
            className="border-dashed border-2 border-gray-300 rounded-lg p-6 text-center mb-4 cursor-pointer hover:border-blue-400 relative"
            onDrop={handleFileDrop}
            onDragOver={handleDragOver}
          >
            {file ? (
              <div className="flex items-center justify-center">
                <p className="text-gray-700">{file.name}</p>
                <button
                  onClick={removeFile}
                  className="ml-2 text-red-500 hover:text-red-700 focus:outline-none"
                >
                  Remove
                </button>
              </div>
            ) : (
              <p className="text-gray-500">
                Drag & drop your CSV file here, or click to select
              </p>
            )}
            {/* Invisible file input over the drop zone */}
            {!file && (
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
            )}
          </div>
          <button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-lg transition-colors duration-200"
          >
            {isUploading ? 'Uploading...' : 'Upload & Analyze'}
          </button>
          <p className="text-xs text-gray-500 mt-4">
            Maximum: 10,000 rows, 100 columns. File size limit: 5 MB.
          </p>
        </div>
        {/* Footer */}
        <footer className="mt-8 text-gray-500 text-xs">
          &copy; 2025 Ninjapivot. All rights reserved.
        </footer>
      </div>
    );
  }

  // Render the results page once the job is initiated
  return (
    <div className="min-h-screen bg-gray-200 flex flex-col items-center justify-center p-4">
      {/* Header Section */}
      <header className="mb-8 text-center">
        <h1 className="text-5xl font-extrabold text-blue-600">Ninjapivot</h1>
        <p className="mt-2 text-xl text-gray-700">Your Automated Statistician</p>
      </header>
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-2xl">
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        {!isComplete ? (
          // Progress indicator while analysis is in progress
          <div className="text-center">
            <p className="text-xl font-medium text-gray-800 mb-4">{statusMessage}</p>
            <div className="w-full bg-gray-300 rounded-full h-4 mb-4">
              <div
                className="bg-blue-600 h-4 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <p className="text-gray-600">Progress: {progress}%</p>
          </div>
        ) : (
          // Display the PDF and download option when complete
          <div>
            <p className="text-xl font-medium text-gray-800 mb-4">Analysis Complete!</p>
            <div className="mb-4">
              <iframe
                src={pdfUrl}
                className="w-full h-96 border border-gray-300 rounded"
                title="PDF Report"
              ></iframe>
            </div>
            <div className="flex flex-col md:flex-row justify-between gap-4">
              <a
                href={`${pdfUrl}?download=true`}
                className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg text-center"
              >
                Download Report
              </a>
              <button
                onClick={() => window.location.reload()}
                className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg text-center"
              >
                New Analysis
              </button>
            </div>
          </div>
        )}
      </div>
      {/* Footer */}
      <footer className="mt-8 text-gray-500 text-xs">
        &copy; 2025 Ninjapivot. All rights reserved.
      </footer>
    </div>
  );
}

export default App;
