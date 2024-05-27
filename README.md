# DroneRacing

## Building and running the containers
1. Download the release files
2. Contact any team member to get the gcp_key.json file, and include it in both the "/api" and "/worker" directories. Without this file in both directories, the API and worker will not connect to the Cloud Storage bucket where files are stored.
3. Run <code>docker-compose build --no-cache</code>
4. Run <code>docker-compose up -d</code>

# Documentation
[Wiki](https://github.com/asmeneses/DroneRacing/wiki)
