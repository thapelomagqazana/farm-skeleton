# Use Node.js as base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy the project
COPY . .

# Build the React app
RUN npm run build

# Expose the frontend port
EXPOSE 5173

# Start the Vite server
CMD ["npm", "run", "preview"]
