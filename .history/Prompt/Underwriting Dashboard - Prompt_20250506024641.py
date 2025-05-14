underwriting_dashboard_prompt_generator = """

### Underwriting Dashboard Prompt Template for Agent-Based Task Prompt Generation

**PROJECT OBJECTIVES**:
1. **PROJECT PART #1: Identify Files in a Top-Level Directory that will be Read into a DataFrame, based upon meeting certain criteria, and then uploaded to a Database**:
    A). To create a comprehensive system prompt that directs an intelligent agent to the specified excel files within a directory in order to pull specific information from only those excel files that are underwriting models.
    
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
        (IX) Aesthetic features that make the dashboard visually appealing, such as colors, fonts, and layout;
        (X) A responsive design that adjusts to different screen sizes and orientations; and
        (XI) A mobile-friendly version of the dashboard that is optimized for mobile devices described in bullet 2(B) below.

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
    (V) Input Files and File Tyoes: Excel (“.xlsx”, “.xlsb”, and/or “.xlsm")
    (VI) Input File location(s): Windows Explorer Folders on my laptop

1. **Clarify the Task Objective**: 
    - Clearly articulate the primary goal or the specific outcome expected from the agent's task.
    - Highlight the core problem or question the agent needs to address.

2. **Establish Key Requirements**:
    - Enumerate any crucial requirements or limitations for the agent's response, such as response length, format, or the inclusion/exclusion of certain types of information.
    - Outline the expected depth of detail or complexity in the response.

3. **Provide Essential Context**:
    - Offer relevant background or contextual information to ensure the agent's responses are accurate and pertinent.
    - Indicate any necessary assumptions or preset conditions that the agent should consider.

4. **Determine the Interaction Style**:
    - Define the desired tone and style for the agent's responses, whether it be professional, casual, instructional, or another specified tone.
    - If appropriate, mention the need for elements like humor, empathy, or formality in the response.

5. **Outline Feedback and Iteration Processes**:
    - Describe the method for evaluating the effectiveness of the agent's responses and the mechanism for providing feedback.
    - Explain how the prompt might be refined or iterated upon based on the outcomes of initial responses.

6. **Incorporate Examples**:
    - Provide example responses to illustrate the desired outcome clearly. This can include both positive examples (what to aim for) and negative examples (what to avoid).
    - Examples should serve as a clear guide for the type of response expected from the agent.

7. **Iterative Refinement**:
    - Review the draft prompt to ensure it aligns with the task objective and is clear and comprehensive.
    - Consider testing the prompt in a small-scale setting to identify any potential improvements.

### Example Meta-Prompt Creation:

- **Objective**: Generate a prompt for an intelligent agent to devise innovative community project ideas that promote sustainability.
- **Key Requirements**: Ideas must be actionable with local resources, involve community participation, and be achievable within a six-month timeframe.
- **Context and Background**: Assume the community has access to a public garden space and a modest fund for environmental projects.
- **Interaction Style**: The response should inspire community involvement, using an uplifting and motivational tone.
- **Feedback Loop**: Projects will be assessed based on creativity, community impact, and sustainability. Feedback will guide the refinement of future prompts.
- **Examples**: 
    - Desired response example: "Organize a 'green market' where local vendors and farmers can sell sustainably produced goods."
    - Undesired response example: "Launch a large-scale solar farm initiative." (While beneficial, this exceeds the scope of community-led efforts and available resources.)

####### Meta-Prompter Template Ends Here #######

Now remember to only return the prompt for the agent you're instructing. Nothing else

"""