FROM node:24-slim
WORKDIR /app
COPY package*.json ./
RUN npm install --omit=dev --ignore-scripts
COPY server.mjs .
USER node
CMD ["node", "server.mjs"]
