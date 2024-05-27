# DroneRacing

## Building and running the containers
1. Download the release files
2. Download [gcp_key.json](https://uniandes-my.sharepoint.com/:u:/g/personal/j_arboleda_uniandes_edu_co/EXfYJPpQnMJDiO5H66HrtC8BuHx9cQgGwZSwHVmhT3OzAg?e=iJRtFa) file, and include it in both "/api" and "/worker" directories. With out this file in both directories, the backend and the worker will not be able to connect to the Cloud Storage bucket where files are stored.
3. Run <code>docker-compose build --no-cache</code>
4. Run <code>docker-compose up -d</code>

# Documentation
[Wiki](https://github.com/asmeneses/DroneRacing/wiki)
