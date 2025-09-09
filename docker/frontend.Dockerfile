# Stage 1: deps
FROM node:20-slim AS deps
WORKDIR /app
COPY apps/frontend/package.json apps/frontend/package-lock.json* ./
RUN npm ci

# Stage 2: builder
FROM node:20-slim AS builder
WORKDIR /app
COPY apps/frontend/package.json apps/frontend/package-lock.json* ./
RUN npm ci
COPY apps/frontend/ .
RUN npm run build

# Stage 3: runner (production)
FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
