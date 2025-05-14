# Underwriting Dashboard

An automated real estate underwriting model monitoring and visualization system for B&R Capital.

## Overview

The Underwriting Dashboard is a comprehensive application designed to streamline the process of monitoring, analyzing, and visualizing real estate underwriting models. It automatically tracks deal folders, extracts key data from Excel models, stores the information in a database, and presents it through an interactive dashboard.

## Features

- **Automated File Processing**

  - Automatically identifies relevant underwriting models in deal folders
  - Extracts data based on predefined cell references
  - Processes updates when files change
- **Interactive Dashboard**

  - Real-time data visualization
  - Multiple views: tables, maps, analytics
  - Filtering and search capabilities
  - Export functionality
- **Real-time Monitoring**

  - Continuous monitoring of deal directories
  - Automatic database updates
  - Background processing to maintain application responsiveness
- **Responsive Design**

  - Optimized for both desktop and mobile viewing
  - Adaptive layout based on screen size
  - Mobile-friendly controls and navigation

## Project Structure

```
├── config/              # Configuration files
├── database/            # SQLite database files
├── logs/                # Application logs
├── notebooks/           # Jupyter notebooks for testing
├── prompt/              # Excel reference files
├── src/                 # Source code
│   ├── dashboard/       # Streamlit dashboard components
│   ├── data_processing/ # Excel data extraction utilities
│   ├── database/        # Database management
│   └── file_monitoring/ # File system monitoring
└── tests/               # Test files
```

## Setup and Installation

1. **Clone the repository**
2. **Set up the environment**

   ```
   conda env create -f environment.yml
   conda activate underwriting-dashboard
   ```
3. **Configure the application**

   - Edit `config/config.py` to set your deal directories and other parameters
4. **Run the application**

   ```
   python main.py
   ```

   Alternatively, use the batch file:

   ```
   run_monitoring.bat
   ```

## Usage

1. After starting the application, the dashboard will be available at http://localhost:8501
2. Use the filters to narrow down deals by various criteria
3. Switch between table view, map view, and analytics view
4. Export data as needed using the export options

## Technologies

- **Python**: Core programming language
- **Streamlit**: Dashboard framework
- **Pandas**: Data processing and analysis
- **SQLite**: Database storage
- **Plotly/Folium**: Data visualization and mapping
- **Watchdog**: File system monitoring

## Development

To contribute to the development:

1. Make sure all tests pass before submitting changes

   ```
   # Run tests
   pytest tests/
   ```
2. Follow the existing code style and structure

## License

Proprietary - B&R Capital
