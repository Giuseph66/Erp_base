FROM postgres:15-alpine

# Install additional extensions if needed
RUN apk add --no-cache postgresql-contrib

# Set environment variables
ENV POSTGRES_INITDB_ARGS="--encoding=UTF8 --lc-collate=C --lc-ctype=C"

# Copy initialization scripts
COPY init/ /docker-entrypoint-initdb.d/

# Expose PostgreSQL port
EXPOSE 5432
