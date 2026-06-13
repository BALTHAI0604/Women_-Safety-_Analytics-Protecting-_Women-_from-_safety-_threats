Project Title

Women Safety Analytics – Protecting Women from Safety Threats

Problem Statement

Women often face safety risks such as harassment, stalking, violence, and emergency situations in public and private environments. Existing safety solutions lack integrated features like real-time location tracking, instant SOS alerts, emergency contact notifications, and incident reporting. There is a need for a digital platform that helps women quickly seek assistance, share their location, report incidents, and improve personal safety through technology.

PROJECT OVERVIEW

The Women Safety Analytics System is a web-based application designed to enhance women's safety through real-time emergency support and safety monitoring. The system enables users to send SOS alerts, share live location details with trusted contacts, report incidents, receive emergency notifications, and access safety-related information. Administrators can monitor incidents, analyze safety trends, and generate reports to improve security awareness and emergency response.

PROJECT OBJECTIVES

Main Objective

To develop a secure and user-friendly Women Safety Analytics System that provides emergency assistance, location tracking, incident reporting, and safety analytics for women.

Specific Objectives

- Enable user registration and authentication.
- Manage emergency contacts.
- Provide one-click SOS alert functionality.
- Track and share live user location.
- Allow users to report safety incidents.
- Generate notifications and emergency alerts.
- Maintain incident history and reports.
- Provide analytics and safety statistics.
- Ensure privacy and security of user data.

MODULE LIST

User Module

The User Module provides functionalities that allow women users to access safety features.

Features

- User Registration
- User Login
- Profile Management
- Emergency Contact Management
- SOS Alert Activation
- Location Tracking
- Incident Reporting
- Notification Viewing
- Safety Report Viewing

Admin Module

The Admin Module manages the overall system and safety monitoring.

Features

- Admin Login
- User Management
- Incident Management
- Notification Management
- Analytics Report Generation
- System Monitoring

CRUD APIs

User APIs

Create

- Register User
- Add Emergency Contact
- Create SOS Alert
- Submit Incident Report

Read

- View User Profile
- View Emergency Contacts
- View Incident History
- View Notifications

Update

- Update Profile
- Update Emergency Contact

Delete

- Delete Emergency Contact
- Delete User Account

TABLE LIST

User

Field| Type
user_id| INT
name| VARCHAR
email| VARCHAR
password| VARCHAR
phone| VARCHAR

Emergency_Contact

Field| Type
contact_id| INT
user_id| INT
contact_name| VARCHAR
contact_phone| VARCHAR

SOS_Alert

Field| Type
alert_id| INT
user_id| INT
alert_time| DATETIME
status| VARCHAR

Incident_Report

Field| Type
report_id| INT
user_id| INT
incident_type| VARCHAR
description| TEXT

Location_History

Field| Type
location_id| INT
user_id| INT
latitude| DECIMAL
longitude| DECIMAL

Notification

Field| Type
notification_id| INT
user_id| INT
message| TEXT
status| VARCHAR

ER DIAGRAM DESIGN

Entities

- USER
- EMERGENCY_CONTACT
- SOS_ALERT
- INCIDENT_REPORT
- LOCATION_HISTORY
- NOTIFICATION
- ADMIN

Relationships

- USER manages EMERGENCY_CONTACT
- USER creates SOS_ALERT
- USER submits INCIDENT_REPORT
- USER generates LOCATION_HISTORY
- USER receives NOTIFICATION
- ADMIN manages USERS
- ADMIN monitors INCIDENT_REPORTS
- ADMIN sends NOTIFICATIONS

USE CASE DIAGRAM

+----------------------+
| Women Safety System  |
+----------------------+

USER
 ├── Register
 ├── Login
 ├── Manage Profile
 ├── Add Emergency Contact
 ├── Send SOS Alert
 ├── Share Location
 ├── Report Incident
 ├── View Notifications
 ├── View Reports
 └── Logout

ADMIN
 ├── Login
 ├── Manage Users
 ├── Manage Incidents
 ├── Send Notifications
 ├── View Analytics
 ├── Monitor Activities
 └── Logout

SQL SCHEMA CREATION

User Table

CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    phone VARCHAR(15)
);

Emergency_Contact Table

CREATE TABLE Emergency_Contact (
    contact_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    contact_name VARCHAR(100),
    contact_phone VARCHAR(15),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

SOS_Alert Table

CREATE TABLE SOS_Alert (
    alert_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    alert_time DATETIME,
    status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

Incident_Report Table

CREATE TABLE Incident_Report (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    incident_type VARCHAR(100),
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);

PAGE LAYOUTS

Home Page

- Welcome Message
- About System
- Login Button
- Register Button

Dashboard

- SOS Alert Section
- Emergency Contacts
- Incident Reports
- Notifications
- Safety Statistics

Profile Page

- User Information
- Contact Details
- Activity History

Admin Dashboard

- User Management
- Incident Monitoring
- Notification Management
- Analytics Reports

UI SCREENS

- Login Screen
- Registration Screen
- User Dashboard
- Emergency Contact Screen
- SOS Alert Screen
- Incident Reporting Screen
- Notification Screen
- Profile Screen
- Admin Dashboard

UI PROTOTYPE

Navigation Flow

Home
 │
 ├── Login
 │      │
 │      └── Dashboard
 │             │
 │             ├── Emergency Contacts
 │             ├── SOS Alert
 │             ├── Incident Report
 │             ├── Notifications
 │             └── Profile
 │
 └── Register
