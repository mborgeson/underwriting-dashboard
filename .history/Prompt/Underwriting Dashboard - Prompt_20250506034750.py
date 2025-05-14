underwriting_dashboard_prompt_generator = """

### UNDERWRITING DASHBOARD PROJECT PROMPT

**PROJECT OBJECTIVES**:
1. **PROJECT PART #1: Identify Files in a Top-Level Directory that will be Read into a DataFrame, based upon meeting certain criteria, and then uploaded to a Database**:
    A). To create project code that identifies excel files within a directory, based upon given criteria, in order to pull specific information from only those excel files that are underwriting models.
    
    B). The project will utilize the below directories and the deal stage subdirectories for the locations of where it still start its review:
        (I) Top-Level Directory:
            (i) "C:\Users\MattBorgeson\B&R Capital\B&R Capital - Real Estate\Deals"
        (II) Deal Stage Subdirectories:
            (i) "C:\Users\MattBorgeson\B&R Capital\B&R Capital - Real Estate\Deals\0) Dead Deals"
            (ii) "C:\Users\MattBorgeson\B&R Capital\B&R Capital - Real Estate\Deals\1) Initial UW and Review"            
            (iii) "C:\Users\MattBorgeson\B&R Capital\B&R Capital - Real Estate\Deals\2) Active UW and Review"
            (iv) "C:\Users\MattBorgeson\B&R Capital\B&R Capital - Real Estate\Deals\3) Deals Under Contract"
            (v) "C:\Users\MattBorgeson\B&R Capital\B&R Capital - Real Estate\Deals\4) Closed Deals"
            (vi) "C:\Users\MattBorgeson\B&R Capital\B&R Capital - Real Estate\Deals\5) Realized Deals"
            
    C). Once inside each of the directories listed within the "first-level deal subdirectories", the project will loop through each of the folders with the deal folder and find the "UW Model" folder. Next the project will loop through each of the files in the "UW Folder" for the below criteria:
        (I) File Criteria:
            (i) The file must be an excel file an be one of the following file types - ".xlsb" or ".xlsm");
            (ii) The file name must include the following text - "UW Model vCurrent";
            (iii) The file name must NOT include the following text - "Speedboat";
            (iv) The last modified date of the file must be in the following date range - Last Modified Date >= 12/31/2024;

    D). After the project determines the excel files to pull data from based upon the criteria under bullet C)(I) above, the code should produce an output with two tables in DataFrame format. See below for the details of the two tables to produce: 
        (I) Table #1 - Excel Files to be INCLUDED in DataFrame:
            (i) The table should include the following columns:
                1) File Summary Data - File Name;
                2) File Summary Data - Absolute File Path;
                3) File Summary Data - Deal Stage Subdirectory Name (i.e., One of the folders listed under bullet B(II) above);
                4) File Summary Data - Deal Stage Subdirectory Path (i.e., One of the folders listed under bullet B(II) above);
                5) File Summary Data - Last Modified Date of the File; and
                6) File Summary Data - File Size in Bytes.
        (II) Table #2 - Excel Files to be EXCLUDED the DataFrame:
            (i) The table should include the following columns:
                1) File Summary Data - File Name;
                2) File Summary Data - Absolute File Path;
                3) File Summary Data - Deal Stage Subdirectory Name (i.e., One of the folders listed under bullet B(II) above);
                4) File Summary Data - Deal Stage Subdirectory Path (i.e., One of the folders listed under bullet B(II) above);
                5) File Summary Data - Last Modified Date of the File; and
                6) File Summary Data - File Size in Bytes.

    E). Next, a DataFrame for each of the excel file paths included in the DataFrame table under bullet D)(I)(i)(2) will be created. The specific values to be pulled from these excel UW Models are included in an excel file within this project directory ("Reference File"). As such, see below for the path to this file along with myriad other details regarding the UW Model to read into a DataFrame:
        (I) Excel Underwriting Model File Data Information:
            (i) Reference File Location:
                (1)"C:\Users\MattBorgeson\OneDrive - B&R Capital\Programming Projects\Underwriting Dashboard\Prompt\Underwriting Dashboard Project - Cell Value References.xlsx"
            (ii) Reference File Contents:
                (1) Sheet Name - "UW Model - Cell Reference Table";
                (2) Cell range references for the values to be pulled from the excel files are located in column "I" within this worksheet, which has the header "Values Reference Range";
                (3) Cell range reference headers of the values to be pulled from the excel files are located in column "J" within this worksheet, which has the header "DataFrame Column Names"; and
                (4) This worksheet contains other columns that breakout references to the sheet names, cell addresses, and cell value category types.
            (iii) Reference Structure:
                (1) The reference structure for a single cell value is as follows:
                    (a) Cell Reference - 'Assumptions (Summary)'!$D$6
                    (b) Cell Reference (Sheet Name) - 'Assumptions (Summary)'
                    (c) Cell Reference (Cell Address) - $D$6
                    (d) Cell Reference (Cell Address - Row) - 6
                    (e) Cell Reference (Cell Address - Column) - D
                (2) The reference structure for a range of cell values is as follows:
                    (a) Cell Reference - 'Assumptions (Summary)'!$D$151:$D$161
                    (b) Cell Reference (Sheet Name) - 'Assumptions (Summary)'
                    (c) Cell Reference (Cell Address) - $D$151:$D$161
                    (d) Cell Reference (Cell Address - Row) - 151:161
                    (e) Cell Reference (Cell Address - Column) - D
                (3) The reference structure for a simple text value column header is as follows:
                    (a) Cell Reference - Loan-to-Value (At Exit)
                    (b) Cell Reference (Sheet Name) - None
                    (c) Cell Reference (Cell Address) - None
                    (d) Cell Reference (Cell Address - Row) - None
                    (e) Cell Reference (Cell Address - Column) - None
                (4) The reference structure for a column header with a cell reference is as follows:
                    (a) Cell Reference - 'Assumptions (Summary)'!$C$619
                    (b) Cell Reference (Sheet Name) - 'Assumptions (Summary)'
                    (c) Cell Reference (Cell Address) - $C$619
                    (d) Cell Reference (Cell Address - Row) - 619
                    (e) Cell Reference (Cell Address - Column) - C
                (5) The reference structure for a column header with a cell reference range is as follows:
                    (a) Cell Reference - 'Assumptions (Summary)'!$C$606:$C$616
                    (b) Cell Reference (Sheet Name) - 'Assumptions (Summary)'
                    (c) Cell Reference (Cell Address) - $C$606:$C$616
                    (d) Cell Reference (Cell Address - Row) - 606:616
                    (e) Cell Reference (Cell Address - Column) - C
                (6) The reference structure for a column header with a cell reference range and a text component to concatenate is as follows:
                    (a) Cell Reference - Studio (General Info) - 'Assumptions (Unit Matrix)'!$E$7:$I$7
                    (b) Cell Reference (Sheet Name) - 'Assumptions (Unit Matrix)'
                    (c) Cell Reference (Cell Address) - $E$7:$I$7
                    (d) Cell Reference (Cell Address - Row) - 7:7
                    (e) Cell Reference (Cell Address - Column) - E:I
                    (f) Text Component - "Studio (General Info) -"
                    (g) For these headers, the text component should be concatenated to each cell value in the cell range to create a unique column header for each cell value in the range (e.g., Studio (General Info) - 'Assumptions (Unit Matrix)'!$E$7, Studio (General Info) - 'Assumptions (Unit Matrix)'!$F$7, Studio, etc.).
                            
    F). Next, the dataframe should be stored in a SQLite database. The database should be named underwriting_models.db and the table should be named underwriting_model_data. The table should have the same columns as the dataframe with the addition of a "Date Uploaded" column to track the dates of any/all changes. Please see below for the details of the table to create:
        (I) Table Name: underwriting_model_data
        (II) Database Location: The database should be created in the following directory - C:\Users\MattBorgeson\OneDrive - B&R Capital\Programming Projects\Underwriting Dashboard\database.
        (III) The code should also check if the database already exists and if it does, it should append the new data to the existing table. If the database does not exist, it should create a new database and a new table.
        
    G). The code should also incorporate functionality to check the existing excel underwriting models for any changes, as well as any new deals added, throughout the  deal folders on a continuous real-time basis.
        (I) If a change is detected, the code should automatically pull the data from the updated excel file and update the underwriting_model_data table in the SQLite database.
        (II) If a new excel file is added to the directory, the code should check if the excel file is an underwriting model based on the criteria under bullet (C)(I) above. If it passes the criteria above, the data from the new excel file will be added it to the underwriting_model_data table in the SQLite database.
        (III) When the code detects a change in the excel underwriting model, it should also check if the file name has changed. If the file name has changed, the code should update the file name in the underwriting_model_data table in the SQLite database.
        (IV) When changes are detected to existing excel underwriting models, the code should pull all cell values from the excel file and update the underwriting_model_data table in the SQLite database by appending the new data to the existing table.
        (V) The code should also log the date of any changes made to the underwriting_model_data table by adding a new column to the table called "Date Uploaded". The date should be in the format MM-DD-YYYY.
        
        
2. **PROJECT PART #2: Create a Frontend Dashboard Using the Database Data from Part #1**:
    A). The project will utilize the database created in Part #1 to create a dashboard that will allow the user to view the data in the underwriting_model_data table. The dashboard should be created using the agent's recommended dashboard package and should have the following features:
        (I) A title for the dashboard;
        (II) A description of the dashboard;
        (III) A table that shows all the data in the underwriting_model_data table;
        (IV) A filter that allows the user to filter the data by file name, last modified date, sheet names, column names, property name, city, submarket, unit count, and deal stage;
        (V) A download button that allows the user to download the data in the underwriting_model_data table as an xlsx file;
        (VI) Query functionality that allows the user to query the data in the underwriting_model_data table by file name, last modified date, sheet names, column names, property name, city, submarket, unit count, and deal stage;
        (VII) A search bar that allows the user to search for specific data in the underwriting_model_data table;
        (VIII) A button that allows the user to refresh the data in the underwriting_model_data table;
        (IX) Ability to map the data in the underwriting_model_data table to a map based on the property name and latitude/longitude coordinates of the subject property, the rent comps, and the sales comps;
        (X) Aesthetic features that make the dashboard visually appealing, such as colors, fonts, and layout;
        (XI) A responsive design that adjusts to different screen sizes and orientations; and
        (XII) A mobile-friendly version of the dashboard that is optimized for mobile devices described in bullet 2(B) below.

    B). Create a mobile-friendly version, including all functionality, of the Frontend Dashboard from this part of the project (i.e., Part #2). The mobile-friendly version should have the following features:
        (I) The mobile-friendly version should have the same features as the desktop version, but should be optimized for mobile devices;
        (II) The mobile-friendly version should also have a responsive design that adjusts to different screen sizes and orientations;
        (III) The mobile-friendly version should have a simplified layout that is easy to navigate on a mobile device;
        (IV) The mobile-friendly version should have larger buttons and text that are easy to read and click on a mobile device;
        (V) The mobile-friendly version should have a simplified filter that allows the user to filter the data by file name, last modified date, sheet names, column names, property name, city, submarket, unit count, and deal stage; and
        (VI) The mobile-friendly version should have a simplified search bar that allows the user to search for specific data in the underwriting_model_data table.


**PROJECT GUIDELINES, FRAMEWORK, AND OUTPUT DETAILS**:
1. **User Software**:
    (I) Operating System: Windows 11 Professional;
    (II) IDE: Jupyter Notebooks within Visual Studio Code;
    (III) Programming Language: Python;
    (IV) Package/Environment Manager: Anaconda;
    (IV) AI LLM Platform: Claude/Claude Desktop;
    (V) Database: SQLite;
    (VI) Dashboard Package: Agent's recommended package);
    (VII) Data Visualization Package: Agent's recommended package;
    (V) Input Files and File Tyoes: Excel (".xlsb" and/or ".xlsm"); and
    (VI) Input File location(s): Windows Explorer Folders on my laptop.

2. **Project Directory**: 
    (I) Project Directory File Path: C:\Users\MattBorgeson\OneDrive - B&R Capital\Programming Projects\Underwriting Dashboard
    (II) Project Directory Prompt Folder Path: C:\Users\MattBorgeson\OneDrive - B&R Capital\Programming Projects\Underwriting Dashboard\Prompt
    (III) Project Directory Database Folder Path: C:\Users\MattBorgeson\OneDrive - B&R Capital\Programming Projects\Underwriting Dashboard\Database
    (IV) Project Directory Reference File Path: C:\Users\MattBorgeson\OneDrive - B&R Capital\Programming Projects\Underwriting Dashboard\Prompt\Underwriting Dashboard Project - Cell Value References.xlsx

3. **Key Requirements**:
    (I) Prior to providing the code to achieve the project objectives, the agent should provide a high-level overview of the code and how it will work to achieve the project objectives.
        (i) This overview should include a description of the key components of the code, how they will work together, and any assumptions or limitations of the code.
        (ii) The agent should also provide a brief explanation of the key packages and libraries that will be used in the code, as well as any relevant documentation or resources for those packages and libraries;
        (iii) The agent should also provide a brief explanation of the key packages and libraries that will be used in the code, as well as any relevant documentation or resources for those packages and libraries, which should be included in a README file in the project directory;
        (iv) The agent should provide a recommended project directory structure for the project, including the folders to add, the files to include in each folder, and any other relevant details about the project directory structure; and
        (v) The agent should provide a recommended package list for the project, including the version numbers of each package, and any relevant documentation or resources for those packages, which should be included in a requirements.txt file in the project directory.
    (II) The code should be well-commented and include docstrings for all functions and classes;
    (III) The code should be modular and organized into functions and classes, with a clear structure and flow;
    (IV) The code should be efficient and optimized for performance, with a focus on speed and memory usage;
    (V) The code should be robust and handle errors gracefully, with appropriate error messages and logging;
    (VI) The code should be tested and validated to ensure it works as expected, with appropriate test cases and test data;
    (VII) The code should be easy to read and understand, with a focus on clarity and simplicity;
    (VIII) The code should be flexible and extensible, with a focus on reusability and maintainability; and
    (IX) The code should be compatible with the latest version of Python and the packages used in the project.

4. **Provide Essential Context**:
    (I) Contextualize the project by providing background information on the purpose and goals of the project based upon the information provided above; and
    (II) Include any relevant details about the data, such as its structure, format, and any specific requirements for processing or analysis.

5. **Determine the Interaction Style**:
    (I) Specify how the agent should interact with the user, including whether it should ask clarifying questions, provide suggestions, or offer explanations:
        (i) The agent should ask clarifying questions to ensure it understands the project objectives and requirements;
        (ii) The agent should provide suggestions and explanations to help the user understand the code and how it works;
        (iii) The agent should provide examples and explanations to help the user understand the code and how it works; and
        (iv) The agent should provide responses that are very detailed and explanatory in nature, as the user is not a programmer and will need to understand the code in order to use it effectively.
    (II) The agent should also provide a summary of the key points and takeaways from the project, as well as any next steps or recommendations for the user.

6. **Outline Feedback and Iteration Processes**:
    (I) The agent should request feedback on the code and the project as a whole, including any suggestions for improvements or changes whenever possible;
    (II) The agent should provide a mechanism for the user to provide feedback on the code and the project as a whole, including any suggestions for improvements or changes whenever possible;
    (III) The agent should provide recommendations for how to iterate on the project and improve the code and the project as a whole, including any suggestions for improvements or changes whenever possible;
    (IV) The agent should provide the user recommendations for how to improve the prompt to make it more effective and efficient, including any suggestions for improvements or changes whenever possible;

7. **Business Context**:
    (I) Primary Business Context: The project is being developed for B&R Capital, a real estate investment firm that specializes in underwriting and analyzing real estate deals. The project is intended to streamline the underwriting process and improve the efficiency of the firm's operations.
    (II) Secondary Business Context: The project is also intended to provide a dashboard that allows the firm to view and analyze the data in the underwriting_model_data table, which will increase the efficiency of accessing data points both previously underwritten deals and current/active deals.

8. **Iterative Refinement**:
    (I) The agent should review the draft prompt to ensure it effective, efficient, clear, and comprehensive.
    (II) The agent should consider testing the prompt in a small-scale setting to identify any potential improvements.
    
9.

"""