FROM node:18-bullseye-slim

WORKDIR /app

RUN corepack enable
RUN apt-get update \
  && apt-get install -y --no-install-recommends openssl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY pnpm-lock.yaml package.json pnpm-workspace.yaml ./
COPY server/package.json ./server/package.json
COPY server/prisma ./server/prisma

RUN pnpm install --frozen-lockfile --filter ./server...
RUN pnpm --filter ./server prisma:generate

COPY server ./server

ENV NODE_ENV=production
EXPOSE 5000

CMD ["pnpm", "--filter", "./server", "start"]
