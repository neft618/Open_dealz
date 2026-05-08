FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

ENV PATH=/app/node_modules/.bin:$PATH

COPY . .

CMD ["./node_modules/.bin/react-scripts", "start"]