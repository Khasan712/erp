FROM node:latest
WORKDIR /chat
COPY ./erp-canada-chat-server/* /chat
RUN npm install
COPY . .
EXPOSE 1221
CMD ["npm", "start"]