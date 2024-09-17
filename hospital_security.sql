CREATE DATABASE hospital_security;
use hospital_security;

CREATE TABLE Admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE Bolge (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ad VARCHAR(255) NOT NULL,
    tehlike_seviyesi INT NOT NULL
);
CREATE TABLE Personel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ad VARCHAR(255) NOT NULL,
    sure FLOAT NOT NULL,
    basari INT NOT NULL
);
CREATE TABLE OlayTuru (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tur VARCHAR(255) NOT NULL,
    carpan INT NOT NULL
);
CREATE TABLE Olay (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bolge_id INT,
    olay_turu_id INT,
    olay_siddeti INT,
    zaman INT,
    personel_id INT,
    mudahale_suresi FLOAT,
    basari INT,
    FOREIGN KEY (bolge_id) REFERENCES Bolge(id),
    FOREIGN KEY (olay_turu_id) REFERENCES OlayTuru(id),
    FOREIGN KEY (personel_id) REFERENCES Personel(id)
);

CREATE TABLE PersonelAtama (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personel_id INT,
    bolge_id INT,
    FOREIGN KEY (personel_id) REFERENCES Personel(id),
    FOREIGN KEY (bolge_id) REFERENCES Bolge(id)
);


