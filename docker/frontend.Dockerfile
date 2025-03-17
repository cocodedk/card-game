FROM node:20

RUN apt-get update && apt-get install -y libnss3 libgbm1 libasound2
RUN apt-get install -y libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb

WORKDIR /app/frontend

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 3000
