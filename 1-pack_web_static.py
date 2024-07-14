#!/usr/bin/env bash
# A Bash script that sets up your web servers for the deployment of web_static

# Update package lists and install Nginx
apt-get update -y && apt-get install -y nginx

# Allow 'Nginx HTTP' through the firewall
ufw allow 'Nginx HTTP'

# Array of directories to be created
directories=(
    "/data/"
    "/data/web_static/"
    "/data/web_static/releases/"
    "/data/web_static/shared/"
    "/data/web_static/releases/test/"
)

# Create directories if they don't exist
for dir in "${directories[@]}"; do
    [ -d "$dir" ] || mkdir -p "$dir"
done

# Create a simple HTML file using a heredoc
cat > /data/web_static/releases/test/index.html << 'EOF'
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
ln -snf /data/web_static/releases/test/ /data/web_static/current

# Change ownership of the /data/ directory to the 'ubuntu' user and group
chown -R ubuntu:ubuntu /data/

# Create a custom 404 page using echo
echo "Ceci n'est pas une page" > /data/web_static/releases/test/404.html

# Configure Nginx to serve the content
cat > /etc/nginx/sites-available/default << 'EOL'
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

# Restart Nginx to apply the new configuration
service nginx restart
