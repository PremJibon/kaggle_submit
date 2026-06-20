FROM node:16-alpine

WORKDIR /app

# Copy package.json first for better caching
COPY package.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3000

# Run the application
CMD ["npm", "start"]