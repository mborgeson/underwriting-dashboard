underwriting_dashboard_prompt_generator = """


### Underwriting Dashboard Prompt Template for Agent-Based Task Prompt Generation

**PROJECT OBJECTIVES**:
1. **Project Part #1: Identify Files in a Top-Level Directory that will be Read into a DataFrame, based upon meeting certain criteria, and then uploaded to a Database**:
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
    
    
    
    The DataFrame
    of the excel files to have their data pulled into a dataframe should be read into a dataframe and the data should be pulled from the excel files. The data that needs to be pulled from the excel files is provided further below in the prompt and broken out by the category of data (i.e., File Summary Data and Sheet Data Values):
            (ii) Sheet Data Values -- General Assumptions (Reference Structure -- "'Sheet Name'!Cell_Range_Start:Cell_Range_End"):
                1) Deal Name ('Assumptions (Summary)'!$D$6)
                2) Deal City ('Assumptions (Summary)'!$D$8)
                3) Deal State ('Assumptions (Summary)'!$D$9)
                4) Year Built ('Assumptions (Summary)'!$D$10)
                5) Year Renovated ('Assumptions (Summary)'!$D$11)
                6) Location Quality ('Assumptions (Summary)'!$D$13)
                7) Building Quality ('Assumptions (Summary)'!$D$14)
                8) Number of Units ('Assumptions (Summary)'!$G$7)                
                9) Average Unit SF ('Assumptions (Summary)'!$G$7)                                
                10) Number of Parking Spaces (Covered) ('Assumptions (Summary)'!$G$7)                
                11) Number of Parking Spaces (Uncovered) ('Assumptions (Summary)'!$G$7)                
                12) Individually-Metered ('Assumptions (Summary)'!$G$7)                                
                13) Current Owner ('Assumptions (Summary)'!$I$6)                
                14) Last Sale Date ('Assumptions (Summary)'!$D$7)                
                15) Last Sale Price ('Assumptions (Summary)'!$D$8)
                16) Last Sale Price per Unit ('Assumptions (Summary)'!$D$9)                
                17) Last Sale Cap Rate ('Assumptions (Summary)'!$D$10)
                18) Building Height ('Assumptions (Summary)'!$I$12)                
                19) Building Type ('Assumptions (Summary)'!$D$12)                
                20) Project Type ('Assumptions (Summary)'!$D$7)
                21) Number of Buildings ('Assumptions (Summary)'!$I$11)                
                22) Building Zoning ('Assumptions (Summary)'!$I$13)
                23) Land Area (Acres) ('Assumptions (Summary)'!$I$14)                
                24) Parcel Number ('Assumptions (Summary)'!$K$7)                
                25) Market (MSA) ('Assumptions (Summary)'!$M$7)                                
                26) Submarket Cluster (Covered) ('Assumptions (Summary)'!$M$8)                
                27) Submarket (Uncovered) ('Assumptions (Summary)'!$M$9)                
                28) County ('Assumptions (Summary)'!$M$10)
                29) Latitude ('Rent Comp Inputs'!:$K$44)
                30) Longitude ('Rent Comp Inputs'!:$L$44)
            (iii) Sheet Data Values -- NOI Assumptions (Reference Structure -- "'Sheet Name'!Cell_Range_Start:Cell_Range_End"):
                1) Refinance Period ('Assumptions (Summary)'!:$D$22)
                2) Exit Period ('Assumptions (Summary)'!:$D$23)
                3) Empirical Rent ('Assumptions (Summary)'!:$D$38)
                4) Rent PSF ('Assumptions (Summary)'!:$D$39)
                5) Gross Potential Rental Income ('Assumptions (Summary)'!:$D$42)
                6) Concessions ('Assumptions (Summary)'!:$D$43)
                7) Loss-to-Lease ('Assumptions (Summary)'!:$D$44)
                8) Vacancy Loss ('Assumptions (Summary)'!:$D$45)
                9) Bad Debts ('Assumptions (Summary)'!:$D$46)
                10) Other Loss ('Assumptions (Summary)'!:$D$47)
                11) Property Management Fee (%) ('Assumptions (Summary)'!:$D$48)
                12) Net Rental Income ('Assumptions (Summary)'!:$D$49)
                13) Parking Income ('Assumptions (Summary)'!:$D$52)
                14) Utility Income ('Assumptions (Summary)'!:$D$53)
                15) Storage Income ('Assumptions (Summary)'!:$D$54)
                16) Laundry Income ('Assumptions (Summary)'!:$D$55)
                17) Pet Income ('Assumptions (Summary)'!:$D$56)
                18) Other/Misc. Income ('Assumptions (Summary)'!:$D$57)
                19) Total Other Income ('Assumptions (Summary)'!:$D$58)
                20) Effective Gross Income ('Assumptions (Summary)'!:$D$60)
                21) Real Estate Taxes ('Assumptions (Summary)'!:$D$63)
                22) Other Expenses ('Assumptions (Summary)'!:$D$64)
                23) Property Insurance ('Assumptions (Summary)'!:$D$65)
                24) Utilities ('Assumptions (Summary)'!:$D$66)
                25) Staffing/Payroll ('Assumptions (Summary)'!:$D$67)
                26) Property Management Fee ('Assumptions (Summary)'!:$D$68)
                27) Repairs & Maintenance ('Assumptions (Summary)'!:$D$69)
                28) Turnover ('Assumptions (Summary)'!:$D$70)
                29) Contract Services ('Assumptions (Summary)'!:$D$71)
                30) Reserves for Replacement ('Assumptions (Summary)'!:$D$72)
                31) Admin, Legal & Security ('Assumptions (Summary)'!:$D$73)
                32) Advertising, Leasing & Marketing ('Assumptions (Summary)'!:$D$74)
                33) Total Operating Expenses ('Assumptions (Summary)'!:$D$75)
                34) Net Operating Income ('Assumptions (Summary)'!:$D$77)
                35) Net Operating Income Margin (%) ('Assumptions (Summary)'!:$D$78)
                36) Total Below-the-Line Expenses ('Assumptions (Summary)'!:$D$88)
                37) Net Income ('Assumptions (Summary)'!:$D$90)
                38) Net Income Margin (%) ('Assumptions (Summary)'!:$D$91)
                39) Revenue Growth Rate - Year #1 ('Assumptions (Summary)'!:$D$151)
                40) Revenue Growth Rate - Year #2 ('Assumptions (Summary)'!:$D$152)
                41) Revenue Growth Rate - Year #3 ('Assumptions (Summary)'!:$D$153)
                42) Revenue Growth Rate - Year #4 ('Assumptions (Summary)'!:$D$154)
                43) Revenue Growth Rate - Year #5 ('Assumptions (Summary)'!:$D$155)
                44) Revenue Growth Rate - Year #6 ('Assumptions (Summary)'!:$D$156)
                45) Revenue Growth Rate - Year #7 ('Assumptions (Summary)'!:$D$157)
                46) Revenue Growth Rate - Year #8 ('Assumptions (Summary)'!:$D$158)
                47) Revenue Growth Rate - Year #9 ('Assumptions (Summary)'!:$D$159)
                48) Revenue Growth Rate - Year #10 ('Assumptions (Summary)'!:$D$160)
                49) Revenue Growth Rate - Year #11 ('Assumptions (Summary)'!:$D$161)
                50) Other Income Growth Rate - Year #1 ('Assumptions (Summary)'!:$D$164)
                51) Other Income Growth Rate - Year #2 ('Assumptions (Summary)'!:$D$165)
                52) Other Income Growth Rate - Year #3 ('Assumptions (Summary)'!:$D$166)
                53) Other Income Growth Rate - Year #4 ('Assumptions (Summary)'!:$D$167)
                54) Other Income Growth Rate - Year #5 ('Assumptions (Summary)'!:$D$168)
                55) Other Income Growth Rate - Year #6 ('Assumptions (Summary)'!:$D$169)
                56) Other Income Growth Rate - Year #7 ('Assumptions (Summary)'!:$D$170)
                57) Other Income Growth Rate - Year #8 ('Assumptions (Summary)'!:$D$171)
                58) Other Income Growth Rate - Year #9 ('Assumptions (Summary)'!:$D$172)
                59) Other Income Growth Rate - Year #10 ('Assumptions (Summary)'!:$D$173)
                60) Other Income Growth Rate - Year #11 ('Assumptions (Summary)'!:$D$174)
                61) Operating Expense Growth Rate - Year #1 ('Assumptions (Summary)'!:$D$177)
                62) Operating Expense Growth Rate - Year #2 ('Assumptions (Summary)'!:$D$178)
                63) Operating Expense Growth Rate - Year #3 ('Assumptions (Summary)'!:$D$179)
                64) Operating Expense Growth Rate - Year #4 ('Assumptions (Summary)'!:$D$180)
                65) Operating Expense Growth Rate - Year #5 ('Assumptions (Summary)'!:$D$181)
                66) Operating Expense Growth Rate - Year #6 ('Assumptions (Summary)'!:$D$182)
                67) Operating Expense Growth Rate - Year #7 ('Assumptions (Summary)'!:$D$183)
                68) Operating Expense Growth Rate - Year #8 ('Assumptions (Summary)'!:$D$184)
                69) Operating Expense Growth Rate - Year #9 ('Assumptions (Summary)'!:$D$185)
                70) Operating Expense Growth Rate - Year #10 ('Assumptions (Summary)'!:$D$186)
                71) Operating Expense Growth Rate - Year #11 ('Assumptions (Summary)'!:$D$187)
                72) Real Estate Tax Expense Growth Rate - Year #1 ('Assumptions (Summary)'!:$D$190)
                73) Real Estate Tax Expense Growth Rate - Year #2 ('Assumptions (Summary)'!:$D$191)
                74) Real Estate Tax Expense Growth Rate - Year #3 ('Assumptions (Summary)'!:$D$192)
                75) Real Estate Tax Expense Growth Rate - Year #4 ('Assumptions (Summary)'!:$D$193)
                76) Real Estate Tax Expense Growth Rate - Year #5 ('Assumptions (Summary)'!:$D$194)
                77) Real Estate Tax Expense Growth Rate - Year #6 ('Assumptions (Summary)'!:$D$195)
                78) Real Estate Tax Expense Growth Rate - Year #7 ('Assumptions (Summary)'!:$D$196)
                79) Real Estate Tax Expense Growth Rate - Year #8 ('Assumptions (Summary)'!:$D$197)
                80) Real Estate Tax Expense Growth Rate - Year #9 ('Assumptions (Summary)'!:$D$198)
                81) Real Estate Tax Expense Growth Rate - Year #10 ('Assumptions (Summary)'!:$D$199)
                82) Real Estate Tax Expense Growth Rate - Year #11 ('Assumptions (Summary)'!:$D$200)
                83) Insurance Expense Growth Rate - Year #1 ('Assumptions (Summary)'!:$D$203)
                84) Insurance Expense Growth Rate - Year #2 ('Assumptions (Summary)'!:$D$204)
                85) Insurance Expense Growth Rate - Year #3 ('Assumptions (Summary)'!:$D$205)
                86) Insurance Expense Growth Rate - Year #4 ('Assumptions (Summary)'!:$D$206)
                87) Insurance Expense Growth Rate - Year #5 ('Assumptions (Summary)'!:$D$207)
                88) Insurance Expense Growth Rate - Year #6 ('Assumptions (Summary)'!:$D$208)
                89) Insurance Expense Growth Rate - Year #7 ('Assumptions (Summary)'!:$D$209)
                90) Insurance Expense Growth Rate - Year #8 ('Assumptions (Summary)'!:$D$210)
                91) Insurance Expense Growth Rate - Year #9 ('Assumptions (Summary)'!:$D$211)
                92) Insurance Expense Growth Rate - Year #10 ('Assumptions (Summary)'!:$D$212)
                93) Insurance Expense Growth Rate - Year #11 ('Assumptions (Summary)'!:$D$213)
                94) Vacancy Loss - Year #1 ('Assumptions (Summary)'!:$D$216)
                95) Vacancy Loss - Year #2 ('Assumptions (Summary)'!:$D$217)
                96) Vacancy Loss - Year #3 ('Assumptions (Summary)'!:$D$218)
                97) Vacancy Loss - Year #4 ('Assumptions (Summary)'!:$D$219)
                98) Vacancy Loss - Year #5 ('Assumptions (Summary)'!:$D$220)
                99) Vacancy Loss - Year #6 ('Assumptions (Summary)'!:$D$221)
                100) Vacancy Loss - Year #7 ('Assumptions (Summary)'!:$D$222)
                101) Vacancy Loss - Year #8 ('Assumptions (Summary)'!:$D$223)
                102) Vacancy Loss - Year #9 ('Assumptions (Summary)'!:$D$224)
                103) Vacancy Loss - Year #10 ('Assumptions (Summary)'!:$D$225)
                104) Vacancy Loss - Year #11 ('Assumptions (Summary)'!:$D$226)
                105) Concessions - Year #1 ('Assumptions (Summary)'!:$D$229)
                106) Concessions - Year #2 ('Assumptions (Summary)'!:$D$230)
                107) Concessions - Year #3 ('Assumptions (Summary)'!:$D$231)
                108) Concessions - Year #4 ('Assumptions (Summary)'!:$D$232)
                109) Concessions - Year #5 ('Assumptions (Summary)'!:$D$233)
                110) Concessions - Year #6 ('Assumptions (Summary)'!:$D$234)
                111) Concessions - Year #7 ('Assumptions (Summary)'!:$D$235)
                112) Concessions - Year #8 ('Assumptions (Summary)'!:$D$236)
                113) Concessions - Year #9 ('Assumptions (Summary)'!:$D$237)
                114) Concessions - Year #10 ('Assumptions (Summary)'!:$D$238)
                115) Concessions - Year #11 ('Assumptions (Summary)'!:$D$239)
                116) Bad Debts - Year #1 ('Assumptions (Summary)'!:$D$242)
                117) Bad Debts - Year #2 ('Assumptions (Summary)'!:$D$243)
                118) Bad Debts - Year #3 ('Assumptions (Summary)'!:$D$244)
                119) Bad Debts - Year #4 ('Assumptions (Summary)'!:$D$245)
                120) Bad Debts - Year #5 ('Assumptions (Summary)'!:$D$246)
                121) Bad Debts - Year #6 ('Assumptions (Summary)'!:$D$247)
                122) Bad Debts - Year #7 ('Assumptions (Summary)'!:$D$248)
                123) Bad Debts - Year #8 ('Assumptions (Summary)'!:$D$249)
                124) Bad Debts - Year #9 ('Assumptions (Summary)'!:$D$250)
                125) Bad Debts - Year #10 ('Assumptions (Summary)'!:$D$251)
                126) Bad Debts - Year #11 ('Assumptions (Summary)'!:$D$252)
                127) Other Loss - Year #1 ('Assumptions (Summary)'!:$D$255)
                128) Other Loss - Year #2 ('Assumptions (Summary)'!:$D$256)
                129) Other Loss - Year #3 ('Assumptions (Summary)'!:$D$257)
                130) Other Loss - Year #4 ('Assumptions (Summary)'!:$D$258)
                131) Other Loss - Year #5 ('Assumptions (Summary)'!:$D$259)
                132) Other Loss - Year #6 ('Assumptions (Summary)'!:$D$260)
                133) Other Loss - Year #7 ('Assumptions (Summary)'!:$D$261)
                134) Other Loss - Year #8 ('Assumptions (Summary)'!:$D$262)
                135) Other Loss - Year #9 ('Assumptions (Summary)'!:$D$263)
                136) Other Loss - Year #10 ('Assumptions (Summary)'!:$D$264)
                137) Other Loss - Year #11 ('Assumptions (Summary)'!:$D$265)
            (iv) Sheet Data Values -- Debt and Equity Assumptions (Reference Structure -- "'Sheet Name'!Cell_Range_Start:Cell_Range_End"):
                1) Operating Cashflow - LP Hurdle Rate (%) ('Assumptions (Summary)'!:$D$306)
                2) Operating Cashflow - LP Profit Split (%) ('Assumptions (Summary)'!:$D$307)
                3) Liquidating Cashflow - LP Hurdle Rate (%) ('Assumptions (Summary)'!:$D$310)
                4) Liquidating Cashflow - LP Profit Split (%) ('Assumptions (Summary)'!:$D$311)
                5) Operating Cashflow - GP Catchup (%) ('Assumptions (Summary)'!:$D$314)
                6) Liquidating Cashflow - GP Catchup (%) ('Assumptions (Summary)'!:$D$315)
                7) Acquisition Fee (% of Total Acquisition Costs) ('Assumptions (Summary)'!:$D$320)
                8) Asset Management Fee (% of EGI) ('Assumptions (Summary)'!:$D$321)
                9) Senior Loan Originator ('Assumptions (Summary)'!:$D$343)
                10) Senior Interest Rate Structure (Fixed / Floating) ('Assumptions (Summary)'!:$D$344)
                11) Senior Loan Term (Years) ('Assumptions (Summary)'!:$D$345)
                12) Senior Interest Rate ('Assumptions (Summary)'!:$D$346)
                13) Senior Interest-Only Period (Years) ('Assumptions (Summary)'!:$D$348)
                14) Senior Amortization Period (Years) ('Assumptions (Summary)'!:$D$349)
                15) Senior Maximum DSCR ('Assumptions (Summary)'!:$D$350)
                16) Senior Loan - Lender Origination Fee (%) ('Assumptions (Summary)'!:$D$351)
                17) Senior Loan - Loan Broker Origination Fee (%) ('Assumptions (Summary)'!:$D$352)
                18) Senior Maximum LTPP ($) ('Assumptions (Summary)'!:$D$355)
                19) Senior Maximum LTPP (%) ('Assumptions (Summary)'!:$D$356)
                20) Senior Loan Renovation Funding ($) ('Assumptions (Summary)'!:$D$357)
                21) Senior Loan Renovation Funding (% Purchase Price) ('Assumptions (Summary)'!:$D$358)
                22) Total Senior Loan Amount ($) ('Assumptions (Summary)'!:$D$359)
                23) Total Senior Loan LTPP (%) ('Assumptions (Summary)'!:$D$360)
                24) Total Senior Loan LTPP + Renovation Costs (%) ('Assumptions (Summary)'!:$D$361)
                25) Senior Loan - Prepayment Structure ('Assumptions (Summary)'!:$D$364)
                26) Senior Loan - Prepayment (Prepay Structure #1) ('Assumptions (Summary)'!:$D$365)
                27) Senior Loan - Prepayment (Prepay Structure #2) ('Assumptions (Summary)'!:$D$366)
                28) Senior Loan - Servicing Fee ('Assumptions (Summary)'!:$D$367)
                29) Refinance - Yes/No ('Assumptions (Summary)'!:$D$371)
                30) Senior Refi Loan Originator ('Assumptions (Summary)'!:$D$372)
                31) Senior Refi Interest Rate Structure (Fixed / Floating) ('Assumptions (Summary)'!:$D$373)
                32) Senior Refi Loan Start (# Months after Close) ('Assumptions (Summary)'!:$D$374)
                33) Senior Refi Loan Term (Years) ('Assumptions (Summary)'!:$D$375)
                34) Senior Refi Interest Rate ('Assumptions (Summary)'!:$D$376)
                35) Senior Refi Interest-Only Period (Years) ('Assumptions (Summary)'!:$D$378)
                36) Senior Refi Amortization Period (Years) ('Assumptions (Summary)'!:$D$379)
                37) Refi Loan Maximum DSCR ('Assumptions (Summary)'!:$D$380)
                38) Lender - Closing Costs/Expenses ('Assumptions (Summary)'!:$D$381)
                39) Equity - Closing Costs/Expenses ('Assumptions (Summary)'!:$D$382)
                40) Senior Refi Loan Sizing - LTV Test - LTV (%) ('Assumptions (Summary)'!:$D$385)
                41) Senior Refi Loan Sizing - LTV Test - Cap Rate (%) ('Assumptions (Summary)'!:$D$386)
                42) Senior Refi Loan Sizing - LTV Test - NOI Calculation Method ('Assumptions (Summary)'!:$D$387)
                43) Senior Refi Loan Sizing - Senior Debt Yield Test (%) ('Assumptions (Summary)'!:$D$388)
                44) Senior Refi Loan Sizing - Coverage Test (DSCR) ('Assumptions (Summary)'!:$D$389)
                45) Senior Refi Loan Sizing - Coverage Test (Cap Rate) ('Assumptions (Summary)'!:$D$390)
                46) Senior Refi Loan Sizing - Coverage Test (Amortization Term) ('Assumptions (Summary)'!:$D$391)
                47) Senior Refi Loan Amount ($) ('Assumptions (Summary)'!:$D$394)
                48) Senior Refi Loan LTV (%) ('Assumptions (Summary)'!:$D$395)
                49) Senior Refi Loan - Prepayment Structure ('Assumptions (Summary)'!:$D$398)
                50) Senior Refi Loan - Prepayment (Prepay Structure #1) ('Assumptions (Summary)'!:$D$399)
                51) Senior Refi Loan - Prepayment (Prepay Structure #2) ('Assumptions (Summary)'!:$D$400)
                52) Senior Refi Loan - Servicing Fee ('Assumptions (Summary)'!:$D$401)
            (v) Sheet Data Values --  Acquisition Budget Assumptions (Reference Structure -- "'Sheet Name'!Cell_Range_Start:Cell_Range_End"):
                1) Purchase Price ('Assumptions (Summary)'!:$D$478)
                2) Other Land Cost ('Assumptions (Summary)'!:$D$479)
                3) Other Acquisition Cost ('Assumptions (Summary)'!:$D$480)
                4) Total Land and Acquisition Costs ('Assumptions (Summary)'!:$D$481)
                5) Deferred Maintenance - Interior ('Assumptions (Summary)'!:$D$484)
                6) Deferred Maintenance - Exterior ('Assumptions (Summary)'!:$D$485)
                7) Renovation Spend - Interior ('Assumptions (Summary)'!:$D$486)
                8) Renovation Spend - Exterior ('Assumptions (Summary)'!:$D$487)
                9) Reserves Funded at Close ('Assumptions (Summary)'!:$D$488)
                10) Total Hard Costs ('Assumptions (Summary)'!:$D$489)
                11) Internal Legal ('Assumptions (Summary)'!:$D$492)
                12) Business Plan ('Assumptions (Summary)'!:$D$493)
                13) Travel and Entertainment ('Assumptions (Summary)'!:$D$494)
                14) Placement Fee ('Assumptions (Summary)'!:$D$495)
                15) Insurance Premium ('Assumptions (Summary)'!:$D$496)
                16) Total Soft Costs ('Assumptions (Summary)'!:$D$497)
                17) Lender DD - PCA/Engineering/Phase I ('Assumptions (Summary)'!:$D$500)
                18) Lender DD - Appraisal ('Assumptions (Summary)'!:$D$501)
                19) Lender DD - Loan Application/Legal ('Assumptions (Summary)'!:$D$502)
                20) Lender DD - Insurance/Underwriting ('Assumptions (Summary)'!:$D$503)
                21) Lender Fee - Origination Fees ('Assumptions (Summary)'!:$D$504)
                22) Lender Closing - Lender Required Holdbacks ('Assumptions (Summary)'!:$D$505)
                23) Total Lender Closing Costs ('Assumptions (Summary)'!:$D$506)
                24) Equity DD - Interest Rate Cap/Swap ('Assumptions (Summary)'!:$D$509)
                25) Equity DD - PCA/Engineering ('Assumptions (Summary)'!:$D$510)
                26) Equity DD - Title Insurance/ALTA Survey ('Assumptions (Summary)'!:$D$511)
                27) Equity DD - Business Plan ('Assumptions (Summary)'!:$D$512)
                28) Equity DD - All Other ('Assumptions (Summary)'!:$D$513)
                29) Equity Fee - Acquisition and Other Fees ('Assumptions (Summary)'!:$D$514)
                30) Equity Reserves ('Assumptions (Summary)'!:$D$515)
                31) Total Closing Costs ('Assumptions (Summary)'!:$D$516)
                32) Total Development Budget ('Assumptions (Summary)'!:$D$518)
                33) Deferred Maintenance (Interior) - General ('Assumptions (Summary)'!:$D$633)
                34) [Deferred Maintenance - Interior Item #2] ('Assumptions (Summary)'!:$D$634)
                35) [Deferred Maintenance - Interior Item #3] ('Assumptions (Summary)'!:$D$635)
                36) [Deferred Maintenance - Interior Item #4] ('Assumptions (Summary)'!:$D$636)
                37) [Deferred Maintenance - Interior Item #5] ('Assumptions (Summary)'!:$D$637)
                38) [Deferred Maintenance - Interior Item #6] ('Assumptions (Summary)'!:$D$638)
                39) [Deferred Maintenance - Interior Item #7] ('Assumptions (Summary)'!:$D$639)
                40) [Deferred Maintenance - Interior Item #8] ('Assumptions (Summary)'!:$D$640)
                41) [Deferred Maintenance - Interior Item #9] ('Assumptions (Summary)'!:$D$641)
                42) [Deferred Maintenance - Interior Item #10] ('Assumptions (Summary)'!:$D$642)
                43) [Deferred Maintenance - Interior Item #11] ('Assumptions (Summary)'!:$D$643)
                44) [Deferred Maintenance - Interior Item #12] ('Assumptions (Summary)'!:$D$644)
                45) [Deferred Maintenance - Interior Item #13] ('Assumptions (Summary)'!:$D$645)
                46) [Deferred Maintenance - Interior Item #14] ('Assumptions (Summary)'!:$D$646)
                47) [Deferred Maintenance - Interior Item #15] ('Assumptions (Summary)'!:$D$647)
                48) [Deferred Maintenance - Interior Item #16] ('Assumptions (Summary)'!:$D$648)
                49) [Deferred Maintenance - Interior Item #17] ('Assumptions (Summary)'!:$D$649)
                50) [Deferred Maintenance - Interior Item #18] ('Assumptions (Summary)'!:$D$650)
                51) [Deferred Maintenance - Interior Item #19] ('Assumptions (Summary)'!:$D$651)
                52) [Deferred Maintenance - Interior Item #20] ('Assumptions (Summary)'!:$D$652)
                53) [Deferred Maintenance - Interior Item #21] ('Assumptions (Summary)'!:$D$653)
                54) [Deferred Maintenance - Interior Item #22] ('Assumptions (Summary)'!:$D$654)
                55) [Deferred Maintenance - Interior Item #23] ('Assumptions (Summary)'!:$D$655)
                56) [Deferred Maintenance - Interior Item #24] ('Assumptions (Summary)'!:$D$656)
                57) [Deferred Maintenance - Interior Item #25] ('Assumptions (Summary)'!:$D$657)
                58) [Deferred Maintenance - Interior Item #26] ('Assumptions (Summary)'!:$D$658)
                59) [Deferred Maintenance - Interior Item #27] ('Assumptions (Summary)'!:$D$659)
                60) [Deferred Maintenance - Interior Item #28] ('Assumptions (Summary)'!:$D$660)
                61) [Deferred Maintenance - Interior Item #29] ('Assumptions (Summary)'!:$D$661)
                62) [Deferred Maintenance - Interior Item #30] ('Assumptions (Summary)'!:$D$662)
                63) [Deferred Maintenance - Interior Item #31] ('Assumptions (Summary)'!:$D$663)
                64) [Deferred Maintenance - Interior Item #32] ('Assumptions (Summary)'!:$D$664)
                65) [Deferred Maintenance - Interior Item #33] ('Assumptions (Summary)'!:$D$665)
                66) [Deferred Maintenance - Interior Item #34] ('Assumptions (Summary)'!:$D$666)
                67) [Deferred Maintenance - Interior Item #35] ('Assumptions (Summary)'!:$D$667)
                68) [Deferred Maintenance - Interior Item #36] ('Assumptions (Summary)'!:$D$668)
                69) [Deferred Maintenance - Interior Item #37] ('Assumptions (Summary)'!:$D$669)
                70) [Deferred Maintenance - Interior Item #38] ('Assumptions (Summary)'!:$D$670)
                71) General Contractor Fee (DM - Interior) ('Assumptions (Summary)'!:$D$671)
                72) Construction Management Fee (DM - Interior) ('Assumptions (Summary)'!:$D$672)
                73) Total Deferred Maintenance - Interior ('Assumptions (Summary)'!:$D$673)
                74) Total Deferred Maintenance - Interior Per Unit ('Assumptions (Summary)'!:$D$674)
                75) Deferred Maintenance (Exterior) - Electrical ('Assumptions (Summary)'!:$D$677)
                76) Deferred Maintenance (Exterior) - Roofing ('Assumptions (Summary)'!:$D$678)
                77) [Deferred Maintenance - Exterior Item #3] ('Assumptions (Summary)'!:$D$679)
                78) [Deferred Maintenance - Exterior Item #4] ('Assumptions (Summary)'!:$D$680)
                79) [Deferred Maintenance - Exterior Item #5] ('Assumptions (Summary)'!:$D$681)
                80) [Deferred Maintenance - Exterior Item #6] ('Assumptions (Summary)'!:$D$682)
                81) [Deferred Maintenance - Exterior Item #7] ('Assumptions (Summary)'!:$D$683)
                82) [Deferred Maintenance - Exterior Item #8] ('Assumptions (Summary)'!:$D$684)
                83) [Deferred Maintenance - Exterior Item #9] ('Assumptions (Summary)'!:$D$685)
                84) [Deferred Maintenance - Exterior Item #10] ('Assumptions (Summary)'!:$D$686)
                85) [Deferred Maintenance - Exterior Item #11] ('Assumptions (Summary)'!:$D$687)
                86) [Deferred Maintenance - Exterior Item #12] ('Assumptions (Summary)'!:$D$688)
                87) [Deferred Maintenance - Exterior Item #13] ('Assumptions (Summary)'!:$D$689)
                88) [Deferred Maintenance - Exterior Item #14] ('Assumptions (Summary)'!:$D$690)
                89) [Deferred Maintenance - Exterior Item #15] ('Assumptions (Summary)'!:$D$691)
                90) [Deferred Maintenance - Exterior Item #16] ('Assumptions (Summary)'!:$D$692)
                91) [Deferred Maintenance - Exterior Item #17] ('Assumptions (Summary)'!:$D$693)
                92) [Deferred Maintenance - Exterior Item #18] ('Assumptions (Summary)'!:$D$694)
                93) [Deferred Maintenance - Exterior Item #19] ('Assumptions (Summary)'!:$D$695)
                94) [Deferred Maintenance - Exterior Item #20] ('Assumptions (Summary)'!:$D$696)
                95) [Deferred Maintenance - Exterior Item #21] ('Assumptions (Summary)'!:$D$697)
                96) [Deferred Maintenance - Exterior Item #22] ('Assumptions (Summary)'!:$D$698)
                97) [Deferred Maintenance - Exterior Item #23] ('Assumptions (Summary)'!:$D$699)
                98) [Deferred Maintenance - Exterior Item #24] ('Assumptions (Summary)'!:$D$700)
                99) [Deferred Maintenance - Exterior Item #25] ('Assumptions (Summary)'!:$D$701)
                100) [Deferred Maintenance - Exterior Item #26] ('Assumptions (Summary)'!:$D$702)
                101) [Deferred Maintenance - Exterior Item #27] ('Assumptions (Summary)'!:$D$703)
                102) [Deferred Maintenance - Exterior Item #28] ('Assumptions (Summary)'!:$D$704)
                103) [Deferred Maintenance - Exterior Item #29] ('Assumptions (Summary)'!:$D$705)
                104) [Deferred Maintenance - Exterior Item #30] ('Assumptions (Summary)'!:$D$706)
                105) [Deferred Maintenance - Exterior Item #31] ('Assumptions (Summary)'!:$D$707)
                106) [Deferred Maintenance - Exterior Item #32] ('Assumptions (Summary)'!:$D$708)
                107) [Deferred Maintenance - Exterior Item #33] ('Assumptions (Summary)'!:$D$709)
                108) [Deferred Maintenance - Exterior Item #34] ('Assumptions (Summary)'!:$D$710)
                109) [Deferred Maintenance - Exterior Item #35] ('Assumptions (Summary)'!:$D$711)
                110) [Deferred Maintenance - Exterior Item #36] ('Assumptions (Summary)'!:$D$712)
                111) [Deferred Maintenance - Exterior Item #37] ('Assumptions (Summary)'!:$D$713)
                112) [Deferred Maintenance - Exterior Item #38] ('Assumptions (Summary)'!:$D$714)
                113) General Contractor Fee (DM - Exterior) ('Assumptions (Summary)'!:$D$715)
                114) Construction Management Fee (DM - Exterior) ('Assumptions (Summary)'!:$D$716)
                115) Total Deferred Maintenance - Exterior ('Assumptions (Summary)'!:$D$717)
                116) Total Deferred Maintenance - Exterior Per Unit ('Assumptions (Summary)'!:$D$718)
                117) Total Demo Renovation Spend ('Assumptions (Summary)'!:$D$721)
                118) Total Painting Renovation Spend ('Assumptions (Summary)'!:$D$722)
                119) Total Lighting Renovation Spend ('Assumptions (Summary)'!:$D$723)
                120) Total Plumbing Renovation Spend ('Assumptions (Summary)'!:$D$724)
                121) Total Bathroom Renovation Spend ('Assumptions (Summary)'!:$D$725)
                122) Total Door & Finishes Renovation Spend ('Assumptions (Summary)'!:$D$726)
                123) Total Electrical Renovation Spend ('Assumptions (Summary)'!:$D$727)
                124) Total Window and Blinds Renovation Spend ('Assumptions (Summary)'!:$D$728)
                125) Total Cabinetry Renovation Spend ('Assumptions (Summary)'!:$D$729)
                126) Total Washer/Dryer Renovation Spend ('Assumptions (Summary)'!:$D$730)
                127) Total Flooring Renovation Spend ('Assumptions (Summary)'!:$D$731)
                128) Total Kitchen Appliances Renovation Spend ('Assumptions (Summary)'!:$D$732)
                129) Total Countertops Renovation Spend ('Assumptions (Summary)'!:$D$733)
                130) Final Cleaning Spend ('Assumptions (Summary)'!:$D$734)
                131) Total Appliance Installation Spend ('Assumptions (Summary)'!:$D$735)
                132) Total Tech Renovation Spend ('Assumptions (Summary)'!:$D$736)
                133) [Renovation Spend - Interior Item #16] ('Assumptions (Summary)'!:$D$737)
                134) [Renovation Spend - Interior Item #17] ('Assumptions (Summary)'!:$D$738)
                135) [Renovation Spend - Interior Item #15] ('Assumptions (Summary)'!:$D$739)
                136) [Renovation Spend - Interior Item #16] ('Assumptions (Summary)'!:$D$740)
                137) [Renovation Spend - Interior Item #17] ('Assumptions (Summary)'!:$D$741)
                138) [Renovation Spend - Interior Item #15] ('Assumptions (Summary)'!:$D$742)
                139) [Renovation Spend - Interior Item #16] ('Assumptions (Summary)'!:$D$743)
                140) [Renovation Spend - Interior Item #17] ('Assumptions (Summary)'!:$D$744)
                141) [Renovation Spend - Interior Item #15] ('Assumptions (Summary)'!:$D$745)
                142) [Renovation Spend - Interior Item #25] ('Assumptions (Summary)'!:$D$746)
                143) [Renovation Spend - Interior Item #26] ('Assumptions (Summary)'!:$D$747)
                144) [Renovation Spend - Interior Item #27] ('Assumptions (Summary)'!:$D$748)
                145) [Renovation Spend - Interior Item #28] ('Assumptions (Summary)'!:$D$749)
                146) [Renovation Spend - Interior Item #29] ('Assumptions (Summary)'!:$D$750)
                147) [Renovation Spend - Interior Item #30] ('Assumptions (Summary)'!:$D$751)
                148) [Renovation Spend - Interior Item #31] ('Assumptions (Summary)'!:$D$752)
                149) [Renovation Spend - Interior Item #32] ('Assumptions (Summary)'!:$D$753)
                150) [Renovation Spend - Interior Item #33] ('Assumptions (Summary)'!:$D$754)
                151) [Renovation Spend - Interior Item #34] ('Assumptions (Summary)'!:$D$755)
                152) [Renovation Spend - Interior Item #35] ('Assumptions (Summary)'!:$D$756)
                153) [Renovation Spend - Interior Item #36] ('Assumptions (Summary)'!:$D$757)
                154) [Renovation Spend - Interior Item #37] ('Assumptions (Summary)'!:$D$758)
                155) [Renovation Spend - Interior Item #38] ('Assumptions (Summary)'!:$D$759)
                156) General Contractor Fee (Renovation - Interior) ('Assumptions (Summary)'!:$D$760)
                157) Construction Management Fee (Renovation - Interior) ('Assumptions (Summary)'!:$D$761)
                158) Total Renovation Spend - Interior ('Assumptions (Summary)'!:$D$762)
                159) Total Renovation Spend - Interior Per Unit ('Assumptions (Summary)'!:$D$763)
                160) Renovation Spend - Exterior ('Assumptions (Summary)'!:$D$765)
                161) Exterior - Paint ('Assumptions (Summary)'!:$D$766)
                162) Exterior - Signage ('Assumptions (Summary)'!:$D$767)
                163) Exterior - Landscaping ('Assumptions (Summary)'!:$D$768)
                164) Exterior - Amazon Hub Lockers ('Assumptions (Summary)'!:$D$769)
                165) Exterior - Pool Area ('Assumptions (Summary)'!:$D$770)
                166) Exterior - Ramada/BBQ ('Assumptions (Summary)'!:$D$771)
                167) Exterior - Tree Trimming ('Assumptions (Summary)'!:$D$772)
                168) Exterior - Overall Landscaping ('Assumptions (Summary)'!:$D$773)
                169) Exterior - LED Site Lighting ('Assumptions (Summary)'!:$D$774)
                170) Exterior - Design Fee ('Assumptions (Summary)'!:$D$775)
                171) [Renovation Spend - Exterior Item #11] ('Assumptions (Summary)'!:$D$776)
                172) [Renovation Spend - Exterior Item #12] ('Assumptions (Summary)'!:$D$777)
                173) [Renovation Spend - Exterior Item #13] ('Assumptions (Summary)'!:$D$778)
                174) [Renovation Spend - Exterior Item #14] ('Assumptions (Summary)'!:$D$779)
                175) [Renovation Spend - Exterior Item #15] ('Assumptions (Summary)'!:$D$780)
                176) [Renovation Spend - Exterior Item #16] ('Assumptions (Summary)'!:$D$781)
                177) [Renovation Spend - Exterior Item #17] ('Assumptions (Summary)'!:$D$782)
                178) [Renovation Spend - Exterior Item #18] ('Assumptions (Summary)'!:$D$783)
                179) [Renovation Spend - Exterior Item #19] ('Assumptions (Summary)'!:$D$784)
                180) [Renovation Spend - Exterior Item #20] ('Assumptions (Summary)'!:$D$785)
                181) [Renovation Spend - Exterior Item #21] ('Assumptions (Summary)'!:$D$786)
                182) [Renovation Spend - Exterior Item #22] ('Assumptions (Summary)'!:$D$787)
                183) [Renovation Spend - Exterior Item #23] ('Assumptions (Summary)'!:$D$788)
                184) [Renovation Spend - Exterior Item #24] ('Assumptions (Summary)'!:$D$789)
                185) [Renovation Spend - Exterior Item #25] ('Assumptions (Summary)'!:$D$790)
                186) [Renovation Spend - Exterior Item #26] ('Assumptions (Summary)'!:$D$791)
                187) [Renovation Spend - Exterior Item #27] ('Assumptions (Summary)'!:$D$792)
                188) [Renovation Spend - Exterior Item #28] ('Assumptions (Summary)'!:$D$793)
                189) [Renovation Spend - Exterior Item #29] ('Assumptions (Summary)'!:$D$794)
                190) [Renovation Spend - Exterior Item #30] ('Assumptions (Summary)'!:$D$795)
                191) [Renovation Spend - Exterior Item #31] ('Assumptions (Summary)'!:$D$796)
                192) [Renovation Spend - Exterior Item #32] ('Assumptions (Summary)'!:$D$797)
                193) [Renovation Spend - Exterior Item #33] ('Assumptions (Summary)'!:$D$798)
                194) [Renovation Spend - Exterior Item #34] ('Assumptions (Summary)'!:$D$799)
                195) [Renovation Spend - Exterior Item #35] ('Assumptions (Summary)'!:$D$800)
                196) [Renovation Spend - Exterior Item #36] ('Assumptions (Summary)'!:$D$801)
                197) [Renovation Spend - Exterior Item #37] ('Assumptions (Summary)'!:$D$802)
                198) [Renovation Spend - Exterior Item #38] ('Assumptions (Summary)'!:$D$803)
                199) General Contractor Fee (Renovation - Exterior) ('Assumptions (Summary)'!:$D$804)
                200) Construction Management Fee (Renovation - Exterior) ('Assumptions (Summary)'!:$D$805)
                201) Total Renovation Spend - Exterior ('Assumptions (Summary)'!:$D$806)
                202) Total Renovation Spend - Exterior Per Unit ('Assumptions (Summary)'!:$D$807)
                203) Contingency (Deferred Maintenance - Interior) ('Assumptions (Summary)'!:$D$810)
                204) Contingency (Deferred Maintenance - Exterior) ('Assumptions (Summary)'!:$D$811)
                205) Contingency (Renovation - Interior) ('Assumptions (Summary)'!:$D$812)
                206) Contingency (Renovation - Exterior) ('Assumptions (Summary)'!:$D$813)
                207) [Reserves Funded at Close Item #5] ('Assumptions (Summary)'!:$D$814)
                208) [Reserves Funded at Close Item #6] ('Assumptions (Summary)'!:$D$815)
                209) [Reserves Funded at Close Item #7] ('Assumptions (Summary)'!:$D$816)
                210) [Reserves Funded at Close Item #8] ('Assumptions (Summary)'!:$D$817)
                211) [Reserves Funded at Close Item #9] ('Assumptions (Summary)'!:$D$818)
                212) [Reserves Funded at Close Item #10] ('Assumptions (Summary)'!:$D$819)
                213) Total Reserves Funded at Close ('Assumptions (Summary)'!:$D$820)
                214) Total Reserves Funded at Close Per Unit ('Assumptions (Summary)'!:$D$821)
                215) Total Hard Costs ('Assumptions (Summary)'!:$D$823)
                216) Total Hard Costs Per Unit ('Assumptions (Summary)'!:$D$824)
                217) Interest Rate Cap - Rate Cap Cost ('Assumptions (Summary)'!:$D$1012)
                218) Loan Rate Buydown (1.25% of the Loan Amount) ('Assumptions (Summary)'!:$D$1016)
                219) Other/Miscellaneous/Contingency ('Assumptions (Summary)'!:$D$1073)
            (vi) Sheet Data Values -- Property Returns Metrics (Reference Structure -- "'Sheet Name'!Cell_Range_Start:Cell_Range_End"):
                1) Purchase Price Return-on-Cost (At Close) ('Executive Summary'!$E$18)
                2) Total Return-on-Cost (At Close) ('Executive Summary'!$E$19)
                3) Trailing Cap Rate (At Close) ('Executive Summary'!$E$20)
                4) Market Cap Rate (At Close) ('Executive Summary'!$E$21)
                5) Basis/Unit (At Close) ('Executive Summary'!$E$22)
                6) Basis/SF (At Close) ('Executive Summary'!$E$23)
                7) Total Basis (At Close) ('Executive Summary'!$E$24)
                8) Purchase Price Return-on-Cost (At Exit) ('Executive Summary'!$F$18)
                9) Total Return-on-Cost (At Exit) ('Executive Summary'!$F$19)
                10) Trailing Cap Rate (At Exit) ('Executive Summary'!$F$20)
                11) Market Cap Rate (At Exit) ('Executive Summary'!$F$21)
                12) Basis/Unit (At Exit) ('Executive Summary'!$F$22)
                13) Basis/SF (At Exit) ('Executive Summary'!$F$23)
                14) Total Basis (At Exit) ('Executive Summary'!$F$24)
                15) T-12 Debt Yield (At Close) ('Executive Summary'!$J$18)
                16) Loan-to-Cost (At Close) ('Executive Summary'!$J$19)
                17) Loan-to-Value (At Close) ('Executive Summary'!$J$20)
                18) Basis/Unit (At Close) ('Executive Summary'!$J$21)
                19) Basis/SF (At Close) ('Executive Summary'!$J$22)
                20) Senior Debt Balance (At Close) ('Executive Summary'!$J$23)
                21) Senior Debt Refi Proceeds (At Close) ('Executive Summary'!$J$24)
                22) Refinance Coverage (At Close) ('Executive Summary'!$J$25)
                23) T-12 Debt Yield (At Exit) ('Executive Summary'!$K$18)
                24) Loan-to-Cost (At Exit) ('Executive Summary'!$K$19)
                25) Loan-to-Value (At Exit) ('Executive Summary'!$K$20)
                26) Basis/Unit (At Exit) ('Executive Summary'!$K$21)
                27) Basis/SF (At Exit) ('Executive Summary'!$K$22)
                28) Senior Debt Balance (At Exit) ('Executive Summary'!$K$23)
                29) Senior Debt Refi Proceeds (At Exit) ('Executive Summary'!$K$24)
                30) Refinance Coverage (At Exit) ('Executive Summary'!$K$25)
                31) Trended NOI - Year 5 ('Executive Summary'!:$Q$29)
                32) Cap Rate ('Executive Summary'!:$Q$30)
                33) Gross Sale Proceeds ('Executive Summary'!:$Q$31)
                34) Less: Transaction Costs ('Executive Summary'!:$Q$32)
                35) Less: Senior Debt ('Executive Summary'!:$Q$33)
                36) Less: Prepayment Penalty ('Executive Summary'!:$Q$34)
                37) Net Sale Proceeds ('Executive Summary'!:$Q$35)
                38) GP Disposition Fee ('Executive Summary'!:$Q$36)
                39) Net Sale Proceeds to Equity ('Executive Summary'!:$Q$37)
                40) Gross Sales Proceeds/B&R Capital Basis - Per Unit ($) ('Returns Metrics (Summary)'!$E$32)
                41) Unlevered Returns - IRR (%) ('Returns Metrics (Summary)'!$E$39)
                42) Unlevered Returns - MOIC (#) ('Returns Metrics (Summary)'!$E$40)
                43) Levered Returns - IRR (%) ('Returns Metrics (Summary)'!$E$43)
                44) Levered Returns - MOIC (#) ('Returns Metrics (Summary)'!$E$44)
            (vii) Sheet Data Values -- Equity Returns Metrics (Reference Structure -- "'Sheet Name'!Cell_Range_Start:Cell_Range_End"):
                1) Refi Proceeds, Net to Equity - Total ($) ('Returns Metrics (Summary)'!$E$86)
                2) Sale Period (Month) ('Returns Metrics (Summary)'!$E$88)
                3) Sales Proceeds, Net to Equity - Total ($) ('Returns Metrics (Summary)'!$E$89)
                4) Operating Cashflow ($) ('Returns Metrics (Summary)'!$E$92)
                5) Liquidating Cashflow ($) ('Returns Metrics (Summary)'!$E$93)
                6) Operating and Liquidating Cashflow - Total ($) ('Returns Metrics (Summary)'!$E$94)
                7) Operating Cashflow (%) ('Returns Metrics (Summary)'!$E$97)
                8) Liquidating Cashflow (%) ('Returns Metrics (Summary)'!$E$98)
                9) Operating and Liquidating Cashflow - Total ($) ('Returns Metrics (Summary)'!$E$99)
                10) LP Returns - IRR (%) ('Returns Metrics (Summary)'!$E$102)
                11) LP Returns - MOIC (#) ('Returns Metrics (Summary)'!$E$103)
                12) LP Returns - Pre-Refi Cash-on-Cash (%) ('Returns Metrics (Summary)'!$E$105)
                13) LP Returns - Post-Refi Cash-on-Cash (%) ('Returns Metrics (Summary)'!$E$106)
                14) LP Returns - Avg. Refi Cash-on-Cash (%) ('Returns Metrics (Summary)'!$E$107)
                15) LP Cashflow - Total Cash Outflow/Contribution ($) ('Returns Metrics (Summary)'!$E$109)
                16) LP Cashflow - Total Cash Inflow/Return ($) ('Returns Metrics (Summary)'!$E$110)
                17) LP Cashflow - Net Cashflow ($) ('Returns Metrics (Summary)'!$E$111)
                18) GP Cashflow - Total Cash Outflow/Contribution ($) ('Returns Metrics (Summary)'!$E$120)
                19) GP Cashflow - Total Cash Inflow/Return ($) ('Returns Metrics (Summary)'!$E$121)
                20) GP Cashflow - Net Cashflow ($) ('Returns Metrics (Summary)'!$E$122)
                21) GP Returns Including Fees - Avg. Annual Cashflow ($) ('Returns Metrics (Summary)'!$E$124)
            (viii) Sheet Data Values -- Rent Comps (Reference Structure -- "'Sheet Name'!Cell_Range_Start:Cell_Range_End"):







                
                
                            
    D). Next the dataframe should be stored in a SQLite database. The database should be named underwriting_models.db and the table should be named underwriting_models. The table should have the same columns as the dataframe.
        - The code should also check if the database already exists and if it does, it should append the new data to the existing table. If the database does not exist, it should create a new database and a new table.
            - 1) file_name, 2) last_modified_date, 3) number_of_sheets, 4) sheet_names, 5) number_of_rows, 6) number_of_columns, 7) column_names, and 8) data_types.
    - The code should also incorporate functionality to check monitor the deal folder directory, in real-time, for any new excel files that are added to the directory.
        - If a new excel file is added to the directory, the code should check if the excel file is an underwriting model and then check the last modification date. If both pass the criteria defined below, the data from the new excel file will be added it to the underwriting_models table in the SQLite database.
        - Also, the code should also be able to check for any changes in the last modified date of the existing excel files in the directory. If a change is detected, the code should automatically pull the data from the updated excel file and update the underwriting_models table in the SQLite database.
        
2. **Project Part #2: Create a Frontend Dashboard Using the Database Data from Part #1, to be incorporated into various parts of the Dashboard for Reviewing the Data, Visualizing the Data and Performing Analyses of the Data**:
    A). This part of the project will entail creating a dashboard that will allow the user to view the data in the underwriting_models table. The dashboard should be created using the agent's recommended dashboard package and should have the following features:
        1) A title for the dashboard, 2) A description of the dashboard, 3) A table that shows all the data in the underwriting_models table, 4) A filter that allows the user to filter the data by file_name, last_modified_date, number_of_sheets, sheet_names, number_of_rows, number_of_columns, column_names, and data_types, 5) A download button that allows the user to download the data in the underwriting_models table as a CSV file.
    B).
    
3. **Project Part #3: Create a mobile-friendly version, including all functionality, of the Frontend Dashboard from Part #2**:
    - A).
    


**PROJECT GUIDELINES, FRAMEWORK, AND OUTPUT DETAILS**:
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