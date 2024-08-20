-- Creating the database
CREATE DATABASE IF NOT EXISTS HospitalManagement;
USE HospitalManagement;

-- Creating the table for Patients
CREATE TABLE Patients (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    DOB DATE NOT NULL,
    Address VARCHAR(255) NOT NULL,
    Phone VARCHAR(20) NOT NULL,
    InsuranceInfo VARCHAR(255)
);

-- Creating the table for Doctors
CREATE TABLE Doctors (
    DoctorID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Specialization VARCHAR(100) NOT NULL,
    Schedule TEXT NOT NULL
);

-- Creating the table for Appointments
CREATE TABLE Appointments (
    AppointmentID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    DoctorID INT NOT NULL,
    Date DATE NOT NULL,
    Time TIME NOT NULL,
    Purpose TEXT,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE CASCADE
);

-- Creating the table for Medical Records
CREATE TABLE MedicalRecords (
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    VisitDate DATE NOT NULL,
    Diagnosis TEXT NOT NULL,
    Treatment TEXT NOT NULL,
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE
);

-- Creating the table for Bills
CREATE TABLE Bills (
    BillID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    Date DATE NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    Status ENUM('Paid', 'Unpaid', 'Pending Insurance') DEFAULT 'Unpaid',
    FOREIGN KEY (PatientID) REFERENCES Patients(PatientID) ON DELETE CASCADE
);

-- Creating the table for Staff
CREATE TABLE Staff (
    StaffID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Role VARCHAR(100) NOT NULL,
    Department VARCHAR(100) NOT NULL
);

-- Creating the table for Inventory
CREATE TABLE Inventory (
    ItemID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Quantity INT DEFAULT 0,
    ReorderLevel INT NOT NULL
);

-- Creating additional tables to handle many-to-many relationships if necessary
-- For instance, a Doctor_Staff link table to associate doctors with their staff members if needed
CREATE TABLE Doctor_Staff (
    DoctorID INT NOT NULL,
    StaffID INT NOT NULL,
    PRIMARY KEY (DoctorID, StaffID),
    FOREIGN KEY (DoctorID) REFERENCES Doctors(DoctorID) ON DELETE CASCADE,
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID) ON DELETE CASCADE
);

-- Indexes to improve search performance
CREATE INDEX idx_patients_name ON Patients(Name);
CREATE INDEX idx_doctors_specialization ON Doctors(Specialization);
CREATE INDEX idx_appointments_date ON Appointments(Date);
CREATE INDEX idx_bills_status ON Bills(Status);
