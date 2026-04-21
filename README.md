# RoomSync

## Our Project
RoomSync is a data-driven web application designed to streamline the apartment search process for students and young professionals. In today's competitive rental market, finding housing near a university is stressful, time-consuming, and fragmented across multiple platforms. RoomSync tackles these challenges by creating a centralized platform that connects renters, landlords, and brokers in one place.

At its core, RoomSync leverages user preferences and dealbreakers to provide personalized listing recommendations based on what renters actually want. The app continuously matches available listings to renter profiles, filters out dealbreakers, and surfaces the most relevant options first. Whether for students looking for housing near campus, landlords managing multiple properties, or brokers tracking listing performance, RoomSync offers a smart, intuitive interface that makes the rental process easier for everyone.

## Our Team
Kiswa Khan, Sean Walker Sydnee Goulet, Sitong Wu, Evan LiVigni,

## How to Build the Containers


1. Make sure you have your choice of IDE and Docker open.
2. Clone this repo.
3. Fill in the .env file with DB_NAME=roomsync and then your choice for the SECRET_KEY and MYSQL_ROOT_PASSWORD
4. Then run `docker compose down -v` (only if there is an old version of the container in Docker) 
5. Then run `docker compose up --build` 

## Running Instructions:
Frontend: http://localhost:8501  
Backend: http://localhost:4000 

## Video Demo
https://drive.google.com/file/d/1retIP9FSgp-ZkX_82nYjZnI2psjVKK_h/view?usp=sharing