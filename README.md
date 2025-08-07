 Step 1: Start the API Server

  cd /Users/husseinsrour/Downloads/sas-model-pipeline/model_pipeline
  docker-compose up -d

  Step 2: Verify API is Running

  # Check if container is running
  docker-compose ps

  # Test the health endpoint
  curl http://localhost:8080/health

  Step 3: Access the Demo Correctly

  Don't double-click the HTML file! Instead:

  Open in browser: http://localhost:8080

  This serves the demo through the API server, not as a static file.

  Step 4: Test the Mobile Form

  1. Click "Start Demo" - You should see the 40-second countdown
  2. Scan the QR code or click the QR code to access mobile interface
  3. Fill out the form with different values
  4. Submit - Now you should get different results based on your inputs

  Step 5: Test Different Scenarios

  Try these to verify it's working:

  Low Risk Customer:
  - Income: $120,000
  - Credit Score: 780
  - Debt Ratio: 20%
  - Age: 35
  - Employment: 10 years

  High Risk Customer:
  - Income: $35,000
  - Credit Score: 580
  - Debt Ratio: 60%
  - Age: 22
  - Employment: 1 year

  You should see dramatically different risk probabilities and interest rates.

  If the API Won't Start:

  # Stop and restart
  docker-compose down
  docker-compose up --build -d

  The key difference: http://localhost:8080 (API server) vs file:// (static file) - only the API server can provide dynamic, calculated results!

⏺ Update Todos