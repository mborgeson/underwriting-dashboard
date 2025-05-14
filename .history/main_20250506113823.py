def main():
    """Initialize and run the underwriting dashboard application."""
    try:
        logger.info("Starting Underwriting Dashboard application")
        
        # Import modules
        from src.data_processing.file_finder import find_underwriting_files
        from src.data_processing.excel_reader import process_excel_files
        from src.database.db_manager import setup_database, store_data
        from src.file_monitoring.monitor import start_monitoring
        import threading
        import os
        
        # Initial setup
        logger.info("Setting up database")
        setup_database()
        
        # Find and process files
        logger.info("Finding underwriting files")
        include_files, exclude_files = find_underwriting_files()
        
        logger.info(f"Processing {len(include_files)} underwriting files")
        data = process_excel_files(include_files)
        
        # Store data
        logger.info("Storing data in database")
        store_data(data)
        
        # Start monitoring in a separate thread
        logger.info("Starting file monitoring")
        monitor_thread = threading.Thread(target=start_monitoring)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Launch Streamlit dashboard
        logger.info("Starting dashboard")
        dashboard_path = str(Path(__file__).resolve().parent / "src" / "dashboard" / "app.py")
        os.system(f"streamlit run {dashboard_path}")
        
    except Exception as e:
        logger.error(f"Error in main application: {str(e)}", exc_info=True)
        print(f"An error occurred: {str(e)}")
        return 1
    
    return 0