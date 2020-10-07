cd /home/alp/deneme/doldur-frontend/doldur-backend
uwsgi_python3 --socket 0.0.0.0:3000 --protocol=http -w app:app
