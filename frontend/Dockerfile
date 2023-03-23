FROM node:latest
COPY ./erp-canada-chat-server/ /chat
WORKDIR /chat
RUN npm install
COPY . .
EXPOSE 1221
CMD ["npm", "start"]
