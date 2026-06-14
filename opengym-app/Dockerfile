FROM node:20-alpine AS builder

WORKDIR /app

COPY opengym-app/package.json opengym-app/package-lock.json ./
RUN npm ci

COPY opengym-app/ .

ARG NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
ENV NEXT_PUBLIC_FASTAPI_URL=$NEXT_PUBLIC_FASTAPI_URL

RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

# Docker sets HOSTNAME to the container ID; Next.js standalone binds to HOSTNAME, not HOST.
ENV HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
