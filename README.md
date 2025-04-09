# LastBite AI

LastBite AI is an AI-powered food rescue platform built in 24 hours at ScarletHacks. It detects soon-to-expire food items using barcode/OCR scanning, predicts shelf life with ML, and connects users with donation centers using smart geolocation-based routing—all to reduce food waste and empower community giving.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

Food waste is a significant issue that impacts the environment and community. LastBite AI aims to tackle this problem by leveraging AI and machine learning to detect food items that are nearing expiration and facilitate their donation to local centers.

## Features

- **Barcode/OCR Scanning**: Detects and reads barcodes and text on food labels.
- **Shelf Life Prediction**: Uses machine learning to predict the remaining shelf life of food items.
- **Smart Routing**: Connects users with nearby donation centers using geolocation-based routing.
- **User-Friendly Interface**: Easy-to-use interface for both individuals and organizations.

## Tech Stack

- **Backend**: Python
- **Frontend**: JavaScript, React
- **Styling**: CSS, HTML
- **Scripts**: Shell

## Installation

### Prerequisites

- Ensure you have Python and Node.js installed on your system.

### Backend Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/Gunjaomprakash/lastbite-ai.git
    cd lastbite-ai
    ```

2. Navigate to the backend directory and install dependencies:
    ```sh
    cd backend
    pip install -r requirements.txt
    ```

3. Run the backend server:
    ```sh
    python app.py
    ```

### Frontend Setup

1. Navigate to the frontend directory and install dependencies:
    ```sh
    cd ../frontend
    npm install
    ```

2. Run the frontend server:
    ```sh
    npm start
    ```

## Usage

To use LastBite AI, follow these steps:

1. Open your browser and navigate to `http://localhost:3000` to access the frontend.
2. Use the barcode scanner to detect food items.
3. View the predicted shelf life and suggested donation centers.

## Contributing

We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
