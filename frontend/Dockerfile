FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (ignore peer deps conflict)
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Optional: fix vulnerabilities
RUN npm audit fix --force

# Build the app
RUN npm run build

# Expose port
EXPOSE 3000

# Start the app in preview mode (serves built files)
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]