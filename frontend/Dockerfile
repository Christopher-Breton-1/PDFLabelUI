FROM node:23.5-slim

# set working directory
WORKDIR /app

# copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# copy the app code into the container
COPY . .

# expose the frontend port
EXPOSE 5174

# run the frontend server
CMD ["npm", "run", "dev"]