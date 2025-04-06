import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import logo from './logo.svg';
import './App.css';

function App() {
  const [cameraActive, setCameraActive] = useState(false);
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [error, setError] = useState(null);

  const toggleCamera = () => {
    setCameraActive((prevState) => !prevState);
    // Reset captured image when toggling camera
    if (capturedImage) setCapturedImage(null);
    // Reset error when toggling
    if (error) setError(null);
  };

  const captureImage = () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      setCapturedImage(imageSrc);
    }
  };

  const handleWebcamError = (err) => {
    console.error(err);
    setError("Camera access denied or not available. Please check permissions.");
  };

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1>Barcode Scanner App</h1>
        
        <button onClick={toggleCamera} className="camera-toggle-button">
          {cameraActive ? 'Deactivate Camera' : 'Activate Camera'}
        </button>
        
        {error && <p className="error-message">{error}</p>}
        
        <div className="camera-container">
          {cameraActive && !capturedImage && (
            <div className="webcam-container">
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                width={320}
                height={240}
                videoConstraints={{
                  facingMode: "environment" // Use rear camera if available (for mobile devices)
                }}
                onUserMediaError={handleWebcamError}
              />
              <button onClick={captureImage} className="capture-button">
                Capture Image
              </button>
            </div>
          )}
          
          {capturedImage && (
            <div className="captured-image-container">
              <img src={capturedImage} alt="Captured" />
              <div className="image-actions">
                <button onClick={() => setCapturedImage(null)}>
                  Retake
                </button>
                <button>
                  Process Barcode
                </button>
              </div>
            </div>
          )}
        </div>
      </header>
    </div>
  );
}

export default App;
