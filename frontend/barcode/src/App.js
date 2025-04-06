import React, { useState, useRef, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Webcam from 'react-webcam';
import axios from 'axios';
import Quagga from 'quagga'; // Import Quagga for barcode scanning
import './App.css';

// Simple placeholder pages
const NotificationsPage = () => (
  <div style={{ flex: 1, backgroundColor: '#4CAF50', height: '100vh' }}>
    Notifications Page
  </div>
);
const RecipesPage = () => (
  <div style={{ flex: 1, backgroundColor: '#FF9800', height: '100vh' }}>
    Recipes Page
  </div>
);
const DonatePage = () => (
  <div style={{ flex: 1, backgroundColor: '#F44336', height: '100vh' }}>
    Donate Page
  </div>
);

// Recycle page with barcode scanner
const RecyclePage = () => {
  const scannerRef = useRef(null);
  const [barcode, setBarcode] = useState(''); // State to store the detected barcode
  const [lastDetectedTime, setLastDetectedTime] = useState(0); // Track the last detection time

  useEffect(() => {
    // Initialize Quagga when the component mounts
    Quagga.init(
      {
        inputStream: {
          type: 'LiveStream',
          target: scannerRef.current, // Attach the scanner to the div
          constraints: {
            width: 640,
            height: 480,
            facingMode: 'environment', // Use the back camera
          },
        },
        decoder: {
          readers: ['upc_reader'], // Use the UPC barcode reader
        },
      },
      (err) => {
        if (err) {
          console.error('Error initializing Quagga:', err);
          return;
        }
        Quagga.start(); // Start the scanner
      }
    );

    // Listen for detected barcodes
    Quagga.onDetected((data) => {
      const currentTime = Date.now();
      if (currentTime - lastDetectedTime >= 3000) { // Allow detection every 3 seconds
        setLastDetectedTime(currentTime); // Update the last detection time
        if (data && data.codeResult && data.codeResult.code) {
          setBarcode(data.codeResult.code); // Store the barcode in state
        }
      }
    });

    // Cleanup when the component unmounts
    return () => {
      Quagga.stop();
    };
  }, [lastDetectedTime]);

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: '#9C27B0',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <h1 style={{ color: 'white', marginBottom: '20px' }}>Scan a Barcode</h1>
      <div
        ref={scannerRef}
        style={{
          width: '640px',
          height: '480px',
          backgroundColor: 'black',
        }}
      ></div>
      {barcode && (
        <div
          style={{
            marginTop: '20px',
            padding: '10px 20px',
            backgroundColor: '#FFF',
            borderRadius: '5px',
            color: '#000',
            fontSize: '18px',
            fontWeight: 'bold',
          }}
        >
          Detected Barcode: {barcode}
        </div>
      )}
    </div>
  );
};

// Scan page with capture, upload, and barcode scanner
const ScanPage = () => {
  const webcamRef = useRef(null);
  const scannerRef = useRef(null);
  const [barcode, setBarcode] = useState(''); // State to store the detected barcode
  const [lastDetectedTime, setLastDetectedTime] = useState(0); // Track the last detection time
  const [isBarcodeScannerActive, setIsBarcodeScannerActive] = useState(false); // Toggle between image capture and barcode scanner
  const [responseImage, setResponseImage] = useState(null); // State to store the server response image

  // Function to capture an image and send it to the server
  const captureImage = async () => {
    const capturedImage = webcamRef.current.getScreenshot(); // Capture the image
    if (!capturedImage) {
      alert('Failed to capture image. Please try again.');
      return;
    }

    try {
      // Convert base64 image to Blob
      const blob = await fetch(capturedImage).then((res) => res.blob());

      // Prepare form data
      const formData = new FormData();
      formData.append('image', blob, 'captured-image.jpg');

      // Define the server URL
      const serverUrl = "https://10.136.138.133:5001/api/classify?image="; // Replace with your server URL

      // Send the image to the server
      const response = await axios.post(serverUrl, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      // Handle the server response
      if (response.data && response.data.imageUrl) {
        setResponseImage(response.data.imageUrl); // Display the response image
      } else {
        alert('Image uploaded successfully, but no response image received.');
      }
    } catch (error) {
      console.error('Error uploading image:', error);
      alert('Failed to upload image. Please check the console for details.');
    }
  };

  // Initialize and handle barcode scanner
  useEffect(() => {
    if (isBarcodeScannerActive) {
      Quagga.init(
        {
          inputStream: {
            type: 'LiveStream',
            target: scannerRef.current, // Attach the scanner to the div
            constraints: {
              width: 640,
              height: 480,
              facingMode: 'environment', // Use the back camera
            },
          },
          decoder: {
            readers: ['upc_reader'], // Use the UPC barcode reader
          },
        },
        (err) => {
          if (err) {
            console.error('Error initializing Quagga:', err);
            return;
          }
          Quagga.start(); // Start the scanner
        }
      );

      // Listen for detected barcodes
      Quagga.onDetected((data) => {
        const currentTime = Date.now();
        if (currentTime - lastDetectedTime >= 3000) { // Allow detection every 3 seconds
          setLastDetectedTime(currentTime); // Update the last detection time
          if (data && data.codeResult && data.codeResult.code) {
            setBarcode(data.codeResult.code); // Store the barcode in state
          }
        }
      });

      // Cleanup when the barcode scanner is turned off
      return () => {
        Quagga.stop();
      };
    }
  }, [isBarcodeScannerActive, lastDetectedTime]);

  return (
    <div
      style={{
        flex: 1,
        backgroundColor: '#2196F3',
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <h1 style={{ color: 'white', marginBottom: '20px' }}>
        {isBarcodeScannerActive ? 'Scan a Barcode' : 'Capture an Image'}
      </h1>

      {/* Toggle Button */}
      <button
        onClick={() => setIsBarcodeScannerActive(!isBarcodeScannerActive)}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          backgroundColor: isBarcodeScannerActive ? '#F44336' : '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          marginBottom: '20px',
        }}
      >
        {isBarcodeScannerActive ? 'Switch to Image Capture' : 'Switch to Barcode Scanner'}
      </button>

      {/* Barcode Scanner */}
      {isBarcodeScannerActive && (
        <div
          ref={scannerRef}
          style={{
            width: '640px',
            height: '480px',
            backgroundColor: 'black',
          }}
        ></div>
      )}

      {/* Image Capture */}
      {!isBarcodeScannerActive && (
        <div style={{ textAlign: 'center' }}>
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            style={{ width: '100%', maxWidth: '400px', marginBottom: '20px' }}
          />
          <button onClick={captureImage} style={buttonStyle}>
            Capture Image
          </button>
        </div>
      )}

      {/* Display Detected Barcode */}
      {barcode && (
        <div
          style={{
            marginTop: '20px',
            padding: '10px 20px',
            backgroundColor: '#FFF',
            borderRadius: '5px',
            color: '#000',
            fontSize: '18px',
            fontWeight: 'bold',
          }}
        >
          Detected Barcode: {barcode}
        </div>
      )}

      {/* Display Response Image */}
      {responseImage && (
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <img
            src={responseImage}
            alt="Response"
            style={{ width: '100%', maxWidth: '400px', marginBottom: '20px' }}
          />
        </div>
      )}
    </div>
  );
};

// Shared button style
const buttonStyle = {
  padding: '10px 20px',
  fontSize: '16px',
  backgroundColor: '#4CAF50',
  color: 'white',
  border: 'none',
  borderRadius: '5px',
  cursor: 'pointer',
  marginTop: '10px',
};

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<ScanPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/recipes" element={<RecipesPage />} />
          <Route path="/recycle" element={<RecyclePage />} />
          <Route path="/donate" element={<DonatePage />} />
        </Routes>

        {/* Bottom Navigation Bar */}
        <div className="bottom-nav">
          <Link to="/notifications" className="nav-button">
            <span role="img" aria-label="notifications">
              🔔
            </span>
          </Link>
          <Link to="/recipes" className="nav-button">
            <span role="img" aria-label="recipes">
              📖
            </span>
          </Link>
          <Link to="/" className="nav-button active">
            <span role="img" aria-label="scan">
              📷
            </span>
          </Link>
          <Link to="/recycle" className="nav-button">
            <span role="img" aria-label="recycle">
              ♻️
            </span>
          </Link>
          <Link to="/donate" className="nav-button">
            <span role="img" aria-label="donate">
              ❤️
            </span>
          </Link>
        </div>
      </div>
    </Router>
  );
}

export default App;