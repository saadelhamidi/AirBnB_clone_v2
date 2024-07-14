#!/usr/bin/env bash
# A Bash script that sets up your web servers for the deployment of web_static

# Update and install Nginx
apt-get -y update
apt-get -y install nginx
ufw allow 'Nginx HTTP'

# Define the directories to be created
directories=(
    "/data/"
    "/data/web_static/"
    "/data/web_static/releases/"
    "/data/web_static/shared/"
    "/data/web_static/releases/test/"
)

# Create the directories if they don't exist
for dir in "${directories[@]}"; do
    [ -d "$dir" ] || mkdir -p "$dir"
done

# Create a simple HTML file
cat << 'EOF' > /data/web_static/releases/test/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple HTML Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
        }
        h1 {
            color: #333;
        }
        p {
            color: #666;
        }
    </style>
</head>
<body>

    <h1>Welcome to My test HTML Page</h1>

    <p>This is a basic HTML page.</p>
    <h2>My favorite programming languages are:</h2>
    <ul>
        <li>C</li>
        <li>Python</li>
        <li>HTML (for web markup)</li>
        <li>CSS (for web styling)</li>
        <li>SQL</li>
        <li>JavaScript (js)</li>
    </ul>

</body>
</html>
EOF

# Create a symbolic link to the test directory
ln -sf /data/web_static/releases/test/ /data/web_static/current

# Set ownership of the /data/ directory to ubuntu user and group
chown -R ubuntu:ubuntu /data/

# Create a custom 404 page
echo "Ceci n'est pas une page" > /data/web_static/releases/test/404.html

# Configure Nginx
cat << 'EOL' > /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    root /data/web_static/releases/test/;
    index index.html;

    location /redirect_me {
        return 301 http://localhost/new_page;
    }
    
    error_page 404 /404.html;
    location = /404.html {
        internal;
    }
    
    location /hbnb_static/ {
        alias /data/web_static/releases/test/;
    }

    location / {
        add_header X-Served-By "$hostname";
    }
}
EOL

# Restart Nginx to apply the changes
service nginx restart
