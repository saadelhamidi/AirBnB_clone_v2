#site.pp

$nginx=@(EOT)
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
      alias /data/web_static/current/;
    }

    location / {
EOT

$index='<html>
  <head>
  </head>
  <body>
    Holberton School
  </body>
</html>
'



exec { 'update':
  path     => '/usr/bin:/usr/sbin:/bin',
  command  => '/usr/bin/sudo apt -y update',
  provider => shell,
}

package { 'nginx':
  ensure => installed,
}

service { 'nginx':
  ensure  => running,
  enable  => true,
  require => Package['nginx'],
}

exec { 'ufw HTTP':
  path     => '/usr/bin:/usr/sbin:/bin',
  command  => '/usr/bin/sudo ufw allow "Nginx HTTP"',
  provider => shell,
}

file { '/etc/nginx/sites-available/default':
  ensure  => file,
  mode    => '0644',
  content => $nginx,
  require => Service['nginx'],
}

exec {'add content':
path     => '/usr/bin:/usr/sbin:/bin',
command  => 'echo -n "    add_header X-Served-By $($(echo hostname));\n    }\n}" | sudo tee -a /etc/nginx/sites-available/default',
provider => shell,
require  => File['/etc/nginx/sites-available/default'],
}

file { [ '/data', '/data/web_static', '/data/web_static/releases', '/data/web_static/shared', '/data/web_static/releases/test' ]:
  ensure => directory,
  owner  => 'ubuntu',
  group  => 'ubuntu',
  mode   => '0755',
}

file { '/data/web_static/releases/test/index.html':
  ensure  => file,
  owner   => 'ubuntu',
  group   => 'ubuntu',
  mode    => '0644',
  content => $index,
  require => File['/data/web_static/releases/test'],
}

file { '/data/web_static/releases/test/404.html':
  ensure  => file,
  owner   => 'ubuntu',
  group   => 'ubuntu',
  mode    => '0644',
  content => 'Ceci n\'est pas une page',
  require => File['/data/web_static/releases/test'],
}

file { '/data/web_static/current':
  ensure  => link,
  target  => '/data/web_static/releases/test',
  owner   => 'ubuntu',
  group   => 'ubuntu',
  require => File['/data/web_static/releases/test/index.html'],
}

exec { 'restart nginx':
  path     => '/usr/bin:/usr/sbin:/bin',
  command  => '/usr/bin/sudo service nginx restart',
  provider => shell,
}
