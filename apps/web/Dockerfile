FROM node:20-alpine

WORKDIR /app

COPY apps/web/package.json ./package.json
RUN npm install

COPY apps/web /app

ENV NEXT_TELEMETRY_DISABLED=1

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]
