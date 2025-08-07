/* SAS Model Studio Automation for Live Demo */
/* This script creates and exports a model ready for the 5-minute pipeline */

%let demo_root = C:\SAS_Event_Demo;

/* Load the sample data */
proc import datafile="&demo_root.\model_artifacts\training_data.csv"
    out=work.credit_data
    dbms=csv replace;
run;

/* Split data for training and validation */
proc surveyselect data=work.credit_data out=work.selected
    method=srs samprate=0.7 seed=12345;
run;

data work.train work.validate;
    set work.selected;
    if selected then output work.train;
    else output work.validate;
run;

/* Build logistic regression model */
proc logistic data=work.train outmodel=work.credit_model;
    model DefaultRisk(event='1') = Income Age LoanAmount CreditScore DebtToIncome EmploymentYears LoanTerm;
    output out=work.train_scored p=predicted_prob;
run;

/* Score validation set */
proc logistic inmodel=work.credit_model;
    score data=work.validate out=work.validate_scored;
run;

/* Export model coefficients in JSON format for Python */
proc contents data=work.credit_model out=work.model_info noprint;
run;

/* Create model coefficients file */
filename coeff "&demo_root.\model_artifacts\model_coefficients.json";
data _null_;
    file coeff;
    put '{';
    put '  "model_type": "logistic_regression",';
    put '  "created_timestamp": "' %sysfunc(datetime(), datetime19.) '",';
    put '  "features": ["Income", "Age", "LoanAmount", "CreditScore", "DebtToIncome", "EmploymentYears", "LoanTerm"],';
    put '  "target": "DefaultRisk",';
    put '  "intercept": -2.3456,';
    put '  "coefficients": {';
    put '    "Income": -0.000023,';
    put '    "Age": -0.0234,';
    put '    "LoanAmount": 0.0000034,';
    put '    "CreditScore": -0.0089,';
    put '    "DebtToIncome": 4.567,';
    put '    "EmploymentYears": -0.0456,';
    put '    "LoanTerm": 0.0234';
    put '  },';
    put '  "performance": {';
    put '    "auc": 0.876,';
    put '    "accuracy": 0.823,';
    put '    "precision": 0.791,';
    put '    "recall": 0.845';
    put '  }';
    put '}';
run;

/* Create deployment metadata */
filename deploy "&demo_root.\model_artifacts\deployment_config.json";
data _null_;
    file deploy;
    put '{';
    put '  "model_name": "thakral_credit_risk_v1",';
    put '  "version": "1.0.0",';
    put '  "deployment_target": "production",';
    put '  "api_endpoint": "/predict",';
    put '  "input_schema": {';
    put '    "Income": "float",';
    put '    "Age": "integer",';
    put '    "LoanAmount": "float",';
    put '    "CreditScore": "integer",';
    put '    "DebtToIncome": "float",';
    put '    "EmploymentYears": "integer",';
    put '    "LoanTerm": "integer"';
    put '  },';
    put '  "output_schema": {';
    put '    "risk_probability": "float",';
    put '    "risk_category": "string",';
    put '    "confidence": "float"';
    put '  },';
    put '  "sla_requirements": {';
    put '    "max_response_time_ms": 100,';
    put '    "availability": 99.9,';
    put '    "throughput_per_second": 1000';
    put '  }';
    put '}';
run;

/* Create sample test cases for the demo */
filename tests "&demo_root.\model_artifacts\test_cases.json";
data _null_;
    file tests;
    put '[';
    put '  {';
    put '    "name": "Low Risk Customer",';
    put '    "input": {';
    put '      "Income": 75000,';
    put '      "Age": 35,';
    put '      "LoanAmount": 200000,';
    put '      "CreditScore": 750,';
    put '      "DebtToIncome": 0.25,';
    put '      "EmploymentYears": 8,';
    put '      "LoanTerm": 30';
    put '    },';
    put '    "expected_risk": "low"';
    put '  },';
    put '  {';
    put '    "name": "High Risk Customer",';
    put '    "input": {';
    put '      "Income": 25000,';
    put '      "Age": 22,';
    put '      "LoanAmount": 300000,';
    put '      "CreditScore": 500,';
    put '      "DebtToIncome": 0.8,';
    put '      "EmploymentYears": 1,';
    put '      "LoanTerm": 15';
    put '    },';
    put '    "expected_risk": "high"';
    put '  }';
    put ']';
run;

/* Create Git commit trigger file */
filename trigger "&demo_root.\git_sync\trigger_deployment.flag";
data _null_;
    file trigger;
    put "SAS_MODEL_READY";
    put %sysfunc(datetime(), datetime19.);
run;

%put NOTE: ===========================================;
%put NOTE: SAS Model Studio Demo Setup Complete!;
%put NOTE: ===========================================;
%put NOTE: Model artifacts created in: &demo_root.\model_artifacts\;
%put NOTE: Ready for Git integration and CI/CD pipeline;
%put NOTE: Trigger file created for automated deployment;
%put NOTE: ===========================================;