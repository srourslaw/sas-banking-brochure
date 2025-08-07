/* SAS Event Demo - Windows Workspace Setup */
/* This script creates a proper workspace accessible by both SAS and Git */

/* Create main demo directory on C: drive */
%let demo_root = C:\SAS_Event_Demo;

/* Create directory structure */
options noxwait;
x "mkdir &demo_root.";
x "mkdir &demo_root.\sas_models";
x "mkdir &demo_root.\model_artifacts";
x "mkdir &demo_root.\git_sync";

/* Set up libnames for demo */
libname DEMO "&demo_root.\sas_models";
libname ARTIFACTS "&demo_root.\model_artifacts";

/* Create sample credit risk dataset for demo */
data DEMO.credit_sample;
    do customer_id = 1 to 1000;
        Income = rand('uniform') * 100000 + 25000;
        Age = int(rand('uniform') * 50) + 18;
        LoanAmount = rand('uniform') * 500000 + 50000;
        CreditScore = int(rand('uniform') * 350) + 450;
        DebtToIncome = rand('uniform') * 0.6 + 0.1;
        EmploymentYears = int(rand('uniform') * 25) + 0;
        LoanTerm = 15 + int(rand('uniform') * 3) * 15; /* 15, 30, or 45 years */
        
        /* Create realistic risk outcome */
        risk_score = (800 - CreditScore) * 0.01 + 
                     DebtToIncome * 50 + 
                     (LoanAmount / Income) * 10 +
                     (40 - Age) * 0.5 +
                     (10 - EmploymentYears) * 2;
        
        DefaultRisk = (risk_score > 30);
        output;
    end;
run;

/* Export to CSV for Python integration */
proc export data=DEMO.credit_sample
    outfile="&demo_root.\model_artifacts\training_data.csv"
    dbms=csv replace;
run;

/* Create model metadata file */
filename meta "&demo_root.\model_artifacts\model_info.txt";
data _null_;
    file meta;
    put "SAS Model Studio Credit Risk Model";
    put "Created: " %sysfunc(datetime(), datetime19.);
    put "Features: Income,Age,LoanAmount,CreditScore,DebtToIncome,EmploymentYears,LoanTerm";
    put "Target: DefaultRisk";
    put "Model Type: Logistic Regression";
    put "Workspace: &demo_root.";
run;

/* Print success message */
%put NOTE: Demo workspace created at &demo_root.;
%put NOTE: SAS libraries DEMO and ARTIFACTS are now available;
%put NOTE: Sample data created with 1000 observations;
%put NOTE: Ready for Model Studio integration;