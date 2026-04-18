# Dependencies base stage
FROM node:18-alpine AS deps

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Development stage
FROM deps AS development

# Install su-exec for safe user switching and create app user
RUN apk add --no-cache su-exec && \
    addgroup -g 1001 appuser && \
    adduser -D -u 1001 -G appuser appuser && \
    mkdir -p /app/node_modules /app/.vite /app/.svelte-kit /tmp && \
    chown -R appuser:appuser /app

# Copy entrypoint script and make it executable
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy source code
COPY . .

# Clean cache thoroughly as root BEFORE setting user
RUN rm -rf /app/node_modules/.cache /app/.vite /app/.svelte-kit 2>/dev/null || true && \
    find /app -name "*.timestamp-*.mjs" -type f -delete 2>/dev/null || true

# Set proper permissions after copying all files
RUN chown -R appuser:appuser /app

# Use entrypoint script to handle permissions and user switching
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Expose development port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5173/ || exit 1

# Default command to run Vite
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

# Production build stage
FROM node:18-alpine AS production-build

# Create app user early for all operations
RUN addgroup -g 1001 appuser && \
    adduser -D -u 1001 -G appuser appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN chown appuser:appuser package*.json && \
    npm ci

# Copy source code
COPY . .

# Set proper permissions after copying all files
RUN chown -R appuser:appuser /app

USER appuser

# Clean cache and build the application
RUN rm -rf node_modules/.cache .vite && npm run build

# Production stage
FROM nginx:alpine AS production

# Copy built application from production-build stage
COPY --from=production-build /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create app user for nginx
RUN addgroup -g 1001 appuser && adduser -D -u 1001 -G appuser appuser

# Set proper permissions
RUN chown -R appuser:appuser /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx

USER appuser

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1