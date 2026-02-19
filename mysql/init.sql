CREATE DATABASE IF NOT EXISTS projectdb;
USE projectdb;

CREATE TABLE IF NOT EXISTS readings (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) NOT NULL,
  metric VARCHAR(50) NOT NULL,
  value DECIMAL(10,2) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metric_created ON readings(metric, created_at);