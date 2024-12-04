# Optimal Coin Transfer with Real-Time Visualization

## Overview

You can view this documentation in multiple languages by selecting your preferred language below:

- [English](/README.md)
- [Korean](/README_ko.md)

This project provides a Python-based tool that calculates the value of Korean Won (KRW) after converting it to various cryptocurrencies (XRP, TRX, or USDT) and transferring them to Binance, while accounting for network fees. It utilizes real-time data from Upbit and Binance APIs to offer accurate calculations and visualizes the data in real-time through interactive plots.

## Features

- **Real-Time Conversion and Transfer Value Calculation**: Calculates the amount of XRP, TRX, or USDT received after fees when transferring from Upbit to Binance.
- **Interactive Visualization**: Real-time data visualization that allows users to choose different timeframes, including 1s, 10s, 30s, 1min, 3min, and up to daily.
- **Data Persistence**: Saves data to allow continuous tracking, even after restarting the application.
- **Adjustable Timeframes**: Visualize average values based on selectable time intervals, providing insights from seconds to daily trends.

## Installation

1. Clone the repository:
    
    ```
    git clone <repository-url>
    
    ```
    
2. Navigate to the project directory:
    
    ```
    cd optimal-coin-transfer
    
    ```
    
3. Create and activate a virtual environment:
    
    ```
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\\Scripts\\activate
    
    ```
    
4. Install the required packages:
    
    ```
    pip install -r requirements.txt
    
    ```
    

## Usage

Run the main script to start the tool:

```
python src/on_thread_data_mine.py

```

Upon running, the application will begin fetching real-time cryptocurrency data from Upbit and Binance and display the results in a PyQt5 GUI window with matplotlib visualization.

## Libraries Used

- **requests**: To get the real-time prices of cryptocurrencies from Upbit and Binance.
- **PyQt5**: To create an interactive graphical user interface (GUI).
- **matplotlib**: To visualize real-time price comparisons.
- **pandas**: To handle and process data effectively.

## Contributing

If you would like to contribute translations for other languages, please feel free to submit a pull request.
Feel free to submit a pull request or open an issue if you have suggestions for improvements or encounter any bugs.

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
