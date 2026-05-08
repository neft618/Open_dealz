FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

ENV PATH=/app/node_modules/.bin:$PATH

COPY . .

CMD ["npx", "react-scripts", "start"]