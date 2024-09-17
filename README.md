
# Hospital Security Personnel Optimization

This project aims to dynamically optimize the deployment of security personnel in hospitals using an artificial intelligence application. The project utilizes genetic algorithms to assign security personnel to the most risky areas based on their response time and success in past incidents. The system continuously updates itself as new incidents and personnel data are added, ensuring the most efficient distribution of security personnel.

## Purpose and Scope of the Project

The goal of the project is to enhance the effectiveness and efficiency of security personnel in a hospital environment by:
- Analyzing the frequency and severity of incidents in different areas.
- Dynamically assigning personnel based on their past performance.
- Re-optimizing security distribution as new data is added.
- Managing personnel and incidents through a web-based interface.

This system aims to provide a quick and effective solution to the ever-changing security needs in a hospital setting.

## Setup and Installation Instructions

1. **Requirements:** Ensure the following requirements are installed on your system before running the project:
   - Python 3.7 or higher
   - `pip` package manager
   - MySQL (or any other SQL database compatible with the provided SQL script)

2. **Clone the Repository:** Clone this project to your local machine:
   ```bash
   git clone <repository-url>
   cd HospitalSecurityOptimization
   ```

3. **Create a Virtual Environment:** Create a virtual Python environment to isolate the project's dependencies:
   ```bash
   python -m venv venv
   ```

4. **Activate the Virtual Environment:** 
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS / Linux:
     ```bash
     source venv/bin/activate
     ```

5. **Install Dependencies:** Install the required packages from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

6. **Set Up the Database:** Use the provided SQL script to set up the database. Run the following command in your SQL database environment:
   ```sql
   source /path/to/hospital_security.sql;
   ```
   Make sure to update the database connection information in `app.py` to match your database configuration.

7. **Run the Project:** Start the web application by running the `app.py` file:
   ```bash
   python app.py
   ```

8. **Access the Web Interface:** Open a web browser and go to [http://localhost:5000](http://localhost:5000) to access the application.

## Requirements and Dependencies

The project requires the following Python packages:
- Flask
- numpy
- pandas
- sklearn
- matplotlib
- MySQL connector (or another SQL database connector if using a different database)

## Brief Overview of Project Functionality

This project provides a dynamic and automated deployment of hospital security personnel to effectively respond to incidents. Key features include:
- **Personnel and Incident Management:** Through the web interface, you can add new security personnel and regions. Incidents can also be recorded, and assignments will be automatically updated based on this information.
- **Genetic Algorithm:** Uses genetic algorithms to assign security personnel to regions based on their performance.
- **Performance Monitoring:** The system tracks response times and success rates of personnel and optimizes assignments based on this data.

## Contribution Guidelines (Optional)

If you wish to contribute to this project, please follow these steps:

1. Fork this repository.
2. Create a new branch for your feature (`git checkout -b feature/YourFeatureName`).
3. Commit your changes (`git commit -m "Added new feature"`).
4. Push the branch to this repository (`git push origin feature/YourFeatureName`).
5. Open a Pull Request.

All feedback and contributions are welcome!
