# Multi-stage Dockerfile for RuangKita (K10)
# Stage 1: Base - Install all dependencies
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Test - Dedicated quality gate stage inside container
FROM base AS test
WORKDIR /app
COPY . .
ENV NODE_ENV=test
RUN npm test

# Stage 3: Runner (Production) - Lightweight and hardened runtime
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8000

# Security hardening: Use non-root user
RUN addgroup -S ruangkita && adduser -S ruangkita -G ruangkita

COPY package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

COPY --chown=ruangkita:ruangkita src/ ./src/
COPY --chown=ruangkita:ruangkita public/ ./public/

USER ruangkita

EXPOSE 8000

# Built-in healthcheck
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1:8000/health || exit 1

CMD ["node", "src/server.js"]
