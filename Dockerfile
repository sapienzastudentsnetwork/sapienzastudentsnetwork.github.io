FROM hugomods/hugo:dart-sass-git-0.152.2

RUN apk add --no-cache nodejs npm

RUN git config --global --add safe.directory /app

# Copia i file del progetto nella directory /app
WORKDIR /app
COPY . .

# Install npm dependencies, update browserslist DB, and build Tailwind CSS
RUN npm install && npx update-browserslist-db@latest && npm run build

# Espone la porta per il server Hugo
EXPOSE 1313

# Comando per avviare il server di sviluppo Hugo
CMD ["hugo", "server", "--disableFastRender", "--bind", "0.0.0.0"]
