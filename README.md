# Docker + WinRM Demo

![Test](https://github.com/pkeech/Docker-WinRM-Demo/workflows/Test/badge.svg)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/pkeech/Docker-WinRM-Demo?include_prereleases)
![GitHub](https://img.shields.io/github/license/pkeech/Docker-WinRM-Demo)

<!-- ![Build](https://github.com/pkeech/Docker-WinRM-Demo/workflows/Build/badge.svg)
![Deploy](https://github.com/pkeech/Docker-WinRM-Demo/workflows/Deployment/badge.svg) -->

## Description

The App is to demonstrates how to create a WinRM conection between a Docker Container (Linux) to a Windows Server.

## Usage

1. Start the application with `Docker-Compose up -d` 
2. Navigate to `http://localhost:8080/`
3. Use the Web Interface to Run PowerShell Commands on the Remote System.

## Dependencies

| Dependency | Version | Description |
| --- | :---: | --- |
| Flask | 1.1.2 | Provides Web FrontEnd |
| PyWinRM | 0.4.1 | Python Module to Communicate with WinRM |
| uWSGI | 2.0.19.1 | Application | 
| NGINX | 1.18 | Server that hosts the Application |
